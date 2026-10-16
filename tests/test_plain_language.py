"""A newcomer reads the landing page, the README's start and the setup guide before the chat takes
over. Jargon there is where people quietly give up, so it is either replaced or explained."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "index.html").read_text(encoding="utf-8")
GUIDE = (ROOT / "docs" / "get_started.md").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
README_START = README[
    README.index("## Start here") : README.index("## How you know you did it right")
]

# Phrases that were jargon and were rewritten. They must not come back.
BANNED = [
    "turn on 2FA",
    "PATH problems",
    "the new PATH",
    "health endpoint",
    "tests green",
    "metered helper",
    "Google OAuth client in",
    "logs in the GitHub CLI",
]


def visible(html: str) -> str:
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S)
    return re.sub(r"<[^>]+>", " ", html)


def test_no_banned_jargon_in_what_a_beginner_reads():
    for name, text in (
        ("index.html", visible(PAGE)),
        ("get_started.md", GUIDE),
        ("README start", README_START),
    ):
        for phrase in BANNED:
            assert phrase not in text, f"{name}: {phrase!r} is jargon; say it in plain words"


def test_two_factor_is_explained_wherever_it_is_asked_for():
    assert "a code from your phone as well as your password" in PAGE
    assert "a code from your phone as well as your password" in README_START
    assert "recovery codes" in GUIDE and "authenticator app" in GUIDE


def page_terms():
    return re.findall(r'<div class="term-def" id="w-([a-z]+)"><dt>(.*?)</dt>', PAGE)


def test_the_page_has_a_glossary_linked_from_the_start_and_the_nav():
    terms = page_terms()
    assert len(terms) >= 20
    assert len({key for key, _ in terms}) == len(terms), "duplicate glossary ids"
    assert 'href="#words"' in PAGE
    for needed in (
        "twofactor",
        "terminal",
        "repository",
        "clone",
        "deploy",
        "dns",
        "secret",
        "datamodel",
    ):
        assert needed in {key for key, _ in terms}, needed


def test_the_guide_and_the_page_define_the_same_words():
    guide_rows = re.findall(r"^\| \*\*(.+?)\*\* \|", GUIDE, flags=re.M)
    assert len(guide_rows) == len(page_terms()), "the two glossaries drifted apart"
    assert "## Words you'll meet" in GUIDE


def test_the_readme_points_to_the_glossary():
    assert "Words you'll meet" in README_START
