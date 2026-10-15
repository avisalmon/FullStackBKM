# Monitoring costs

You should never be surprised by a bill. Three layers:

1. **Provider-side limits** (set once, humans): OpenAI monthly budget + alerts; GCP budget alert
   (Billing -> Budgets & alerts); Render shows your plan in Billing.
2. **In-app caps**: OpenAI monthly cap and per-person daily token limit ([openai.md](openai.md)).
3. **The cost report** (this page): one view of everything.

## The report

```powershell
python manage.py report_costs            # refresh + print this month
python manage.py report_costs --notify   # also email OWNER_EMAIL when over MONTHLY_BUDGET_USD
```

Staff-only page: `/ops/costs/`. Records live in Admin -> Cost records.
`.github/workflows/scheduled-tasks.yml` runs `report_costs` daily (set `MONTHLY_BUDGET_USD` and
`OWNER_EMAIL` and it becomes an alert).

| Service | Source | How it's computed |
|---|---|---|
| Render | estimate | `RENDER_MONTHLY_USD` (default 7.25 = Starter $7 + 1 GB disk $0.25). Change it with your plan/disk |
| OpenAI | estimate, or live with `OPENAI_ADMIN_KEY` | Sum of the site's own `AIUsage` meter; live = OpenAI Costs API |
| GCS | estimate | Bucket size via the API; cost above the free allowance |
| Domain | estimate | `DOMAIN_YEARLY_USD / 12` |
| Resend | estimate | 0 (free tier assumed) |

**Pin the truth**: when a real invoice differs, open the record in the admin, type the real amount and
set Source = *Manual*. The automatic run never overwrites a manual record.

## Adding a service

Subclass `CostAdapter` in `core/costs.py` (`service`, `label`, `deep_link`, `fetch(period) -> (amount, source, note)`),
add it to `ADAPTERS`, add a test. A failing adapter reports 0 with the reason in the note; it can't break the rest.

## Typical monthly cost

Render $7.25 + domain ~$1 + OpenAI (whatever you allow, capped) + GCS ~$0. About **$8-10/month** plus AI usage.
