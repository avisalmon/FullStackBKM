"""The tutorial is part of the product: a broken link or a quiz with no right answer teaches the
wrong thing. These read the HTML structurally (not by substring) and follow every local link."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urlparse

import pytest

ROOT = Path(__file__).resolve().parent.parent
TUTORIAL = ROOT / "tutorial"
PAGES = sorted(TUTORIAL.glob("*.html"))


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids, self.quizzes, self.titles = [], set(), [], []
        self._in_title = False
        self._quiz = None
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag in ("link",) and "href" in a:
            self.links.append(a["href"])
        if tag == "script" and "src" in a:
            self.links.append(a["src"])
        if tag == "title":
            self._in_title = True
        if tag == "div" and "quiz" in (a.get("class") or "").split():
            self._quiz = {"answer": a.get("data-answer"), "choices": []}
            self._depth = 1
            self.quizzes.append(self._quiz)
        elif self._quiz is not None:
            if tag == "div":
                self._depth += 1
            if tag == "button" and "data-choice" in a:
                self._quiz["choices"].append(a["data-choice"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if self._quiz is not None and tag == "div":
            self._depth -= 1
            if self._depth == 0:
                self._quiz = None

    def handle_data(self, data):
        if self._in_title:
            self.titles.append(data)


def parse(path):
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    return page


def test_the_tutorial_pages_exist():
    assert {p.name for p in PAGES} == {"index.html", "data-models.html"}
    assert (TUTORIAL / "tutorial.css").exists() and (TUTORIAL / "quiz.js").exists()


@pytest.mark.parametrize("path", PAGES, ids=lambda p: p.name)
def test_every_local_link_resolves(path):
    page = parse(path)
    for href in page.links:
        parts = urlparse(href)
        if parts.scheme in ("http", "https", "mailto"):
            continue
        file_part, fragment = urldefrag(href)
        target = (path.parent / file_part).resolve() if file_part else path
        assert target.exists(), f"{path.name}: {href} -> missing {target}"
        if fragment and target.suffix == ".html":
            assert fragment in parse(target).ids, f"{path.name}: {href} -> no #{fragment}"


@pytest.mark.parametrize("path", PAGES, ids=lambda p: p.name)
def test_each_quiz_has_a_correct_answer_among_its_choices(path):
    page = parse(path)
    for quiz in page.quizzes:
        assert quiz["answer"] in quiz["choices"], quiz
        assert len(quiz["choices"]) >= 2


def test_the_lessons_have_quizzes_and_titles():
    assert len(parse(TUTORIAL / "data-models.html").quizzes) >= 5
    for path in PAGES:
        assert "".join(parse(path).titles).strip()


def test_the_relationship_picker_covers_all_four_answers():
    js = (TUTORIAL / "quiz.js").read_text(encoding="utf-8")
    for key in ("no,no", "yes,no", "no,yes", "yes,yes"):
        assert f'"{key}"' in js
    page = parse(TUTORIAL / "data-models.html")
    assert {"picker", "a-many", "b-many"} <= page.ids
