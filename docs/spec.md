# Site spec

> This file is **your site's** spec. Claude fills it in with you during the interview
> (the `build-my-site` skill, Phase 1). The blueprint's own documentation is in
> [README.md](../README.md) and [docs/README.md](README.md).

## 0. What this site is

_(Written together with Claude: one paragraph in plain words. Who it's for, what problem it solves, what it is **not**.)_

## 1. Architecture (given by the blueprint, do not rewrite)

* Django 5.2 on Render, gunicorn, WhiteNoise; SQLite on a persistent disk (`/var/data`); media on the same disk.
* Sign-in: email + password and Google (django-allauth). `core` holds site-level pages; every feature area is its own app
  ([building_an_app.md](building_an_app.md)).
* Ops: health check, scheduled backups (+ offsite to GCS), cost report, error alerts by email.

## 2. Apps

| App | Path | One-line purpose | Docs |
|---|---|---|---|
| notes (example) | `/notes/` | Demonstrates the methodology; delete when done | [notes/](notes/spec.md) |

## 3. Decisions log

_(Date, decision, why. Append as you go.)_
