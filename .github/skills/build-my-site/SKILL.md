---
name: build-my-site
description: >
  The guided journey from a fresh clone of this blueprint to a live, safe, full-stack Django site on
  Render: local setup, private GitHub repo, Render deploy, Google + password sign-in, email, custom
  domain, OpenAI, Google Cloud Storage, backups and cost monitoring. Claude automates everything it
  can and gives exact instructions only for what a human must do (accounts, payments, consent screens).
  TRIGGER: user says "tell me what to do", "what should I do", "what's next", "what now", "continue", "where were we",
  "help me build my full stack site", "let's build a site", "build me a website", "build a site", "new site", "get started",
  "set up my site", "start", "help", or opens this repo for the first time and asks how to begin.
---

# Build my site

You are the owner's **guide and doer** for building their site from this blueprint. They may never have
deployed anything. The goal: a fully working site like the reference (Django on Render, SQLite on a persistent
disk, Google + password sign-in, email, own domain, OpenAI, backups, cost monitoring), built with the best
practices in this repo, with the owner safe at every step.

The source of truth for steps is [docs/new_site_checklist.md](../../../docs/new_site_checklist.md); the detail
for each is in [docs/procedures/](../../../docs/procedures/). **Re-read the relevant procedure before each phase**
rather than working from memory; they change as the owner learns. Tick boxes in the checklist as you finish things.

## The first message, and coming back

The owner reached you by getting an editor with an AI chat open on their private copy of this project ([docs/get_started.md](../../../docs/get_started.md)), then typing something like
**"Tell me what to do"**. Assume they are new to all of this and that nothing but git and the editor is installed.

**Every time you are invoked, orient first (do this before anything else):**

0. **Check GitHub for updates and pull them in when safe** (CLAUDE.md rule 0): `python scripts/check_updates.py` (env Python if it exists; before Python is installed,
   `git fetch --all` and `git pull --ff-only` on a clean folder). Tell the owner in one plain sentence what arrived, if anything. If playbooks changed, **re-read
   this skill and `CLAUDE.md` before continuing**: the steps below may have improved.
1. Read [docs/new_site_checklist.md](../../../docs/new_site_checklist.md), `docs/spec.md`, `docs/backlog.md` and `docs/privacy_decisions.md`, and look at `git status` / `git log -5`.
2. **Fresh start** (no ticked boxes, `docs/spec.md` still a template): greet them in two sentences, show the journey in six lines (set up the computer; your idea; first working site; private repo; go live; extras),
   say you will do everything you can yourself and tell them exactly what to click when it needs *them*, then go to Phase 0.
3. **Coming back** (some boxes ticked): say where you are in three lines ("Done: ... Next: ... Waiting on you: ..."), and propose the very next step. Don't restart, don't re-ask what the docs already record.
4. Ask **one thing at a time**. When the owner just wants "what's next", answer with the single next action, not the whole plan.

Keep the checklist honest: tick a box in the same commit that does the work, so the next session can resume from it.

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

## Skills map (hand over to these; each has its own triggers)

| Need | Skill |
|---|---|
| Teach, explain, quiz, certify understanding | `site-mentor`, `data-model-coach`, `design-review` |
| Privacy advice (the owner decides) | `privacy-advisor` |
| Install and repair tools (Python, git, `gh`, PATH, venv) | `setup-my-computer` |
| GitHub repo, `gh` login, push, Pages | `publish-to-github` |
| Deploy and deploy trouble | `render-django` |
| Google sign-in / email / domain / AI | `google-sign-in`, `email-resend`, `custom-domain`, `openai-ai-features` |
| Backups, restore, costs | `backups-and-restore`, `cost-monitoring` |
| Check the work, security | `verify-my-site`, `site-security` |
| New feature or app, day-to-day operation | `building-an-app`, `site-ops` |

## The journey

