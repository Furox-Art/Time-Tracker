"""Disposable native Tk GUI smoke test on Windows. Validation branch only."""
from __future__ import annotations
import json
import shutil
import tempfile
import time
import urllib.request
import zipfile
from datetime import date, datetime, time as clocktime, timedelta
from pathlib import Path
import tkinter as tk

from timetracker.database import ActivityDatabase
from timetracker.models import ActivityState
import windows_app as appmod

RELEASE = "https://github.com/HafidIdrissi/Time-Tracker/releases/download/v1.3.0/LocalTimeTracker-1.3.0-portable-x64.zip"

def create_fixture(path: Path, z: zipfile.ZipFile, today: date) -> None:
    path.mkdir()
    z.extractall(path)
    (path / "data").mkdir(exist_ok=True)
    database = ActivityDatabase(path / "data" / "activity.db")
    start = datetime.combine(today, clocktime(hour=11,minute=0)).astimezone()
    end = start + timedelta(minutes=15)
    period = database.create_period(
        ActivityState(application="Fictional Editor",window_title="Fictional test activity",is_idle=False), start)
    database.update_period(period, start, end)
    database.close()
    (path / "preferences.json").write_text(json.dumps({"sample_seconds":"5","idle_minutes":"10"}))
    shutil.copyfile(path / "config.example.json",path / "config.json")
    (path / "reports").mkdir(exist_ok=True)
    (path / "reports" / "old-fictional-report.html").write_text("<p>fictional</p>")

def check_app(path: Path, today: date, generate: bool):
    appmod.APP_DIRECTORY = path
    appmod.DATABASE_PATH = path / "data" / "activity.db"
    appmod.REPORTS_DIRECTORY = path / "reports"
    root = tk.Tk()
    try:
        app = appmod.TimeTrackerApp(root)
        root.update_idletasks()
        # Do not record new activity: patch automatic start_tracking before this function.
        expected_sample, expected_idle = "5", "10"
        got = (app.interval_box.get(),app.idle_box.get())
        assert got == (expected_sample,expected_idle),("unexpected visible settings",got)
        assert app.status_text.get() == "Stopped", app.status_text.get()
        print("PASS native Tk controls: visible sample=5 seconds; idle=10 minutes",flush=True)
        db = ActivityDatabase(path / "data" / "activity.db")
        try:
            original = db.all_periods()
        finally:
            db.close()
        assert len(original)==1 and original[0].application=="Fictional Editor",original
        print("PASS native Tk copy: fictional fifteen-minute database period retained",flush=True)
        if generate:
            app.notebook.select(2)  # Reports and data tab
            app.report_date.set(today.isoformat())
            app.report_button.invoke()  # invoke actual Tk UI button handler
            report = path / "reports" / ("report-"+today.isoformat()+".html")
            deadline = time.monotonic()+20
            while time.monotonic()<deadline and not report.is_file():
                root.update()
                time.sleep(0.12)
            assert report.is_file(),"GUI-generated report missing"
            text = report.read_text(encoding="utf-8")
            assert "Fictional Editor" in text, "GUI-generated HTML lacks fictional activity"
            assert len(text)>1000
            print("PASS native Tk button: fictional 15-minute activity included in generated HTML report",flush=True)
    finally:
        root.destroy()

def main() -> None:
    # Native Windows test; never inspect the actual user's machine or activity.
    with tempfile.TemporaryDirectory(prefix="time-tracker-pr367-") as temp:
        parent=Path(temp)
        zip_path=parent/"release.zip"
        urllib.request.urlretrieve(RELEASE,zip_path)
        with zipfile.ZipFile(zip_path) as z:
            today=date.today()
            old=parent/"old"
            create_fixture(old,z,today)
            backup=parent/"backup"
            new=parent/"new"
            rollback=parent/"rollback"
            shutil.copytree(old,backup)
            new.mkdir()
            z.extractall(new)
            for name in ("data","reports","config.json","preferences.json"):
                source=old/name
                if source.exists():
                    if source.is_dir():shutil.copytree(source,new/name)
                    else:shutil.copyfile(source,new/name)
        # Test actual GUI values and button command, with tracking disabled
        # to avoid adding data to the fictional fixture.
        appmod.TimeTrackerApp.start_tracking=lambda self: None
        check_app(new,today,generate=True)
        shutil.copytree(backup,rollback)
        check_app(rollback,today,generate=False)
        assert (backup/"preferences.json").read_bytes()==(rollback/"preferences.json").read_bytes()
        assert (backup/"data"/"activity.db").read_bytes()==(rollback/"data"/"activity.db").read_bytes()
        print("PASS restored fresh copy retained GUI preferences and fictional activity",flush=True)
if __name__=="__main__":
    main()
