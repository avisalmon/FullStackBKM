# FullStackBKM

### Go from "I have an idea" to a real, live, safe website, with Claude building it beside you.

<!-- last-updated:start -->
**Last updated 20 October 2026** · 4 new lessons · [See what's new](docs/lessons_log.md)
<!-- last-updated:end -->

---

## What you will have

In an afternoon you will have a **real website on the internet**, not a demo and not a mock-up:

* **Your own address** (`https://your-name.com`) with the padlock, served from a professional host.
* **Visitors who can sign up and sign in**, with an email and password or with one click through Google.
* **A database that remembers things**, uploaded photos and files included, that survives every update.
* **Email that actually arrives**: password resets, notifications, alerts to you.
* **AI built in** when you want it, with a spending cap so it can never run away with your money.
* **Backups running by themselves**, a copy stored in a separate Google Cloud bucket, and a restore you have practised.
* **A cost dashboard and a budget alert**, so the bill never surprises you (the baseline is about $7 a month).
* **A site that is safe by default**: a private code repository, no passwords or keys in your code, scanning on every change,
  and an automatic checker that tells you if you did something risky.
* **Privacy built in**, advised not imposed: HTTPS and safe cookies, policy and terms pages generated from how your site really works,
  a "My data" page where people download or delete their own data, consent records, and guidance for sites used by young people.

## What you will be able to do

* **Add a feature by describing it.** "Members should be able to post recipes and review each other's." Claude interviews you,
  designs the data with you, builds it with tests, and you review it on your screen before anything goes live.
* **Ship with confidence.** You push when *you* decide. Every change is tested first, and a bad release can be rolled back.
* **See and steer your site.** What it costs, what it is doing, what went wrong: ask, and Claude reads the logs and tells you.
* **Prove it is healthy.** One command (`scripts/verify_site.py`) checks your repo and your live site and tells you exactly what to fix.
* **Recover from disasters.** Wrong deploy, deleted data, lost disk: there is a written procedure for each, and you will have rehearsed one.
* **Hand it to someone else.** Everything about how the site works is written down in the repo.

## What you will learn

You will not just receive a site; you will understand it. Claude acts as your **mentor** as it builds:

* **How a web app works**, in plain words, and the shared vocabulary (model, view, migration, API...) so you and Claude speak the same language.
* **How to design your data**, which is the skill that decides whether a site is easy or painful to grow: what a *data model* is,
  why *relationships* matter, how to find them in your own idea, and the classic mistakes. There is a short interactive tutorial for it:
  **[tutorial/index.html](tutorial/index.html)** (open it in your browser, it works offline).
* **How to judge design**: hierarchy, spacing, mobile, forms, empty states. Claude reviews each screen with you using a real checklist
  ([docs/design_guide.md](docs/design_guide.md)).
* **How to think about privacy**: cookies, what to collect (and not), consent, students and minors, people's rights. Claude is your **advisor**: it explains what it
  recommends and why, you decide, and your choices are recorded ([docs/privacy.md](docs/privacy.md)). It is not legal advice.
* **How to work with an AI engineer well**: what to decide yourself, what to delegate, and what to double-check.

## What to expect (honestly)

| | |
|---|---|
| **Time** | A live site in about an hour, most of it signing up for accounts. Google sign-in, email, domain, AI and backups take a few minutes each, at your pace |
| **Cost** | Hosting about **$7.25/month** on Render; a domain about $10-15/year. Your AI engine: GitHub Copilot and Claude both have plans with limited free use, and a long guided build usually needs a **paid plan** (check yours before you start). Resend, Google and GitHub free tiers are enough to start; OpenAI is pay-as-you-go **and capped** |
| **Your part** | Opening accounts, adding a payment card, clicking consent screens, creating DNS records, choosing a password, and *deciding what your site is for*. Claude tells you exactly what to click and waits |
| **Claude's part** | Everything else: code, configuration, tests, deploys, logs, backups, documentation, and explaining it as it goes |
| **Not magic** | The first deploy can hit a snag (every platform does). The repo records 30 known traps and a debugging routine, and Claude reads the logs and fixes things in front of you |
| **You stay in charge** | Nothing goes live without your say-so, no secret ever needs to be pasted into chat, and every decision about your product is yours |
| **Not for** | Sites with strict compliance needs (payments, medical data, minors' data) without proper advice. This gets you a solid foundation and privacy-minded defaults, not a legal review |

---

## Start here

You do a few things once; after that the chat guides you and does the work.

**1. Get this page.** You are here. Everything below is the whole path.

**2. Get a working editor with an AI chat (once, 20-40 minutes).** Every click is in **[docs/get_started.md](docs/get_started.md)**, with a
"you know it worked when" check at each step. In short:

* a free [GitHub](https://github.com/signup) account, with two-factor sign-in on (a code from your phone as well as your password),
* [VS Code](https://code.visualstudio.com), the editor,
* an AI chat inside VS Code: **GitHub Copilot** (Agent mode) **or** **Claude Code**. Sign in and type `hello`: when it answers, your editor works.
* [Git](https://git-scm.com/downloads), the tool that copies the project to your computer (reopen VS Code afterwards).

**3. Copy the project to your computer and open it.** In VS Code choose **Terminal -> New Terminal**. A terminal is a panel where you type commands instead of clicking;
the guide explains it from scratch. Run these four lines one at a time (press Enter after each, wait for the prompt to come back), using your own short site name instead of `my-site`:

```powershell
mkdir C:\sites
cd C:\sites
git clone https://github.com/avisalmon/FullStackBKM.git my-site
code my-site
```

A new VS Code window opens on your copy; click **Yes, I trust the authors**. This copy lives only on your computer; the chat creates your own **private** GitHub repository for it later, with your OK.

**4. Open the AI chat** in that window (Copilot: **Agent** mode; Claude Code: its panel) **and type:**

> **Tell me what to do**

**5. Follow the chat.** It checks your computer and **installs what is missing itself** (Python, the GitHub CLI, the project's tools), asks what your site is for, builds it with you,
and tells you exactly what to click whenever a step needs *you*. Come back any day, say the same sentence, and it resumes where you stopped, after first pulling in any improvements to the blueprint (safely, and it tells you what changed).

| You do (once) | The chat does (for you) |
|---|---|
| Create a GitHub account; install Git and VS Code | Installs Python and GitHub's command-line tool, fixes "command not found" problems, builds the project |
| Install and sign in to Copilot or Claude Code | Interviews you, writes the plan and the data model with you, builds the site, runs the tests |
| Log in to GitHub once in the browser; click through accounts that only you can open (Render, Google, Resend, OpenAI, a domain registrar) and add a card | Creates your private GitHub repo, deploys, reads the logs, sets the keys without you pasting them, sets up backups and cost alerts |
| Decide what your site is for and what to collect | Teaches you as it goes, reviews each screen, checks your work |

New to a word (repository, terminal, deploy, DNS...)? The setup guide ends with **Words you'll meet**, in plain language.
The whole journey, phase by phase and who does what, is in [docs/new_site_checklist.md](docs/new_site_checklist.md).

## How you know you did it right

Run the checker whenever you like. It is read-only and tells you what to fix:

```powershell
.\env\Scripts\python.exe scripts\verify_site.py                                  # your repository
.\env\Scripts\python.exe scripts\verify_site.py --url http://127.0.0.1:8000      # + your local site
.\env\Scripts\python.exe scripts\verify_site.py --url https://your-site.onrender.com   # + your live site
```

You have **graduated** when: the checker shows no FAIL, your tests pass, you have practised one restore, and you can explain in your own words
what your data model is and why its main relationship exists. Ask Claude "quiz me" if you want to find out.

---

## What's in the box

```
CLAUDE.md                   Claude's standing instructions for this repo
.claude/skills/             18 playbooks for Claude Code: build-my-site, setup-my-computer, publish-to-github, render-django, site-ops, building-an-app, site-mentor,
                            privacy-advisor, google-sign-in, email-resend, custom-domain, openai-ai-features, backups-and-restore,
                            cost-monitoring, verify-my-site, site-security, data-model-coach, design-review
.github/skills/             The same 18 playbooks for GitHub Copilot (generated copy, kept identical by CI)
.github/copilot-instructions.md, AGENTS.md   Generated instructions + an index of every skill and its trigger phrases
tutorial/                   Interactive lessons: how Django works, data models and relationships
mysite/                     Django project (production-ready settings, URLs)
core/                       Home page, health check, OpenAI helper, cost report, GCS client, backup & ops commands
notes/                      A small example app that shows the methodology (copy its shape, delete it later)
templates/ static/          Site layout and assets
tests/                      The safety net (deploy-config guards, API refusals, backups, caps, secret scan)
docs/                       Methodology, procedures, security, design guide, checklists. Start at docs/README.md
scripts/                    init_site.py, render_api.py (drive Render), verify_site.py (check your work)
render.yaml  build.sh       The Render Blueprint
.github/workflows/          CI (lint, tests, secret scan), scheduled backup & cost jobs
```

## Doing it by hand (without Claude)

Everything Claude does is written down. Follow [docs/new_site_checklist.md](docs/new_site_checklist.md); each phase links to a step-by-step procedure. For a quick local run:

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
The blueprint backs this up with git-ignored secrets, secret scanning, fail-shut settings, caps, tests and the verify script, but the few steps only you can do are listed in
[docs/security.md](docs/security.md).

## Honest status

The code and its 120+ tests run locally and in CI, and a fresh clone has been installed and run end to end. A few steps talk to real services (Render Blueprint creation, GCS, OpenAI, the Render API's deploy/env endpoints) and were written
from a working production site's proven calls and the vendors' docs, but have not yet all been exercised end to end. They are listed in
[docs/blueprint_roadmap.md](docs/blueprint_roadmap.md); if one misbehaves, Claude reads the logs, fixes it in your copy and tells you.

## License

[MIT](LICENSE): use it, change it, build your own sites and products with it. Keep the copyright notice.

## Share it

To help a friend build a site, send them the page: **https://avisalmon.github.io/FullStackBKM/** . It leads them through setting up an editor with an AI chat, and from there the chat does the rest.

## GitHub Pages

[index.html](index.html) is the blueprint's landing page and the tutorial is under `/tutorial/`. They are live at **https://avisalmon.github.io/FullStackBKM/**
(Settings -> Pages -> Deploy from branch `main`, folder `/`). Your own site's pages are served by Render, not GitHub Pages, and a private repo cannot use Pages on the free plan.
