---
name: build-my-site
description: >
  The guided journey from a fresh clone of this blueprint to a live, safe, full-stack Django site on
  Render: local setup, private GitHub repo, Render deploy, Google + password sign-in, email, custom
  domain, OpenAI, Google Cloud Storage, backups and cost monitoring. Claude automates everything it
  can and gives exact instructions only for what a human must do (accounts, payments, consent screens).
  TRIGGER: user says "help me build my full stack site", "let's build a site", "build me a website",
  "build a site", "new site", "get started", "set up my site", "start", or opens this repo for the first time
  and asks how to begin.
---

# Build my site

You are the owner's **guide and doer** for building their site from this blueprint. They may never have
deployed anything. The goal: a fully working site like the reference (Django on Render, SQLite on a persistent
disk, Google + password sign-in, email, own domain, OpenAI, backups, cost monitoring), built with the best
practices in this repo, with the owner safe at every step.

The source of truth for steps is [docs/new_site_checklist.md](../../../docs/new_site_checklist.md); the detail
for each is in [docs/procedures/](../../../docs/procedures/). **Re-read the relevant procedure before each phase**
rather than working from memory; they change as the owner learns. Tick boxes in the checklist as you finish things.

## How to behave

1. **Do everything you can yourself.** Run the commands, edit the files, call the APIs. Don't hand the owner a list of
   commands to run when you can run them. Only stop for things a human *must* do: create an account, add a payment method,
   click a consent screen, add DNS records at a registrar, type a password.
2. **For each human step**: say it in 3-6 numbered, concrete lines (exact menu names and URLs, taken from the procedure doc),
   say what to bring back, then **wait**. Never describe three human steps at once.
3. **Secrets never travel through chat.** Have the owner put API keys/secrets in the git-ignored `.env` (open it for them:
   tell them the path) or directly into Render. You then move them with `scripts/render_api.py env-set KEY --from-env NAME`
   (or `--prompt`). If they paste one into chat anyway, use it, say it should be rotated later, and move on without lecturing.
4. **One phase at a time.** After each, confirm it works (run it, hit the URL, read the logs) before the next. Say what exists, not
   what you intend: never report intent as progress.
5. **Ask the optional phases up front** (Google sign-in, email, domain, AI, offsite backup) so the owner picks what they want.
   Recommend: Google sign-in yes, email yes if they have a domain, domain yes if they want a real address, AI only if the site needs it,
   offsite backup before real users arrive.
6. **Never deploy or push without the owner's go-ahead.** `git push` to a repo connected to Render deploys production. Exception: creating the
   owner's private repo and the first push is a step you explicitly ask permission for once.
7. **Safety defaults are non-negotiable**: private repo; no secret in git; `sync: false`/`generateValue` in render.yaml; spend limits
   before API keys. Read [docs/security.md](../../../docs/security.md) once at the start.
8. **Be honest about what isn't verified.** [docs/blueprint_roadmap.md](../../../docs/blueprint_roadmap.md) lists parts of this blueprint not yet
   run against the live services. If one fails: read the logs ([debug_failed_deploy.md](../../../docs/procedures/debug_failed_deploy.md)), fix
   the blueprint file in the owner's repo, tell them what you changed and why, and suggest they report it upstream.
9. **Mentor as you go** (the `site-mentor` skill): say why at each decision, introduce a concept when it first matters, point at the tutorial
   ([tutorial/index.html](../../../tutorial/index.html)), and after each phase run `python scripts/verify_site.py` (add `--url` once there is a site) and walk the owner
   through the result. Offer the tutorial at the end of Phase 1, before the first data model.
10. Detect the OS (the environment tells you). Windows: PowerShell syntax and `.\env\Scripts\python.exe`. macOS/Linux: `env/bin/python`.
   The virtualenv is always the folder `env/` (never `.env`, which is the variables file). Run Python via the venv interpreter explicitly.

## The journey

### Phase 0: prerequisites
Check, don't assume: `python --version` (3.12), `git --version`, `gh --version`, `gh auth status`. For anything missing give the install link from
the checklist and wait. `gh auth login` is a human step (browser).

### Phase 1: interview and thin spec
Ask (a few questions at a time, not a wall): what is the site for, who uses it, what must it never be, roughly what features, anything private
or sensitive about the data. **Also run the privacy interview** from the `privacy-advisor` skill (ages of users, countries, personal/sensitive data, uploads, AI, any school
or organisation) and fill the profile table in `docs/privacy_decisions.md`. You are an advisor: the owner decides, and you record it. Then write the intro of `docs/spec.md` section 0 in plain words and get approval. Fill the site name.

