# Get started: from zero to a chat that guides you

You do this part once, by yourself. Its only goal is a **working editor with an AI chat inside it, opened on your own copy of this project**.
From the moment you type *"Tell me what to do"* in that chat, the assistant takes over: it installs the rest (Python, GitHub's command-line tool, project tools),
creates your private GitHub repository (your project's folder on GitHub), fixes problems, and guides you step by step. You never have to come back to this page.

Time: 20-40 minutes, mostly downloads and sign-ups. Windows is described first; macOS and Linux notes are in each step.

```
 1. GitHub account  ->  2. VS Code  ->  3. an AI chat in VS Code (say hello)  ->  4. Git  ->  5. copy the project to your PC  ->  6. "Tell me what to do"
```

## 1. A GitHub account (free)

GitHub is where your site's code will live, privately.

1. Go to https://github.com/signup and create an account. Pick a username you won't mind seeing in your site's address.
2. Turn on **two-factor sign-in** (GitHub calls it "two-factor authentication", often written 2FA). It means signing in needs your password **and** a one-time code
   from your phone, so someone who steals your password still can't get in. This matters: your account will hold your site's code.
   * GitHub -> click your picture (top right) -> **Settings** -> **Password and authentication** -> **Enable two-factor authentication**.
   * Choose an **authenticator app** on your phone (for example Google Authenticator or Microsoft Authenticator): scan the square code GitHub shows, then type the 6-digit code the app shows.
     (A **passkey** is a newer option that uses your phone's or computer's fingerprint/face/PIN instead of a code; either is fine.)
   * GitHub then shows **recovery codes**. Save them somewhere safe (a password manager, or printed): they are how you get back in if you lose your phone.

*You know it worked when* you can sign in at https://github.com.

## 2. VS Code (the editor)

Download from https://code.visualstudio.com and install it. On Windows, keep the option **"Add to PATH"** ticked (it is on by default).
(Other editors that support an AI assistant can work, but this guide and the assistant's instructions assume VS Code.)

*You know it worked when* VS Code opens.

## 3. An AI chat inside VS Code (pick one), and say hello

You need a chat that can **read your project and run commands for you**. Two options work with this project; its playbooks are included for both.

### Option A: GitHub Copilot

1. In VS Code open Extensions, the add-ons store (**Ctrl+Shift+X**, or the icon of four squares on the left), search **GitHub Copilot**, click **Install**.
2. Click **Sign in** when it asks, and sign in with the GitHub account from step 1.
3. Plan: Copilot has a free tier with limited monthly use; a long guided build usually needs a paid plan. Check yours at https://github.com/settings/copilot.
4. Open the chat (**Ctrl+Alt+I**, or the chat icon at the top of the window) and set the mode to **Agent** (the dropdown in the chat box). Agent mode is what lets it run commands and edit files.

### Option B: Claude Code

1. You need a Claude account on a plan that includes Claude Code (see https://claude.com/claude-code), or API credits.
2. In VS Code open Extensions (**Ctrl+Shift+X**), search **Claude Code** (published by Anthropic), click **Install**.
3. Open the Claude Code panel (the Claude icon at the top right of the editor, or press **Ctrl+Shift+P** and type *Claude Code*) and sign in when it asks.

**Now type `hello` in the chat.**

*You know it worked when* it answers. You now have a working editor with an AI in it. That's the hard part done.

## 4. Git

Git is the tool that copies the project to your computer and keeps track of every change.

* **Windows:** download from https://git-scm.com/download/win and accept the default choices. (Or, in a terminal: `winget install --id Git.Git -e`.)
* **macOS:** open Terminal and run `xcode-select --install` (or `brew install git`).
* **Linux:** `sudo apt install git` (or your distribution's equivalent).

Then **close VS Code completely and open it again**, so it notices Git.

### First, what is a "terminal"?

A **terminal** is a window where you give the computer instructions by **typing** them instead of clicking. Each instruction is one line of text, called a **command**.
You only need it for a few lines in this guide; after that, the AI chat runs commands for you (and shows you what it runs).

* **How to open one:** VS Code has one built in. In the top menu click **Terminal -> New Terminal** (or press **Ctrl+`**, the key under Esc). A panel opens at the bottom of the window.
* **What you will see:** a line ending in `>`, something like `PS C:\Users\dana>`. This is the **prompt**: it means "ready, type a command". (On macOS/Linux it ends in `$` or `%`.)
* **How to run a command:** click inside the terminal panel, type the command (or paste it: copy from this page, then **Ctrl+V** or right-click in the terminal), and press **Enter**.
* **How to know it finished:** the prompt line comes back. Some commands take a few seconds and print nothing while they work: that's normal, just wait for the prompt.
* **If you see red text,** something went wrong. Read the first red line, and check the table at the end of this page. You can't break your computer with the commands in this guide.
* **Run one line at a time:** paste one line, press Enter, wait for the prompt, then the next.

*You know it worked when* you open a terminal in VS Code, type `git --version`, press Enter, and see something like `git version 2.47.1`.

## 5. Copy the project to your computer and open it

You are going to make a folder for your sites, copy (clone) the project into it, and open it in VS Code.

1. In VS Code, open a terminal: **Terminal -> New Terminal** (a panel opens at the bottom; see *What is a terminal?* above).
2. Run these four commands **one at a time**: paste or type a line, press **Enter**, wait for the prompt to come back, then the next line.
   Replace `my-site` with a short name for your site (lowercase, no spaces) in the last two lines:

   ```
   mkdir C:\sites
   cd C:\sites
   git clone https://github.com/avisalmon/FullStackBKM.git my-site
   code my-site
   ```

   What each line does, in plain words:
   * `mkdir C:\sites` makes a new, empty folder called `sites` on your C: drive ("make directory").
   * `cd C:\sites` moves the terminal into that folder ("change directory"); the prompt now ends in `C:\sites>`.
   * `git clone ... my-site` copies the whole project from GitHub into a new folder `C:\sites\my-site`. It prints a few lines of progress, then the prompt returns.
   * `code my-site` opens that folder in a new VS Code window.

   (macOS/Linux: use `mkdir ~/sites` and `cd ~/sites` for the first two lines.)

3. A new VS Code window opens on your project. It asks **"Do you trust the authors of the files in this folder?"** Click **Yes, I trust the authors**: the assistant needs to run commands here.
   If the last line says `code` is not recognised, use **File -> Open Folder** and choose `C:\sites\my-site` instead.

Why `C:\sites` and not your Documents folder: Documents is often synced by OneDrive, which locks files while it syncs and breaks long file paths. A plain folder avoids both.

*You know it worked when* the Explorer on the left shows folders like `docs`, `tutorial` and `mysite`, and files like `CLAUDE.md` and `README.md`.

**This is a copy on your computer only.** Nothing you do in it can change the original project online. Your own private GitHub repository is created by the assistant later,
before anything about your site is saved online, and you approve that step.

## 6. Say it

Open the chat again in this new window (**Agent** mode for Copilot; the Claude Code panel for Claude Code) and type:

> **Tell me what to do**

(Saying *"Help me build my full stack site"* works too.) The assistant looks at your computer, tells you what it found, installs anything missing, asks what your site is for,
and walks you through everything: the plan, the first working site on your computer, your private GitHub repository, going live on Render, and the optional extras (Google sign-in,
email, your own domain, AI features, backups, cost alerts). It tells you exactly what to click whenever a step needs *you*. You never need to paste a password or key into the chat.

**Coming back later?** Open the project in VS Code (**File -> Open Recent**), open the chat, and say *"Tell me what to do"* again. It reads the checklist and continues where you stopped.

## Things you will be asked to approve

* The assistant asks permission before running commands; read what it wants to run and approve if it makes sense. It explains each step. If a command looks unrelated to what it just said, say no and ask why.
* **A Windows "Do you want to allow this app to make changes?" window** can appear when something installs. It may open *behind* VS Code: if an install seems stuck, look for it in the taskbar and click **Yes** (or tell the assistant, and it will use a way that needs no admin rights).
* It will ask you to open a few websites (GitHub once to log in, then Render, Google and so on) and click specific buttons. That's the part nobody can do for you.

## If something goes wrong in this part

| Symptom | Fix |
|---|---|
| The chat can't run commands or edit files | Copilot: switch the mode to **Agent**. Claude Code: make sure the project folder is open and trusted |
| `git` is not recognised | Close VS Code completely and open it again after installing Git, so it notices the newly installed program |
| `code` is not recognised (step 5) | Use **File -> Open Folder** -> `C:\sites\my-site` instead |
| `mkdir` says the folder already exists | That's fine: carry on with `cd C:\sites` |
| `git clone` says the destination already exists | Pick another name instead of `my-site`, or delete the old folder first |
| Copilot or Claude says you've run out of messages | Check your plan; the free tiers are limited |
| You use another editor, or only a terminal | The playbooks work in any assistant that reads `AGENTS.md`; open the folder there and say the same sentence |

**Already comfortable with GitHub?** You can instead click **Use this template** on the project's GitHub page, create a **private** repository, and clone *that*. The assistant handles both starting points.

## Words you'll meet

Plain meanings, so nothing on the way sounds like a secret code. You can always ask the chat *"what does that mean?"*.

| Word | Meaning |
|---|---|
| **GitHub** | a website that stores code. Your site's code will live there, privately. |
| **Repository ("repo")** | one project's folder on GitHub, with the full history of every change. |
| **Git** | the program on your computer that copies projects from GitHub and records every change you make. |
| **Clone** | make a copy of a repository on your own computer. |
| **VS Code** | the editor: the program where you see your project's files and talk to the AI. |
| **Extension** | an add-on you install inside VS Code, like GitHub Copilot or Claude Code. |
| **Agent mode** | the Copilot setting that lets the chat *do* things (run commands, edit files), not just answer. |
| **Terminal** | a panel where you type commands instead of clicking. In VS Code: Terminal -> New Terminal. |
| **Command** | one typed instruction. You run it by pressing Enter, then wait until the terminal is ready again. |
| **Two-factor sign-in (2FA)** | signing in needs your password *and* a one-time code from your phone, so a stolen password alone is not enough. |
| **Python** | the programming language your site is written in. The chat installs it for you. |
| **GitHub command-line tool ("GitHub CLI")** | a small program that lets the chat talk to GitHub for you, for example to create your private repository. The chat installs it; you log in once in the browser. |
| **Private vs public** | private: only you can see it. Your site's code is private. This blueprint is public so anyone can start from it. |
| **Render** | the hosting company whose computers run your site on the internet, about $7.25 a month. |
| **Blueprint (on Render)** | Render's one-click setup: it reads a settings file in your project and creates everything your site needs. |
| **Deploy, go live** | put the latest version of your site on the internet. Here it happens when you say so. |
| **Logs** | the server's diary of what happened. When something fails, the chat reads them before changing anything. |
| **Domain** | your own address, like `your-name.com`, rented yearly from a domain shop (a "registrar"). |
| **DNS records** | a few settings at the domain shop that point your address at Render. You copy them from Render. |
| **HTTPS, the padlock** | the encrypted connection that shows a padlock in the browser. Render sets it up for you. |
| **Secret, key** | a password your site uses to talk to a service (Render, Google, OpenAI). It goes in a private file or in Render's settings, never in the chat. |
| **Google sign-in key ("OAuth client")** | what you create in Google's console so your site can offer "Continue with Google". |
| **Bucket** | a storage space in Google Cloud. Your offsite backup copies go there. |
| **Data model** | the plan of what your site remembers and how those things connect. You approve it before anything is built. |
| **Playbooks ("skills")** | step-by-step instructions inside this project that the AI follows, so it builds your site the same careful way every time. |

When the chat answers *"Tell me what to do"*, stop reading this page. The assistant has it from here.
