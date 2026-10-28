# Building an app on this site

The methodology, distilled from building a real multi-app production site. It is a **living file**:
when you learn something while building, add it here (in the section it fits, or a new one), and say
*what happened and why it mattered*. A rule without the failure behind it gets ignored the next time
someone is in a hurry.

**When to add something.** Not "when you remember". Do a short post-mortem (what happened, why the way you
work let it happen, the rule that now prevents it) whenever: the owner corrects how something was done; a bug
reaches the live site; a review, a screenshot or a full test run finds something the feature's own tests missed;
you find a better way of working; or a stretch of work ends. Then put the rule where it will be read: here, and
in the skill that covers it. New lessons are listed by date in [lessons_log.md](lessons_log.md).

An "app" here means a Django app that is one feature area of the site: its own folder, models, URLs,
templates, docs. The example is [notes/](../notes/) with docs in [docs/notes/](notes/spec.md). Copy its shape.

---

## Core rules (strong defaults)

> Seven rules below. Rule 7 (personal data) was added when privacy became part of the blueprint.

A default means: this is what we do unless a specific case needs something else, and **that exception gets
written down when it happens**, not assumed silently.

**Rule 1 - Real data is database models. Never text or JSON files.**
Every piece of real data is a row in a proper model. A one-time JSON import to seed a model is fine; a
file the app keeps reading as its data is not. If a person can't see it, act on it or query it through the app,
it isn't data, it's documentation.

**Rule 2 - An app is fully encapsulated.**
It never touches another app's models, views or data. The one thing apps share is the user account, for login.
If an app needs something app-specific about a person (a preference, a role), it makes its **own model with a
one-to-one link to the user**; it never adds fields to `User`. Test: could this folder be lifted into a different
site and still work, with only the shared login? If building a feature meant editing outside the app's folder,
the boundary was crossed.

**Rule 3 - An app has its own base template and menu.**
It does not extend the site's `base.html`, and links back to the main site only if explicitly asked. A visitor
inside the app shouldn't need to know the rest of the site exists.

**Rule 4 - An app has its own docs directory.**
`docs/<app>/` holds `spec.md` (what and why), `backlog.md` (sprints and status), `data_model.md` (the models
and relationships, *separate* from the spec so the shape of the database can be read on its own), and, if you
want one, a dashboard.

**Rule 5 - Migrate and deploy scoped to the app.**
`python manage.py migrate <app_label>` locally while developing; don't bundle unrelated apps' half-finished
work into one commit or push. (One repo = one deploy pipeline, so a push still deploys everything: be deliberate.)

**Rule 6 - Every app gets a full, documented CRUD REST API (Django REST Framework).**
Create, read, update and delete for the things that make sense to expose, not just what today's screen needs.
The API is the infrastructure; pages are consumers of it. DRF's browsable API is the documentation. The default
permission is deny (`IsAuthenticated`) and each viewset scopes its queryset (`filter(owner=request.user)`), so
other people's objects don't exist for you.

**Rule 7 - Personal data is declared, exportable and erasable.**
Every app that stores something about a person says so, in three places: (1) a **Personal data** section in `docs/<app>/data_model.md` (for each field: personal? sensitive? why
collected? who sees it? how long kept? public or private file?); (2) an **exporter and an eraser** registered in `core.privacy` from the app's `AppConfig.ready()` (the eraser removes what
a cascade will not: uploaded **files**); (3) a **test** that erasing a person removes their rows and files and leaves everyone else's alone. Collect the least you can. This is advice, not
a lock: the owner can choose otherwise, and the choice goes in `docs/privacy_decisions.md`. See [privacy.md](privacy.md).

---

## Starting a new app: the kickoff sequence

Each step waits for the owner before the next one starts. It is not a checklist to rush through in one pass.

1. **Interview first.** Ask until you understand: who it's for, what problem it solves, what it is *not*. Don't assume.
2. **A thin intro spec.** One short chapter, plain words: "this is the app we're talking about." Not the full spec.
3. **The data model, on its own.** `docs/<app>/data_model.md`: the main classes and how they relate. Not complete,
   but it must give real understanding of what the app will do from the data's point of view.
   **Teach before you ask for approval**: if the owner is new to data modelling, walk them through
   [the tutorial](../tutorial/data-models.html) (what a model is, why relationships matter, the four shapes, what happens on delete) using *their*
   entities. **Stop and wait for the owner's approval.** Getting the shape of the data right early is what everything is built on;
   getting it wrong is expensive to unwind.
4. **The full spec, in high-level chapters**, only after the data model is approved.
5. **The normal flow:** backlog, sprints, test-first, scaled to the app's size (below).

Scaffold with: `python manage.py startapp <name>`, add it to `INSTALLED_APPS`, mount it in `mysite/urls.py` **before**
the `core` catch-all, give it `app_name` + a namespace, its own `templates/<name>/base.html` and `static/<name>/`.

## Per-app checklist

- [ ] `docs/<app>/{spec,backlog,data_model}.md`, data model approved
- [ ] Personal data section in the data model; exporter + eraser registered; erase test (Rule 7)
- [ ] Models + migrations (`makemigrations --check` clean)
- [ ] DRF serializers + viewsets + router, permission and queryset scoping tested (the refusals first)
- [ ] Own base template; classes prefixed with the app name
- [ ] Pages built on the API (fetch + DOM), not hand-rolled JSON views
- [ ] Admin registration
- [ ] Tests: refusals, happy paths, and a seed command run **twice** if there is one
- [ ] Looked at every screen as an image at least once, at phone width
- [ ] Error pages (403/404/500) routed to the app's own templates, with a test that reads what the page *says*
- [ ] If the app shares a URL prefix with an older app: a test that every older route still reaches its owner
- [ ] No page anyone but an admin sees ever shows an email address (test it with a user who has no name)
- [ ] If the app has roles or stages: every link on every role's home opens for that role, at every stage
- [ ] Anything with a time and a place shows times in that place's timezone, named by its city
- [ ] Deploy discipline below

