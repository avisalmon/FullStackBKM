# Deploy to Render

**Local = dev. Render = production. Never mix them.** `git push` to `main` deploys to
production (auto-deploy). Push only when the owner says "deploy", "push" or "go live". Never push
"just to see if it works on Render": if it does not work locally it will not work there.

## What you get

Django + gunicorn + WhiteNoise, SQLite on a 1 GB persistent disk at `/var/data` (database
*and* uploaded media), HTTPS and a `*.onrender.com` hostname, deploy on every push.
Cost about **$7.25/month**: Starter instance $7 + disk $0.25. A persistent disk requires a
paid instance; the free tier cannot hold your database.

## One-time: humans only (nobody can do these for you)

1. **Render account** at https://render.com, sign in with GitHub.
2. **Billing**: add a card (Account Settings -> Billing). A Blueprint will not parse without it (gotcha #5).
3. **Install the Render GitHub App** on your account and select *only this repo*:
   https://github.com/apps/render/installations/new (gotchas #6 and #14).

## Deploy with the Blueprint

1. Make sure the repo is on GitHub (private) and `python scripts/init_site.py --name <slug>` has been run and pushed.
2. Render dashboard -> **New** -> **Blueprint** -> pick the repo -> branch `main`.
3. Render reads `render.yaml` and asks for the `sync: false` values:
   * `DJANGO_SUPERUSER_USERNAME` / `_EMAIL` / `_PASSWORD`: your admin login. Use a password manager.
   * Everything else (Google, Resend, OpenAI, GCS, `TASK_TRIGGER_TOKEN`) can be left blank now and added later.
   * `SECRET_KEY` is generated for you (`generateValue: true`); you never see or paste it.
4. Confirm the cost (~$7.25/mo) -> **Deploy Blueprint**.
5. Wait for the build. Open `https://<service>.onrender.com/healthz`: it should answer `{"status": "ok"}`.

What happens on each deploy: `build.sh` installs dependencies and collects static files
(no database access: the disk is read-only during the build). Then
`python manage.py bootstrap_site` migrates, creates your admin if missing, and points the
Site record at the real hostname, and only if that succeeds does gunicorn start.

## Smoke test after the first deploy

- [ ] `/healthz` returns 200
- [ ] Home page loads, CSS applied (WhiteNoise working)
- [ ] `/admin/` login works with the superuser you set
- [ ] Sign up a normal account, sign out, sign in
- [ ] Notes: add a note with an image, image displays (media on the disk)
- [ ] Trigger a redeploy: the note and image are still there (persistent disk)
- [ ] Render logs show no errors

## Everyday loop

```powershell
.\env\Scripts\Activate.ps1
pytest -q                      # tests green
ruff check . ; ruff format .   # lint
python manage.py runserver     # look at it
git add <files> ; git commit -m "what and why"
# ... only when told to go live:
git push
```

After a push, **verify the live site picked up the change** with something the old build could
not have (a new page, a new CSS class), not just "the homepage loads". A transient 502 right
after a push is usually the new instance still starting; check again before assuming a bad build.

## Changing settings later

Dashboard values win over `render.yaml` once the service exists (gotcha #8). Change env vars in
Render -> Environment, or `python scripts/render_api.py env-set --service srv-... KEY --prompt`.
Every env-var change redeploys.

If something fails: [debug_failed_deploy.md](debug_failed_deploy.md). Roll back: [rollback.md](rollback.md).
