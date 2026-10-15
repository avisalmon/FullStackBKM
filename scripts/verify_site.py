#!/usr/bin/env python
"""Did I do it right? A checklist you can run, with a fix hint for everything that fails.

    python scripts/verify_site.py                              # checks this repository
    python scripts/verify_site.py --url http://127.0.0.1:8000  # ...and your running local site
    python scripts/verify_site.py --url https://my-site.onrender.com   # ...and the live site

Each line is PASS, WARN (worth fixing, not fatal) or FAIL (fix before you tell anyone about the
site), followed by what to do. Exit code is 1 if anything FAILed, so CI can use it too.
Read-only: it only looks (GET requests, and one POST that is *supposed* to be refused).
"""

import argparse
import re
import secrets
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from secret_patterns import PATTERNS  # noqa: E402

PASS, WARN, FAIL, INFO = "PASS", "WARN", "FAIL", "INFO"
SKIP_DIRS = {"env", ".git", "staticfiles", "data", "media", "backups", "__pycache__", ".ruff_cache"}


@dataclass
class Result:
    status: str
    title: str
    hint: str = ""


# --------------------------------------------------------------------------- repository checks


def git(*args):
    if not shutil.which("git"):
        return None
    done = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else None


def check_env_file_not_tracked():
    tracked = git("ls-files", ".env", "env")
    if tracked is None:
        return Result(WARN, "Could not run git to check tracked files", "Install git, then re-run.")
    if tracked:
        return Result(
            FAIL,
            f"A secret/virtualenv path is tracked by git: {tracked.splitlines()[0]}",
            "Run `git rm -r --cached .env env`, commit, and ROTATE any key that was in it.",
        )
    return Result(PASS, ".env and env/ are not tracked by git")


def check_env_file_ignored():
    ignored = git("check-ignore", ".env")
    if ignored is None:
        return Result(FAIL, ".env is not git-ignored", "Add `.env` to .gitignore (and `env/`).")
    return Result(PASS, ".env is git-ignored")


