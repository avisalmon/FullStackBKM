"""Guards for the deploy config. Each one exists because the opposite broke a real deploy
(see docs/procedures/gotchas.md). They read files, not Render, so they run anywhere."""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SECRET_WORDS = ("SECRET", "PASSWORD", "TOKEN", "KEY")


def render_service():
    config = yaml.safe_load((ROOT / "render.yaml").read_text(encoding="utf-8"))
    (service,) = [s for s in config["services"] if s["type"] == "web"]
    return service


def env_vars():
    return {item["key"]: item for item in render_service()["envVars"]}


def code_lines(path):
    lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
    return [ln for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def test_build_never_migrates():
    """Gotcha #3: the disk is read-only during the build, so migrate cannot work there."""
    assert not any("migrate" in ln for ln in code_lines("build.sh"))
    assert "migrate" not in render_service()["buildCommand"]


def test_build_script_is_unix_ready():
    """Gotcha #1: CRLF in the shebang breaks the build on Render's Linux builders."""
    raw = (ROOT / "build.sh").read_bytes()
    assert raw.startswith(b"#!/usr/bin/env bash\n")
    assert b"\r" not in raw
    assert "*.sh text eol=lf" in (ROOT / ".gitattributes").read_text()


def test_start_command_is_one_simple_chain():
    """Gotcha #23: no `|| true` chains whose parentheses may be dropped on restart."""
    start = render_service()["startCommand"]
    assert "bootstrap_site" in start
    assert "||" not in start
    assert "gunicorn mysite.wsgi:application" in start
    assert "$PORT" in start


def test_health_check_and_disk_are_configured():
    service = render_service()
    assert service["healthCheckPath"] == "/healthz"
    assert service["disk"]["mountPath"] == env_vars()["PERSISTENT_ROOT"]["value"]


def test_no_secret_is_committed_in_render_yaml():
    for key, item in env_vars().items():
        if any(word in key for word in SECRET_WORDS):
            assert item.get("sync") is False or item.get("generateValue") is True, key
            assert "value" not in item, key


def test_production_flags():
    assert env_vars()["DEBUG"]["value"] == "False"


def test_env_files_are_ignored_and_the_example_is_not():
    ignore = (ROOT / ".gitignore").read_text().splitlines()
    assert "env/" in ignore  # the virtualenv
    assert ".env" in ignore  # the variables file
    assert "!.env.example" in ignore


def test_runtime_requirements_cover_the_start_command():
    names = {
        re.split(r"[<>=\[ ]", ln, maxsplit=1)[0].lower() for ln in code_lines("requirements.txt")
    }
    assert {"django", "gunicorn", "whitenoise", "django-allauth", "djangorestframework"} <= names
    assert "pytest" not in names  # dev tooling stays out of the production image


def test_python_version_is_pinned_for_render():
    assert re.fullmatch(r"3\.\d+\.\d+", env_vars()["PYTHON_VERSION"]["value"])
