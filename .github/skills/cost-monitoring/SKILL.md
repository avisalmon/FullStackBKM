---
name: cost-monitoring
description: >
  Monitor and control what the site costs: the monthly cost report (Render, OpenAI, Google Cloud Storage, domain,
  email), budget alerts by email, pinning real invoice figures, provider-side spend limits, adding a new service to
  the report, and explaining the bill. TRIGGER: "cost", "costs", "how much", "bill", "budget", "spending",
  "expensive", "invoice", "pricing", "monthly cost", "spend limit", "report_costs".
---

# Cost monitoring

Source of truth: [docs/procedures/cost_monitoring.md](../../../docs/procedures/cost_monitoring.md). Re-read it first.

## Three layers (explain them to the owner)

1. **Provider-side limits** (owner, once): OpenAI monthly budget and alerts; GCP budget alert (Billing -> Budgets & alerts); Render plan visible in Billing.
2. **In-app caps:** OpenAI monthly cap and per-person daily token limit ([openai-ai-features](../openai-ai-features/SKILL.md)).
3. **The report:** `python manage.py report_costs` (add `--notify` to email `OWNER_EMAIL` when over `MONTHLY_BUDGET_USD`), the staff page `/ops/costs/`, and Admin -> Cost records. The scheduled workflow runs it daily.

## What to do

* Set `MONTHLY_BUDGET_USD` (ask the owner what they are comfortable with) and `OWNER_EMAIL` on Render. Typical baseline: Render ~$7.25 + domain ~$1 + AI (capped) = $8-10/month.
* Run `report_costs` (`render_api.py job --command "python manage.py report_costs"`) and explain each row's **source**: *live* (provider API), *estimate* (computed or metered here), *manual* (a human pinned it).
* When a real invoice differs: open the record in the admin, type the real amount, set Source = Manual; the automatic run never overwrites manual records.
* Keep `RENDER_MONTHLY_USD` and `DOMAIN_YEARLY_USD` accurate when the plan, disk or domain changes.
* **Add a service** (e.g. a new paid API): subclass `CostAdapter` in `core/costs.py`, add it to `ADAPTERS`, add a test. A failing adapter reports 0 with the reason and never breaks the report.
* A surprising number is a question, not a verdict: check the provider's own dashboard before concluding anything, and say what is estimated.
