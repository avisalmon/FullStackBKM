# The release train (optional)

> **You probably don't need this.** It is for a site where **more than one app is built at the same time by several
> AI sessions on one repository**. With one app, or one session at a time, commit, test and push when you decide,
> as [deploy_to_render.md](deploy_to_render.md) describes, and skip this page.

**Prefer pictures?** [release_train.html](../release_train.html) says the same with diagrams; open it in a browser.

## The problem it solves

Several AI sessions working on one repository share one live branch. Any of them can push, and a push publishes
**everybody's** commits. On the site this was learned on, with five sessions on five apps, ten days produced:

- a finished feature published by another session in the middle of its own test run;
- four apps' failures reaching the live site in other sessions' pushes, unnoticed;
- a full test run taking three hours instead of one, because several ran at once and fought over the database
  and the network ports;
- a new app left unregistered for three days, because nobody's scoped tests covered it.

## The idea

**One small program is the only thing allowed to publish.** Each session asks it; it tests what the change
touches and publishes, or says exactly whose test failed. The full suite runs once a night, for everyone, instead
of once per session.

## The parts

| Part | What it does |
|---|---|
| A pre-push hook in every copy of the repo | Refuses a push to the live branch unless the train is pushing; an emergency override exists for the owner only. Side branches stay allowed |
| `ship` | A session (or a bot) records a request and usually starts a train at once, waiting for the answer |
| The train | In **its own copy** of the repo: builds a candidate (the live branch, the shared working copy's commits, any side branch a request named), chooses tests from the changed files, runs them in parallel, pushes only if nothing new failed, waits for the deploy |
| Test selection | An app's files: that app's tests. A test file: itself. **A shared file** (project settings, the main app, requirements, deploy config, site-wide templates): **everything**. Documentation: nothing. Always: a short "site contract" set that catches one app breaking another |
| Known failures | A file listing tests known to fail, each with its owner, the date and why, so old failures stop hiding new ones |
| The board | A file outside the repo: what is waiting, the last trains and nights, whose failure is whose, who is editing which shared file. Every session reads it first |
| The night | The full suite on what is live, reporting only new failures, by app |
| The watchdog | Runs on every tick: breaks a lock whose process died or hung and re-queues its work, notices a silent bot or a missed night, and sends each alert once |

## Staying alive

It runs on one computer, so say plainly what that means:

- A scheduled task ticks every few minutes and at sign-in, catches up on missed runs, and never runs twice at once.
- The task runs the **published** copy of the train script, not the one a session may be editing.
- The lock carries a heartbeat; no process, no heartbeat or past its time limit means it gets broken and its work
  re-queued. Every test run has a time limit.
- Anything else unattended (a mail bot) and the train watch each other's heartbeats and mail the owner once if
  the other goes quiet.
- **It cannot survive the computer being off, or on but signed out**, unless the scheduled tasks are set to "run
  whether the user is logged on or not". Only the owner can choose that.

## Rules for every session

1. Never push the live branch; ask the train.
2. A commit means "ready to ship", because any train may carry it.
3. Run your own app's tests while you work; leave the full suite to the night.
4. Read the board when you start; a failure it names as yours is yours.
5. Claim a shared file before editing it, and release it after.

## Reference implementation

The site this was learned on uses one Python script (`ship`, `run`, `nightly`, `tick`, `watchdog`, `status`,
`claim`, `release`), a shell pre-push hook and a Windows scheduled task, with 22 tests that drive the real script
in a throwaway world (a fake remote and two tiny apps whose tests pass or fail on purpose):
the train script, `train.py`, in [that site's scripts folder](https://github.com/avisalmon/Render/tree/main/scripts),
[its tests](https://github.com/avisalmon/Render/blob/main/tests/test_release_train.py) and
[its procedure](https://github.com/avisalmon/Render/blob/main/docs/procedures/release_train.md).
Adapt the paths and the test selection to your own apps rather than copying it as it is.
