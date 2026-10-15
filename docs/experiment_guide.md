# Running the experiment: does a newcomer succeed?

For the blueprint's owner. The goal is to learn **where a stranger gets stuck**, not to prove the blueprint is perfect. Every snag you capture
becomes a fix in the blueprint, and the next person goes further.

## Before you hand it over (15 minutes, you)

- [ ] Repo published, marked as a **template** (Settings -> General -> Template repository), README renders well on GitHub
- [ ] GitHub Pages enabled if you want the tutorial online (Settings -> Pages -> `main`, `/`)
- [ ] CI green on `main` (Actions tab); it runs the pinned gitleaks binary over the full history
- [ ] You have **practised the journey yourself** at least as far as the first Render deploy, so the roadmap's unverified items ([blueprint_roadmap.md](blueprint_roadmap.md)) are verified or fixed
- [ ] Pick a tester who is **motivated, not technical** (the target user), with a real, small idea for a site
- [ ] Agree what they may spend (about $7.25 for the first month) and who owns the accounts: **theirs**, not yours

## What you give them

One message: *"Here is the page: https://avisalmon.github.io/FullStackBKM/ . Follow it, and good luck."* Nothing else. (The page leads to the setup guide, then to the one sentence *"Tell me what to do"*.) If you answer questions mid-way, each answer is a **gap in the docs**: write it down.

## What to watch (observe, don't rescue)

Sit beside them or ask them to share their screen. Stay quiet for at least five minutes on any stuck point, because a real user would not have you.
Record, with timestamps:

| Moment | What to note |
|---|---|
| Setting up tools (account, Git, VS Code, Copilot or Claude Code) | Which step lost time? Was anything unclear or missing in the page or `docs/get_started.md`? Which AI engine did they pick, and did the plan/limits get in the way? |
| Terminal and clone | Did the *What is a terminal?* explanation land? Did the four clone lines work first time? Did `code my-site` open the folder, or did they need File -> Open Folder? |
| First words to the chat | Did "Tell me what to do" trigger the `build-my-site` skill, in **both** Copilot and Claude Code? Did it check the computer first and install what was missing (Python, GitHub CLI) without asking the person to? (If not, `CLAUDE.md`, `copilot-instructions.md` or the skill needs work) |
| Coming back | In a second session, did "Tell me what to do" resume from the checklist instead of starting over? |
| The interview | Did Claude ask good questions? Did the privacy questions feel natural or heavy? |
| Each **human-only step** (accounts, card, consent screens, DNS) | Were Claude's instructions exact? Where did the person click the wrong thing? |
| Secrets | Did they ever paste a secret into the chat? Why? (It means the instruction for where to put it was unclear) |
| Data model approval | Did they understand the diagram? Could they say what a relationship was *in their own words*? Did they open the tutorial? |
| First deploy | What failed? Did Claude read the logs *first*, as the skill requires? How long to green? |
| Surprises | Anything Claude did that the person did not expect or did not understand |
| Emotions | Frustration, confusion, delight. These are data |

## Success criteria

Rate each: **pass / partial / fail**.

1. **Live site:** they end with a working HTTPS site that is theirs (their GitHub, their Render, their accounts).
2. **Verified:** `python scripts/verify_site.py --url https://<site>` shows no FAIL.
3. **Safe:** repo is private; no secret in git; they can say where their secrets live.
4. **Understood:** they can explain, without looking, what their data model is and why its main relationship exists. (Ask: "Why is `<their link>` a ForeignKey and not a text field?")
5. **Independent:** they asked Claude for one small change themselves ("add a field", "change the heading") and shipped it with tests, deciding when to push.
6. **Recoverable:** they can say what they would do if the site broke or data were lost, and found the procedure.
7. **Privacy-aware:** they made (and recorded) at least one deliberate privacy decision, even if it was "no change".
8. **Time and cost:** within the expectations in the README (about an hour to first live site; about $7.25/month).

Overall: **success** = criteria 1-4 pass and none of 5-8 fail. **Partial** = live but not understood. Both teach you something.

## After the session (you, same day)

1. Write down the **top five friction points** in order of cost (time lost or confusion).
2. For each: is it a docs fix, a skill fix, a code fix, or a vendor quirk? Fix the first three in the blueprint. Add the fourth to [procedures/gotchas.md](procedures/gotchas.md).
3. Add a regression test where a test can catch it (see how `isolation` and `init_site` came from cold-start runs).
4. Update [blueprint_roadmap.md](blueprint_roadmap.md): tick what was verified live, add what failed.
5. Ask the tester three questions: *What was the most confusing moment? What would you have wanted Claude to explain sooner? Would you do another site this way?*
6. Thank them, and make sure they know how to delete everything they created if they do not want to keep it (Render service and disk, GCS bucket, API keys, Google project).

## Ethics of the experiment

The tester spends real money and creates real accounts. Say so up front, let them stop at any point, and never ask them to paste secrets for your convenience. If they build something for
young users, do the privacy review ([privacy.md](privacy.md)) before the site is shared with anyone.
