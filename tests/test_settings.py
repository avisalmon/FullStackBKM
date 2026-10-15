"""Settings are read at import time, so these run in a fresh interpreter."""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PROBE = (
    "import json, mysite.settings as s;"
    "print(json.dumps({'hosts': s.ALLOWED_HOSTS, 'csrf': s.CSRF_TRUSTED_ORIGINS}))"
)


def load_settings(**env):
    base = {
        k: v for k, v in os.environ.items() if k not in {"SECRET_KEY", "DEBUG", "ALLOWED_HOSTS"}
    }
    base.pop("RENDER_EXTERNAL_HOSTNAME", None)
    base.update(env)
    return subprocess.run(
        [sys.executable, "-c", PROBE],
        cwd=ROOT,
        env={**base, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
    )


def test_production_refuses_the_dev_secret_key():
    result = load_settings(DEBUG="False", SECRET_KEY="")
    assert result.returncode != 0
    assert "SECRET_KEY must be set" in result.stderr


def test_production_boots_with_a_real_secret_key():
    result = load_settings(DEBUG="False", SECRET_KEY="a-real-secret-" + "x" * 40)
    assert result.returncode == 0, result.stderr


def test_render_hostname_is_trusted_automatically():
    result = load_settings(
        DEBUG="False", SECRET_KEY="k" * 50, RENDER_EXTERNAL_HOSTNAME="my-site-ab12.onrender.com"
    )
    data = json.loads(result.stdout)
    assert "my-site-ab12.onrender.com" in data["hosts"]
    assert "https://my-site-ab12.onrender.com" in data["csrf"]


def test_custom_domain_needs_only_allowed_hosts():
    result = load_settings(
        DEBUG="False", SECRET_KEY="k" * 50, ALLOWED_HOSTS="example.com,www.example.com"
    )
    data = json.loads(result.stdout)
    assert "https://example.com" in data["csrf"]
    assert "https://www.example.com" in data["csrf"]
