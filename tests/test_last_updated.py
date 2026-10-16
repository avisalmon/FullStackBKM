"""The "Last updated" mark on the README and the landing page.

It exists so that anybody using this blueprint can see, without reading a commit
history, when it last learned something and what. A date typed by hand goes stale
the first time a lesson is added and the date is forgotten, so the mark is computed
from docs/lessons_log.md by scripts/sync_skills.py, and these tests fail while it
is behind.
"""

import re
from pathlib import Path

import pytest

from scripts import sync_skills

ROOT = Path(__file__).resolve().parent.parent


def test_the_newest_lessons_date_is_read_from_the_log():
    when, count = sync_skills.latest_lessons()
    assert re.fullmatch(r"\d{1,2} [A-Z][a-z]+ \d{4}", when), when
    assert count >= 1


@pytest.mark.parametrize("name", ["README.md", "index.html"])
def test_the_front_pages_show_the_newest_date_and_link_to_the_log(name):
    text = (ROOT / name).read_text(encoding="utf-8")
    when, _count = sync_skills.latest_lessons()
    block = re.search(r"<!-- last-updated:start -->(.*?)<!-- last-updated:end -->", text, re.S)
    assert block, f"{name} lost its last-updated markers"
    assert f"Last updated {when}" in block[1]
    assert "lessons_log.md" in block[1]


def test_a_new_lesson_date_makes_the_check_fail_until_the_mark_is_restamped(tmp_path, monkeypatch):
    log = tmp_path / "lessons_log.md"
    log.write_text(
        "# What we learned\n\n## 2099-01-02\n\n- **Something new.** x\n", encoding="utf-8"
    )
    monkeypatch.setattr(sync_skills, "LESSONS", log)
    assert sync_skills.latest_lessons() == ("2 January 2099", 1)
    assert any("README.md" in p or "index.html" in p for p in sync_skills.drift())


def test_the_date_is_written_out_in_full():
    """Never 16/10: half the readers would read it as the tenth of the sixteenth month."""
    when, _count = sync_skills.latest_lessons()
    assert "/" not in when
