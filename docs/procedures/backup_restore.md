# Backup and restore

## What is backed up, and where

| Copy | Where | Protects against | Needs |
|---|---|---|---|
| Local snapshot | `/var/data/backups/db_<UTC stamp>.sqlite3` (newest 14 kept) | bad deploy, bad migration, accidental delete | nothing |
| Offsite database | bucket `db/db_...sqlite3` (30 days kept) | losing the disk or the Render account | [GCS](gcs_bucket.md) |
| Offsite media | bucket `media/...` (mirrored, incremental) | same | GCS |
| Render disk snapshots | Render keeps automatic daily snapshots of persistent disks | disk corruption | nothing (dashboard) |
| Code | GitHub | everything in git | your private repo |

Snapshots use SQLite's online backup API, safe while the site serves requests. A plain file copy
of a WAL-mode database can be corrupt.

## Running a backup

```powershell
python manage.py backup_db                 # snapshot (+ offsite when GCS is configured)
python manage.py backup_db --dry-run
python manage.py backup_db --keep 30 --retention-days 60 --skip-media
```

## Automatic schedule

`.github/workflows/scheduled-tasks.yml` calls `POST /internal/run/backup/` every Monday 03:00 UTC (and
`costs` daily). It runs *inside the web service* because only that service sees the disk. Set up once:

```powershell
$token = .\env\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(40))"
gh variable set SITE_URL --body "https://your-domain.com"
$token | gh secret set TASK_TRIGGER_TOKEN
# and the same value on Render:
$env:TT = $token; .\env\Scripts\python.exe scripts\render_api.py env-set --service srv-xxxx TASK_TRIGGER_TOKEN --from-env TT
```

Test it: GitHub -> Actions -> **Scheduled tasks** -> *Run workflow* -> `backup`. A failing backup turns the run red.
Without the token the endpoint answers 403 to everyone (fail shut). Want it more often? Edit the cron line.

## Restore

**Practise this once on a throwaway copy before you need it.**

### From a local snapshot (Render shell)

1. Render -> service -> **Shell**.
2. `ls /var/data/backups/` and pick the snapshot.
3. Stop writes: dashboard -> **Suspend** the service (shell access ends; use a one-off job, or do steps 3-5 quickly from the shell and accept a short window).
4. `cp /var/data/data/db.sqlite3 /var/data/db_before_restore.sqlite3` (keep what you had)
5. `cp /var/data/backups/db_YYYYMMDD_HHMMSS.sqlite3 /var/data/data/db.sqlite3`; remove `db.sqlite3-wal` and `-shm` beside it.
6. Resume the service; `bootstrap_site` runs `migrate` on boot, bringing an older snapshot up to the current schema.

### From the bucket

Download `db/db_...sqlite3` (Cloud Console, or `gsutil cp`), upload it to the service
(Shell: `curl -o` from a short-lived signed URL, or put it in the bucket and fetch it there), then follow
the local steps. Media: copy `media/` objects back into `/var/data/media/`.

### Locally (to inspect production data)

Download a snapshot to `data/db.sqlite3`, run `python manage.py migrate`, `runserver`.
**A production snapshot contains real people's data**: keep it out of git (it is ignored) and off shared drives.

### If the disk was lost entirely

Re-create the service from the Blueprint (new disk), restore the newest bucket snapshot and media as above, redeploy.

## Retention policy

Local 14 snapshots; bucket 30 days (`--retention-days`); optional bucket lifecycle rule 90 days. Raise them
when the data becomes precious; the cost is pennies.
