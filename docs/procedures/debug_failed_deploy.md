# Debug a failed deploy

## The rule: fetch the logs BEFORE touching code

No guessing, no "let me try X". On the reference site, one outage burned five deploys by
guessing. The loop, followed strictly:

1. **Fetch the logs** for the failed deploy.
2. **Read the actual last error**, not the commit message and not the notification banner
   (the banner often quotes the *previous* error).
3. Make **one** targeted fix for that exact error.
4. Commit, push (with the owner's go-ahead), watch the deploy.
5. Fetch the logs again. Go to 1.

Anti-patterns: bundling unrelated "improvements" into the fix; pushing a speculative "let's see";
fixing only the one migration named in the error when there is clearly a chain behind it.

## Getting the logs (works over HTTPS, so it works behind a corporate firewall)

```powershell
.\env\Scripts\python.exe scripts\render_api.py services                       # find srv-...
.\env\Scripts\python.exe scripts\render_api.py logs --service srv-xxxx --minutes 30
.\env\Scripts\python.exe scripts\render_api.py logs --service srv-xxxx --minutes 30 --grep Traceback
.\env\Scripts\python.exe scripts\render_api.py deploys --service srv-xxxx     # status of recent deploys
```

Build logs and runtime logs are one stream; filter by time. The Render dashboard -> Logs shows the
same thing. (Raw API: `GET /v1/logs?ownerId=...&resource=srv-...&startTime=...&endTime=...`.
The endpoint is *owner*-scoped, so both ids are required; `/deploys/{id}/logs` does not exist.)

To run a one-off command in the service's environment: `render_api.py job --service srv-xxxx
--command "python manage.py check --deploy"` (job output lands in the same log stream), or use
the dashboard's web **Shell** (`python manage.py shell`).

## Common signatures

| You see | Likely cause |
|---|---|
| Build ok, deploy `update_failed`, runtime traceback | See the traceback; usually a missing env var or package (gotchas #20, #21) |
| `ImproperlyConfigured: SECRET_KEY must be set` | `SECRET_KEY` missing in the service environment (gotcha #26) |
| `Bad Request (400)` in the browser | Host not in `ALLOWED_HOSTS` (gotcha #4) |
| `CSRF verification failed` on a custom domain | Domain missing from `ALLOWED_HOSTS` (CSRF origins derive from it) |
| `permission denied: ./build.sh` / `bad interpreter` | Gotcha #1 |
| `unable to open database file` in the build | `migrate`/DB access in the build step (gotcha #3) |
| `InconsistentMigrationHistory` | Gotcha #22, below |
| `ModuleNotFoundError` | Package missing from `requirements.txt` (gotcha #21) |
| Health check failing, site works in a browser | Gotcha #25 |

## Migration self-repair

If production has a ghost migration history (a later migration recorded as applied while an
earlier one is not, typically after restoring a backup or editing the database by hand), every
`manage.py` command crashes in `check_consistent_history`, so you cannot reach a shell to fix it.
The fix has to run before Django's checks: in `AppConfig.ready()` with raw `sqlite3`.

```python
import sqlite3
from django.apps import AppConfig


def _repair(db_path):
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations'")
        if not c.fetchone():
            conn.close()
            return  # first ever boot
        for name in [
            "0001_initial",
            "0002_next",
        ]:  # EVERY migration from the lowest missing one up to HEAD
            c.execute("SELECT id FROM django_migrations WHERE app=? AND name=?", ["myapp", name])
            if not c.fetchone():
                c.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (?,?,?)",
                    ["myapp", name, "2024-01-01 00:00:00+00:00"],
                )
        conn.commit()
        conn.close()
    except Exception:
        pass  # never break startup; let migrate show the real error


class MyAppConfig(AppConfig):
    name = "myapp"

    def ready(self):
        from django.conf import settings

        path = settings.DATABASES["default"]["NAME"]
        if path and path != ":memory:":
            _repair(path)
```

Why it works: `ready()` runs for every `manage.py` invocation, including `migrate`, before the
consistency check; raw sqlite3 works even when models and schema disagree; it is idempotent, so it
is safe to leave in. Errors chain backwards (fix 0010, then 0009 surfaces...), so list the whole range
at once. Only add it to an app when you actually hit this; do not ship it speculatively.
