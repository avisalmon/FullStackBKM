# The documentation, and where each thing lives

If you are looking for something and this file does not name it, the file is in the wrong place.

## Start here

| File | What it is |
|---|---|
| [../README.md](../README.md) | How to clone and begin. One page. |
| [new_site_checklist.md](new_site_checklist.md) | The whole journey, phase by phase, with who does what (Claude / you) |
| [security.md](security.md) | What protects you and the few things only you can do |
| [../tutorial/index.html](../tutorial/index.html) | **Learn first**: how a Django site works, then data models and relationships (interactive, works offline) |
| [design_guide.md](design_guide.md) | Practical design advice and the review checklist Claude uses on every screen |

## How we build

| File | What it is |
|---|---|
| [building_an_app.md](building_an_app.md) | **The authority for building anything new**: six core rules, the kickoff sequence, the mistakes behind the rules. A living file: add to it as you learn |
| [spec.md](spec.md), [backlog.md](backlog.md) | Your site's spec and backlog (filled in with Claude) |
| [notes/](notes/spec.md) | The example app's spec, data model and backlog: copy this shape |

## Procedures (how to *do* things)

| File | When you need it |
|---|---|
| [deploy_to_render](procedures/deploy_to_render.md) | First deploy, everyday loop, smoke test |
| [debug_failed_deploy](procedures/debug_failed_deploy.md) | Anything went red. Logs first |
| [gotchas](procedures/gotchas.md) | 30 proven traps, numbered |
| [env_vars](procedures/env_vars.md) | Every setting and where it goes |
| [auth_google_oauth](procedures/auth_google_oauth.md) | Google sign-in |
| [email_resend](procedures/email_resend.md) | Real email |
| [custom_domain_dns](procedures/custom_domain_dns.md) | Your own domain |
| [openai](procedures/openai.md) | AI features, caps, metering |
| [gcs_bucket](procedures/gcs_bucket.md) | Google Cloud Storage: offsite backups, big media |
| [backup_restore](procedures/backup_restore.md) | Backups, schedule, restore |
| [cost_monitoring](procedures/cost_monitoring.md) | Never be surprised by a bill |
| [rollback](procedures/rollback.md) | Undo a bad deploy |
| [cicd](procedures/cicd.md) | CI, branch policy, pre-push checklist |

## For the blueprint's maintainer

[blueprint_roadmap.md](blueprint_roadmap.md): what is verified, what is not, what was deliberately left out.
