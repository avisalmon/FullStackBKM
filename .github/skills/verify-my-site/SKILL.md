---
name: verify-my-site
description: >
  Check that the owner built everything correctly: run scripts/verify_site.py against the repository, the local site
  and the live site, explain every line, fix FAILs, decide on WARNs, and certify graduation (no FAIL, tests pass, a
  restore practised, the owner can explain their data model). TRIGGER: "verify", "did I do it right", "check my site",
  "is it working", "is my site safe", "health check", "audit", "graduate", "am I done", "smoke test", "checklist".
---

# Verify my site

Tool: [scripts/verify_site.py](../../../scripts/verify_site.py). Read-only: GET requests plus one POST that is supposed to be refused.

```
python scripts/verify_site.py                                   # this repository
python scripts/verify_site.py --url http://127.0.0.1:8000       # + the local site
python scripts/verify_site.py --url https://<live-host>         # + the live site
```

Run it with the venv interpreter (`.\env\Scripts\python.exe` on Windows, `env/bin/python` elsewhere). Exit code 1 means at least one FAIL.

## Walk the owner through the output

Each line is **PASS**, **WARN** (worth fixing, not a blocker; the owner may decide otherwise) or **FAIL** (fix before telling anyone), plus a fix hint. Don't just paste the output: say what each check protects and why it matters.
It checks: `.env`/`env/` not tracked and git-ignored; no key-shaped strings in files; GitHub repo is private; pre-commit installed; site renamed; local `SECRET_KEY` set; `/healthz`; home page; static files; sign-in pages; DEBUG off (note: DEBUG on is expected and fine on a local server);
the scheduled-task endpoint refuses callers without a token; the cost page is not public; HTTPS redirect and HSTS; privacy headers and cookie flags; the privacy policy page and whether it is still a DRAFT; whether Google sign-in is configured.

## Graduation (say it out loud when true)

- [ ] `verify_site.py --url https://<live-host>` shows **no FAIL**
- [ ] `pytest -q` passes
- [ ] a restore has been practised ([backups-and-restore](../backups-and-restore/SKILL.md))
- [ ] the owner can explain in their own words what their data model is and why its main relationship exists (ask them; this is the real test, see [data-model-coach](../data-model-coach/SKILL.md))

When you add a feature that has a checkable property, add a check to `scripts/verify_site.py` and a test in `tests/test_verify_site.py`.
