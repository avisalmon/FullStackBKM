"""A cheap last line of defence: no recognisable credential is sitting in a tracked-looking file.

The real defences are .gitignore, a private repository and secret scanning (pre-commit + CI;
see docs/security.md). This catches the case where a key gets pasted into a doc or a test.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {
    "env",
    ".git",
    "node_modules",
    "staticfiles",
    "data",
    "media",
    "backups",
    "__pycache__",
}
SKIP_FILES = {".env", "test_no_secrets_committed.py"}
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".yml",
    ".yaml",
    ".toml",
    ".txt",
    ".html",
    ".js",
    ".css",
    ".ps1",
    ".sh",
    ".json",
    ".example",
}

PATTERNS = {
    "OpenAI key": re.compile(r"sk-(?:proj-|admin-)?[A-Za-z0-9_-]{32,}"),
    "Google OAuth secret": re.compile(r"GOCSPX-[A-Za-z0-9_-]{20,}"),
    "Resend key": re.compile(r"\bre_[A-Za-z0-9]{20,}"),
    "Render API key": re.compile(r"\brnd_[A-Za-z0-9]{20,}"),
    "GitHub token": re.compile(r"\b(?:ghp|gho|github_pat)_[A-Za-z0-9_]{20,}"),
    "AWS key id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Private key block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "Service-account JSON": re.compile(r'"private_key_id"\s*:'),
}


def candidate_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name in SKIP_FILES:
            continue
        if SKIP_DIRS & set(path.relative_to(ROOT).parts):
            continue
        if path.suffix in TEXT_SUFFIXES or path.name == ".env.example":
            yield path


def test_no_credentials_in_the_repository():
    hits = []
    for path in candidate_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                hits.append(f"{path.relative_to(ROOT)}: looks like a {label}")
    assert not hits, "\n".join(hits)


def test_the_scanner_would_catch_a_leak(tmp_path):
    """A test that cannot fail is worse than none."""
    fake = "sk-proj-" + "a" * 40
    assert PATTERNS["OpenAI key"].search(f"OPENAI_API_KEY={fake}")
