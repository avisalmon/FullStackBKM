# FullStuckBKM: build a real full-stack website with Claude

A blueprint for building, deploying and running a **production full-stack website** (Django on Render) by
working with Claude. It carries every skill, best practice and piece of infrastructure from a real production site,
so Claude can walk you from zero to a live, safe site and do almost all of the work for you.

**What you end up with**

| | |
|---|---|
| Hosting | [Render](https://render.com): Django, HTTPS, auto-deploy from GitHub, about **$7.25/month** |
| Data | SQLite on a persistent disk; uploaded files (media) and static files handled |
| Sign-in | Email + password **and** "Continue with Google" |
| Email | Real transactional email (password resets, alerts) via Resend |
| Domain | Your own domain name with HTTPS |
| AI | OpenAI built in, with a monthly spend cap and per-user limits |
| Storage / backups | Scheduled backups, offsite copy in a Google Cloud Storage bucket, tested restore |
| Costs | A monthly cost report and a budget alert, so a bill never surprises you |
| Safety | Private GitHub repo, no secrets in git (scanned on every commit), safe-by-default settings, 2FA guidance |
| Method | The same way of building apps (data model first, encapsulated apps, REST API, tests) as the reference site |

## Start in three steps

**1. Install the basics once** (only what you don't already have):

* [Python 3.12](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads)
* A [GitHub](https://github.com) account, and the [GitHub CLI](https://cli.github.com) (then run `gh auth login`)
* [Claude Code](https://claude.com/claude-code): the VS Code extension, the desktop app, or the terminal CLI, signed in to your Claude account
* [VS Code](https://code.visualstudio.com) if you want an editor

**2. Get your own private copy**

Easiest: on this repo's GitHub page click **Use this template -> Create a new repository -> Private**, name it after your site,
then clone *your* new repo:

```bash
git clone https://github.com/<you>/<your-site>.git
cd <your-site>
```

(Alternative: `git clone` this repo directly; Claude will create your private repo for you in the next step.)

**3. Open the folder in Claude Code and say:**

> **Help me build my full stack site**

That's it. Claude takes it from there: it interviews you about the site, sets everything up on your computer, creates your private repo,
deploys to Render, and then, only if you want them, adds Google sign-in, email, your own domain, AI, backups and cost monitoring.
Claude does everything it can by itself; when something needs *you* (opening an account, adding a card, a consent screen, a DNS record)
it tells you exactly what to click and waits. You never need to paste a secret into the chat.

## What to expect

| | |
|---|---|
| Time | The first live site: about an hour, most of it account sign-ups. The rest at your own pace |
| Cost | Render Starter + disk ~**$7.25/month**; domain ~$10-15/year; Resend, Google, GitHub free tiers are enough to start; OpenAI is pay-as-you-go **and capped** |
| You provide | Accounts (Render, Google Cloud, Resend, OpenAI, a domain registrar), a card for Render/OpenAI, passwords for your admin login |
| Claude provides | Everything else: code, configuration, deploys, tests, logs, backups, documentation |

The full journey, phase by phase, with who does what, is in [docs/new_site_checklist.md](docs/new_site_checklist.md).

## What's in the box

```
CLAUDE.md                   Claude's standing instructions for this repo
.claude/skills/             The playbooks: build-my-site, building-an-app, render-django, site-ops
mysite/                     Django project (production-ready settings, URLs)
core/                       Home page, health check, OpenAI helper, cost report, GCS client, backup & ops commands
notes/                      A small example app that shows the methodology (copy its shape, delete it later)
templates/ static/          Site layout and assets
tests/                      The safety net (deploy-config guards, API refusals, backups, caps, secret scan)
docs/                       Methodology, procedures, security, checklists. Start at docs/README.md
scripts/                    init_site.py (rename placeholders), render_api.py (drive Render from the terminal)
render.yaml  build.sh       The Render Blueprint
.github/workflows/          CI (lint, tests, secret scan), scheduled backup & cost jobs
```

## Doing it by hand (without Claude)

Everything Claude does is written down. Follow [docs/new_site_checklist.md](docs/new_site_checklist.md); each phase links to a step-by-step procedure.
For a quick local run:

```powershell
python -m venv env                                  # the virtualenv is ALWAYS the folder `env`
.\env\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env                         # then edit .env
.\env\Scripts\python.exe manage.py migrate
.\env\Scripts\python.exe manage.py runserver        # http://127.0.0.1:8000
.\env\Scripts\python.exe -m pytest -q
```
(macOS/Linux: `python3 -m venv env && env/bin/pip install -r requirements-dev.txt`, then `env/bin/python manage.py ...`.)

## Safety, in one paragraph

Keep your GitHub repo **private**, turn on two-factor authentication everywhere, set spend limits at OpenAI and Google, and never put a key in a chat or a commit.
The blueprint backs this up with git-ignored secrets, secret scanning, fail-shut settings, caps and tests, but the few steps only you can do are listed in [docs/security.md](docs/security.md).

## Honest status

The code and its 70+ tests run locally and in CI. A few steps talk to real services (Render Blueprint creation, GCS, OpenAI, the Render API's deploy/env endpoints) and
were written from a working production site's proven calls and the vendors' docs, but have not yet all been exercised end to end.
They're listed in [docs/blueprint_roadmap.md](docs/blueprint_roadmap.md); if one misbehaves, Claude reads the logs, fixes it in your copy and tells you.

## Share it

To help a friend build a site: *"Read the README of this repo and good luck: `<this repo's URL>`."* That's the whole instruction.

## GitHub Pages

[index.html](index.html) is a one-page overview of this blueprint, served at `https://<user>.github.io/<repo>/` when Pages is enabled
(Settings -> Pages -> Deploy from branch `main`, folder `/`). Your own site's pages are served by Render, not GitHub Pages.
