"""The landing page remembers which steps a visitor has finished (localStorage, this browser
only). Behaviour was verified in a real browser; these tests keep the structure it relies on."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")

STEPS = re.findall(r'<li id="step-([a-z]+)" data-step="([a-z]+)" data-kind="([a-z]+)">', HTML)
EXTRAS = {"google", "email", "domain", "ai"}


def test_every_step_has_a_matching_id_kind_and_checkbox():
    assert len(STEPS) == 12
    ids = [step for step, _, _ in STEPS]
    assert len(set(ids)) == len(ids), "duplicate step ids would share one tick"
    for step, data_step, kind in STEPS:
        assert step == data_step
        assert kind in {"core", "extra"}
        assert HTML.count(f'data-step-box="{step}"') == 1, step


def test_optional_steps_are_exactly_the_extras():
    extras = {step for step, _, kind in STEPS if kind == "extra"}
    assert extras == EXTRAS
    core = len(STEPS) - len(extras)
    # the panel's no-JavaScript text must match the real counts
    assert f"Core steps: 0 of {core}" in HTML and f"Extras: 0 of {len(extras)}" in HTML


def test_storage_access_cannot_break_the_page():
    """localStorage throws in some private modes; every access must be inside try/catch."""
    script = HTML[HTML.index("fullstackbkm-progress-v1") - 200 :]
    assert re.search(r"try \{\s*store = window\.localStorage;", script)
    assert re.search(r"try \{ store\.setItem\(KEY", script)
    assert "fullstackbkm-progress-v1" in HTML, "a versioned key lets the format change later"
    assert "This browser is not letting the page save" in HTML


def test_progress_ui_starts_hidden_until_there_is_progress():
    for element in (
        'id="nav-progress" href="#journey" hidden',
        'id="resume" href="#journey" hidden',
        'id="live-banner" hidden',
        'id="graduated" hidden',
    ):
        assert element in HTML, element


def test_privacy_promise_and_motion_preference():
    assert "saved in this browser only; nothing is sent anywhere" in HTML
    assert "prefers-reduced-motion: reduce" in HTML.split("function confetti")[1][:400]


def test_every_step_says_how_long_and_what_you_get():
    for step, _, _ in STEPS:
        block = HTML[HTML.index(f'id="step-{step}"') :]
        block = block[: block.index("</li>")]
        assert 'class="meta"' in block, step
        assert "minute" in block or "pace" in block, step
        assert 'class="result"' in block, step
