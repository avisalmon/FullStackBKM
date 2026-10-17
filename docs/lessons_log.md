# What we learned, by date

The short version of every lesson added to this blueprint, newest first, so you can see what changed since you
last looked. Each line points to where the full rule lives. They come from building a real production site with
an AI engineer, and most of them came from something going wrong.

## 2026-10-17

- **A pipe hides a failure.** Don't chain an action after `tests | tail`; act on the test command's own result.
  [mistake 24](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)

## 2026-10-16

- **Every session starts by checking GitHub for blueprint updates, and pulls them in when it is safe.** Unsaved work
  blocks the pull, a conflict is undone rather than left half-done, and it never pushes; then the AI says what arrived
  and re-reads any playbooks that changed. [CLAUDE.md, rule 0](../CLAUDE.md) · [scripts/check_updates.py](../scripts/check_updates.py)
- **When several AI sessions share one folder, a commit is a release.** Another session's push can ship it.
  [mistake 23](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Lessons get a post-mortem every time, not when someone remembers.** The triggers are written down.
  [building_an_app.md](building_an_app.md#building-an-app-on-this-site)
- **Each feature's tests passing is not the same as the product working.** Check every role at every stage, together.
  [building_an_app.md, mistake 18](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them) · [design-review skill](../.claude/skills/design-review/SKILL.md)
- **Never show an email address on a page the public can see**; ask for a display name instead.
  [mistake 19](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them) · [privacy-advisor skill](../.claude/skills/privacy-advisor/SKILL.md)
- **An app's error pages must be its own.** [building_an_app.md](building_an_app.md#error-pages-stay-inside-the-apps-walls)
- **A new app under a shared URL prefix can silently take an older app's routes.**
  [building_an_app.md](building_an_app.md#two-apps-under-one-url-prefix)
- **One door to anything irreversible.** [building_an_app.md](building_an_app.md#one-door-to-an-irreversible-action)
- **Refusing one thing must not throw away what the person typed.**
  [building_an_app.md](building_an_app.md#a-refusal-never-costs-the-person-what-they-already-typed)
- **Show times in the place's own timezone, named by its city.** [building_an_app.md](building_an_app.md#times-belong-to-a-place)
- **Seeds add what is missing, and never touch what exists.** [building_an_app.md](building_an_app.md#data-seeding-is-one-time-only)
- **POST for changes, and never redirect off the site.** [mistake 20](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them) · [site-security skill](../.claude/skills/site-security/SKILL.md)
- **When a fix doesn't show, suspect the server.** [mistake 21](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **On Windows, write code to a file instead of pushing it through the shell.** [mistake 22](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
