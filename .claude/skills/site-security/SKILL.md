---
name: site-security
description: >
  Keep the site, the repository and the owner's accounts safe: secrets handling, .gitignore and secret scanning,
  private repository, two-factor authentication, spend limits, hardened settings, rotating a leaked key, incident
  response, dependency updates, and reviewing security before launch. TRIGGER: "security", "secure", "secret", "api
  key leaked", "password in git", "rotate", "2fa", "two-factor", "hack", "breach", "vulnerability", "dependabot",
  "gitleaks", "is this safe", "leaked".
---

# Site security

Source of truth: [docs/security.md](../../../docs/security.md) (and [docs/privacy.md](../../../docs/privacy.md) for personal data). Re-read before advising.

## What is already protecting the owner (explain, don't re-build)

`.gitignore` for `.env`/`env/`/databases/backups/keys; a pre-commit check (`scripts/check_staged_secrets.py`) plus gitleaks over the full history in CI; a test that fails on key-shaped strings; `render.yaml` holds no secret values (`sync: false` / `generateValue`, enforced by a test); boot **refuses** to start on the dev `SECRET_KEY`;
HTTPS redirect, secure/HttpOnly/SameSite cookies, HSTS, Permissions-Policy; deny-by-default API with owner-scoped querysets; a fail-shut machine endpoint with constant-time token compare; AI spend caps; Dependabot.

## What only the owner can do (walk them through, one at a time)

Keep the GitHub repo **private** ([publish-to-github](../publish-to-github/SKILL.md)); **2FA** on GitHub, Render, Google, OpenAI and the registrar; restrict the Render GitHub App to this repo; provider-side spend limits; protect `main` and turn on GitHub secret scanning + push protection.

## Handling secrets in conversation

Never ask the owner to paste a secret into chat. They put it in `.env` or Render; you move it with `scripts/render_api.py env-set KEY --from-env NAME` or `--prompt`. If one lands in chat anyway, use it, say it should be rotated later, and continue. Never run `gh auth token`, never print `.env`.

## If a secret may have leaked

Revoke/rotate at the provider **first** (OpenAI, Google, Resend, Render, GitHub), update Render and `.env`, check provider usage logs for activity the owner doesn't recognise, and only then think about git history (rotating makes the old key dead; rewriting history is optional and needs the owner's OK).
Then add a test or hook so that mistake fails next time. If personal data may have been exposed, hand over to [privacy-advisor](../privacy-advisor/SKILL.md) (breach duties can have deadlines, e.g. 72 hours under GDPR).

## Two slips worth checking in every app

* **Anything that changes data is a POST.** A page load (GET) that creates or changes something can be triggered by a link preview, a prefetch or a crawler.
* **Redirects stay on the site.** Any `?next=` or similar parameter goes through Django's `url_has_allowed_host_and_scheme` before it is followed; otherwise a link can send a
  freshly signed-up person anywhere.

## Before launch

Run [verify-my-site](../verify-my-site/SKILL.md); `python manage.py check --deploy` with `DEBUG=False` and a throwaway key must be clean; read the CI result; confirm Dependabot PRs are merged only with green CI.
