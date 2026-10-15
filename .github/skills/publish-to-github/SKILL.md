---
name: publish-to-github
description: >
  Put the site's code on GitHub safely: install and log in to the GitHub CLI (no admin rights needed), choose the right
  account, set a privacy-safe commit identity, run the pre-push secret check, create the repository (PRIVATE for an owner's
  site, public only for a blueprint or a public static site), push, turn on GitHub Pages when wanted, mark a repo as a
  template, check CI, and update later. Asks before every irreversible or outward-facing step.
  TRIGGER: "create the repo", "push to github", "publish", "make a repository", "gh auth login", "github pages", "make it
  private", "make it public", "template repository", "git push", "github login", "put this on github".
---

# Publish to GitHub

Part of the build journey ([build-my-site](../build-my-site/SKILL.md), Phase 3). Based on the owner's own GitHub runbook plus what actually happened
when this blueprint was first published. **Every step below was run for real when this blueprint was published (2026-10-15): the install, login, account check, identity rewrite, pre-push check, repo creation,
push, template flag, Pages, and CI. Gotchas marked (found) bit us for real.**

## Rules (non-negotiable)

1. **Never print, log, commit, paste into chat or email a token or password.** Don't run `gh auth token`; don't echo `GH_TOKEN`. Login is done by the owner in a browser.
2. **Ask first** (unless the owner asked for exactly that in the current task) before you: create a repository, make one public, turn Pages on or off, delete a repo/branch/history,
   force push, or rewrite commit history that has already been pushed.
3. **Public means public, forever.** A published repo, and every file in its history, is readable by anyone. GitHub Pages on the free plan needs a **public** repo, so a Pages site
   and a private site are different repositories.
4. **An owner's site repo is PRIVATE** (it holds their business, and the site runs on Render, which can deploy private repos). Only the blueprint itself, or a deliberately public
   static site, is public.
5. **Run the pre-push check (below) before every first push and any push that adds many files.**
6. Finish by reporting what changed and giving the link.

## 1. Install the GitHub CLI (no admin needed) (verified)

Check first: `gh --version`. If missing:

* **Try winget** (`winget install --id GitHub.cli -e --source winget --silent`) but **watch for a hang**: it can wait forever on a Windows permission (UAC) prompt the
  owner doesn't see. If it hasn't finished in ~2 minutes, stop `winget`/`msiexec` and use the portable install below.
* **Portable install, no admin (verified):** get the latest release from `https://api.github.com/repos/cli/cli/releases/latest`, download the `windows_amd64.zip` and
  `checksums.txt` into a fresh empty folder, **verify the SHA-256 matches**, extract to a user folder such as `C:\Users\<user>\tools\gh`, and run `...\tools\gh\bin\gh.exe`
  by full path (no PATH change needed). macOS: `brew install gh`. Linux: see https://github.com/cli/cli/blob/trunk/docs/install_linux.md.
* Also need git (`git --version`).

## 2. Log in (the owner does one browser step) (verified)

Start the device flow yourself so the owner only types a code (run it in the background and read its output; give it a stdin file containing one newline):

```
gh auth login --hostname github.com --git-protocol https --web --scopes workflow
```

It prints a one-time code (and copies it to the clipboard) and a URL: https://github.com/login/device. Tell the owner: **open the URL, sign in as the right account, enter the code, authorize.**
The `workflow` scope is needed only to push files under `.github/workflows/`. Then verify and finish setup:

```
gh auth status                      # logged in as the intended account; scopes include repo (+ workflow)
gh auth setup-git
git config --global core.quotepath false     # shows non-English file names properly
```

**Check the account.** People often have two GitHub accounts. Look up the candidates through the public API (`https://api.github.com/users/<name>`: id, repo count, created) and
confirm with the owner which one before logging in or creating anything. If the device flow signs in as the wrong one, `gh auth logout` and redo it.

