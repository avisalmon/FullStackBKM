# Rollback

Render deploys whatever is on `main`. To undo a bad deploy:

## 1. Revert the commit (preferred: fast, leaves a trail)

```powershell
git revert <bad-commit>      # or: git revert HEAD
git push                     # auto-deploys the revert (hotfixes for a down site are pre-approved by the owner)
```

## 2. Redeploy a previous build

Render -> service -> **Deploys** -> pick the last good one -> **Rollback** / *Redeploy*. Quick, but the next
push deploys `main` again, so also fix `main`.

## 3. Force-push (emergency only, destructive)

`git reset --hard <good>; git push --force origin main`. Rewrites history; avoid.

## Data

Code rollback does not undo **migrations** or data changes. If a deploy corrupted data, restore a snapshot
([backup_restore.md](backup_restore.md)). Make destructive migrations reversible, or take
`python manage.py backup_db` immediately before deploying one.

## Environment variables

Render -> Environment -> set the old value -> Save (this redeploys).

## After any rollback

- [ ] `/healthz` is 200
- [ ] Home page loads, sign-in works
- [ ] Render logs are clean ([debug_failed_deploy.md](debug_failed_deploy.md))
- [ ] Write down what happened, and add a test for it
