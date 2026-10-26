# What we learned, by date

The short version of every lesson added to this blueprint, newest first, so you can see what changed since you
last looked. Each line points to where the full rule lives. They come from building a real production site with
an AI engineer, and most of them came from something going wrong.

## 2026-10-26

- **A page in another language than the site prints its dates in the site's language.**
  [mistake 66](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **A grid item needs both a row and a column, and a track needs `minmax(0, ...)`.**
  [mistake 67](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **A middleware is placed by what it reads; a sweep knows its own alphabet; a row of tap targets is sized by the thumb.**
  [mistake 65](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **A one-time link lets its own holder back in, and every door that grants access sends the mail.**
  [mistake 64](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **"Sent" is what the mail backend said, not what the code hoped.** [mistake 62](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Mark each item handled by its id; never infer "handled" from time.** [mistake 63](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **A clean copy is not the developers' copy.** The first real train failed five tests that were not code: a newer
  linter, no built static files, no local config. Derive the train's environment from the shared tree by code (pinned
  tool versions, the production build step, local config filtered of every secret-shaped name), and list the failures
  already on main before the first train, or it blames the requester for everyone's debt.
  [procedure](procedures/release_train.md#the-first-train) · [illustrated](release_train.html#first)
- **Optional: when several AI sessions build several apps at once, let one release train publish for all of them.**
  Only that case; with one app, ignore it. [release-train skill](../.claude/skills/release-train/SKILL.md) · [illustrated](release_train.html) ·
  [procedure](procedures/release_train.md)

## 2026-10-24

- **A new form control runs the narrowest-phone test the day it ships.** [mistake 61](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **JSON inside a script tag is HTML too.** [mistake 58](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Members' markdown is cleaned after rendering, not trusted.** [mistake 59](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Run the security sweep before saying "secure".** [mistake 60](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)

## 2026-10-23

- **The control follows the shape of the decision, not the word the person used.**
  [mistake 57](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **A screen test stubs every outside source, keyless ones too.**
  [mistake 56](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Build an image feature against made-up photos with known answers, from a real camera**, judged on a set it was
  not tuned on. [mistake 55](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **When a fact starts being written earlier, find everyone who read its absence as an event.**
  [mistake 54](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Test a browser API with the events the real device sends.** Android speech results repeat and grow; rebuild,
  never append. [mistake 53](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Count what a person did as they do it, not when they close it.** Heartbeat and pause save it; count from what
  is saved. [mistake 52](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)

## 2026-10-22

- **Walk the newcomer's road as the newcomer**, from the link to the first screen that pays off, data loaded.
  [mistake 49](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Image work inside the web process: decode small, a few at a time, let go.**
  [mistake 50](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Many small private images go to the browser from storage**, by day-signed links, not through the one worker.
  [mistake 51](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **One app's whole test suite is a full regression too.** Twice a day or on request; otherwise test what you changed.
  [mistake 48](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **A safety net can blind the check it backs up.** Move the check where the net cannot reach, and prove it against
  the bug. [mistake 47](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Whoever sees a mistake in shared data needs a way to fix it.** Gate by a trail of old values, not a permission.
  [mistake 46](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Every way of pointing: a finger, a mouse, a wheel.** Test drag and scroll widgets with each.
  [mistake 44](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Never measure an image while drawing a page.** Store its size when it is made.
  [mistake 45](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)

## 2026-10-21

- **When asked to ask, always ask, prefilled.** A question hidden when data exists never shows once automation fills
  it. [mistake 43](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Test at the narrowest phones, not one convenient width.** 320, 360, 375 and 412, and the header alone.
  [mistake 42](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Watch a deploy on the site, not by hammering an API.** Poll the live site for a marker of the new code; an API
  error is not a state. [mistake 41](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **A timer counts only while its screen is in front; a sheet opens without the keyboard.** Pause on `pagehide`,
  focus the likely first action. [mistake 40](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **A ring drawn with a radial mask needs `closest-side`.** Otherwise the stops fall outside the box and nothing is
  drawn. [mistake 39](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **In a right-to-left language, check direction and signs by eye.** What is ahead comes from the left; signed
  numbers get `dir="ltr"`. [mistake 38](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **On a phone, a too-wide page hides from an overflow check.** Pass the device width and check the document's own
  width too. [mistake 37](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)

## 2026-10-20

- **Detail pages: one main action on top, the rest folds with its value showing.** No raw file inputs, no bare zero.
  [mistake 36](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Test the task on a phone, not only the pages.** One browser test per flow does the whole job, with real-sized
  data. [mistake 35](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **A real key on the developer's machine reaches the tests.** Blank paid keys and background work in one shared
  test fixture. [mistake 34](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **On a phone, the content comes first and options fold.** Test that the first list row starts in the top half of
  the screen. [mistake 33](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **A setting that limits cost is not a limit until measured.** One real call, read the bill, budget on that, and
  keep your own daily cap. [mistake 32](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **A picker must offer every value the stored data can hold**, and show a saved answer as chosen.
  [mistake 31](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)

## 2026-10-19

- **Background work a person waits on must heal itself, end in a visible state, and keep reminding.** Every deploy
  is a restart. [mistake 30](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Importing code never touches the persistent disk.** The build has no disk mounted. Create folders on first use.
  [mistake 25](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Adding to the shared page frame means running every test of the app**, and it must survive every state of the
  person, including "just deleted". [mistake 26](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Colour pairs made in code need their own contrast test**, over the whole list.
  [mistake 27](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **A count after a filter on the same relation is a count of the filtered rows.** Annotate first, test with two.
  [mistake 28](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)
- **Read every number on a screenshot against the seeded data.** The browser check sees shape, not meaning.
  [mistake 29](building_an_app.md#mistakes-we-actually-made-and-the-rules-that-came-out-of-them)

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
