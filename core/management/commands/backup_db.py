"""Consistent snapshot of the SQLite database, optionally copied offsite to Google Cloud Storage.

    python manage.py backup_db                 # local snapshot (+ offsite if GCS is configured)
    python manage.py backup_db --keep 30       # keep the newest 30 local snapshots
    python manage.py backup_db --retention-days 60
    python manage.py backup_db --skip-media    # database only
    python manage.py backup_db --dry-run

Local snapshots use sqlite3's online backup API, which is safe while the site is serving
requests (copying db.sqlite3 with `cp` while WAL is active can yield a corrupt copy).

A snapshot on the SAME persistent disk protects against a bad deploy or migration, not against
losing the disk. Configure GCS (docs/procedures/gcs_bucket.md) and this command also uploads the
snapshot to `db/` in the bucket, mirrors MEDIA_ROOT to `media/` (only files that are new or
changed in size), and deletes bucket snapshots older than --retention-days.
Restore steps: docs/procedures/backup_restore.md.
"""

import sqlite3
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.gcs import Bucket

PREFIX = "db_"
SUFFIX = ".sqlite3"


class Command(BaseCommand):
    help = "Snapshot the SQLite database locally and (if configured) offsite to GCS."

    def add_arguments(self, parser):
        parser.add_argument("--keep", type=int, default=14, help="Local snapshots to retain")
        parser.add_argument(
            "--retention-days", type=int, default=30, help="Bucket snapshot age limit"
        )
        parser.add_argument("--skip-media", action="store_true", help="Do not mirror media files")
        parser.add_argument("--dry-run", action="store_true", help="Report what would happen")

    def handle(self, *args, keep, retention_days, skip_media, dry_run, **options):
        if keep < 1:
            raise CommandError("--keep must be at least 1")
        db_path = settings.DATABASES["default"]["NAME"]
        if db_path == ":memory:" or "mode=memory" in db_path:
            raise CommandError("Cannot back up an in-memory database")

        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        target = settings.BACKUP_DIR / f"{PREFIX}{stamp}{SUFFIX}"
        bucket = Bucket.from_env()

        if dry_run:
            where = f"and upload to gs://{bucket.name}" if bucket else "(offsite not configured)"
            self.stdout.write(f"dry-run: would write {target} {where}; keep newest {keep} locally")
            return

        self._snapshot(db_path, target)
        self._prune_local(keep)

        if bucket is None:
            self.stdout.write("offsite: GCS not configured - local snapshot only")
            return
        bucket.upload(target, f"db/{target.name}")
        self.stdout.write(f"offsite: uploaded db/{target.name}")
        if not skip_media:
            self._mirror_media(bucket)
        self._prune_bucket(bucket, retention_days)

    def _snapshot(self, db_path, target):
        settings.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        source = sqlite3.connect(db_path)
        try:
            dest = sqlite3.connect(target)
            try:
                source.backup(dest)
            finally:
                dest.close()
        finally:
            source.close()
        self.stdout.write(f"backup: wrote {target} ({target.stat().st_size} bytes)")

    def _prune_local(self, keep):
        # Names sort chronologically because the stamp is UTC YYYYmmdd_HHMMSS.
        snapshots = sorted(settings.BACKUP_DIR.glob(f"{PREFIX}*{SUFFIX}"))
        for old in snapshots[:-keep]:
            old.unlink()
            self.stdout.write(f"backup: pruned {old.name}")

    def _mirror_media(self, bucket):
        root = settings.MEDIA_ROOT
        if not root.exists():
            return
        existing = {item["name"]: item["size"] for item in bucket.list("media/")}
        uploaded = 0
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            name = f"media/{path.relative_to(root).as_posix()}"
            if existing.get(name) != path.stat().st_size:
                bucket.upload(path, name)
                uploaded += 1
        self.stdout.write(f"offsite: media mirrored ({uploaded} new or changed files)")

    def _prune_bucket(self, bucket, retention_days):
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
        removed = 0
        for item in bucket.list("db/"):
            if item["created"] < cutoff:
                bucket.delete(item["name"])
                removed += 1
        self.stdout.write(
            f"offsite: removed {removed} snapshot(s) older than {retention_days} days"
        )
