---
name: setup-my-computer
description: >
  Get the owner's computer ready, automatically: check and install Python, Git, the GitHub CLI and editor extensions without admin rights
  where possible, fix PATH and "command not found" problems, create the virtualenv, and diagnose Windows, macOS and Linux setup trouble.
  Installs only what is missing, with time limits, checksums and the owner's knowledge. TRIGGER: "install python", "python not found",
  "git not found", "command not found", "not recognized", "set up my computer", "set up my environment", "install the tools", "winget",
  "brew install", "venv", "virtual environment", "pip install fails", "path problem", "prerequisites", "what do I need to install".
---

# Set up my computer

The owner has an editor with an AI chat open on this project and nothing else guaranteed. Your job: find out what is installed, **install what is missing yourself**,
fix what is broken, and tell them in plain words what you did. Only a few things need the owner (accounts, a Windows permission popup). Source of the human part:
[docs/get_started.md](../../../docs/get_started.md). The journey that follows is [build-my-site](../build-my-site/SKILL.md).

## Principles

1. **Look before you install.** Run the checks, show the owner a short table (installed / missing / wrong version), then fix only what is missing or wrong.
2. **No admin rights where possible.** Prefer per-user installs. Say plainly before anything that may show a permission popup.
3. **Time-box every install** (about 2 minutes; run it in the background and poll). A package manager waiting on a permission window the owner cannot see hangs forever (this happened).
   If it hangs: tell the owner a Windows "allow changes?" window may be hidden behind VS Code (taskbar), ask them to click **Yes**; if still stuck, stop the process and use the fallback.
4. **Verify what you download** (checksum from the publisher) and download into an empty scratch folder, never into the project. Don't run installers you can't verify without telling the owner.
5. **Never touch what you don't need to** (don't change PATH globally, don't uninstall things). Say what changed.
6. After any install, **new terminals see the new PATH; the current one may not**. Re-check with the full path to the program, or open a fresh terminal.
7. The virtualenv is the folder `env/` (never `.env`, which is the variables file). Run Python through it explicitly.

## 1. Detect (run these, show a table)

Windows PowerShell (macOS/Linux equivalents in brackets):

```
python --version ; py -3.12 --version        # [python3 --version]
git --version
gh --version                                  # GitHub CLI (may be installed by us below)
code --version                                # [VS Code's command line; optional]
winget --version                              # [brew --version / apt --version]
Get-Content .env -ErrorAction SilentlyContinue | Out-Null ; Test-Path env     # project env present?
```

Interpret: **Python 3.12 is the target; 3.11-3.13 work locally** (Django 5.2). Older than 3.11, or no Python, or the Microsoft Store stub ("Python was not found; run without arguments to install from the Microsoft Store"),
means install Python. `git` missing is rare here (they cloned the repo) but fix it the same way.

## 2. Install what is missing

### Python (Windows)
```
winget install --id Python.Python.3.12 -e --scope user --silent --accept-package-agreements --accept-source-agreements
```
Run it in the background with a 2-minute limit. Afterwards verify with a **new** terminal, or the full path: `%LOCALAPPDATA%\Programs\Python\Python312\python.exe --version`.
**Fallback** (no winget, or hung): ask the owner to download the installer from https://www.python.org/downloads/ and tick **"Add python.exe to PATH"** on the first screen, then reopen VS Code.
If the Microsoft Store stub intercepts `python`: Settings -> Apps -> Advanced app settings -> App execution aliases -> turn off the Python entries (a human click; tell them exactly), or use `py -3.12`.

### Python, Git, GitHub CLI (macOS / Linux)
macOS: `brew install python@3.12 git gh` (Homebrew from https://brew.sh if missing; it asks for the owner's password: that's theirs to type). Debian/Ubuntu: `sudo apt install python3 python3-venv python3-pip git`; GitHub CLI: https://github.com/cli/cli/blob/trunk/docs/install_linux.md.
`sudo` needs the owner's password in their terminal; say so and let them run it (prefix `!` in Claude Code to run it in the session).

### Git (Windows, if somehow missing)
`winget install --id Git.Git -e --scope user --silent` (time-boxed) or https://git-scm.com/download/win.

### GitHub CLI (Windows): the no-admin way that is known to work
Follow the install section of [publish-to-github](../publish-to-github/SKILL.md): download the latest `windows_amd64.zip` and `checksums.txt` from the official `cli/cli` release into an empty scratch folder,
**verify the SHA-256**, extract to `C:\Users\<user>\tools\gh`, and call `...\tools\gh\bin\gh.exe` by full path. (winget's installer hung on a hidden permission window; this does not.)

### Editor extensions (optional, offer, don't force)
If `code` works: `code --install-extension ms-python.python` and `code --install-extension charliermarsh.ruff`. Skip silently if `code` isn't on PATH.

## 3. The project environment

```
python -m venv env                                              # [python3 -m venv env]
.\env\Scripts\python.exe -m pip install -r requirements-dev.txt   # [env/bin/pip install -r requirements-dev.txt]
Copy-Item .env.example .env                                     # [cp .env.example .env]
```
Then a fresh `SECRET_KEY` in `.env` (generate with Python; write it into the file, don't echo it), `manage.py migrate`, `pytest -q`. Details in build-my-site Phase 2.
`pip install` failures: read the error. "No matching distribution" for a wheel usually means a too-new or too-old Python: use 3.12. Corporate proxy or SSL errors: tell the owner; don't disable verification.

## 4. Things that go wrong (fix, then say what you changed)

| Symptom | Likely cause and fix |
|---|---|
| `'python' is not recognized` right after installing | Old PATH in this terminal. Open a new terminal / reopen VS Code, or use the full path |
| `python` opens the Microsoft Store | App execution alias; turn it off (human click) or use `py -3.12` |
| `running scripts is disabled on this system` | Don't change policy; call `.\env\Scripts\python.exe` directly instead of `Activate.ps1` |
| `git` asks to set a name/email | Use the GitHub noreply address, never a work email ([publish-to-github](../publish-to-github/SKILL.md) section 3) |
| `pip` can't build a package | Wrong Python version; recreate the venv with 3.12 |
| Long path errors on Windows | Keep the project near the drive root (e.g. `C:\sites\mysite`), not deep in OneDrive; OneDrive-synced folders can also lock files: move it out of OneDrive |
| Antivirus quarantines something | Tell the owner what and why; don't disable the antivirus |

## 5. Finish

Re-run the detect table and show the owner "all green". Record it in `docs/new_site_checklist.md` Phase 0 (tick the boxes), then continue with [build-my-site](../build-my-site/SKILL.md) Phase 1.
Be honest about anything you could not fix: say what, why, and the one thing the owner can do.