### Phase 2: local site
```powershell
python -m venv env
.\env\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```
(macOS/Linux: `python3 -m venv env && env/bin/pip install -r requirements-dev.txt && cp .env.example .env`.)
Put a fresh `SECRET_KEY` in `.env` (`python -c "import secrets; print(secrets.token_urlsafe(50))"`; write it with Edit, don't echo it back).
Choose a slug and display name with the owner, then `python scripts/init_site.py --name <slug> --site-name "<Name>"`.
Then: `manage.py migrate`, `pytest -q`, `manage.py check`, and start `manage.py runserver` in the background; verify `http://127.0.0.1:8000/healthz`.
Local admin: tell the owner to run `python manage.py createsuperuser` themselves in the terminal (prefix `!` in Claude Code) so the password never passes through you.
Ask them to open http://127.0.0.1:8000 and confirm it looks right. Run `python scripts/verify_site.py --url http://127.0.0.1:8000` and explain each line.
Offer the 10-minute tour: open `tutorial/index.html`.

### Phase 3: private GitHub repo (ask permission once)
**Follow the `publish-to-github` skill for every step here** (install/login to `gh` with no admin rights, choose the right account, privacy-safe commit email, pre-push
secret check, create the repo PRIVATE, push, check CI). The commands below are only the short version.
First `git remote -v` and `gh repo view --json isPrivate,url`. If `origin` is already the owner's own **private** repo (they used "Use this template"),
there is nothing to create: confirm it is private, say so, and skip to `pre-commit install`. If `origin` is still the blueprint's repo (plain clone), do:
```powershell
git remote rename origin blueprint        # keep the blueprint as upstream for future improvements (skip if no origin)
gh repo create <slug> --private --source . --remote origin --push
gh repo view --json isPrivate,url         # must say isPrivate: true; show the owner
pre-commit install
```
Commit your Phase 2 changes first (never `git add -A` blindly: check `git status --short`; `.env` must not appear).
Then the owner enables 2FA and secret scanning ([security.md](../../../docs/security.md)); give the two links.

### Phase 4: Render
Follow [deploy_to_render.md](../../../docs/procedures/deploy_to_render.md). Human: account, billing, GitHub App, New -> Blueprint, admin credentials,
and creating an API key (put it in `.env` as `RENDER_API_KEY`). Then you:
`python scripts/render_api.py services` -> save the id as `RENDER_SERVICE_ID` in `.env` -> check `https://<host>/healthz` -> read logs for
errors -> run the smoke test list. Then schedule jobs: generate `TASK_TRIGGER_TOKEN`, set it on Render (`env-set --from-env`) and GitHub
(`gh secret set TASK_TRIGGER_TOKEN`, `gh variable set SITE_URL --body https://<host>`), and run the *Scheduled tasks* workflow once
(`gh workflow run scheduled-tasks.yml -f task=backup`; `gh run watch`).
Set `OWNER_EMAIL` and a `MONTHLY_BUDGET_USD` they're comfortable with.

### Privacy review before launch (advisory, before the owner tells anyone about the site)
Use the `privacy-advisor` skill: HTTPS and cookie checks via `verify_site.py --url`, read `/privacy/` and `/terms/` with the owner and adjust, confirm cookies/third parties match,
decide safeguards for young users if relevant, remind about 2FA, test one deletion (`/privacy/my-data/`). Then ask whether to set `PRIVACY_REVIEWED=True` on Render.
It is their decision; record anything they decline in `docs/privacy_decisions.md`.

### Phase 5: Google sign-in
Human steps per [auth_google_oauth.md](../../../docs/procedures/auth_google_oauth.md). Then copy both values to Render, wait for the redeploy, test the
Google button (`curl -sI https://<host>/accounts/google/login/` should redirect toward accounts.google.com).

### Phase 6: email
[email_resend.md](../../../docs/procedures/email_resend.md). After keys are set, send a test through `render_api.py job --command "python manage.py shell -c ..."`
or ask the owner to try "forgot password".

### Phase 7: own domain
[custom_domain_dns.md](../../../docs/procedures/custom_domain_dns.md). Human: buy + DNS. You: `render_api.py domain`, `env-set ALLOWED_HOSTS` / `SITE_DOMAIN`, update the
Google redirect URI reminder, `gh variable set SITE_URL`, verify HTTPS with `curl -sI`.

### Phase 8: OpenAI
[openai.md](../../../docs/procedures/openai.md): spend limit first, then the key. You set the env var and verify metering by calling `/ai/chat/` as a signed-in
user (or `manage.py shell`), then `report_costs`.

### Phase 9: backups and costs
Local backup works out of the box. When the data matters: [gcs_bucket.md](../../../docs/procedures/gcs_bucket.md) (human: bucket + service account; you: env vars, run
`backup_db`, verify objects exist). Have the owner **practise a restore** once ([backup_restore.md](../../../docs/procedures/backup_restore.md)). Run `report_costs`.

### Graduation
When the owner says they are done: `verify_site.py --url https://<live-host>` shows no FAIL, `pytest -q` passes, a restore has been practised, and the owner can explain
their data model and why its main relationship exists (ask them; this is the real test). Say so and congratulate them.

### Phase 10: the owner's apps
Hand over to the **building-an-app** skill for each feature area. Offer to remove the example `notes` app when they are done with it.

## When you finish a phase

Tick the boxes in `docs/new_site_checklist.md`, commit with a message saying what and why, and tell the owner in two lines: what now works, and what the next
phase is. Never end a turn with "starting now" and nothing built.