If the browser flow is impossible on this machine, the fallback is a **token created just for this machine** (classic, scopes `repo`, `read:org`, `gist`, plus `workflow` if needed,
90-day expiry, named after the machine), pasted into `gh auth login` at its hidden prompt. Never saved anywhere else.

## 3. Commit identity: don't publish a work email (verified)

Commits carry an author email, and **a public repo publishes it**. On this blueprint's first publish, all commits were authored with the owner's employer address.

* Look: `git log --format="%an <%ae>" | sort -u` and `git config user.email`.
* Use the account's **noreply** address: `<numeric-id>+<username>@users.noreply.github.com` (the id is in the public API lookup; the owner can also confirm at https://github.com/settings/emails).
  Set it: `git config --global user.email "<that>"` and `git config --global user.name "<Name>"`.
* **If commits already carry the wrong email and nothing has been pushed yet**, offer to rewrite the author on the local history. What worked (commit dates are preserved):
  `FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --env-filter 'export GIT_AUTHOR_NAME=...; export GIT_AUTHOR_EMAIL=<noreply>; export GIT_COMMITTER_NAME=...; export GIT_COMMITTER_EMAIL=<noreply>' -- --all`.
  **Then delete the backup it leaves behind** (`git for-each-ref --format="%(refname)" refs/original`, delete each with `git update-ref -d`, then `git reflog expire --expire=now --all` and `git gc --prune=now`) and verify:
  searching every commit's author, committer and message for the work domain must find nothing, and neither must `git grep` across `git rev-list --all` (found: the backup ref still held every old commit).
  This is safe only before the first push. **If it was already pushed, stop and tell the owner**: removing it means rewriting published history and treating the address as exposed.

## 4. Pre-push check: keep private material out (verified)

Run in the project folder, read every hit, and show the owner the summary:

```
git ls-files | wc -l                              # how many files will be public
git ls-files .env env                             # must print nothing
git ls-files | grep -Ei "private|secret|token|password|\.env"          # file names; judge each
git grep -nIE "ghp_|gho_|github_pat_|sk-proj-|GOCSPX-|rnd_[A-Za-z0-9]{20}"   # key shapes in contents; must print nothing
python scripts/verify_site.py                     # this repo's own checker (secrets, ignore rules, private repo)
```

* Private folders go in `.gitignore` **before** the first commit. `.gitignore` does not un-track files already tracked: `git rm -r --cached <path>` and commit.
* **If private files were ever pushed, they were public.** Stop and tell the owner; the fix is rewriting history and treating the content as exposed (rotate any key).
* Safest: keep private material outside any public repository.
* Also check size: GitHub rejects files over 100 MB.

## 5. Create the repo and push (verified)

Decide visibility with the owner first (rule 4). Then, in the project folder:

```
git branch -M main                                 # if needed
gh repo create <account>/<name> --private --source . --remote origin --push --description "One line"
```

Use `--public` only when agreed. If a `blueprint` or other remote already exists, keep it under another name (`git remote rename origin blueprint`) before creating `origin`.
Confirm: `gh repo view --json isPrivate,url` and show the owner.

**Mark a repo as a template** (so others get a clean private copy with "Use this template"), only for the public blueprint: `gh repo edit <account>/<name> --template` (verified; fallback: Settings -> General -> Template repository).
The owner's "Use this template" link is `https://github.com/<account>/<name>/generate`.

## 6. GitHub Pages (only for a public static site; ask first) (verified)

```
gh api -X POST repos/<account>/<name>/pages -f "source[branch]=main" -f "source[path]=/"   # root of main
gh api repos/<account>/<name>/pages --jq .html_url
gh api repos/<account>/<name>/pages --jq .status                            # wait for: built
```