---

## Practices that came from real mistakes

### Data: seeding is one-time only
A seed command that imports from a static file must **check whether the data exists and leave it alone if so**.
On the reference site, a seed command ran on every deploy and wholesale deleted and recreated rows from a JSON
snapshot; the moment a person could edit those rows, every deploy would have destroyed their edits.
The database, once populated, is the only source of truth. Write a test that calls the real seed command twice and
asserts nothing a user could have changed was touched the second time.

The opposite trap is just as real: a seed that stops at "already exists" never delivers anything added to it later.
A demo event was seeded before its challenges existed; when challenges were added to the seed, production would
never have received them, because the event was already there. *Rule:* a seed **adds what is absent, matched on a
natural key (a title, a slug), and never touches what is present**. Test it against the state production is actually
in (delete the new parts, run the seed, check they arrive; run it again, check nothing changes), not only on an
empty database.

### Every item is a real object: add, edit, delete, reorder
A list isn't finished when you can only append. The question before calling it done: *"can someone fix a mistake in this
without going to `/admin/`?"* (A singleton fact doesn't need delete, but still needs edit.)

### Access control: a real Group, closed by default
For a private app: a plain auth `Group` created **by a migration** (so it exists the moment the app deploys); one function
decides access (authenticated AND in the group), used everywhere; superuser bypass is a *deliberate, named* exception in
the spec; non-members get a plain access-denied page unless the app must hide that it exists (then 404).

### Auth: reuse `User`, a lighter front door is fine
A new app doesn't get its own user table. A five-person invite-only app doesn't need email-verification ceremony: access
is gated by the Group. Build the app's own login-looking pages inside its own chrome, against the one shared `User`.

### Error pages stay inside the app's walls
Django has one set of error handlers for the whole project. An app with its own look still rendered the *main
site's* "forbidden" page, with the main site's header and language, for months. Every permission test passed,
because they checked for a 403, and a 403 is a 403 whichever page it shows. *Rule:* on day one, add the app's URL
prefix to the project's error dispatch (`handler403/404/500` composed by path), and have at least one test read
what an error page *says*.

### Two apps under one URL prefix
When a new app is mounted before an older one that shares its prefix, Django takes the **first** match. Claiming a
path the older app already owns is not an error, it is a silent takeover: an old QR code link started returning
404 and only the older app's own test, in a full test run, noticed. It happened twice. *Rule:* one test walks every
route of the older app and requires each to still resolve to it, with any deliberate takeover listed by name.

### One door to an irreversible action
"Publish the results" had its own careful screen, and a generic "next stage" button could also do it, skipping two
of the three things publishing has to do. *Rule:* an action that cannot be undone has exactly one code path; any
other way in redirects to it.

### A refusal never costs the person what they already typed
A form saved inside one transaction and stopped at the first problem, so ticking one box too early threw away two
fields typed beside it. *Rule:* save what is valid, collect the problems, then say what is wrong. Refusing one
thing must not cost the others.

### Times belong to a place
The server works in UTC, which is right for storing and wrong for showing: a 10:00 start in Israel printed as 07:00,
and a time typed into a form was read as UTC. The abbreviation "IST" then meant Israel to the organiser and India to
half the readers. *Rule:* render every page of something that has a place in that place's timezone (one wrapper
around `render`, not a line per view), read typed times in that zone, and name the zone by its city
("Jerusalem time").

### Process weight scales to the app's size
A multi-sprint product with strangers as users earns REQ-IDs and a test plan. A small private app keeps a `spec.md` and a
`backlog.md` as the two sources of truth, updated together, tests for whatever can break silently, informal sprints.
Decide explicitly per app.

### Deploy discipline
Dev first, always. Before pushing: run the app's tests, run `manage.py check`, smoke-test real pages against real data.
After pushing: verify the live site actually picked up the change with something the old build could not have shown
(a new CSS class, a new page), not just "the homepage loads". A transient 502 right after a push is usually the instance starting.

---

## BKM: giving an agent a key, without giving it the house

**The problem.** Some jobs can't be done from the UI by design (granting access, approving a request) and end up as "open
the admin on your phone and tick a box". The tempting fix, a general admin API key, is a skeleton key to a database shared
with other apps, and it will end up pasted in a chat transcript because that's how it reaches the agent.

**Build a key that is boring to steal.** The scope is fenced by the *code*, so the worst case is bounded by what the endpoint
can express, not by who holds the secret:

1. **One job per key.**
2. **Name the privileged thing in code, never in the request** (a caller passing `{"group": "staff"}` still gets the hard-coded group).
3. **Never create the principal**: grant access to accounts that already exist; refuse anything else.
4. **Never escalate**: no `is_staff`, no `is_superuser`, no password, no deleting accounts.
5. **Fail shut**: an unset env var means closed. Classic bug: empty expected value equals empty header, door open in exactly
   the environment nobody configured. (`/internal/run/<task>/` in this repo is the worked example, with the test.)
