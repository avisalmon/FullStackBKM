"""The test suite must never reach the owner's real services, whatever their .env contains."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_real_credentials_are_invisible_inside_tests(settings):
    from core import gcs

    for name in ("GCS_BUCKET", "OPENAI_API_KEY", "RESEND_API_KEY", "RENDER_API_KEY"):
        assert name not in os.environ
    assert gcs.Bucket.from_env() is None
    assert settings.OPENAI_API_KEY == ""


def test_suite_passes_even_when_the_owners_environment_is_full_of_real_keys():
    """Run a slice of the suite in a subprocess whose environment looks like a configured owner.
    If isolation broke, the GCS tests would try to decode this garbage as a real service account
    and the AI tests would try to use this key."""
    env = {
        **os.environ,
        "GCS_BUCKET": "someones-real-bucket",
        "GCS_SERVICE_ACCOUNT": "bm90LXJlYWwtanNvbg==",
        "OPENAI_API_KEY": "sk-proj-" + "r" * 40,
        "OPENAI_ADMIN_KEY": "sk-admin-" + "r" * 40,
        "RESEND_API_KEY": "re_" + "r" * 30,
        "TASK_TRIGGER_TOKEN": "real-token",
        "SITE_NAME": "Coffee Club",
        "PYTHONPATH": str(ROOT),
    }
    done = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "tests/test_backup_db.py",
            "tests/test_backup_offsite.py",
            "tests/test_ai.py",
            "tests/test_costs.py",
            "tests/test_run_task.py",
            "tests/test_core.py",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, done.stdout[-1500:] + done.stderr[-500:]