### Phase 0: prerequisites (you install them; the owner does not)
The owner already has git, an editor and this chat. **Hand over to the `setup-my-computer` skill**: it detects what is installed, installs what is missing (Python, the GitHub CLI, optional editor
extensions) without admin rights where possible, fixes PATH and "command not found" problems, and builds the virtualenv. Show the owner the detect table before and after.
`gh auth login` is the one human step here (browser; see `publish-to-github`).
**Python:** 3.12 is the target. Any 3.11-3.13 works locally (Django 5.2), but then set `PYTHON_VERSION` in `render.yaml` to a version you actually run, so "works here" means "works there" (gotcha #28).
Only if you cannot fix something yourself, give the owner the one specific thing to do (a download link, a checkbox), and wait.

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
First `git remote -v` and `gh repo view --json isPrivate,url`.

**Commit Phase 2 first.** `init_site.py` renamed `render.yaml`, and Render deploys *what is on GitHub*: if you skip this, the first deploy uses the placeholder name `my-site`.
```powershell
git status --short                  # .env and env/ must NOT appear; read the list
git add <the files shown>           # name them; use -A only once the list looks right
git commit -m "Name the site and set it up locally"
```
(The pre-commit hook, installed below, also refuses secrets; the first run downloads ruff, so allow a minute.)

* **Normal path: `origin` is still the blueprint** (`github.com/avisalmon/FullStackBKM`; the setup guide has everyone clone it directly). The owner cannot push to it
  (no write access), so nothing can leak there. Explain in one sentence that you are now creating *their own private* copy on GitHub, ask for the OK, then:
```powershell
git remote rename origin blueprint        # keep the blueprint as upstream for future improvements
gh repo create <slug> --private --source . --remote origin --push     # creates the repo and pushes
gh repo view --json isPrivate,url         # must say isPrivate: true; show the owner
```
* **Alternative: `origin` is already the owner's own private repo** (people who used "Use this template"): confirm it is private, say so, then `git push`. Nothing deploys yet, because Render is not connected.

Then, in both cases: `pre-commit install` (inside the env), and the owner enables 2FA and secret scanning ([security.md](../../../docs/security.md)); give the two links.
**From the moment Render is connected (Phase 4), every push deploys production**: ask first.

### Phase 4: Render
Follow [deploy_to_render.md](../../../docs/procedures/deploy_to_render.md). Human: account, billing, GitHub App, New -> Blueprint, admin credentials,
and creating an API key (put it in `.env` as `RENDER_API_KEY`). Then you:
`python scripts/render_api.py services` (prints each service's id, name and live URL) -> save the id as `RENDER_SERVICE_ID` in `.env` -> check `<url>/healthz` (the dashboard shows the URL too) -> read logs for
errors -> run the smoke test list. Then schedule jobs: generate `TASK_TRIGGER_TOKEN`, set it on Render (`env-set --from-env`) and GitHub
(`gh secret set TASK_TRIGGER_TOKEN`, `gh variable set SITE_URL --body https://<host>`), and run the *Scheduled tasks* workflow once
(`gh workflow run scheduled-tasks.yml -f task=backup`; `gh run watch`).
Set `OWNER_EMAIL` and a `MONTHLY_BUDGET_USD` they're comfortable with.

### Privacy review before launch (advisory, before the owner tells anyone about the site)
Use the `privacy-advisor` skill: HTTPS and cookie checks via `verify_site.py --url`, read `/privacy/` and `/terms/` with the owner and adjust, confirm cookies/third parties match,
decide safeguards for young users if relevant, remind about 2FA, test one deletion (`/privacy/my-data/`). Then ask whether to set `PRIVACY_REVIEWED=True` on Render.
It is their decision; record anything they decline in `docs/privacy_decisions.md`.

### Phase 5: Google sign-in
*Use the `google-sign-in` skill for the detail.*
Human steps per [auth_google_oauth.md](../../../docs/procedures/auth_google_oauth.md). Then copy both values to Render, wait for the redeploy, test the
Google button (`curl -sI https://<host>/accounts/google/login/` should redirect toward accounts.google.com).

### Phase 6: email
*Use the `email-resend` skill for the detail.*
[email_resend.md](../../../docs/procedures/email_resend.md). After keys are set, send a test through `render_api.py job --command "python manage.py shell -c ..."`
or ask the owner to try "forgot password".

### Phase 7: own domain
*Use the `custom-domain` skill for the detail.*
[custom_domain_dns.md](../../../docs/procedures/custom_domain_dns.md). Human: buy + DNS. You: `render_api.py domain`, `env-set ALLOWED_HOSTS` / `SITE_DOMAIN`, update the
Google redirect URI reminder, `gh variable set SITE_URL`, verify HTTPS with `curl -sI`.

### Phase 8: OpenAI
*Use the `openai-ai-features` skill for the detail.*
[openai.md](../../../docs/procedures/openai.md): spend limit first, then the key. You set the env var and verify metering by calling `/ai/chat/` as a signed-in
user (or `manage.py shell`), then `report_costs`.

### Phase 9: backups and costs
*Use the `backups-and-restore` and `cost-monitoring` skill for the detail.*
Local backup works out of the box. When the data matters: [gcs_bucket.md](../../../docs/procedures/gcs_bucket.md) (human: bucket + service account; you: env vars, run
`backup_db`, verify objects exist). Have the owner **practise a restore** once ([backup_restore.md](../../../docs/procedures/backup_restore.md)). Run `report_costs`.

### Graduation
When the owner says they are done: `verify_site.py --url https://<live-host>` shows no FAIL, `pytest -q` passes, a restore has been practised, and the owner can explain
their data model and why its main relationship exists (ask them; this is the real test). Say so and congratulate them.

**Then offer to make the repo theirs** (optional, one at a time): replace the blueprint's `README.md` with a short README for *their* site (name, what it is, how to run it, link to `docs/`);
replace `index.html` (the blueprint's landing page) or delete it; remove the example `notes` app if they no longer need it ([removal steps](../../../docs/new_site_checklist.md)); keep or change `LICENSE`
(MIT came with the template; a private business site may prefer to remove it); fill in `docs/spec.md` and `docs/backlog.md`. Keep `git remote blueprint` if they want future blueprint improvements (`git fetch blueprint`).

### Phase 10: the owner's apps
Hand over to the **building-an-app** skill for each feature area. Offer to remove the example `notes` app when they are done with it.

## When you finish a phase

Tick the boxes in `docs/new_site_checklist.md`, commit with a message saying what and why, and tell the owner in two lines: what now works, and what the next
phase is. Never end a turn with "starting now" and nothing built.