6. **Constant-time compare** (`django.utils.crypto.constant_time_compare`).
7. **Log every use**: who, how, when.
8. **Allow a superuser session as well as the token**, so the browsable API works and the endpoint still works if the env var was never set.

Write the tests for the refusals first; refusals should outnumber happy paths about two to one. That ratio is what makes it safe
to hand the token over. And say the quiet part to whoever holds it: the token travels to the agent, so it will sit in a transcript;
treat it as burnable (rotate by changing one env var) and be able to state the blast radius in one boring sentence.

---

## Mistakes we actually made, and the rules that came out of them

Several happened **more than once**, which is the strongest argument for writing them down: knowing the principle didn't stop us
repeating it.

1. **A substring is not an assertion.** `assert "/home/" not in body` failed on `/static/img/home/`; `"bj-state-shaky" in html` passed
   because the page *legend* carries the class name; a number matched inside "25 hands"; the `<title>` carried the text under test.
   *Rule:* assert on the thing, not text that happens to contain it. Check a link as `href="/home/"`; scope to the element
   (extract the `<tbody>` first). Ask where else the string could legitimately appear: legend, tooltip, attribute, asset path, another
   number, the page title.
2. **Test the surface a person touches.** A test clicked a *disabled* button three times to prove a double-tap counts once (clicking
   disabled dispatches nothing). A tap-target test flagged a 22 px checkbox inside a 48 px label (the label is what a thumb hits).
   `parseInt(getComputedStyle(el).animationDelay)` of `"0.16s"` is `0`. *Rule:* measure the effective thing; check units before parsing.
3. **A test that cannot fail is worse than none.** One "proved" a 40 % bias by counting calls to Python's RNG. *Rule:* ask what change to
   the product would make it fail; if none, delete it. Drive browser logic in a browser; don't reimplement it next to the test.
4. **Perturb the property, not the line.** Five times, breaking one guard changed nothing because a *second independent thing* also
   held the property (`read_only` field **plus** `perform_create` setting it; `answered` flag **plus** disabled buttons). *Rule:* find
   what else holds it; break both and confirm failure, or say plainly that two independent things hold it. (`notes` has exactly this.)
5. **When a perturbation proves nothing, suspect the perturbation.** Deleting `partial_update = update` changed nothing because DRF
   delegates anyway; a link added inside an empty `{% for %}` can't render. *Rule:* confirm the defect is reachable; if a guard is
   unreachable by any current input, write the test that constructs the input.
6. **Screenshot what you build, at least once.** A class defined twice made a front page render with 64 px tiles for four sprints,
   shipped to production twice, caught by no HTML-reading test. *Rule:* look at every screen as an image, at phone width, then write the
   *general* guard ("every tile is a real share of its container and its text fits") not the specific one.
7. **Namespace component classes.** Two meanings of `.card` collide silently by stylesheet order. Name after the component and prefix with the app.
8. **A page that POSTs needs a CSRF cookie.** A page that posts via `fetch` but renders no form never gets a `csrftoken` cookie, so every POST
   was refused and the retry queue dropped them as unfixable 4xx. *Rule:* `@ensure_csrf_cookie` (or render `{% csrf_token %}` / `data-csrf`
   as `notes` does), and pair "drop 4xx" retry logic with a test that something actually arrives.
9. **Don't run a formatter across a shared tree.** `ruff check --fix tests/` rewrote 55 files belonging to other sessions. *Rule:* scope
   every auto-fix to the files you are editing; `git status --short` before and after anything that writes many files; stage only your paths.
10. **Keep status honest, including about yourself.** Documents said OPEN about decided things; a turn ended "starting now" having built nothing.
    *Rule:* update status in the same commit that acts on a decision; never report intent as progress.
11. **Say "pre-existing" only after measuring.** A 242 px overflow was blamed on the nav drawer; the real cause was a hero rendering 1440 px in a
    1116 px column, found by comparing signed-in vs signed-out. *Rule:* prove it by removing your change; record numbers, not theories.
12. **Watch line endings when scripting edits.** A script rewrote `spec.md` with different endings and a one-line change became a 1,959-line diff.
    *Rule:* read with `newline=""`, write back the same ending, check `git diff --stat` (hundreds of lines for a one-line change = a flip).
13. **A class that styles nothing is silence, not an error.** `class="bj-btn-quiet"` didn't exist, three gold buttons shouted equally and one closed
    a shared link forever. *Rule:* test structurally that every class the markup uses is defined in the stylesheet, with deliberate exceptions named.
14. **Scope an assertion to the element, not the page** (see 1: the `<title>` is a hiding place too).
15. **Show the thing where the moment happens.** A note promised "every twenty hands" was stored and shown on a history page nobody opens
    mid-drill. *Rule:* for "after X the person gets Y", the test drives the screen where X happens and finds Y *there*.
16. **A rule applied to the case that prompted it is not yet a rule.** "Five columns is a thumb" was applied to one table and three others stayed
    ten columns wide for five sprints. *Rule:* when a principle lands, grep for every place it applies; write the test over the principle
    ("no cell outside a 390 px viewport"), not the instance.
17. **A guard that can't be tripped needs its own test.** (Added in this blueprint.) `tests/test_no_secrets_committed.py` includes a test that the
    scanner *would* catch a leak, otherwise a broken regex looks like a clean repo.

18. **Each feature's tests passing is not the same as the product working.** Six stretches of work on one app, each
    with its own passing tests; then one review that put every role side by side at every stage, on a phone, found
    seven real bugs and home screens that routed people correctly while telling them nothing about themselves.
    *Rule:* for any app with roles or stages, one test opens every link on every role's home, at every stage, as that
    role; and at each checkpoint, look at one image per stage with every role side by side.
