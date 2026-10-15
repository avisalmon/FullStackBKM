# Gotchas - every one proven in practice

Each row is a failure that really happened building a production Django site on Render
(numbers 1-24 are from the reference site, babook.co.il; 25+ were found building this
blueprint). Code comments and tests refer to these numbers, so do not renumber.

| # | Gotcha | Fix |
|---|--------|-----|
| 1 | `build.sh` fails on Linux: not executable, or CRLF line endings after a Windows checkout | `git update-index --chmod=+x build.sh`; `.gitattributes` forces `*.sh text eol=lf` (already in this repo, and a test guards it) |
| 2 | `mkdir /var/data` fails during the build (disk is read-only then) | `try/except OSError: pass` around the mkdir in settings.py (already done) |
| 3 | `migrate` fails during the build (nowhere to write the DB) | Never migrate in `build.sh`; `bootstrap_site` migrates at start (a test guards this) |
| 4 | `400 Bad Request` after deploy | `ALLOWED_HOSTS` lacks the hostname. Handled automatically via `RENDER_EXTERNAL_HOSTNAME`; custom domains go in `ALLOWED_HOSTS` |
| 5 | Blueprint parse error / will not create | Billing must be set up on the Render account first |
| 6 | Render can see all your GitHub repos | Restrict: GitHub -> Settings -> Applications -> Render -> Repository access -> only the repos you choose |
| 7 | Workspace plan is not the service plan | A Hobby *workspace* is fine; `plan: starter` is the *instance* tier (needed for a persistent disk) |
| 8 | Editing `render.yaml` does not change the start command / env vars of an existing service | After the first deploy, dashboard values win. Change them in the dashboard (or `scripts/render_api.py env-set`) |
| 9 | `createsuperuser` crashes on every redeploy | `bootstrap_site` only creates the user if absent |
| 10 | allauth deprecation warnings | Use 65.x settings `ACCOUNT_LOGIN_METHODS`, `ACCOUNT_SIGNUP_FIELDS` (done) |
| 11 | Google login shows a signup form for someone who already has an account | Expected once: a security feature that links the accounts; seamless afterwards |
| 12 | Sites record still says `example.com` | `bootstrap_site` sets it from `SITE_DOMAIN` / `RENDER_EXTERNAL_HOSTNAME` |
| 13 | Media files 404 in production | `django.conf.urls.static.static()` returns `[]` when `DEBUG=False`. This repo serves media through `core.views.media_serve` (tested with DEBUG off) |
| 14 | Auto-deploy never triggers | The Render **GitHub App** must be installed (OAuth login alone is not enough): https://github.com/apps/render/installations/new, select the repo |
| 15 | SSH blocked on a corporate network | Use the Render API over HTTPS (`scripts/render_api.py`) or the dashboard's web Shell |
| 16 | Registrar form appends your domain to the host | Enter just `www`, not `www.example.com` |
| 17 | `check --deploy` warns about HSTS | HSTS settings are in settings.py, gated on `not DEBUG` (CI runs `check --deploy`) |
| 18 | Google login fails on a custom domain (`redirect_uri_mismatch`) | Add `https://<domain>/accounts/google/login/callback/` to the OAuth client's redirect URIs, and set `SITE_DOMAIN` |
| 19 | `.co.il` domain stuck in `serverHold` for days | Israeli registry updates 4x/day; new domains can take up to 72h. Not a misconfiguration |
| 20 | Deploy `update_failed`, no obvious reason | **Never guess: fetch the logs first** ([debug_failed_deploy.md](debug_failed_deploy.md)). Build can succeed while runtime crashes |
| 21 | `ModuleNotFoundError` at runtime although the package is "installed" | Any import error in a templatetag module crashes *every* management command incl. `migrate`. Add the package to `requirements.txt` |
| 22 | `InconsistentMigrationHistory: X is applied before its dependency Y` | A "ghost" migration after manual DB surgery or a partial restore. Fake-apply the whole missing range at once; errors chain backwards. See [debug_failed_deploy.md](debug_failed_deploy.md#migration-self-repair) |
| 23 | Start-command parentheses dropped on a container restart | `a && (b \|\| true) && gunicorn` becomes "start gunicorn even if migrate failed". Keep the start command to one simple `&&` chain; logic lives in `bootstrap_site` (a test forbids `\|\|`) |
| 24 | PATCHing `startCommand` through the API silently does nothing | Wrong field path. Correct: `serviceDetails.envSpecificDetails.startCommand` |
| 25 | Health check fails with a 301 | `SECURE_SSL_REDIRECT` redirects the plain-http probe. `/healthz` is exempt via `SECURE_REDIRECT_EXEMPT` (tested) |
| 26 | Production boots on the well-known dev `SECRET_KEY` | settings.py refuses to start when `DEBUG` is off and the key is unset or empty (tested) |
| 27 | An empty env var is not "unset" | `os.environ.get("X", default)` returns `""` for `X=`; use `get(...) or default` where an empty value must fall back |
| 28 | Local Python newer than Render's | Pin `PYTHON_VERSION` in render.yaml to a version you also run locally, so "works here" means "works there" |
| 29 | Backups on the same disk are not backups | They survive a bad deploy, not a lost disk. Configure the GCS offsite copy ([gcs_bucket.md](gcs_bucket.md)) |
| 30 | A scheduled job cannot reach the SQLite disk | Only the web service mounts it. Jobs run *inside* it via `POST /internal/run/<task>/` (a separate Render cron container sees an empty disk) |
