---
name: building-an-app
description: >
  The standing methodology for building any new feature area on this site as its own isolated Django app: full encapsulation,
  database models only (never text/JSON as real data), a Django REST Framework CRUD API for every app, own templates/menu/docs,
  and the interview-first kickoff (thin intro spec, then a standalone data model the owner approves before the full spec and the
  normal backlog/sprint flow). Includes the mistakes-and-rules list behind each practice.
  TRIGGER: "new app", "build an app", "add a feature", "start an app", "add a page for", "app methodology",
  "add this to the methodology file", "kick off a new app", or any request to build a new feature area.
---

# Building an app on this site

**The authoritative content is [docs/building_an_app.md](../../../docs/building_an_app.md), not this file.** It is a living notes file the owner
adds to ("add this to the methodology file" means: edit that doc directly, in the section it fits, and confirm what you wrote).
**Always re-read it in full at the start of any work this skill covers.** The worked example is the `notes` app
([notes/](../../../notes/) + [docs/notes/](../../../docs/notes/spec.md)): copy its shape.

## What to do when this skill fires

1. Read `docs/building_an_app.md` in full.
2. **Starting a new app** -> run the kickoff sequence, one step at a time, waiting for the owner at the gate after step 3:
   1. **Interview** until purpose, audience and boundaries are clear. Don't assume.
   2. **Thin intro spec** (`docs/<app>/spec.md`): what the app is, in plain terms. Not the full spec.
   3. **Standalone data model** (`docs/<app>/data_model.md`): main classes and relationships. **Stop and wait for approval.**
   4. **Full spec**, high-level chapters, only after approval.
   5. **Normal flow**: `docs/<app>/backlog.md`, sprints, test-first, scaled to the app's size.
3. **Ongoing work on an existing app** -> apply the core rules as defaults unless a recorded exception exists.
4. **A new lesson was learned** -> add it to the doc (what happened, why it mattered, the rule).

## Core rules (quick reference; the doc has the reasoning)

1. Real data is database models, never text/JSON files (one-time seeding is fine, and must be idempotent: test it by running it twice).
2. Full encapsulation: never touch another app's models/views/data; app-specific user data = own one-to-one profile model.
3. Own base template and menu; classes prefixed with the app name; no link back to the site unless asked.
4. Own `docs/<app>/`: spec.md, backlog.md, data_model.md (separate), optional dashboard.
5. Migrate and deploy scoped to the app (`migrate <app_label>`); don't bundle unrelated work.
6. Every app gets a full documented CRUD REST API (DRF): deny by default, queryset scoped to the owner, owner never client-supplied.

## While building

* Tests: **refusals first** (anonymous, other user, bad input), then happy paths. Assert on the element, not a substring of the page.
  Ask of every test: what change to the product would make it fail?
* Look at each screen as an image once, at phone width.
* Scope any formatter/auto-fix to your own files. Update status docs in the same commit that acts on a decision.
* Wire it up: `INSTALLED_APPS`, `mysite/urls.py` (before the `core` catch-all, with a namespace), admin, docs, `.env.example`/`render.yaml`/`env_vars.md` for any new variable.
* Before saying done: `pytest -q`, `ruff check .`, `manage.py check`, `makemigrations --check`. **Don't push**; ask.
