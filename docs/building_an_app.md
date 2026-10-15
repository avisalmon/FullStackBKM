# Building an app on this site

The methodology, distilled from building a real multi-app production site. It is a **living file**:
when you learn something while building, add it here (in the section it fits, or a new one), and say
*what happened and why it mattered*. A rule without the failure behind it gets ignored the next time
someone is in a hurry.

An "app" here means a Django app that is one feature area of the site: its own folder, models, URLs,
templates, docs. The example is [notes/](../notes/) with docs in [docs/notes/](notes/spec.md). Copy its shape.

---

## Core rules (strong defaults)

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
- [ ] Models + migrations (`makemigrations --check` clean)
- [ ] DRF serializers + viewsets + router, permission and queryset scoping tested (the refusals first)
- [ ] Own base template; classes prefixed with the app name
- [ ] Pages built on the API (fetch + DOM), not hand-rolled JSON views
- [ ] Admin registration
- [ ] Tests: refusals, happy paths, and a seed command run **twice** if there is one
- [ ] Looked at every screen as an image at least once, at phone width
- [ ] Deploy discipline below

---

## Practices that came from real mistakes

### Data: seeding is one-time only
A seed command that imports from a static file must **check whether the data exists and leave it alone if so**.
On the reference site, a seed command ran on every deploy and wholesale deleted and recreated rows from a JSON
snapshot; the moment a person could edit those rows, every deploy would have destroyed their edits.
The database, once populated, is the only source of truth. Write a test that calls the real seed command twice and
asserts nothing a user could have changed was touched the second time.

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

*Add new entries here as you make them.*
