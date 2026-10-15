# Get started: from zero to a chat that guides you

You do this part once, by yourself. Its only goal is a **working editor with an AI chat inside it, opened on your copy of this project**.
From the moment you type *"Tell me what to do"* in that chat, the assistant takes over: it installs the rest (Python, the GitHub CLI, project tools),
fixes problems, and guides you step by step. You never have to come back to this page for anything else.

Time: 20-40 minutes, mostly downloads and sign-ups. Windows is described first; macOS and Linux notes are in each step.

```
 1. GitHub account  ->  2. Git  ->  3. VS Code  ->  4. an AI engine in VS Code  ->  5. your copy of the project  ->  6. "Tell me what to do"
```

## 1. A GitHub account (free)

1. Go to https://github.com/signup and create an account. Pick a username you won't mind seeing in your site's address.
2. Turn on **two-factor authentication** (GitHub -> your picture -> Settings -> Password and authentication). Use an authenticator app or passkey.

*You know it worked when* you can sign in at https://github.com.

## 2. Git

Git is the tool that copies the project to your computer and tracks changes.

* **Windows:** download from https://git-scm.com/download/win and accept the default choices. Or open PowerShell and run `winget install --id Git.Git -e`.
* **macOS:** open Terminal and run `xcode-select --install` (or `brew install git`).
* **Linux:** `sudo apt install git` (or your distribution's equivalent).

*You know it worked when* `git --version` prints a version in a **new** terminal window (close and reopen it after installing).

## 3. VS Code (the editor)

Download from https://code.visualstudio.com and install it. On Windows, tick **"Add to PATH"** if asked.
(Other editors that support an AI assistant can work, but this guide and the assistant's instructions assume VS Code.)

*You know it worked when* VS Code opens.

## 4. An AI engine inside VS Code (pick one)

You need a chat that can **read your project and run commands for you**. Two options work with this project; the playbooks are included for both.

### Option A: GitHub Copilot

1. In VS Code open Extensions (**Ctrl+Shift+X**), search **GitHub Copilot**, click **Install**.
2. Click **Sign in** when it asks and sign in with the GitHub account from step 1.
3. Plan: Copilot has a free tier with limited monthly use; a long guided build usually needs a paid plan. Check your plan at https://github.com/settings/copilot.
4. Open the chat (**Ctrl+Alt+I**, or the chat icon at the top of the window) and set the mode to **Agent** (the dropdown in the chat box). Agent mode is what lets it run commands and edit files.

### Option B: Claude Code

1. You need a Claude account on a plan that includes Claude Code (see https://claude.com/claude-code), or API credits.
2. In VS Code open Extensions (**Ctrl+Shift+X**), search **Claude Code** (published by Anthropic), click **Install**.
3. Open the Claude Code panel (the Claude icon at the top right of the editor, or press **Ctrl+Shift+P** and type *Claude Code*) and sign in when it asks.
   If you prefer a terminal: follow the official setup page linked from https://claude.com/claude-code, then run `claude` inside your project folder.

*You know it worked when* you can type "hello" in the chat and get an answer.

## 5. Your own private copy of the project, opened in VS Code

1. Open the project's page on GitHub and click **Use this template -> Create a new repository**. Name it after your site, choose **Private**, create it.
   (Private matters: this will be your real website's code.)
2. On your new repository's page click the green **Code** button and copy the HTTPS address.
3. In VS Code: **Ctrl+Shift+P** -> *Git: Clone* -> paste the address -> choose a folder (for example `Documents\sites`) -> **Open** when it offers.
   Or in a terminal: `git clone <address>` and then `code <folder-name>`.
   GitHub may ask you to sign in the first time: do it in the browser window it opens.
4. VS Code asks **"Do you trust the authors of the files in this folder?"** Click **Yes, I trust the authors**. It is your own copy, and the assistant needs to run commands.

*You know it worked when* the Explorer on the left shows folders like `docs`, `tutorial` and `mysite`, and a file `CLAUDE.md`.

## 6. Say it

In the chat (Agent mode for Copilot), type:

> **Tell me what to do**

(Saying *"Help me build my full stack site"* works too.) The assistant looks at your computer, tells you what it found, installs anything missing, asks what your site is for,
and walks you through everything: the plan, the first working site on your computer, your private repo, going live on Render, and the optional extras (Google sign-in, email,
your own domain, AI features, backups, cost alerts). It tells you exactly what to click whenever a step needs *you*. You never need to paste a password or key into the chat.

**Coming back later?** Open the project in VS Code, open the chat, and say *"Tell me what to do"* again. It reads the checklist and continues where you stopped.

## Things you will be asked to approve

* The assistant asks permission before running commands; read what it wants to run and approve if it makes sense. It will explain each step. If a command looks unrelated to what it just said, say no and ask why.
* **A Windows "Do you want to allow this app to make changes?" window** can appear when something installs. It may open *behind* VS Code: if an install seems stuck, look for it in the taskbar and click **Yes** (or tell the assistant, and it will use a way that needs no admin rights).
* It will ask you to open a few websites (Render, Google, and so on) and click specific buttons. That's the part nobody can do for you.

## If something goes wrong in this part

| Symptom | Fix |
|---|---|
| `git` is not recognised | Close and reopen VS Code (or the terminal) after installing Git so it sees the new PATH |
| The chat can't run commands | Copilot: switch the mode to **Agent**. Claude Code: make sure the folder is open and trusted |
| Clone asks for a password and rejects it | GitHub no longer accepts account passwords on the command line; use the browser sign-in that VS Code opens (or install the GitHub CLI and run `gh auth login`) |
| "Use this template" button is missing | You must be signed in to GitHub; the repository's owner must have enabled it as a template |
| Copilot/Claude says you've run out of messages | Check your plan; the free tiers are limited |
| You use another editor or terminal-only | The skills work in any assistant that reads `AGENTS.md`; open the folder there and say the same sentence |

When the chat answers your first message, stop reading this page. The assistant has it from here.
