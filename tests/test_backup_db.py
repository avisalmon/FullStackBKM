import sqlite3
import time

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.fixture
def real_db(tmp_path, settings):
    """A real on-disk SQLite file (the test database itself lives in memory)."""
    path = tmp_path / "live.sqlite3"
    conn = sqlite3.connect(path)
    conn.execute("create table t (v text)")
    conn.execute("insert into t values ('hello')")
    conn.commit()
    conn.close()
    settings.DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": str(path)}}
    settings.BACKUP_DIR = tmp_path / "backups"
    return path


def test_snapshot_is_a_readable_copy(real_db, settings):
    call_command("backup_db", verbosity=0)
    (snapshot,) = settings.BACKUP_DIR.glob("db_*.sqlite3")
    assert sqlite3.connect(snapshot).execute("select v from t").fetchall() == [("hello",)]


def test_keeps_only_the_newest_n(real_db, settings):
    for _ in range(4):
        call_command("backup_db", keep=2, verbosity=0)
        time.sleep(1.1)  # the stamp has one-second resolution
    assert len(list(settings.BACKUP_DIR.glob("db_*.sqlite3"))) == 2


def test_dry_run_writes_nothing(real_db, settings):
    call_command("backup_db", dry_run=True, verbosity=0)
    assert not settings.BACKUP_DIR.exists()


def test_refuses_an_in_memory_database(settings):
    settings.DATABASES = {"default": {"ENGINE": "x", "NAME": ":memory:"}}
    with pytest.raises(CommandError):
        call_command("backup_db", verbosity=0)
