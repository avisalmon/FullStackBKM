# Environment variables

Everything that differs between your laptop and production is an environment variable.

* **Local**: the git-ignored file `.env` (copy `.env.example`). Loaded by `python-dotenv`.
  Note `.env` is a *variables file*; your virtualenv is the separate folder `env/`.
* **Production**: Render -> your service -> **Environment** (initial values come from `render.yaml`).
* **Never** commit a real value. Never paste one into a chat or an issue. Treat anything that
  has appeared in a transcript as burnable: rotate it (change the env var; nothing else needs redeploying).

## Core

| Variable | Default | Notes |
|---|---|---|
| `DEBUG` | `True` | `False` on Render (render.yaml). Turns on HTTPS redirect, secure cookies, HSTS |
| `SECRET_KEY` | dev key | Required when `DEBUG=False` (boot refuses otherwise). Render generates it |
| `SITE_NAME` | `My Site` | Display name; also stored in the Site record |
| `PERSISTENT_ROOT` | repo dir | `/var/data` on Render: database, media, backups live under it |
| `ALLOWED_HOSTS` | localhost | Comma list. Only needed for **custom domains**; the Render hostname is added automatically |
| `CSRF_TRUSTED_ORIGINS` | derived | Derived from `ALLOWED_HOSTS` (https). Use only for extras |
| `SITE_DOMAIN` | Render hostname | Your canonical domain for the Site record (used by allauth links) |
| `PYTHON_VERSION` | 3.12.6 | Render only; keep equal to your local Python |
| `DJANGO_SUPERUSER_USERNAME` | unset | Your admin login name. `bootstrap_site` creates the admin once, only if it does not exist yet |
| `DJANGO_SUPERUSER_EMAIL` | unset | Your admin's email address |
| `DJANGO_SUPERUSER_PASSWORD` | unset | Your admin password (type it into Render's prompt or `.env`; use a password manager; it is never reset on redeploy) |
| `RENDER_EXTERNAL_HOSTNAME` | set by Render | **Do not set this yourself.** Render provides your `*.onrender.com` hostname; the settings trust it automatically |
| `PRIVACY_REVIEWED` | `False` | Set `True` once **you** have read `/privacy/` and `/terms/` and are happy: removes the DRAFT banner ([privacy.md](../privacy.md) section 13) |
| `SESSION_COOKIE_AGE` | 1209600 (14 days) | Seconds a sign-in lasts. Shorten for sensitive sites or shared computers |

## Sign-in ([auth_google_oauth.md](auth_google_oauth.md))

| Variable | Notes |
|---|---|
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Both set -> "Continue with Google" appears |

## Email ([email_resend.md](email_resend.md))

| Variable | Notes |
|---|---|
| `RESEND_API_KEY` | Unset -> email prints to the console |
| `DEFAULT_FROM_EMAIL` | e.g. `noreply@your-domain.com`; must be on a verified Resend domain |
| `OWNER_EMAIL` | Receives error alerts (unhandled 500s) and cost alerts |

## AI ([openai.md](openai.md))

| Variable | Default | Notes |
|---|---|---|
| `OPENAI_API_KEY` | unset | Unset = stub mode, no spend |
| `OPENAI_DEFAULT_MODEL` | `gpt-4o-mini` | Change when OpenAI retires/renames models |
| `OPENAI_MONTHLY_COST_CAP_USD` | `20` | Hard stop for calls made through `core.ai`. `0` = off |
| `OPENAI_DAILY_TOKEN_LIMIT_PER_USER` | `50000` | Per signed-in person per UTC day. `0` = off |
| `OPENAI_ADMIN_KEY` | unset | Optional `sk-admin-...` key so the cost report can read real org-wide spend |

## Storage, backups, schedules, costs

| Variable | Notes |
|---|---|
| `GCS_BUCKET`, `GCS_SERVICE_ACCOUNT` | Both set -> `backup_db` also copies offsite ([gcs_bucket.md](gcs_bucket.md)). The second is the base64 service-account JSON |
| `TASK_TRIGGER_TOKEN` | Shared secret for `/internal/run/<task>/`. Unset = endpoint closed. Same value as the GitHub secret |
| `MONTHLY_BUDGET_USD` | `0` = no alerts ([cost_monitoring.md](cost_monitoring.md)) |
| `RENDER_MONTHLY_USD` | `7.25`. Change if you change plan/disk size |
| `DOMAIN_YEARLY_USD` | Your registrar's yearly price, for the cost report |
| `PLAUSIBLE_DOMAIN` | Set to your domain to enable Plausible analytics |
| `RENDER_API_KEY` | **Local only** (`.env`), for `scripts/render_api.py`. Never put it on Render |

## Adding a new variable

1. Read it in `mysite/settings.py`: `NEW_VAR = os.environ.get("NEW_VAR", "safe-default")`. The default must be the *closed/safe* one.
2. Add it to `.env.example` and to this table.
3. Add it to `render.yaml` (`sync: false` for anything secret).
4. Set it on Render and in your local `.env`.
