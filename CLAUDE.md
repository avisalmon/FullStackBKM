# Instructions for Claude working in this repo

This repo is a **blueprint for a full-stack website: Django on Render**, with SQLite on a persistent disk, Google + password
sign-in, email, OpenAI, Google Cloud Storage, backups and cost monitoring, plus the methodology for building apps on it.
The person you are helping is the **site owner** and may be new to all of this.

## First thing: which situation are you in?

* The owner says anything like **"Tell me what to do"**, "what's next", "continue", "help me build my full stack site", "let's build a site", "get started" (or this is clearly a fresh
  clone of the blueprint, or a site started from it) -> **invoke the `build-my-site` skill** and follow it. It orients from `docs/new_site_checklist.md` (fresh start, or resume
  where the last session stopped), guides the whole journey, automates what it can, and gives exact instructions only for steps a human must do. The owner may be a complete beginner who
  has only an editor, git and this chat: **you install the rest** (`setup-my-computer` skill). The human-only setup that comes before this chat is in [docs/get_started.md](docs/get_started.md).
* Something is not installed / "command not found" / Python or PATH trouble -> `setup-my-computer` skill.
* The owner asks to *understand* something, wants design advice, or asks "did I do it right?" -> `site-mentor` skill. **Teach as you build** (see rule 9).
* They want a new feature or app -> `building-an-app` skill (and read [docs/building_an_app.md](docs/building_an_app.md) in full first; it changes).
* Privacy, cookies, consent, children/students, personal data, policies -> `privacy-advisor` skill (an advisor: the owner decides).
* Creating the GitHub repo, `gh` login, pushing, GitHub Pages, templates -> `publish-to-github` skill (asks before anything irreversible or public).
* Google sign-in -> `google-sign-in`; email -> `email-resend`; domain/DNS/HTTPS -> `custom-domain`; AI -> `openai-ai-features`; backups/restore/GCS -> `backups-and-restore`; costs -> `cost-monitoring`;
  "did I do it right"/checks -> `verify-my-site`; secrets/leaks/2FA -> `site-security`; data model/relationships -> `data-model-coach`; page design -> `design-review`.
* Deploy or deploy trouble -> `render-django` skill. Day-to-day operation (logs, backups, costs, rollback) -> `site-ops` skill.
* "Add this to the methodology file" -> edit [docs/building_an_app.md](docs/building_an_app.md) directly and confirm what you wrote.

The map of all documentation is [docs/README.md](docs/README.md).

## Standing rules (apply to everything)

0. **Start every session by checking GitHub for updates, and pull them in when it is safe.** Before anything else, run
   `python scripts/check_updates.py` (with the env's Python once it exists). It fetches the **blueprint** (the remote `origin` right after cloning,
   `blueprint` once the owner's private repo exists) and the owner's **own** repository, and pulls only when the folder has no unsaved changes and the update
   applies cleanly; a conflict is undone and reported, never left half-done; it never pushes. Then tell the owner in one or two plain sentences what arrived
   ("the setup guide got clearer; nothing you need to do"), and act on what the script says: **re-read `CLAUDE.md` and your skills if they changed**,
   reinstall dependencies, run `migrate`, run the tests. Unsaved changes? Commit them first (with a clear message), then run it again. Conflicts? Resolve them
   with the owner: keep their content, take the update's fixes. No Python yet (very first session)? Do the same with git directly: `git fetch --all`, then
   `git pull --ff-only` if `git status` is clean. Offline? Say so and carry on.
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
11. **Everything this repo knows how to do is a skill.** Skills live in `.claude/skills/` (Claude Code) and are mirrored to `.github/skills/` (GitHub Copilot) by
    `python scripts/sync_skills.py`; `.github/copilot-instructions.md` and `AGENTS.md` are generated too. Edit only `.claude/skills/` and `CLAUDE.md`, then run the sync
    (CI and a test fail if the copies drift). New knowledge you gain while building becomes a new or updated skill, with the detail in `docs/`.
    When something goes wrong, the owner corrects you, or you find a better way: do a short post-mortem (what happened, why the way we work let it,
    the rule that prevents it) and land it in [docs/building_an_app.md](docs/building_an_app.md), the skill that covers it, and [docs/lessons_log.md](docs/lessons_log.md).

## Layout in one glance

`mysite/` project settings and URLs · `core/` site-level pages, health check, AI helper, costs, GCS, backup & ops commands ·
`tutorial/` the interactive lessons · `notes/` the **example app** (copy its shape; removable) · `templates/`, `static/` · `tests/` · `docs/` · `scripts/`
(`init_site.py`, `render_api.py`, `verify_site.py`, `check_updates.py`) · `render.yaml`, `build.sh` (deploy) · `.github/workflows/` (CI, scheduled tasks) · `.claude/skills/` (your playbooks).

The index page `index.html` and the GitHub Pages setup describe the *blueprint*; a site owner may replace or delete them.
