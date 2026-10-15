# From clone to live site: the checklist

The `build-my-site` skill walks you through this. Tell Claude **"Help me build my full stack site"** and it
does everything marked **Claude** itself and stops with exact instructions for each **You** step.
Claude updates the tick-boxes here (this file becomes your site's journey log).

Legend: **Claude** = automated, no action needed. **You** = only a human can do it (accounts, payments, consent screens).

## Phase 0 - Prerequisites (You, once per computer)

- [ ] Python 3.12 (https://www.python.org/downloads/)
- [ ] Git (https://git-scm.com/downloads)
- [ ] GitHub account + GitHub CLI: https://cli.github.com, then `gh auth login`
- [ ] Claude Code (VS Code extension, desktop app or CLI), signed in
- [ ] A code editor if you don't have one (VS Code)

## Phase 1 - Understand what you're building (Claude interviews you)

- [ ] Claude asks what the site is for, who uses it, what it must never be
- [ ] Claude writes the thin intro to `docs/spec.md`; you approve it

## Phase 2 - Local site (Claude)

- [ ] Virtualenv `env` created, dependencies installed
- [ ] `.env` created with a fresh secret key
- [ ] `python scripts/init_site.py --name <slug> --site-name "<Name>"`
- [ ] Database migrated, tests green, site running at http://127.0.0.1:8000
- [ ] **You:** open it in a browser and say it looks right

## Phase 3 - Private GitHub repo (Claude, after your OK)

- [ ] Blueprint remote renamed `blueprint` (so you can pull blueprint improvements later)
- [ ] `gh repo create <slug> --private`, first push
- [ ] Verified private. **You:** turn on 2FA, secret scanning ([security.md](security.md))

## Phase 4 - Go live on Render

- [ ] **You:** Render account, billing, install the Render GitHub App on the repo ([deploy_to_render.md](procedures/deploy_to_render.md))
- [ ] **You:** New -> Blueprint -> pick repo; type admin username/email/password; Deploy
- [ ] **You:** Render -> Account Settings -> API Keys -> create; put it in `.env` as `RENDER_API_KEY` (local only)
- [ ] **Claude:** finds the service, checks `/healthz`, reads logs, smoke-tests the live site
- [ ] **Claude:** generates `TASK_TRIGGER_TOKEN`, sets it on Render and in GitHub, sets `SITE_URL` ([backup_restore.md](procedures/backup_restore.md))

## Phase 5 - Sign-in with Google (optional but recommended)

- [ ] **You:** Google Cloud project, consent screen, OAuth client ([auth_google_oauth.md](procedures/auth_google_oauth.md)); keys into `.env`
- [ ] **Claude:** copies them to Render, redeploys, tests the Google button

## Phase 6 - Email (optional)

- [ ] **You:** Resend account, domain, DNS records, API key ([email_resend.md](procedures/email_resend.md))
- [ ] **Claude:** sets variables, sends a test email

## Phase 7 - Your own domain (optional)

- [ ] **You:** buy a domain; add the DNS records Render shows ([custom_domain_dns.md](procedures/custom_domain_dns.md))
- [ ] **Claude:** adds the domain to Render, sets `ALLOWED_HOSTS`/`SITE_DOMAIN`, updates `SITE_URL`, checks HTTPS

## Phase 8 - AI features (optional)

- [ ] **You:** OpenAI account, **spend limit first**, API key ([openai.md](procedures/openai.md))
- [ ] **Claude:** sets `OPENAI_API_KEY`, verifies metering and the caps

## Phase 9 - Backups and cost monitoring

- [ ] **Claude:** local backup works; weekly schedule verified by a manual workflow run
- [ ] **You (when the data matters):** Google Cloud Storage bucket + service account ([gcs_bucket.md](procedures/gcs_bucket.md))
- [ ] **Claude:** offsite backup verified; **You:** practise one restore ([backup_restore.md](procedures/backup_restore.md))
- [ ] **Claude:** `MONTHLY_BUDGET_USD`, `OWNER_EMAIL` set; daily cost report running ([cost_monitoring.md](procedures/cost_monitoring.md))

## Phase 10 - Build your apps

For each feature area, Claude follows [building_an_app.md](building_an_app.md): interview, thin spec,
**data model for your approval**, full spec, then backlog/sprints with tests. The example `notes` app is removed
when you no longer need it (see below).

### Removing the example `notes` app

1. `mysite/settings.py`: delete `"notes"` from `INSTALLED_APPS`
2. `mysite/urls.py`: delete the `notes/` include
3. `templates/core/home.html`: delete the link to `notes:list`; `core/views.py`: remove `/notes/` from robots
4. Delete `notes/`, `static/notes/`, `docs/notes/`, `tests/test_notes_api.py`
5. `pytest -q` and `python manage.py check` still pass

## Ongoing

Use the `site-ops` skill: "check the logs", "back up now", "how much is this costing", "roll back".
