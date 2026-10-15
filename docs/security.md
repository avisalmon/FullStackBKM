# Keeping your site and your accounts safe

The blueprint is built so the *default* is the safe choice. This page is the list of what protects
you, and the few things only you can do.

## What is already done for you

| Risk | Protection |
|---|---|
| Secrets in git | `.gitignore` excludes `.env`, `env/`, databases, media, backups, keys. `pre-commit` runs **gitleaks** before each commit; CI scans history; `tests/test_no_secrets_committed.py` fails on anything key-shaped |
| Secrets in the cloud config | `render.yaml` holds no secret values: `sync: false` (you type them in Render) or `generateValue` (Render invents them). A test enforces it |
| Weak production key | Boot **refuses** to start with `DEBUG=False` and no real `SECRET_KEY` |
| Plain-http traffic | HTTPS redirect, secure cookies, HSTS (all on when `DEBUG=False`); `check --deploy` runs in CI |
| Leaked machine endpoint | `/internal/run/<task>/` is POST-only, constant-time token compare, **fails shut** when the token is unset, and can only run two allow-listed tasks |
| Data exposure | The API is deny-by-default (`IsAuthenticated`); each viewset scopes its queryset to the owner; another person's object is a 404 |
| Bots mailing strangers | `ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS = False` |
| Runaway AI spend | Monthly cap + per-person daily limit + stub mode |
| Bad dependencies | Dependabot weekly PRs |
| Lost data | Snapshots, offsite copy, [restore procedure](procedures/backup_restore.md) |

## What only you can do

1. **Keep the GitHub repo PRIVATE** (`gh repo create <name> --private`; the `build-my-site` skill does this).
   Check: Settings -> General -> Danger Zone shows "Change visibility" -> *Private*. Do not make it public
   without first reading the full history for secrets (a deleted secret is still in history; rotate it).
2. **Two-factor authentication** on GitHub, Render, Google, OpenAI and your registrar. Use a password manager.
3. **Restrict the Render GitHub App** to this repo only (gotcha #6).
4. **Set provider-side spend limits** (OpenAI budget, GCP budget alert).
5. **Protect `main`** (GitHub -> Settings -> Branches): require the CI checks to pass. Optional for a solo owner, wise for a team.
6. **Turn on GitHub secret scanning + push protection** (Settings -> Code security). Free for private repos on most plans.
7. **Never paste a secret into a chat, issue, or screenshot.** Put it in `.env` or Render. If one leaks anywhere, rotate it immediately
   (new key -> update Render -> revoke the old). Rotation costs minutes; a leak costs far more.

## Secrets and Claude

Claude can run commands for you, so it can *use* secrets without seeing them: `render_api.py env-set --from-env NAME`
reads a value from your environment, and `--prompt` asks you to type it hidden. Prefer those. If you must
share a key with an assistant, treat it as burnable: it will sit in a transcript.

When an automation needs a key, give it a **narrow** one: a single-purpose token whose worst case you can state in one
boring sentence (see "a key, without giving it the house" in [building_an_app.md](building_an_app.md)).

## If you suspect a leak

1. Revoke/rotate the credential at its provider (OpenAI, Google, Resend, Render, GitHub).
2. Update the new value in Render and your `.env`.
3. Check provider usage logs for activity you don't recognise.
4. If it was committed: rotating is mandatory; rewriting history is optional because the old key is dead.
5. Add a test or hook so that shape of mistake fails next time.

## Personal data

If your site stores other people's data (accounts, uploads), you own that responsibility: publish a privacy page,
collect only what you need, keep backups encrypted at rest (GCS does by default) and delete on request. Never
commit a production database snapshot. For minors' data, take proper advice before launching.
