---
name: release-train
description: >
  OPTIONAL, and most owners never need it. Only for a site where several AI sessions build more than one app at
  the same time on one repository and their pushes collide: one release train becomes the only thing that publishes,
  tests what each change touches, runs the full suite once a night, and is watched by a watchdog. If you build one
  app, or work in one AI session at a time, ignore this skill. TRIGGER: "several agents", "parallel chats",
  "two apps at once", "pushes collide", "who pushes", "release train", "deploy queue", "agents stepping on each other".
---

# Release train (optional)

**First, check that it applies. Most owners stop here.** This is for a site where **more than one app is being
built at the same time, by several AI sessions on one repository**. Signs that it does: two or more chats open on
the same project at once, each on a different app; a commit reaching the live site through somebody else's push
before its own tests finished; the full test run getting slower because several run at once; failures nobody owns.

If you build **one app**, or use **one AI session at a time**, you do not need any of this: commit, test, and push
when you decide, as [render-django](../render-django/SKILL.md) and [building-an-app](../building-an-app/SKILL.md)
describe. The train adds moving parts that depend on one computer staying on, and that is a cost worth paying only
when the collisions are real. Say so to the owner in one sentence, and stop.

Source of truth: [docs/procedures/release_train.md](../../../docs/procedures/release_train.md). Re-read it first.

## When it does apply

Explain the idea in plain words before building anything: *"Right now any of your AI sessions can publish, and
publishing sends everyone's work. We'll make one small program the only one allowed to publish. Each session asks
it; it tests what changed and publishes, or says whose test failed."* Then, with the owner's agreement:

1. A **pre-push hook** that refuses pushes to the live branch unless the train is pushing (and an emergency override
   only the owner uses). Side branches stay allowed.
2. The **train script**, running in **its own copy of the repo**, never a session's working folder: builds a
   candidate from what is waiting, picks the tests from the files that changed (an app's tests for an app's files;
   everything for shared files like settings and requirements; nothing for documentation), ignores a written list of
   known failures, pushes only if nothing new failed, and waits for the deploy.
3. A **board** outside the repo (what is waiting, the last runs, whose failure is whose, who is editing which shared
   file), and the rule that every session reads it before starting.
4. The **full suite once a night**, reporting only new failures.
5. **Staying alive**: a scheduled task that ticks every few minutes and at sign-in; a lock with a heartbeat, broken
   when its process dies or hangs; a time limit on every test run; and anything else that runs unattended (a mail
   bot, for example) watching the train's heartbeat while the train watches its. Tell the owner plainly what it cannot
   survive: the computer off, or signed out, unless they set the tasks to run whether signed in or not.

Test it in a throwaway world before trusting it: a fake remote, two tiny apps with tests that pass or fail on
purpose, and the real script driven through every promise (nobody else reaches the live branch; a new failure blocks
and names its app; a known one does not; a shared change tests everything; a dead train is cleaned up).

## While it runs

Every session, every time: never push the live branch, commit only what is ready to ship, run your app's own tests,
leave the full suite to the night, read the board when you start, and ask the train when the owner says "publish".
