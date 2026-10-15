# CI/CD

* **Source**: your private GitHub repo, branch `main`.
* **CI** (`.github/workflows/ci.yml`): on every push and pull request: secret scan (gitleaks), `ruff`, `pytest`,
  `manage.py check`, `check --deploy` with production settings, and a missing-migrations check.
* **CD**: Render auto-deploys `main` after `git push` (the Render GitHub App must be installed, gotcha #14).
* **Scheduled jobs** (`scheduled-tasks.yml`): backup weekly, costs daily ([backup_restore.md](backup_restore.md)).
* **Dependabot** opens weekly PRs for outdated dependencies. Merge them only with green CI.

## Local commands

```powershell
.\env\Scripts\Activate.ps1
python manage.py runserver
pytest -q
ruff check . ; ruff format .
python manage.py makemigrations --check --dry-run
pre-commit install            # once: secret scan + lint on every commit
```

## Rules

* **Push only when the owner says so**; commit as often as you like. Push = production.
* Commit messages: imperative, say *why*. Hotfixes may be prefixed `HOTFIX:`.
* Run the test suite and `manage.py check` before pushing; after pushing, verify the live site changed.
* Scope formatter/auto-fix runs to your own files when several people or sessions share a working tree
  ([building_an_app.md](../building_an_app.md), mistake 9).

## Pre-push checklist

- [ ] `pytest -q` green
- [ ] `ruff check .` clean
- [ ] No `DEBUG=True` in committed config; no secrets in the diff (`git diff --staged`)
- [ ] New env vars documented in `env_vars.md`, `.env.example`, `render.yaml` and set on Render
