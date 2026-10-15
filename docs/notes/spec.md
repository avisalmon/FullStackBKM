# Notes (example app) - spec

**Purpose:** a deliberately tiny app that demonstrates the blueprint's app methodology end to end.
Copy its shape for your own apps; delete it when you're done ([removal steps](../new_site_checklist.md#removing-the-example-notes-app)).

## What it is

A signed-in person keeps private notes, each with a title, optional text and an optional picture.
Nobody else can see or change them.

## Decisions (and the rule each demonstrates)

| Decision | Rule |
|---|---|
| Notes are database rows (`Note`), the picture is a file under `MEDIA_ROOT` | Rule 1, media on the persistent disk |
| Only a foreign key to the shared `User`; nothing else touches other apps | Rule 2 |
| Own layout `notes/base.html`, own CSS with `notes-` prefix, no link back to the site | Rule 3, mistake 7 |
| Docs live in `docs/notes/` incl. a separate `data_model.md` | Rule 4 |
| Full CRUD API at `/notes/api/notes/` (DRF); the page is one consumer | Rule 6 |
| Queryset scoped to the owner; owner never client-supplied | refusals-first tests |
| Page built with `fetch` + `textContent` (no innerHTML), CSRF token in `data-csrf` | mistake 8 |

## Scope

In: create, list, edit (API), delete, image upload. Out: sharing, tags, search, rich text.

## Access

Signed-in only. Anonymous API calls get 403; the page redirects to login. Staff can see everything in `/admin/`.
