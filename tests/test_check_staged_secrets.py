import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_staged_secrets.py"
spec = importlib.util.spec_from_file_location("check_staged_secrets", SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

FAKE_KEY = "sk-proj-" + "a" * 40


def test_a_clean_commit_passes():
    assert guard.check_files({"app.py": b"print('hi')", "README.md": b"# hello"}) == []


def test_key_shaped_strings_are_blocked():
    problems = guard.check_files({"notes.md": f"OPENAI_API_KEY={FAKE_KEY}".encode()})
    assert len(problems) == 1 and "OpenAI key" in problems[0]


@pytest.mark.parametrize(
    "name",
    [".env", "site/.env", ".env.local", ".env.production", "data/db.sqlite3", "x.sqlite3-wal",
     "deploy.pem", "id_rsa", "env/Scripts/python.exe"],
)  # fmt: skip
def test_private_files_are_blocked_by_name_even_if_empty(name):
    assert guard.check_files({name: b""}), name


def test_the_example_env_file_is_allowed():
    assert guard.check_files({".env.example": b"SECRET_KEY=dev-only-insecure-key\n"}) == []


def test_binary_files_are_not_scanned_as_text():
    assert guard.check_files({"logo.png": b"\x89PNG\0\0" + FAKE_KEY.encode()}) == []


@pytest.mark.skipif(not shutil.which("git"), reason="needs git")
def test_the_real_hook_blocks_a_real_staged_commit(tmp_path):
    """End to end in a throwaway repo: stage a leak and a clean file, run the actual script."""

    def git(*args):
        return subprocess.run(["git", *args], cwd=tmp_path, capture_output=True, text=True)

    git("init", "-q")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    (tmp_path / "clean.txt").write_text("nothing here")
    git("add", "clean.txt")
    run = lambda: subprocess.run(  # noqa: E731
        [sys.executable, str(SCRIPT)], cwd=tmp_path, capture_output=True, text=True
    )
    assert run().returncode == 0

    (tmp_path / "leak.txt").write_text(f"key = {FAKE_KEY}")
    git("add", "leak.txt")
    blocked = run()
    assert blocked.returncode == 1
    assert "leak.txt" in blocked.stdout and "Commit blocked" in blocked.stdout

    git("rm", "--cached", "-q", "leak.txt")  # unstage (no HEAD yet, so no `restore`)
    assert run().returncode == 0


def test_the_config_uses_the_local_hook_not_an_external_scanner():
    config = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "scripts/check_staged_secrets.py" in config
    assert "gitleaks/gitleaks" not in config, "an external hook can block a newcomer's first commit"
