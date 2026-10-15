# Google Cloud Storage bucket

Used for **offsite backups** (default use) and, when you outgrow the 1 GB disk, as the place
for **user uploads**. "When needed": skip this until the site holds data you would hate to lose.

Free tier: roughly 5 GB-months of Standard storage in some US regions (verify current terms at
https://cloud.google.com/storage/pricing). Backups of a small SQLite site cost cents.

## Setup (humans, ~15 minutes, one time)

1. https://console.cloud.google.com -> same project as OAuth, or a new one. Enable **billing** (the free tier still requires a billing account).
2. **Cloud Storage -> Buckets -> Create**: a globally unique name (e.g. `my-site-backups-7342`),
   location a single region near you, class Standard, **"Enforce public access prevention" ON**,
   access control **Uniform**. (Nothing here should ever be public.)
3. **IAM & Admin -> Service accounts -> Create** (e.g. `site-backup`). Skip the optional role steps.
4. Open the bucket -> **Permissions -> Grant access**: principal = that service account's email,
   role **Storage Object Admin** (this bucket only; not project-wide).
5. Service account -> **Keys -> Add key -> JSON**. A file downloads. This is a credential: it never goes in git.
6. Base64-encode it into one line and put it in your clipboard / `.env`:
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("$HOME\Downloads\site-backup-key.json")) | Set-Clipboard
   ```
7. Set `GCS_BUCKET=<bucket name>` and `GCS_SERVICE_ACCOUNT=<the base64 line>` in local `.env` and on Render.
8. **Delete the downloaded JSON file** (the base64 copy in Render is now the only one).
9. Optional but recommended: bucket -> **Lifecycle** rule to delete objects older than 90 days, as a
   second line of retention behind `backup_db --retention-days`.

## Test

```powershell
.\env\Scripts\python.exe manage.py backup_db --dry-run     # says whether GCS is configured
.\env\Scripts\python.exe manage.py backup_db               # local snapshot + upload + media mirror
```
Then look in the bucket: `db/db_YYYYMMDD_HHMMSS.sqlite3` and `media/...`.

## Using the bucket for media (when the disk is too small)

Not wired by default (it pulls in heavy dependencies). When you need it:

1. Add `django-storages[google]` to `requirements.txt`.
2. In `settings.py`, when `GCS_MEDIA_BUCKET` is set, point `STORAGES["default"]` at
   `storages.backends.gcloud.GoogleCloudStorage` with `bucket_name` and credentials built from
   `GCS_SERVICE_ACCOUNT` (`service_account.Credentials.from_service_account_info(json.loads(base64.b64decode(...)))`),
   and drop the `/media/` route from `mysite/urls.py`.
3. Use a **separate** bucket from the backups, with signed URLs (`querystring_auth=True`) if files are private.
4. Add a test that an upload lands in the bucket (with a fake client) and a restore note to
   [backup_restore.md](backup_restore.md).

## Safety

* One service account, one bucket, one role. Rotate the key (create new, update Render, delete old) if it ever appears anywhere it shouldn't.
* Public access prevention ON; no `allUsers` grants, ever.