19. **`|default:email` is a privacy leak.** Sign-up asked for no name, so public pages fell back to the email address
    and would have printed every participant's on a page that is public forever. The developer's own account had a
    name, so it looked fine. *Rule:* ask for a display name at sign-up; outside admin screens the fallback is a
    description ("A participant"), never contact details; test with a nameless user.
20. **Anything that changes data is POST, and redirects stay home.** Applying to an event happened on a page load,
    so a link preview or prefetch could apply someone; sign-up followed any `?next=` link to any site. *Rule:* POST
    only for changes; every redirect from a request parameter goes through `url_has_allowed_host_and_scheme`.
21. **When a fix does not show, suspect the server before the code.** Screenshots came back unchanged after a fix
    because the dev server was started with `--noreload`; browser tests failed in a full run because dev servers held
    their ports. *Rule:* screenshot against an auto-reloading server on its own port; stop your dev servers before a
    full test run.
22. **On Windows, don't push code through the shell.** Heredocs carrying Python or HTML with quotes failed again and
    again in Git Bash. A screenshot script that touched the database inside Playwright's sync API failed with
    `SynchronousOnlyOperation`. *Rule:* write the code to a file and run the file; in a screenshot script, do every
    database write before Playwright starts (or set `DJANGO_ALLOW_ASYNC_UNSAFE` for that script only).

23. **In a shared working copy, a commit is a release.** Several AI sessions worked in one folder, and "push" meant push
    everything. One session committed a finished feature and started the full test run it had promised before
    pushing; another session pushed first, and the feature reached the live site before that run had finished. Four
    failures from other sessions shipped the same way. *Rule:* when sessions share a working copy, commit only what
    you would ship right now, after its own tests pass; whoever pushes runs the full test run first and owns whatever
    it finds, including other sessions' work.

24. **A pipe hides a failure.** `pytest tests/x*.py | tail -1 && git commit ...` committed even though tests had
    failed: a pipe's exit status is its *last* command's, and `tail` succeeded. The same line threw away the names of
    the failures, and the file pattern matched nothing, so "run these tests" quietly became "run every test" (three
    hours). *Rule:* never chain an action after a piped test run; write the output to a file and act on the test
    command's own exit code; check that a file pattern actually matched something before passing it on.

25. **Nothing that runs at import may touch the persistent disk.** A storage module created its media folder when it
    was imported. The build step imports the code too, and the build has no persistent disk mounted, so the deploy
    failed. *Rule:* importing code never writes files or folders; create them the first time they are used, and treat
    a missing secret or a bad key as "fall back and log", never as a crash at import.

26. **Something added to the shared page frame needs the whole app's tests, not the sprint's.** A notification bell in
    the base template counted unread items for the signed-in person. On the one request that deletes the person's
    profile, the page then rendered with a profile that no longer existed, and crashed. The sprint's own tests never
    deleted anyone; an older test did. *Rule:* anything in the shared layout must survive every state of the person
    (signed out, not set up yet, just deleted on this request), and adding to it means running every test of the app
    before calling the sprint done.

27. **Colours made in code escape the colour checks.** The design tokens were checked for contrast, but a palette of
    book-spine colours lived in Python as data. It looked fine as large spines; a new screen used the same pairs for
    small text and two of them were unreadable (3.6:1). The browser check caught it only because that screen happened
    to show those pairs. *Rule:* every colour pair the code generates gets a unit test over the whole list, not only
    the pairs some screen happens to render.

28. **A count after a filter on the same relation counts the filtered rows.** In Django,
    `filter(members__profile=me).annotate(n=Count("members"))` shares one join between the filter and the count, so
    a group of three showed "1 members". The test group had one member, so the wrong number equalled the right one.
    *Rule:* annotate before filtering on the same relation, or filter with a subquery (`pk__in=...`), and test with
    at least two rows on that relation so the wrong number can show.

29. **Read the numbers on a screenshot against the data you seeded.** The browser check knows tap sizes, contrast
    and labels; it does not know the group you seeded has two members and three books. Two wrong numbers (the count
    above, and "nothing offered" on a page whose owner had offered two) were visible only to a person comparing the
    picture with the seed. *Rule:* when you look at a screenshot at the end of a sprint, read every number and every
    empty state on it against what the seeded world contains.

