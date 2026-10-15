# Instructions for Claude working in this repo

This repo is a **blueprint for a full-stack website: Django on Render**, with SQLite on a persistent disk, Google + password
sign-in, email, OpenAI, Google Cloud Storage, backups and cost monitoring, plus the methodology for building apps on it.
The person you are helping is the **site owner** and may be new to all of this.

## First thing: which situation are you in?

* The owner says anything like **"help me build my full stack site"**, "let's build a site", "get started" (or this is clearly a fresh
  clone) -> **invoke the `build-my-site` skill** and follow it. It guides the whole journey, automates what it can, and gives exact
  instructions only for steps a human must do.
* The owner asks to *understand* something, wants design advice, or asks "did I do it right?" -> `site-mentor` skill. **Teach as you build** (see rule 9).
* They want a new feature or app -> `building-an-app` skill (and read [docs/building_an_app.md](docs/building_an_app.md) in full first; it changes).
* Privacy, cookies, consent, children/students, personal data, policies -> `privacy-advisor` skill (an advisor: the owner decides).
* Deploy or deploy trouble -> `render-django` skill. Day-to-day operation (logs, backups, costs, rollback) -> `site-ops` skill.
* "Add this to the methodology file" -> edit [docs/building_an_app.md](docs/building_an_app.md) directly and confirm what you wrote.

The map of all documentation is [docs/README.md](docs/README.md).

## Standing rules (apply to everything)

1. **The virtualenv is the folder `env/`**, always: not `.env` (that is the git-ignored variables file), not `venv`/`.venv`. Run Python through it:
   Windows `.\env\Scripts\python.exe` / `.\env\Scripts\Activate.ps1; <cmd>`; macOS/Linux `env/bin/python`. Shell state does not persist between
   commands, so activate or call the interpreter explicitly in every command.
2. **`git push` deploys production** (Render auto-deploys `main`). Commit freely; **push only when the owner says** deploy / push / go live. Never push to "see if it works".
3. **Secrets**: never in git, never in `render.yaml` values (only `sync: false` / `generateValue`), never in chat. Use `.env` (local) and the Render dashboard or
   `scripts/render_api.py env-set --from-env/--prompt`. Never `git add -A` without checking `git status --short` (`.env` and `env/` must never appear).
   The repo on GitHub must be **private**.
4. **Dependencies** live in `requirements.txt` (runtime) and `requirements-dev.txt` (tooling). Add a package there when you need it, then install with
   `pip install -r requirements-dev.txt` inside `env`.
5. **Local = dev, Render = production.** Test locally first: `pytest -q`, `ruff check .`, `python manage.py check`.
6. **Logs before code** when a deploy fails ([docs/procedures/debug_failed_deploy.md](docs/procedures/debug_failed_deploy.md)).
7. **Tell the truth about status**: say what exists, not what you intend; mark docs DONE in the same commit that does the work; say plainly
   when something is unverified ([docs/blueprint_roadmap.md](docs/blueprint_roadmap.md) lists what hasn't been run against live services).
8. Match the code that is already there: small modules, comments that explain *why* (usually a past failure), tests that fail when the behaviour breaks.
9. **Mentor, don't just build.** The owner may be new to this. At each decision say *why* in a sentence, use the shared vocabulary from
   [tutorial/index.html](tutorial/index.html), and before any data-model approval teach the data model and relationships using
   [tutorial/data-models.html](tutorial/data-models.html). Review each finished screen against [docs/design_guide.md](docs/design_guide.md)
   (at most three ranked suggestions). Verify work with `python scripts/verify_site.py [--url ...]` and walk the owner through the result.
10. **Advise on privacy, don't dictate it.** Raise privacy questions at the interview, the data model and before launch (`privacy-advisor` skill,
    [docs/privacy.md](docs/privacy.md)): HTTPS, cookies, minimal data, young users and consent, users' right to export and delete, third parties, uploads, AI.
    Say why and how serious; the owner decides; record overrides in [docs/privacy_decisions.md](docs/privacy_decisions.md). Not legal advice.

## Layout in one glance

`mysite/` project settings and URLs · `core/` site-level pages, health check, AI helper, costs, GCS, backup & ops commands ·
`tutorial/` the interactive lessons · `notes/` the **example app** (copy its shape; removable) · `templates/`, `static/` · `tests/` · `docs/` · `scripts/`
(`init_site.py`, `render_api.py`, `verify_site.py`) · `render.yaml`, `build.sh` (deploy) · `.github/workflows/` (CI, scheduled tasks) · `.claude/skills/` (your playbooks).

The index page `index.html` and the GitHub Pages setup describe the *blueprint*; a site owner may replace or delete them.
