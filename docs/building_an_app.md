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

*Add new entries here as you make them, and a line in [lessons_log.md](lessons_log.md).*
