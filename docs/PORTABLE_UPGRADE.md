# Upgrading a portable installation

This walkthrough upgrades a portable Local Time Tracker installation while
keeping every recorded period, report and preference. Every step uses
disposable folders and fictional activity, so nothing here touches real data.

The portable build stores its data inside its own folder, not in
`%LOCALAPPDATA%\LocalTimeTracker`. That is what makes an upgrade a file copy:
the application files come from the new release, and the data stays exactly
where it is.

## What a portable folder holds

A portable installation extracted from `LocalTimeTracker-<version>-portable-x64.zip`
looks like this once it has run:

```
<portable-folder>\
├── data\
│   ├── activity.db          recorded periods
│   └── preferences.json     sample interval and idle threshold
├── reports\                 generated HTML reports
├── config.json              personal category keywords
├── LocalTimeTracker.exe
├── portable.mode            marks the folder as a portable installation
└── ...                      remaining release files
```

`portable.mode` and the executable are the two files that must come from the
**new** release. Everything else under `data\`, `reports\` and `config.json`
is yours and must survive the upgrade untouched.

## Before you start

- Close the old portable installation. A running instance keeps the database
  open, and copying a database that is being written produces a corrupt file.
- Never run the installed version and a portable version at the same time.
  Both track independently and can record overlapping periods.
- Have both release ZIPs downloaded if you are upgrading more than one
  version. This walkthrough upgrades 1.3.0 as the current release; older
  versions work the same way.

## Step 1 — Stop the old installation

Open the old portable folder and run `LocalTimeTracker.exe`. Press **Stop**.
The badge returns to **Stopped** and the detail line says tracking is not
running. Close the window — closing also stops tracking, but pressing
**Stop** first makes the state unambiguous.

## Step 2 — Back up the old folder before touching anything

Copy the **entire** old portable folder to a backup location outside it. A
release ZIP does not include your data, so this copy is the only rollback.

```powershell
Copy-Item -Recurse -Path C:\demo-time-tracker -Destination C:\demo-time-tracker-backup
```

Verify the backup before continuing — a backup you have not read back is a
hope, not a backup:

```powershell
Get-FileHash -Algorithm SHA256 -Path C:\demo-time-tracker-backup\data\activity.db
```

Compare the hash with the same command run against the original file. The two
lines must match exactly. Then confirm the backup folder contains
`data\activity.db`, `data\preferences.json`, `config.json` and `reports\`
with the same sizes as the originals.

Observed on 12 October 2026, upgrading a disposable 1.3.0 portable folder on
WSL (Linux) with fictional data: the copied folder's `data` and `config.json`
compared byte-for-byte identical to the original (`diff -r` reported no
differences), and the release ZIP verified `LocalTimeTracker-1.3.0-portable-x64.zip:
OK` against `SHA256SUMS.txt`.

## Step 3 — Download and verify the new release

Open the [latest release](https://github.com/HafidIdrissi/Time-Tracker/releases/latest)
and download `LocalTimeTracker-<new-version>-portable-x64.zip` together with
`SHA256SUMS.txt`. Keep both in the same folder and check the ZIP before
extracting it:

```powershell
Get-FileHash -Algorithm SHA256 -Path LocalTimeTracker-<new-version>-portable-x64.zip
```

Compare the hash with the line for that exact filename in `SHA256SUMS.txt`.
A mismatch means the download is incomplete or corrupted — download it again,
do not extract it.

Observed on 12 October 2026: `SHA256SUMS.txt` for v1.3.0 lists
`7de28ed97a9ea2911c1213a81e730019536ce2d93b1ddc81d7d0c7202c058059 *LocalTimeTracker-1.3.0-portable-x64.zip`,
and `sha256sum -c` against the downloaded file reported `OK`.

## Step 4 — Extract the new release into a separate folder

Never extract over the old folder. Extract the verified ZIP to a new, empty
folder beside it:

```powershell
Expand-Archive -Path LocalTimeTracker-<new-version>-portable-x64.zip -DestinationPath C:\demo-time-tracker-new
```

The extracted folder has the application files and `config.example.json`, but
no `data\`, no `reports\`, and no `config.json`. That is expected — those come
from the old folder next.

## Step 5 — Carry your data into the new folder

Copy exactly three things from the old folder into the new one, keeping the
same names:

```powershell
Copy-Item -Recurse -Path C:\demo-time-tracker\data -Destination C:\demo-time-tracker-new\data
Copy-Item -Recurse -Path C:\demo-time-tracker\reports -Destination C:\demo-time-tracker-new\reports
Copy-Item -Path C:\demo-time-tracker\config.json -Destination C:\demo-time-tracker-new\config.json
```

`data\` contains `activity.db` and `preferences.json`; `reports\` contains
your generated HTML reports; `config.json` holds your personal category
keywords. Copy `config.json` only if you have one — without it the app falls
back to `config.example.json` and categories use the shipped defaults.

`portable.mode` comes from the extracted ZIP — the new release's copy — so
do not carry the old one over. Observed on 12 October 2026: after the copy,
the new folder's `data\activity.db`, `data\preferences.json` and
`config.json` compared identical to the old folder's, and `portable.mode`
was the new release's file.

## Step 6 — Start the new installation and confirm your data is there

Run `LocalTimeTracker.exe` in the new folder. The badge moves from
**Stopped** to **Starting…**, then to **Running**.

Confirm the data survived:

- **Reports and data** — open **Open reports folder**; your previous reports
  are listed. Open one generated before the upgrade: the periods in it match
  what you recorded on the old version.
- **Settings** — the sample interval and idle threshold match what the old
  folder's `preferences.json` held.
- **Categories** — your `config.json` keywords still categorize activity.

Generate one new report covering the date range of your fictional data to
prove both old and new recording work in the new folder.

## Step 7 — Retire the old folder only after the new one is proven

Keep the old folder and the backup from step 2 until you are satisfied with
the new installation. When you are, delete the old portable folder — but
keep the step 2 backup somewhere separate, since deleting the folder also
deletes its data.

## Rolling back

If the new version misbehaves, roll back without touching the backup:

1. Close the new installation (**Stop**, then close the window).
2. Copy the step 2 backup folder to a fresh location, or extract the backup
   ZIP if you made one:

   ```powershell
   Expand-Archive -Path demo-time-tracker-backup.zip -DestinationPath C:\demo-time-tracker-rollback
   ```

3. Run `LocalTimeTracker.exe` from the restored folder. The data, reports
   and preferences are exactly as they were before the upgrade.

Rolling back this way never writes into the backup folder, so a failed
rollback can be retried. Observed on 12 October 2026: restoring a disposable
backup and comparing the restored `data` and `config.json` against the
original reported no differences.

## Notes

- This walkthrough never overwrites the backup: the upgrade extracts the new
  release beside the old folder, and rollback reads the backup to a new
  location.
- All dates and observed results in this document come from disposable
  folders with fictional activity, run on WSL (Linux) against the real
  v1.3.0 release on 12 October 2026. The Windows paths and PowerShell
  commands are the supported user-facing form; the file-level operations —
  copy, checksum verify, extract, compare — were executed exactly as written
  using their Linux equivalents.
- Do not publish `activity.db`, personal reports, or screenshots that show
  real window titles. Window titles can contain private document names,
  searches, or mail subjects.
