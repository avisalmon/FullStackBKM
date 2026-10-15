import sqlite3
from datetime import datetime, timedelta, timezone

import pytest
from django.core.management import call_command

from core import gcs


class FakeBucket:
    name = "test-bucket"

    def __init__(self):
        self.objects = {}  # name -> {"size", "created"}
        self.uploads = []

    def upload(self, path, name):
        from pathlib import Path

        self.uploads.append(name)
        self.objects[name] = {
            "size": Path(path).stat().st_size,
            "created": datetime.now(timezone.utc),
        }

    def list(self, prefix=""):
        return [{"name": n, **v} for n, v in self.objects.items() if n.startswith(prefix)]

    def delete(self, name):
        del self.objects[name]


@pytest.fixture
def setup(tmp_path, settings, monkeypatch):
    db = tmp_path / "live.sqlite3"
    conn = sqlite3.connect(db)
    conn.execute("create table t (v text)")
    conn.commit()
    conn.close()
    settings.DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": str(db)}}
    settings.BACKUP_DIR = tmp_path / "backups"
    settings.MEDIA_ROOT = tmp_path / "media"
    (settings.MEDIA_ROOT / "notes").mkdir(parents=True)
    (settings.MEDIA_ROOT / "notes" / "a.png").write_bytes(b"12345")
    bucket = FakeBucket()
    monkeypatch.setattr(gcs.Bucket, "from_env", classmethod(lambda cls: bucket))
    return bucket


def test_snapshot_and_media_go_offsite(setup):
    call_command("backup_db", verbosity=0)
    assert any(name.startswith("db/db_") for name in setup.objects)
    assert "media/notes/a.png" in setup.objects


def test_media_is_incremental(setup, settings):
    call_command("backup_db", verbosity=0)
    first = [u for u in setup.uploads if u.startswith("media/")]
    call_command("backup_db", verbosity=0)
    second = [u for u in setup.uploads if u.startswith("media/")]
    assert first == second  # nothing changed, nothing re-uploaded
    (settings.MEDIA_ROOT / "notes" / "a.png").write_bytes(b"123456789")
    call_command("backup_db", verbosity=0)
    assert len([u for u in setup.uploads if u.startswith("media/")]) == 2


def test_old_bucket_snapshots_are_pruned_but_media_is_not(setup):
    old = datetime.now(timezone.utc) - timedelta(days=40)
    setup.objects["db/db_19990101_000000.sqlite3"] = {"size": 1, "created": old}
    setup.objects["media/ancient.png"] = {"size": 1, "created": old}
    call_command("backup_db", retention_days=30, verbosity=0)
    assert "db/db_19990101_000000.sqlite3" not in setup.objects
    assert "media/ancient.png" in setup.objects


def test_skip_media(setup):
    call_command("backup_db", skip_media=True, verbosity=0)
    assert not any(name.startswith("media/") for name in setup.objects)


def test_bucket_from_env_is_none_when_unconfigured(monkeypatch):
    monkeypatch.delenv("GCS_BUCKET", raising=False)
    monkeypatch.delenv("GCS_SERVICE_ACCOUNT", raising=False)
    assert gcs.Bucket.from_env() is None
