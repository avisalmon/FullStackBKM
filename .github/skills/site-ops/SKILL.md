---
name: site-ops
description: >
  Day-to-day operation of the live site: read logs, check deploy status, trigger a backup now, restore, see what the site costs,
  change an environment variable, roll back a bad deploy, rotate a leaked secret, update dependencies, check the site is healthy.
  TRIGGER: "check the logs", "is the site up", "back up now", "restore the database", "how much is this costing", "costs",
  "roll back", "revert the deploy", "change an env var", "rotate the key", "update dependencies", "site is down", "site is slow".
---

# Operating the live site

Prerequisite: `RENDER_API_KEY` and `RENDER_SERVICE_ID` in the git-ignored `.env` (see `build-my-site`, Phase 4). All commands use the venv
interpreter (`.\env\Scripts\python.exe` on Windows, `env/bin/python` elsewhere). Read-only checks you can just do; **anything that changes
production (env vars, deploys, restores, pushes) needs the owner's go-ahead first.**

| The owner says | You do |
|---|---|
| "Is the site up?" | `curl -s https://<host>/healthz`; `render_api.py deploys` for the last deploy status |
| "Check the logs" / "something's wrong" | `render_api.py logs --minutes 30` (add `--grep Traceback`); follow [debug_failed_deploy.md](../../../docs/procedures/debug_failed_deploy.md): logs before code |
| "Back up now" | `curl -X POST -H "X-Task-Token: ..."` is for CI; interactively use `render_api.py job --command "python manage.py backup_db"` (or `gh workflow run scheduled-tasks.yml -f task=backup`), then confirm the snapshot/bucket object exists |
| "Restore" | Walk through [backup_restore.md](../../../docs/procedures/backup_restore.md) with the owner; take a fresh snapshot of the current DB first; practise on a throwaway if it's the first time |
| "What does it cost?" | `render_api.py job --command "python manage.py report_costs"` or open `/ops/costs/` (staff); explain sources (live/estimate/manual); compare with provider dashboards |
| "Roll back" | [rollback.md](../../../docs/procedures/rollback.md): `git revert`, push (with go-ahead); data problems go to restore |
| "Change a setting" | `render_api.py env-set KEY --from-env NAME` or `--prompt`; remind them it redeploys; update `docs/procedures/env_vars.md` + `.env.example` if it's new |
| "I think a key leaked" | [security.md](../../../docs/security.md) "If you suspect a leak": rotate at the provider, update Render and `.env`, check usage logs |
| "Update dependencies" | Merge Dependabot PRs only with green CI; locally `pip install -r requirements-dev.txt`, `pytest -q`, `manage.py check --deploy` with `DEBUG=False` and a throwaway `SECRET_KEY` |
| "Site is slow / 502" | A 502 right after a deploy is usually the instance starting; otherwise logs. SQLite is single-writer: look for long requests (AI calls) and consider moving them to a command |

Always finish by saying what you checked and what you found, not what you plan to check.
