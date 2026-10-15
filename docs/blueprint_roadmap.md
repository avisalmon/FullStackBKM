# Blueprint roadmap and known limits

For whoever maintains the blueprint itself (not for site owners who cloned it).

## Verified here (automated, 76+ tests)

Settings safety (secret-key refusal, host/CSRF derivation), health check, media with DEBUG off, notes CRUD API with
refusals, `bootstrap_site` idempotency, local + offsite backup logic (against a fake bucket), OpenAI metering/caps
(against a fake HTTP layer), cost adapters, the task endpoint's fail-shut behaviour, deploy-config guards, secret scan.

## NOT yet verified against the real services

These are written from the reference site's proven calls or the vendors' docs, but have not been run live by the blueprint's author.
The first person to deploy should confirm each and fix the blueprint:

- [ ] `render.yaml` Blueprint creation end to end (`generateValue`, `healthCheckPath`, disk on `starter`)
- [ ] `RENDER_EXTERNAL_HOSTNAME` is present at runtime and in `bootstrap_site`
- [ ] `scripts/render_api.py`: `deploy`, `env-set` (PUT env-vars), `domain` endpoints (services/logs/job are the reference site's proven calls)
- [ ] Real Google Cloud Storage upload/list/delete via `core.gcs.Bucket`
- [ ] Real OpenAI call shape and the pricing table in `core/ai.py`
- [ ] `scheduled-tasks.yml` against a live `SITE_URL`
- [ ] Gitleaks pre-commit hook version pin, `gitleaks-action` on a private personal repo
- [ ] Python 3.12.6 available on Render's builder

## Deliberately left out of the reference site (and why)

The reference site is a large multi-product platform. Not carried over because they're product-specific or heavy:
video CDN (Bunny), billing mock, GitHub Copilot seat management, content-moderation pipeline, course engine, push notifications,
the mail "guard" wrapper (caps per-recipient sends), Hebrew/RTL i18n, dashboards.

## Ideas

- Optional "recipes": content moderation for uploads; mail guard; GCS-backed media storage wired behind a flag; Postgres option
  (Render managed DB) for when SQLite's single-writer limit bites; Cloudflare automation; uptime monitor (UptimeRobot on `/healthz`).
- A `blueprint-update` skill: `git fetch blueprint` and merge improvements into a site that has diverged.
- Dashboard generated from each app's spec/backlog with a test that fails when it drifts.
