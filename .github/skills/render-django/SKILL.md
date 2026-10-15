---
name: render-django
description: >
  Deploy and operate this Django site on Render: SQLite on a persistent disk, WhiteNoise static files, media uploads,
  GitHub auto-deploy via render.yaml, bootstrap_site start command, health check, custom domains, and the 30 proven
  gotchas. Includes the failed-deploy debugging discipline (fetch logs before touching code).
  TRIGGER: "deploy to render", "render deployment", "set up render", "create render service", "render.yaml",
  "deploy failed", "update_failed", "502", "400 bad request", "allowed hosts", "add a custom domain", "persistent disk".
---

# Render + Django

The authoritative content lives in the repo docs; this file is the operating summary. **Re-read the relevant doc before acting.**

* How to deploy: [docs/procedures/deploy_to_render.md](../../../docs/procedures/deploy_to_render.md)
* When it breaks: [docs/procedures/debug_failed_deploy.md](../../../docs/procedures/debug_failed_deploy.md)
* Known traps (numbered; code and tests cite them): [docs/procedures/gotchas.md](../../../docs/procedures/gotchas.md)
* Variables: [docs/procedures/env_vars.md](../../../docs/procedures/env_vars.md); domain: [custom_domain_dns.md](../../../docs/procedures/custom_domain_dns.md)

## Shape of the deployment

* `render.yaml` Blueprint: one web service (Starter, ~$7.25/mo with the 1 GB disk at `/var/data`).
* `build.sh`: install + `collectstatic` only. **Never `migrate` here**: the disk is read-only during the build.
* Start: `python manage.py bootstrap_site && gunicorn mysite.wsgi:application ...`. `bootstrap_site` migrates, creates the superuser if absent
  and syncs the Site record. Keep the start command a single simple chain; no `|| true`.
* `PERSISTENT_ROOT=/var/data` holds `data/db.sqlite3`, `media/`, `backups/`.
* Hostname: `RENDER_EXTERNAL_HOSTNAME` is trusted automatically; custom domains via `ALLOWED_HOSTS` + `SITE_DOMAIN`.
* Media is served by `core.views.media_serve`, never `django.conf.urls.static.static()` (returns `[]` when `DEBUG=False`).
* Health check `/healthz` (exempt from the HTTPS redirect).

## Dev flow: mandatory

**Local = dev, Render = production.** Develop and test locally. Commit freely. **Push only when the owner says deploy / push / go live**; a push
auto-deploys production. Never push to "see if it works on Render". After a push, verify the live site changed with something the old build could not show.

## When a deploy fails

**Logs first, always.** `python scripts/render_api.py logs --service srv-... --minutes 30 --grep Traceback`. Read the last real error, make ONE
targeted fix, redeploy, fetch logs again. No speculative pushes, no bundled "improvements". Match the error against the signature table in
`debug_failed_deploy.md` and the gotcha list.

## Editing config after the first deploy

`render.yaml` does not override values already set in the dashboard (gotcha #8). Use the dashboard or
`python scripts/render_api.py env-set KEY --from-env LOCALVAR` (secrets are never accepted as arguments). Env changes redeploy.

## Do not

* put a secret in `render.yaml`, a test, a doc or a commit (`sync: false` / `generateValue` only);
* run `migrate` in `build.sh`; * add `|| true` chains to the start command; * change `PYTHON_VERSION` without running that version locally;
* ask the owner to paste a secret into chat.
