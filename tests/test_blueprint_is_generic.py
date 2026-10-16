"""This blueprint is public and meant for anyone. Nothing in it may point at its author's own
sites, machines, accounts or services. Secrets are covered by test_no_secrets_committed.py; this
is about the quieter leaks: a real domain, a real service id, a home folder, a work email domain."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"env", ".git", "staticfiles", "data", "media", "backups", "__pycache__", ".ruff_cache"}
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
    ".sh",
    ".json",
}

# The only personal identifiers that are allowed, because the repo lives there and the licence
# names its author.
ALLOWED = (
    "github.com/avisalmon/",
    "avisalmon.github.io/",
    "Copyright (c) 2026 Avi Salmon",
    "Licensed MIT (2026, Avi Salmon)",
    r"PS C:\Users\dana>",  # the setup guide's example of what a terminal prompt looks like
)

PERSONAL = {
    "the author's production site": re.compile(r"babook", re.I),
    "a Render service or owner id": re.compile(r"\b(srv|tea|dpg)-[a-z0-9]{20}\b"),
    # Render appends a random 4-character suffix with digits in it (mysite-0tu0). Placeholders
    # like your-site.onrender.com have no such suffix.
    "a real onrender hostname": re.compile(
        r"\b[a-z0-9-]+-(?=[a-z0-9]{4}\.onrender)[a-z]*\d[a-z0-9]*\.onrender\.com\b"
    ),
    "a home folder on the author's machine": re.compile(
        r"C:\\Users\\[A-Za-z]|/Users/[a-z]+/|/home/[a-z]+/"
    ),
    "a work email domain": re.compile(r"@intel\.com", re.I),
    "the author's other repositories": re.compile(r"avisalmon/(homepage|academia360|Render)\b"),
    "a real email address": re.compile(
        r"\b[A-Za-z0-9._%+-]+@(?!example\.com|your-domain\.com|users\.noreply\.github\.com|anthropic\.com|github\.com)[A-Za-z0-9.-]+\.[a-z]{2,}\b"
    ),
}

PLACEHOLDER_HOSTS = {"my-site-ab12.onrender.com"}  # used in tests as an obviously fake example


def files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if SKIP_DIRS & set(path.relative_to(ROOT).parts) or path.name == ".env":
            continue
        yield path


def test_nothing_points_at_the_authors_own_sites_machines_or_accounts():
    hits = []
    for path in files():
        if path.name == "test_blueprint_is_generic.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for allowed in ALLOWED:
            text = text.replace(allowed, "")
        for what, pattern in PERSONAL.items():
            for match in pattern.finditer(text):
                if match.group(0) in PLACEHOLDER_HOSTS:
                    continue
                hits.append(f"{path.relative_to(ROOT)}: {what}: {match.group(0)!r}")
    assert not hits, "\n".join(hits)


def test_the_scanner_would_catch_each_kind_of_leak():
    """A guard that cannot be tripped is worthless."""
    samples = {
        "the author's production site": "see babook.co.il",
        "a Render service or owner id": "srv-d6ttohq4d50c73chm4tg",
        "a home folder on the author's machine": r"C:\Users\someone\Projects",
        "a work email domain": "mail dana@intel.com",
        "a real email address": "contact dana.levi@gmail.com",
    }
    for what, sample in samples.items():
        assert PERSONAL[what].search(sample), what
    assert not PERSONAL["a real email address"].search("alice@example.com")
    assert not PERSONAL["a real email address"].search("noreply@your-domain.com")
    host = PERSONAL["a real onrender hostname"]
    assert host.search("mysite-0tu0.onrender.com")
    assert not host.search("your-site.onrender.com") and not host.search("my-site.onrender.com")