* Address: `https://<account>.github.io/<name>/`. The first build took about a minute. Poll `.status` until `built`, then fetch the live URLs (landing page and any sub-pages) and check the content.
* Add an empty `.nojekyll` file first (stops Jekyll skipping `_` files). Links must be **relative** (`about.html`, not `/about.html`) because a project site lives under `/<name>/`.
* Git Bash: prefix `MSYS_NO_PATHCONV=1` if you pass a path like `/docs`. Turning Pages off: `gh api -X DELETE repos/<account>/<name>/pages` (ask first).
* **Pages is public.** Never publish a private repo's content this way; the owner's real site is served by Render, not Pages.

## 7. After the push

* **Watch CI:** `gh run list --limit 3`, `gh run watch <id> --exit-status`. If the first run fails in the secret scan, read the log before changing anything: see the gitleaks gotcha below.
* **Updates:** `git add <files>` (never blind `-A` without `git status`), commit with a message saying why, `git push`. A push to a repo connected to Render **deploys production**: only
  push on the owner's say-so ([render-django](../render-django/SKILL.md)).
* **Scheduled-task secrets** (backups and cost reports): `gh variable set SITE_URL --body <url>` and `gh secret set TASK_TRIGGER_TOKEN` (value from a prompt or a local variable, never typed into chat).
* **Turn on GitHub secret scanning and push protection** and two-factor authentication ([security.md](../../../docs/security.md)).

## Gotchas (verified unless noted)

* Windows PowerShell 5.1 has no `&&`; use `;` and check `$LASTEXITCODE`. Double quotes inside arguments to native programs get stripped: don't put JSON in `gh api` arguments;
  use `-f key=value`, `--jq .field` without quotes, or `--input file.json`.
* `gh` uses `GH_TOKEN` from the environment instead of the saved login if it is set; `gh auth status` shows which is active.
* Two accounts with similar names exist for many people (`name` vs `first-last`): check before creating anything.
* File names are case-sensitive on GitHub and Pages but not on Windows.
* A background `winget` or installer that waits for a prompt the owner can't see will hang silently: set a time limit and fall back.
* `gh auth login` in the background needs a stdin file with a newline; the one-time code appears on **stderr**.
* (found) **PowerShell strips quotes inside arguments to native programs**: `gh repo view --json a,b --jq '.x + .y'` fails with "accepts at most 1 arg(s)". Use `--json ... | ConvertFrom-Json`, or `--jq .field` with no spaces.
* (found) **`$home` (and `$host`, `$pid`, `$args`) are reserved PowerShell variables**: assigning them fails. Use other names.
* (found) **`gitleaks/gitleaks-action` fails on a repository's first push**: it scans `<first-commit>^..<head>` and the root commit has no parent, so it aborts without scanning. CI in this blueprint downloads the pinned gitleaks binary, verifies its SHA-256, and scans the whole history instead.
* (found) **Windows checks files out with CRLF** by default. `.gitattributes` with `* text=auto eol=lf` keeps every checkout identical, so shell scripts run on Render and generated files compare equal.
* (found) **Dependabot opens pull requests the moment a repo is public.** Leave them for the owner; merge only with green CI.
* A public repo with no `LICENSE` is "all rights reserved": others may view and fork it on GitHub but have no clear right to reuse it. Ask the owner which licence (MIT is the usual permissive choice); never pick one silently.

## Hand-off checklist

- [ ] Right account, `gh auth status` clean (repo + workflow scopes)
- [ ] Commit identity is the noreply address; no work email in history that is about to be public
- [ ] Pre-push check clean; `.env` and `env/` not tracked
- [ ] Visibility confirmed with the owner (private for a site, public only if intended)
- [ ] Repo created, pushed, link shown; CI green (`gh run watch --exit-status`)
- [ ] Pages / template only if asked; Pages `built` and the live URLs fetched and checked
- [ ] A fresh clone from GitHub installs and passes the tests (the real proof)
- [ ] Licence question asked (public repos)
- [ ] The owner knows: 2FA on, secret scanning on, never paste tokens into chat