def check_no_secrets_in_files():
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if not path.is_file() or SKIP_DIRS & set(rel.parts) or path.name == ".env":
            continue
        if path.name == "secret_patterns.py" or path.name.startswith("test_no_secrets"):
            continue
        if path.suffix in {".png", ".jpg", ".ico", ".pyc", ".sqlite3"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                return Result(
                    FAIL,
                    f"{rel} contains something shaped like a {label}",
                    "Remove it, put the value in .env / Render, and rotate the key.",
                )
    return Result(PASS, "No key-shaped strings in the project files")


def check_repo_private():
    if not shutil.which("gh"):
        return Result(
            WARN,
            "GitHub CLI not installed; cannot confirm the repo is private",
            "Install gh (https://cli.github.com) or check Settings -> General on GitHub.",
        )
    done = subprocess.run(
        ["gh", "repo", "view", "--json", "isPrivate,url"], cwd=ROOT, capture_output=True, text=True
    )
    if done.returncode != 0:
        return Result(
            WARN,
            "No GitHub repo linked yet (or gh is not logged in)",
            "Phase 3 of the checklist creates your private repo.",
        )
    if '"isPrivate":true' in done.stdout.replace(" ", ""):
        return Result(PASS, "GitHub repo is private")
    return Result(
        FAIL,
        "GitHub repo is PUBLIC",
        "Make it private: GitHub -> Settings -> General -> Danger Zone -> Change visibility.",
    )


def check_precommit_installed():
    hook = ROOT / ".git" / "hooks" / "pre-commit"
    if hook.exists():
        return Result(PASS, "pre-commit secret scan is installed")
    return Result(
        WARN,
        "pre-commit hook not installed (no automatic secret scan on commit)",
        "Run `pre-commit install` inside the env.",
    )


def check_site_renamed():
    render = (ROOT / "render.yaml").read_text(encoding="utf-8")
    if re.search(r"^\s+name: my-site$", render, flags=re.M):
        return Result(
            WARN,
            "render.yaml still uses the placeholder name `my-site`",
            'Run `python scripts/init_site.py --name <slug> --site-name "<Name>"`.',
        )
    return Result(PASS, "render.yaml carries your site's name")


def check_secret_key_set():
    env = ROOT / ".env"
    if not env.exists():
        return Result(WARN, "No .env file yet", "Copy .env.example to .env (checklist Phase 2).")
    text = env.read_text(encoding="utf-8")
    match = re.search(r"^SECRET_KEY=(.*)$", text, flags=re.M)
    if not match or match.group(1).strip() in {"", "dev-only-insecure-key"}:
        return Result(
            WARN,
            "Local SECRET_KEY is still the placeholder",
            'Put a random one in .env: python -c "import secrets;print(secrets.token_urlsafe(50))"',
        )
    return Result(PASS, "Local SECRET_KEY is set")


REPO_CHECKS = [
    check_env_file_not_tracked,
    check_env_file_ignored,
    check_no_secrets_in_files,
    check_repo_private,
    check_precommit_installed,
    check_site_renamed,
    check_secret_key_set,
]


# --------------------------------------------------------------------------- live-site checks


class Site:
    """One place that talks to the site, so tests can replace it."""

    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")
        self.session = requests.Session()

    def request(self, method: str, path: str, **kwargs):
        kwargs.setdefault("timeout", 20)
        kwargs.setdefault("allow_redirects", False)
        url = path if path.startswith("http") else self.base + path
        return self.session.request(method, url, **kwargs)


def check_health(site):
    r = site.request("GET", "/healthz")
    ok = r.status_code == 200 and '"ok"' in r.text
    return Result(
        PASS if ok else FAIL,
        "Health check /healthz answers ok",
        ""
        if ok
        else f"Got HTTP {r.status_code}. Read the logs: docs/procedures/debug_failed_deploy.md",
    )


def check_home(site):
    r = site.request("GET", "/")
    return Result(
        PASS if r.status_code == 200 else FAIL,
        "Home page loads",
        "" if r.status_code == 200 else f"Got HTTP {r.status_code}.",
    )


def check_static(site):
    home = site.request("GET", "/").text
    match = re.search(r'href="([^"]+\.css)"', home)
    if not match:
        return Result(WARN, "No stylesheet found on the home page to test")
    r = site.request("GET", match.group(1))
    ok = r.status_code == 200
    return Result(
        PASS if ok else FAIL,
        "Static files (CSS) are served",
        "" if ok else "WhiteNoise/collectstatic problem: docs/procedures/gotchas.md #1, #2",
    )


def check_login_pages(site):
    bad = [
        p
        for p in ("/accounts/login/", "/accounts/signup/", "/admin/login/")
        if site.request("GET", p).status_code != 200
    ]
    return Result(
        PASS if not bad else FAIL,
        "Sign-in, sign-up and admin pages load",
        "" if not bad else f"Not loading: {', '.join(bad)}",
    )


def check_debug_off(site):
    r = site.request("GET", f"/no-such-page-{secrets.token_hex(4)}/")
    leaks = "You're seeing this error because you have" in r.text or "URLconf defined in" in r.text
    local = urlparse(site.base).hostname in ("127.0.0.1", "localhost")
    if leaks and local:
        return Result(INFO, "Local site runs with DEBUG on (right for development, never for live)")
    if leaks:
        return Result(
            FAIL,
            "DEBUG is ON: error pages reveal how the site is built",
            "Set DEBUG=False in the environment (production must never run with DEBUG).",
        )
    if r.status_code != 404:
        return Result(WARN, f"Unknown pages answer HTTP {r.status_code}, expected 404")
    return Result(PASS, "Unknown pages give a plain 404 (DEBUG is off)")


def check_machine_endpoint_closed(site):
    r = site.request("POST", "/internal/run/costs/")
    ok = r.status_code in (403, 404)
    return Result(
        PASS if ok else FAIL,
        "Scheduled-task endpoint refuses a caller with no token",
        ""
        if ok
        else f"Got HTTP {r.status_code}; it must be 403. Check TASK_TRIGGER_TOKEN handling.",
    )


def check_ops_private(site):
    r = site.request("GET", "/ops/costs/")
    ok = r.status_code in (301, 302, 403, 404)
    return Result(
        PASS if ok else FAIL,
        "Cost page is not public",
        "" if ok else "Anonymous visitors can see /ops/costs/. It must be staff-only.",
    )


def check_https(site):
    host = urlparse(site.base)
    if host.scheme != "https":
        return Result(INFO, "Local http site: HTTPS checks skipped (they apply to the live site)")
    plain = site.request("GET", f"http://{host.netloc}/")
    redirects = plain.status_code in (301, 302, 307, 308) and plain.headers.get(
        "Location", ""
    ).startswith("https://")
    return Result(
        PASS if redirects else FAIL,
        "http:// redirects to https://",
        "" if redirects else "Check SECURE_SSL_REDIRECT / DEBUG=False on Render.",
    )


def check_hsts(site):
    if urlparse(site.base).scheme != "https":
        return None
    r = site.request("GET", "/")
    ok = "max-age" in r.headers.get("Strict-Transport-Security", "")
    return Result(
        PASS if ok else WARN,
        "HSTS header is sent",
        "" if ok else "Set DEBUG=False (HSTS is gated on it).",
    )


def check_privacy_headers(site):
    r = site.request("GET", "/")
    h = {k.lower(): v for k, v in r.headers.items()}
    missing = [
        name
        for name in ("x-content-type-options", "referrer-policy", "permissions-policy")
        if name not in h
    ]
    return Result(
        PASS if not missing else WARN,
        "Privacy/security headers are sent (nosniff, referrer policy, permissions policy)",
        ""
        if not missing
        else f"Missing: {', '.join(missing)}. See docs/privacy.md section 'Headers'.",
    )


def check_cookie_flags(site):
    if urlparse(site.base).scheme != "https":
        return None
    r = site.request("GET", "/accounts/login/")
    cookies = r.headers.get("Set-Cookie", "")
    if "csrftoken" not in cookies:
        return Result(INFO, "No cookie to inspect on the login page")
    ok = "secure" in cookies.lower() and "samesite" in cookies.lower()
    return Result(
        PASS if ok else WARN,
        "Cookies are marked Secure and SameSite",
        "" if ok else "Set DEBUG=False on the live site (cookie flags are tied to it).",
    )


def check_privacy_pages(site):
    page = site.request("GET", "/privacy/")
    if page.status_code != 200:
        return Result(WARN, "No /privacy/ page", "Visitors are owed one: docs/privacy.md")
    if 'class="draft-banner"' in page.text:
        return Result(
            WARN,
            "Privacy policy is still marked DRAFT",
            "Read /privacy/ and /terms/, adjust them to your real practices, then set "
            "PRIVACY_REVIEWED=True. (Your call. Record it in docs/privacy_decisions.md.)",
        )
    return Result(PASS, "Privacy policy page exists and has been reviewed by the owner")


def check_google_button(site):
    r = site.request("GET", "/")
    on = "Continue with Google" in r.text
    return Result(
        INFO,
        "Google sign-in is " + ("ON" if on else "not configured yet (optional)"),
        "" if on else "docs/procedures/auth_google_oauth.md",
    )


LIVE_CHECKS = [
    check_health,
    check_home,
    check_static,
    check_login_pages,
    check_debug_off,
    check_machine_endpoint_closed,
    check_ops_private,
    check_https,
    check_hsts,
    check_privacy_headers,
    check_cookie_flags,
    check_privacy_pages,
    check_google_button,
]


# --------------------------------------------------------------------------- runner


def run(site=None) -> list[Result]:
    results = [check() for check in REPO_CHECKS]
    if site is not None:
        for check in LIVE_CHECKS:
            try:
                result = check(site)
            except requests.RequestException as exc:
                result = Result(
                    FAIL,
                    f"{check.__name__[6:].replace('_', ' ')}: could not reach the site",
                    f"{type(exc).__name__}. Is the server running / the URL right?",
                )
            if result is not None:
                results.append(result)
    return results


def report(results) -> int:
    marks = {PASS: "PASS", WARN: "WARN", FAIL: "FAIL", INFO: "info"}
    for r in results:
        print(f"[{marks[r.status]}] {r.title}")
        if r.hint:
            print(f"        -> {r.hint}")
    fails = sum(r.status == FAIL for r in results)
    warns = sum(r.status == WARN for r in results)
    passed = sum(r.status == PASS for r in results)
    print(f"\n{passed} passed, {warns} to improve, {fails} to fix.")
    print(
        "All clear."
        if not fails and not warns
        else "Fix the FAIL lines first, then the WARN lines."
        if fails
        else "No blockers. The WARN lines are worth a look."
    )
    return 1 if fails else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--url", help="also check a running site, e.g. https://my-site.onrender.com"
    )
    args = parser.parse_args(argv)
    return report(run(Site(args.url) if args.url else None))


if __name__ == "__main__":
    raise SystemExit(main())
