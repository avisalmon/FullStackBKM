import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("verify_site", ROOT / "scripts" / "verify_site.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class Resp:
    def __init__(self, status=200, text="", headers=None):
        self.status_code, self.text, self.headers = status, text, headers or {}


class FakeSite:
    """A site that answers from a dict of path -> Resp (default 404)."""

    def __init__(self, routes, base="https://example.onrender.com"):
        self.base, self.routes, self.calls = base, routes, []

    def request(self, method, path, **kwargs):
        self.calls.append((method, path))
        return self.routes.get((method, path), self.routes.get(path, Resp(404, "Not Found")))


GOOD = {
    "/healthz": Resp(200, '{"status": "ok"}'),
    "/": Resp(
        200,
        '<link href="/static/css/site.css"> Continue with Google',
        {
            "Strict-Transport-Security": "max-age=31536000",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "same-origin",
            "Permissions-Policy": "camera=()",
        },
    ),
    "/privacy/": Resp(200, "<h1>Privacy</h1>"),
    "/static/css/site.css": Resp(200, "body{}"),
    "/accounts/login/": Resp(200, "", {"Set-Cookie": "csrftoken=x; Secure; SameSite=Lax"}),
    "/accounts/signup/": Resp(200),
    "/admin/login/": Resp(200),
    ("POST", "/internal/run/costs/"): Resp(403),
    "/ops/costs/": Resp(302),
    "http://example.onrender.com/": Resp(301, "", {"Location": "https://example.onrender.com/"}),
}


def statuses(routes, **kw):
    results = verify.run(FakeSite(routes, **kw))
    return {r.title: r.status for r in results}


def live_results(routes, **kw):
    site = FakeSite(routes, **kw)
    return [c(site) for c in verify.LIVE_CHECKS]


def test_a_healthy_site_has_no_live_failures():
    results = [r for r in live_results(GOOD) if r is not None]
    assert all(r.status in (verify.PASS, verify.INFO) for r in results), results


@pytest.mark.parametrize(
    "path, response, fragment",
    [
        ("/healthz", Resp(500), "Health check"),
        ("/", Resp(500), "Home page"),
        ("/static/css/site.css", Resp(404), "Static files"),
        ("/accounts/login/", Resp(500), "Sign-in"),
        ("/ops/costs/", Resp(200, "costs"), "Cost page"),
        (("POST", "/internal/run/costs/"), Resp(200), "Scheduled-task endpoint"),
        ("http://example.onrender.com/", Resp(200), "redirects to https"),
    ],
)
def test_each_live_problem_is_reported_as_a_failure(path, response, fragment):
    results = live_results({**GOOD, path: response})
    failed = [r for r in results if r is not None and r.status == verify.FAIL]
    assert any(fragment in r.title for r in failed), [r.title for r in results if r]


def test_debug_mode_is_caught_by_the_error_page_leaking():
    leaky = Resp(404, "You're seeing this error because you have DEBUG = True")
    site = FakeSite({**GOOD})
    site.routes = {**GOOD}
    site.request = lambda m, p, **k: leaky if "no-such-page" in p else GOOD.get(p, Resp(404))
    result = verify.check_debug_off(site)
    assert result.status == verify.FAIL
    assert "DEBUG" in result.hint


def test_local_http_site_skips_https_checks_instead_of_failing():
    site = FakeSite(GOOD, base="http://127.0.0.1:8000")
    assert verify.check_https(site).status == verify.INFO
    assert verify.check_hsts(site) is None


def test_every_failure_has_a_hint():
    bad = FakeSite({}, base="https://example.onrender.com")
    for check in verify.LIVE_CHECKS:
        result = check(bad)
        if result is not None and result.status == verify.FAIL:
            assert result.hint, check.__name__


def test_unreachable_site_is_a_failure_not_a_crash(monkeypatch):
    class Down:
        base = "http://127.0.0.1:1"

        def request(self, *a, **k):
            raise verify.requests.ConnectionError("refused")

    results = verify.run(Down())
    assert any(r.status == verify.FAIL and "could not reach" in r.title for r in results)


def test_planted_secret_is_found(tmp_path, monkeypatch):
    (tmp_path / "notes.md").write_text("key = sk-proj-" + "a" * 40)
    monkeypatch.setattr(verify, "ROOT", tmp_path)
    result = verify.check_no_secrets_in_files()
    assert result.status == verify.FAIL
    assert "notes.md" in result.title


def test_clean_tree_passes_secret_scan(tmp_path, monkeypatch):
    (tmp_path / "notes.md").write_text("nothing secret here")
    monkeypatch.setattr(verify, "ROOT", tmp_path)
    assert verify.check_no_secrets_in_files().status == verify.PASS


def test_exit_code_reflects_failures():
    assert verify.report([verify.Result(verify.PASS, "ok")]) == 0
    assert verify.report([verify.Result(verify.WARN, "meh", "fix")]) == 0
    assert verify.report([verify.Result(verify.FAIL, "bad", "fix")]) == 1


def test_this_repository_passes_its_own_secret_and_ignore_checks():
    assert verify.check_no_secrets_in_files().status == verify.PASS
    assert verify.check_env_file_ignored().status == verify.PASS
    assert verify.check_env_file_not_tracked().status == verify.PASS


def test_debug_on_is_fine_locally_but_a_failure_on_a_live_site():
    leaky = Resp(404, "You're seeing this error because you have DEBUG = True")

    def make(base):
        site = FakeSite({}, base=base)
        site.request = lambda m, p, **k: leaky
        return site

    assert verify.check_debug_off(make("http://127.0.0.1:8000")).status == verify.INFO
    assert verify.check_debug_off(make("https://example.onrender.com")).status == verify.FAIL


def test_privacy_checks_warn_but_never_block():
    """The owner may override privacy advice, so these are WARN (advice), not FAIL (blocker)."""
    draft = {**GOOD, "/privacy/": Resp(200, '<p class="draft-banner">Draft</p>')}
    assert verify.check_privacy_pages(FakeSite(draft)).status == verify.WARN
    assert (
        verify.check_privacy_pages(FakeSite({**GOOD, "/privacy/": Resp(404)})).status == verify.WARN
    )
    assert verify.check_privacy_pages(FakeSite(GOOD)).status == verify.PASS
    bare = {**GOOD, "/": Resp(200, "", {})}
    assert verify.check_privacy_headers(FakeSite(bare)).status == verify.WARN
    loose = {**GOOD, "/accounts/login/": Resp(200, "", {"Set-Cookie": "csrftoken=x"})}
    assert verify.check_cookie_flags(FakeSite(loose)).status == verify.WARN
    assert verify.check_cookie_flags(FakeSite(GOOD)).status == verify.PASS