30. **Background work a person waits on must heal itself and always say where it is.** A shelf photo was read on a
    background thread inside the web process. Two deploys that day restarted the process, the threads died, and the
    scans sat as "reading" for good: a recovery command existed, but nothing was scheduled to call it, and nothing on
    the page said the work was lost. The owner found it by using the app ("it disappeared and nothing is waiting for
    me"). *Rule:* any job a person waits for (1) is recovered from the person's own page visits, not only from a
    scheduler, with a time limit and a cap on retries; (2) always ends in a state the person can see, including
    "failed, try again"; (3) leaves its result somewhere that keeps reminding them until they deal with it. And every
    deploy is a restart: test what happens to work that was in flight.

31. **A picker must offer every value the rest of the system stores.** A "what do you like" survey listed genres
    from a tree but filtered to the top level, so it offered six broad headings while the books, the
    recommendations and the saved answers all used the forty specific genres underneath. A saved "fantasy" could
    neither be chosen nor seen. The tests built answers in code, never through the form. *Rule:* for every choice
    list, test that it offers every value the stored data can hold, and that a saved answer shows as chosen.

32. **A setting that limits cost is not a limit until you have measured it.** A web-search feature was priced per
    search, so the code passed the AI API's "at most two tool calls" setting and budgeted on two. One real call ran
    three searches anyway: the setting did not bound that tool. Asking in the prompt for one search was obeyed once in
    three and then lost the data that mattered. The tests used a fake client, which obeys whatever the code assumes.
    *Rule:* before a cost estimate goes to the owner, make one real call and read the actual count and bill from the
    response; budget on the measured number, keep a hard daily cap in your own code, and never rely on the vendor's
    knob alone.

33. **On a phone, the content comes first; options fold.** Every list screen opened with a title, an explaining
    sentence, a row of five buttons and a four-field filter form. On the library screen not one book was visible
    without scrolling. The browser checks passed: nothing overflowed and every button was big enough to tap. They
    measured fit, not priority. The owner found it on his phone. *Rule:* on a phone, the main content of a list screen
    starts in the top half of the first screen (make it a test that measures the first row's position); one main
    action as an icon, the rest in a menu; search and filters behind one slim line that opens on tap and stays open
    when a filter is active; list rows of two lines, not cards; explaining sentences hidden on small screens.

34. **A real key in the developer's environment reaches the tests.** The AI key was set on the developer's machine,
    and the app turns its paid features on whenever a key exists. Each test file was meant to clear it; the ones that
    forgot could make real, billed calls, and the background threads those features start outlived browser tests and
    locked the test database. *Rule:* one shared test fixture blanks every paid key and switches off background work
    for all of the app's tests; a test that needs a key sets a fake one and replaces the client. Never rely on each
    test file remembering.

35. **Test the task on a phone, not only the pages.** A "start reading" feature passed every page check: the start
    page, the timer page and the summary each fitted, had labels and big enough buttons. The owner tried it on his
    phone and could not use it: his books were in a long drop-down with no search, and choosing one led to a second
    screen before any Start button appeared. No test had ever done the job itself. *Rule:* for every new flow, one
    browser test at phone size does what the person does, start to finish (type, tap, tap, see the result), and
    before shipping, walk it yourself with a realistic amount of data (forty books, not two).

36. **Detail pages: one main action on top; everything else folds, showing its value.** After the list screens were
    fixed, the detail pages still opened every form at once: one item's page was a single long form with every
    setting, another had its review and correction forms open, the home page stacked five big buttons under a large
    "0", and photo uploads showed the browser's raw "Choose File" box. It all worked; the owner called it "nice, not
    amazing." *Rule:* a detail page opens with what the thing is and its one main action. Every other form folds
    behind one line whose summary shows the current value, and opens by itself when it has an error or something
    active. Never show a raw file input: use a big labelled button that sends as soon as a photo is chosen. A zero is
    not a score: when there is nothing yet, say how to start.

37. **On a phone, a too-wide page hides from an overflow check.** A new page passed the browser check for "nothing
    wider than the screen" at phone size, and its screenshot came out 536px wide on a 390px phone. A mobile browser
    zooms out to fit a page that is too wide, and the page's measured width grows with it, so a check that compares
    elements to that width compares the page to itself and never fails. *Rule:* give the overflow check the device's
    real width and also fail when the whole document is wider than it (`document.documentElement.scrollWidth`). In
    CSS, a grid column that holds a sideways-scrolling strip needs `minmax(0, 1fr)` and children with `min-width: 0`.
    And keep reading the screenshots: that is what caught it.

38. **In a right-to-left language, check anything with a direction or a sign by eye.** A page-turning wheel passed
    its browser tests (dragging forward raised the page number, dragging back stopped at the first page), and its
    screenshot still showed two bugs: in Hebrew its ruler placed the pages ahead on the right, so a forward drag
    pulled the next page away from the middle, and the "−1" button read "1−". Tests read values; they do not see
    which way things move or where a minus sign lands in right-to-left text. *Rule:* lay out any widget with a
    direction (ruler, slider, carousel, page turn) from the reader's side, so in Hebrew or Arabic what is ahead comes
    from the left; give any label that is a signed number or a range `dir="ltr"`; and check both on a right-to-left
    screenshot before shipping.

39. **A ring drawn with a radial mask needs `closest-side`.** A progress ring passed its tests (the element was in
    the page, its percentage and label were right) and was invisible on the screenshot. In CSS,
    `radial-gradient(circle, ...)` sizes the circle to the box's farthest corner, about 1.41 times the radius, so a
    mask stop at 90% falls outside the box and hides everything. Tests read the markup and the numbers, not what is
    painted. *Rule:* rings and donuts made with a radial mask use `radial-gradient(circle closest-side, ...)` so the
    percentages are of the real radius, and every new drawn shape is checked on a screenshot.

40. **A timer counts only while its screen is in front; a sheet opens without the keyboard.** A reading timer kept
    counting after the owner left the screen, and opening a "my thoughts" sheet popped the phone keyboard although he
    meant to speak. Both followed the request to the letter and missed how a phone is actually held: put down, picked
    up, switched away from, spoken to. *Rule:* a clock that measures a person's activity pauses when its screen is
    hidden or left (`visibilitychange` and `pagehide`, with `navigator.sendBeacon` to tell the server) and resumes on
    return, and the server subtracts the pauses. A sheet or dialog never focuses a text field when it opens (on a
    phone that opens the keyboard); focus the likely first action instead, and when voice input is offered, put the
    microphone first.

41. **Watch a deploy on the site, not by hammering an API.** A deploy check said "no deployment" for fifteen minutes.
    The loop polled the GitHub Deployments API every 20 seconds without a token, ran through GitHub's 60 anonymous
    requests an hour, and read the rate-limit error as an empty answer. Another session had also pushed on top, so
    the deployment to watch belonged to a different commit anyway. *Rule:* confirm a deploy by asking the live site
    for something only the new code has (a class in the CSS, a string in a script) every 20 to 30 seconds; use an
    API at most once to find the deployment, and check every API answer for an error before reading it as a state.

42. **Test at the narrowest phones, not one convenient width.** On the owner's phone every page was a little wider
    than the screen and slid left and right. All phone checks ran at 390px, where the header just fitted; it needed
    about 380px, so on 360px and 375px phones (most Android phones, many iPhones) the whole page grew wider. The
    header had gained one item at a time, and each passed at 390. *Rule:* run the phone checks at 320, 360, 375 and
    412 as well, and measure the header on its own; keep a phone header to three or four items and move the rest
    (language, sign out) to settings; and as a safety net set `html, body { overflow-x: clip }`, which, unlike
    `hidden`, does not break sticky headers.

43. **A question that hides when the data is known never shows once automation fills the data.** The owner asked to
    be asked how many pages a book has whenever he starts one. It was built to appear only when the catalogue did not
    know; an automatic lookup had already filled a count, so he was never asked and could not correct a wrong count.
    The tests passed because their books were blank. *Rule:* when the person asks to be asked, always ask, filled in
    with what is known, and keep a different answer as theirs alone instead of overwriting shared data. Test such a
    question with the data the automation would have filled, not only with blanks.

44. **Every way of pointing: a finger, a mouse, a wheel.** On a computer, dragging a shelf of books with the mouse
    moved the books instead of the shelf. On a phone a swipe is the browser's own scrolling and a long press picks
    an item up; a mouse has no swipe, so the drag fell through to "pick up". The tests used a phone, or a mouse only
    to pick items up. *Rule:* test a widget that scrolls or drags with each pointer it will meet: a finger on a
    phone, a mouse drag and the scroll wheel on a computer. With a mouse, let a drag pan and holding still pick up,
    the same gesture as a long press on a phone.

45. **Never measure an image while drawing a page.** A page read each image's width and height from the image
    file to lay out a shelf. With the files in cloud storage, every visit fetched every image just to measure it.
    *Rule:* store an image's width and height in the database when the image is made, and never read
    `ImageField.width` or `.height` (or open the file) while rendering; a test can make that access fail so it
    never comes back.

46. **Whoever sees a mistake in shared data needs a way to fix it.** The owner found a wrong title on a record
    and could not change it: direct edits were open to staff and to whoever had typed the record in by hand, but
    most records were created automatically, so almost nobody could fix them, only file a suggestion that waited for
    a curator. *Rule:* let the people closest to a shared record (here, anyone who holds a copy of the item) fix it
    directly, and keep every direct change with its old value as an accepted correction, so curators can see it and
    put it back. When the people are trusted and the change is reversible, gate by a trail, not by a permission.

47. **A safety net can blind the check it backs up.** Pages were set to clip sideways overflow as a safety net, and
    the phone-width test kept measuring the document's scroll width, which the clip keeps equal to the screen. A new
    page then grew wider than the phone and the test still passed; only a screenshot caught it. *Rule:* when you add a
    safety net that hides a failure, move the check to where the net cannot reach (here, every element's own position
    against the screen width, skipping the parts that scroll on purpose), give it content that would push (a long
    list), and prove the check by running it once against the bug before trusting it.

48. **One app's whole test suite is a full regression too.** The owner's rule was: run the tests for what you
    changed, and the full regression only when asked. The agent read "full regression" as the site-wide suite, so it
    ran one app's entire suite (about 20 minutes) before nearly every push for two days, slowing every change. *Rule:*
    any whole suite counts, whether site-wide or one app's. After a change run the tests you changed, the guards and the
    browser checks for the screens you touched, then ship; run a whole suite at most twice a day, or when asked.

49. **Walk the newcomer's road as the newcomer, from the link to the first screen that pays off.** An invite
    feature had a test for every page and none for the invited person's road through them: the welcome page barely
    named the inviter, sign-in and the first form said nothing, a survey stood between joining and the friend's
    shelf, the newcomer got a different theme than the inviter, and the payoff screen looked empty because its
    pictures were still loading. The owner found it by walking his own link. *Rule:* for every way a new person can
    arrive, one browser test walks the whole road as that person, with a fresh account and a newcomer's defaults, and
    checks the payoff screen with its data actually loaded; build the road so each step names the reason to go on.

50. **Image work inside the web process: decode small, a few at a time, let go.** A background job re-reading photos
    decoded each 4000px image two or three times at once, 25 photos in a row, inside the single web worker; the host
    restarted the service for exceeding its memory. *Rule:* decode at the size you need (JPEG draft mode), close what
    you open, collect garbage after each item, take a few items per pass, keep one API client per process, and watch
    the host's memory graph after shipping such a job.

51. **Many small private images go to the browser from storage, not through the one web worker.** Twenty small
    pictures per page each streamed from the bucket through the single sync worker, one after another, so the page
    looked empty for seconds. *Rule:* sign links for the rest of the day (the same link all day, so browsers cache
    them) and let the browser fetch from the bucket in parallel; keep the app's endpoint only as the disk fallback;
    and while a picture loads, show the text it will replace.

52. **Count what a person did as they do it, not when they close it.** A reading timer wrote a sitting's time only
    when "done" was pressed and counted the day's streak only then; the owner read ten minutes, left the screen, and
    got nothing. What people do is leave: lock the phone, switch apps, put the book down. *Rule:* save progress as it
    accrues (a heartbeat every minute or two, and the moment the screen is left) and count from what is saved, so a
    closed app or a forgotten button never loses it; and make the closing button say it is only a break, with the
    reassurance that the time is kept.

53. **Test a browser API with the events the real device sends, not the ones the spec describes.** Voice notes added
    each update's final speech results to a running text. Correct by the spec, but Android Chrome resends results it
    already finalized on every update, and they grow ("I think", "I think this", "I think this book"), so every
    thought was written three or four times. The test's fake recognizer sent one clean result and passed. *Rule:* a
    fake for a device API plays back what the worst supported device really sends; and code reading a stream of
    updates rebuilds the whole from each update instead of adding to a running total.

54. **When a fact starts being written earlier, find everyone who read its absence as an event.** A celebration screen
    appeared when a request found a day "not counted before, counted after". A fix that counted the day earlier (a
    heartbeat while the user was still active) meant the request almost always found it counted already, and the
    celebration silently stopped. No test failed, because the tests never sent a heartbeat first. *Rule:* when a
    change writes something sooner or more often, search for every place that inferred an event from its absence and
    give the event its own definition; test the event along the new path too.

55. **Build an image feature against made-up photos with known answers, from a real camera.** Judge it on photos
    it was not tuned on. A cover-straightening feature had no real samples. The first generated angles were a turn
    plus a shear rather than a real camera, and the proportion formula, correct for a real camera, looked wrong on
    them; with a true 3D projection it was right almost every time. *Rule:* generate test photos whose answer is
    known with the physics of the real thing (camera projection, real-looking surfaces, something in the way),
    measure every change on one set, keep a second set aside for the verdict, keep a small set in the test suite,
    and look at the failures as pictures with the true answer drawn over the guess before changing anything.

56. **A screen test stubs every outside source, keyless ones too.** A screen test of an "add a book" page searched a
    public books API for real (no key needed, so the "blank the paid key" guard did not apply). One day the API
    rate-limited, the lookup thread was still writing at teardown, and four unrelated screen tests failed with
    "database table is locked". *Rule:* a module that drives real pages stubs every outside source in its autouse
    fixture, keyed or not; a test of the source itself replaces the stub with its own fake.

57. **The control follows the shape of the decision, not the word the person used.** The owner asked for
    "checkboxes" on every row (show, give, lend, sell); four boxes went in side by side. He came back: one box for
    show, and under it one small menu of how the item is offered, because showing is a gate and the way of offering
    is one choice at a time. *Rule:* before drawing a row of controls, write the decision as the person makes it:
    a gate is a box, one choice among several is a menu, only "many at once" is a row of boxes; and remove a
    control that sat on the row for another reason once the row's job changes.

58. **JSON inside a script tag is HTML too.** A page embedded user data as `{{ data|safe }}` inside a
    `<script type="application/json">`. `json.dumps` escapes quotes but not `<`, so a record named
    `</script><img onerror=...>` closed the block and ran in every viewer's browser. *Rule:* JSON that lands in a
    `<script>` is written with `<`, `>` and `&` as JSON escapes (one `script_json` helper, or Django's `json_script`);
    `|safe` on anything a person wrote is a finding until proven otherwise; the test puts `</script>` in a title.

59. **Members' markdown is cleaned after rendering, not trusted.** Forum posts and comments were rendered with a
    markdown library and marked safe; markdown passes raw HTML through, so a `<script>` ran for every reader,
    staff included. *Rule:* HTML made from a person's text goes through an allowlist sanitizer (nh3, bleach) before
    it is marked safe; author-only content may keep its HTML, and that exception is written down.

60. **Run the security sweep before saying "secure".** A review found its issues with a short list of searches,
    not insight: `|safe` and `mark_safe` (who wrote the text?); `json.dumps` into a page (is `<` escaped?);
    `csrf_exempt` and `AllowAny` (what gate replaces the one removed?); `redirect(request.GET["next"])` (validated
    against the host?); `==` on a secret (constant-time, fail shut when unset); the public media folder (anything
    private under it gets its own folder and a checking view); every paid API call (who can reach it, from how many
    accounts, with what daily cap per person and site-wide: instant signup plus an uncapped paid call is a bill
    with no ceiling); every login form (failures counted and locked, django-axes covers them all); public write
    endpoints (per-address throttle); headers (CSP, nosniff, frame options); and the tree for key shapes.
    *Rule:* keep the list, run it at every launch, and write a failing test for each finding before fixing it.

61. **A new form control runs the narrowest-phone test the day it ships.** A select went out with 14px text; on an
    iPhone any field under 16px zooms the page in when touched, then the page slides sideways: a failure an earlier
    rule had already closed. The sprint ran its own tests, not the all-widths phone sweep that enforces the rule,
    which caught it a day later in another sprint. *Rule:* any change that adds a field, select or text box runs the
    narrow-phone sweep before it ships; a rule enforced by a sweep is only enforced when the sweep runs.

62. **"Sent" is what the mail backend said, not what the code hoped.** A screen told an admin "sent" for access
    mails that never left: the send used `fail_silently=True` inside a `try` that returned `True`, so a refused send
    read as success. A second screen that granted the same access sent no mail at all, and the client was pointed
    at it without anyone walking it first. *Rule:* show "sent" only from the backend's answer (`send_mail` returns how
    many went); test a refused send and check the screen says so; route every way of granting access through the one
    function that also sends the mail; and before pointing a person at a screen, walk it as them, to the mail in
    their inbox.

63. **Mark each item handled by its id; never infer "handled" from time.** An AI agent answering client mail on a
    timer counted a mail as new only if it was later than its own last reply in the thread. A mail that arrived while
    it was still working was older than the reply it then sent, so it was skipped for hours. Its heartbeat, written
    only when a run started, also went stale during a long job, and the watchdog reported a busy agent as dead.
    *Rule:* a worker on a queue writes down the ids it takes at the start and marks each one done (a mail label, a
    status column) only after the work is really done; "new" means "not marked". A heartbeat beats while busy too,
    or the watchdog cries wolf and the real alarm gets ignored.

64. **A one-time link lets its own holder back in, and every door that grants access sends the mail.** A
    patient's one-time sign-in link checked "used or expired" before "is this already theirs", so the person who
    opened their own link twice (a refresh, a back button) was refused. And the first path that granted a role
    created the invitation and sent no mail, because the mail function was written a sprint later. The refusal
    tests, written first, caught both. *Rule:* ownership first, validity second: the owner coming back is a quiet
    success, and the second visit is tested for the owner and for a stranger. Every path that grants access,
    including the first one built, goes through the one function that also sends the mail, and a test counts the
    mails per path. Two browser-test notes: a page's inner text carries the stylesheet's upper-casing, so compare
    lower-case; and a list of languages written in their own scripts is not the page's language, so leave option
    labels out of an "English only" check.

65. **A middleware is placed by what it reads; a sweep knows its own alphabet; a row of tap targets is sized by
    the thumb.** A middleware that read a session key was put first in the chain out of habit, before the session
    and the user existed, and silently did nothing until three tests said so. The same day, the "every class the
    markup uses is defined" sweep failed on a class with an underscore its regex did not allow, and a chart put
    eight 34px teeth in a row on a 320px phone. *Rule:* a middleware that reads the session or the user goes after
    the session and authentication middleware, with one test asserting through a real request that the state
    reached the view; a sweep over names matches the alphabet the stylesheet allows (letters, digits, `-`, `_`);
    and when a row of targets does not fit the width at 44px each, it scrolls in its own box rather than shrinking.

66. **A page in another language than the site prints its dates in the site's language.** An English app on a
    site whose default language is Hebrew showed comment dates with Hebrew month names. The "every screen is
    English" test passed, because the pages it read had no comments, so no date was on them. *Rule:* an app whose
    language differs from the site's default switches its own language on in its base template, for the whole
    page; and the language test puts every kind of localised value on the page first (a date, a number, a
    plural), because an empty page proves nothing about them.

67. **A grid item needs both a row and a column, and a track needs `minmax(0, ...)`.** Two grid bugs, each passed
    by every test and caught only by a screenshot. Two items given the same `grid-row` and no column made the grid
    open a second, implicit column, and a card fell apart into two. A one-column grid whose track was plain `1fr`
    grew to fit a long `git clone` line and an unbroken link, and the page slid sideways at every width. *Rule:*
    when you place a grid item explicitly, place it on both axes (`grid-area: 1 / 1`); size tracks with
    `minmax(0, 1fr)` and give children `min-width: 0`; let long commands scroll in their own box and long links
    break. Then look at the screenshot: markup tests cannot see layout.

68. **A change of content is a screen, not a deploy.** To swap one picture on a live card, the AI prepared a data
    migration so the next deploy would replace it, then proposed an API token so it could call the live API itself.
    The owner stopped both: content belongs to whoever owns it, and they need a screen for it. *Rule:* every piece
    of content a site shows has an edit screen in the site for its owner (for content only the owner edits, a form
    only they see), covering every field, pictures included. A deploy is for code; a migration seeds day one and
    never changes content after it. Asked to change content, point the owner to the screen, or build the screen.

69. **Poll from the oldest unfinished item, and say what the work is doing.** A chat page polled for "messages
    after the newest one on screen". When the person sent a second message while the first answer was still being
    built, the first answer finished later and was never asked for again: it said "Building" forever, and the person
    asked how to know it was not stuck. *Rule:* a page that polls a list asks from its oldest unfinished item, and a
    test finishes an older item after a newer one exists. Long work shows its current step in words, how long it has
    been running (counted from the server's clock, since a phone's clock can be off), and a line once it is slower
    than usual; whatever is ready shows as soon as it is ready.

70. **A heavy outside program gets a whole-group kill, a memory ceiling and a recipe.** *Rule:* when an app runs
    an outside program, start it in its own process group, kill the whole group at the time limit, and give it a
    memory ceiling well below the server's; a test proves a child of the program dies too. Time the heavy but common
    request, not only the simple one. When an AI is told "avoid X", also tell it the fast way to do what X does. A
    long job keeps a log the person can open: each step, when, and what failed.

71. **A live update moves everything that depends on it.** *Rule:* when a page updates something without a
    reload, list every control that depends on it and update them all. The browser test uses that control after the
    live update, not after a reload, and checks that no id is used twice on the page.

72. **A test that needs the real function keeps it before the fixtures stub it.** *Rule:* when a test file
    replaces a function for every test, a test that must reach the real one keeps a reference to it at import time.
    A cached lookup never keeps an empty answer.

*Add new entries here as you make them, and a line in [lessons_log.md](lessons_log.md).*
