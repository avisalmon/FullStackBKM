"""The landing page is the front door: every link must lead somewhere real, it must stay
self-contained, and the sentence it teaches must be the one the skill triggers on."""

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urlparse

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"
REPO = "https://github.com/avisalmon/FullStackBKM"
SENTENCE = "Help me build my full stack site"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids, self.tags, self.attrs = [], set(), [], []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append(tag)
        self.attrs.append((tag, a))
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def page():
    p = Page()
    p.feed(PAGE.read_text(encoding="utf-8"))
    return p


def test_basics_for_search_phones_and_accessibility():
    p = page()
    assert p.title.strip()
    metas = {a.get("name"): a.get("content") for t, a in p.attrs if t == "meta"}
    assert metas.get("viewport") and len(metas.get("description", "")) > 60
    assert dict(p.attrs[0][1]).get("lang") == "en" or any(
        t == "html" and a.get("lang") == "en" for t, a in p.attrs
    )
    assert p.tags.count("h1") == 1
    assert all(a.get("alt") is not None for t, a in p.attrs if t == "img")


def test_the_page_is_self_contained():
    """No external scripts, fonts or stylesheets: fast, works offline, leaks no visitor data."""
    for tag, a in page().attrs:
        if tag == "script":
            assert "src" not in a, "external script"
        if tag == "link":
            assert a.get("rel") != "stylesheet" or not str(a.get("href", "")).startswith("http")
    assert "fonts.googleapis" not in PAGE.read_text(encoding="utf-8")


def test_every_in_page_anchor_exists():
    p = page()
    for href in p.links:
        if href.startswith("#") and len(href) > 1:
            assert href[1:] in p.ids, href


def test_relative_links_resolve():
    for href in page().links:
        if href.startswith(("http", "#", "mailto:")):
            continue
        assert (ROOT / urldefrag(href)[0]).exists(), href


def test_repository_links_point_at_files_that_exist():
    """A github.com/.../blob/main/<path> link is only good if <path> exists in this repo."""
    seen = 0
    for href in page().links:
        if not href.startswith(REPO + "/blob/main/"):
            continue
        seen += 1
        rel = urldefrag(href[len(REPO + "/blob/main/") :])[0]
        assert (ROOT / rel).exists(), href
    assert seen >= 15, "the journey should link to the real procedures"


def test_only_expected_external_hosts_are_linked():
    hosts = {urlparse(h).netloc for h in page().links if h.startswith("http")}
    assert hosts <= {
        "github.com", "www.python.org", "git-scm.com", "cli.github.com", "claude.com",
        "code.visualstudio.com",
    }, hosts  # fmt: skip


def test_the_copy_button_carries_exactly_the_trigger_sentence():
    html = PAGE.read_text(encoding="utf-8")
    assert f'data-copy="{SENTENCE}"' in html
    skill = (ROOT / ".claude" / "skills" / "build-my-site" / "SKILL.md").read_text(encoding="utf-8")
    assert SENTENCE.lower() in skill.lower(), (
        "the page teaches a sentence the skill does not trigger on"
    )


def test_every_journey_phase_has_a_real_procedure_link():
    html = PAGE.read_text(encoding="utf-8")
    for doc in (
        "deploy_to_render",
        "auth_google_oauth",
        "email_resend",
        "custom_domain_dns",
        "openai",
        "backup_restore",
        "gcs_bucket",
        "cost_monitoring",
        "debug_failed_deploy",
        "gotchas",
    ):
        assert f"docs/procedures/{doc}.md" in html, doc  # fmt: skip


def test_both_assistants_are_named_with_their_skill_folders():
    html = PAGE.read_text(encoding="utf-8")
    assert (
        ".claude/skills/" in html
        and ".github/skills/" in html
        and "copilot-instructions.md" in html
    )


def test_template_link_uses_the_repository_generate_url():
    assert f"{REPO}/generate" in page().links


def test_the_claims_on_the_page_match_the_repository():
    html = PAGE.read_text(encoding="utf-8")
    traps = (ROOT / "docs" / "procedures" / "gotchas.md").read_text(encoding="utf-8")
    rows = len(re.findall(r"^\| \d+ \|", traps, flags=re.M))
    assert f"{rows} known traps" in html, f"page says one number, gotchas.md has {rows}"


def test_code_blocks_are_readable():
    """Found by a screenshot: the inline `code` highlight leaked into dark code blocks (light text
    on a light chip). No HTML-reading test could see that, so guard the CSS rule itself."""
    css = PAGE.read_text(encoding="utf-8")
    rule = re.search(r"pre code\s*\{([^}]*)\}", css)
    assert rule, "no `pre code` rule"
    assert "background: none" in rule.group(1) and "color: inherit" in rule.group(1)


def test_terminal_prompts_keep_a_space_after_the_chevron():
    css = PAGE.read_text(encoding="utf-8")
    assert css.count(r"\203a\00a0") == 2
