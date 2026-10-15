---
name: backups-and-restore
description: >
  Back up and restore the site's SQLite database and uploaded media: local snapshots, offsite copies in a Google Cloud
  Storage bucket (project, bucket, service account), scheduled backups through GitHub Actions, retention, restore
  procedures, practising a restore, and disaster recovery. TRIGGER: "backup", "back up", "restore", "recover", "lost
  data", "disaster", "google cloud storage", "gcs", "bucket", "service account", "scheduled backup", "retention",
  "rollback the database".
---

# Backups and restore

Sources of truth: [docs/procedures/backup_restore.md](../../../docs/procedures/backup_restore.md) and [docs/procedures/gcs_bucket.md](../../../docs/procedures/gcs_bucket.md). Re-read them first.

## What exists

`python manage.py backup_db` writes a consistent SQLite snapshot (online backup API, safe under load) to `PERSISTENT_ROOT/backups/` (newest 14 kept). With `GCS_BUCKET` + `GCS_SERVICE_ACCOUNT` it also uploads the snapshot to `db/` in the bucket, mirrors `MEDIA_ROOT` to `media/`
(only new or changed files) and prunes bucket snapshots older than 30 days. **A snapshot on the same disk is not a backup against losing the disk**: recommend the bucket before real users arrive.

## Who does what

**The owner (Google Cloud, about 15 minutes, once):** create/choose a project with billing enabled; create a bucket (single region, Standard, **public access prevention ON**, uniform access); create a service account and grant it **Storage Object Admin on that bucket only**; create a JSON key;
base64-encode it into `.env` as `GCS_SERVICE_ACCOUNT` (command in the procedure doc), set `GCS_BUCKET`; then **delete the downloaded JSON file**. Optional: a bucket lifecycle rule (90 days).

**You:** move both values to Render (`env-set --from-env`), run `backup_db --dry-run` then `backup_db` (via `render_api.py job` or the scheduled workflow), confirm objects exist under `db/` and `media/`. Set up the schedule: generate `TASK_TRIGGER_TOKEN`, set it on Render and with `gh secret set`, `gh variable set SITE_URL`,
run `gh workflow run scheduled-tasks.yml -f task=backup` and watch it (`gh run watch`). A failing backup turns the run red.

## Restore (practise once on a throwaway before it matters)

Follow the procedure doc: take a fresh snapshot of the current database first; suspend writes; replace `/var/data/data/db.sqlite3` (remove `-wal`/`-shm`); resume (`bootstrap_site` migrates an older snapshot forward). Local snapshots first, bucket snapshots if the disk is gone;
total loss -> recreate the service from the Blueprint, restore the newest bucket snapshot and media. **Do restores only with the owner's go-ahead.**

## Privacy

Backups contain everything, including data people asked to delete, until they age out (30 days in the bucket): say so in the policy (the generated page does). Keep the bucket private. A production snapshot contains real people's data: never commit it, never share it.
