# AI features with OpenAI

All AI goes through one function, `core.ai.call_openai`, so there is one place that meters,
limits and stubs it. Use it; do not call the OpenAI API from views directly.

```python
from core.ai import call_openai

result = call_openai(
    [{"role": "user", "content": question}],
    user=request.user,  # per-person daily limit + attribution
    feature="recipe-helper",  # shows up in the usage log
    system_prompt="You are ...",
)
result["content"]  # the reply, or a human-readable reason when blocked
result["blocked"]  # "" | "cap" | "daily" | "error"
result["stub"]  # True when no key is configured
```

A working example is `POST /ai/chat/` (`core.views.ai_chat`): signed-in only, JSON in and out.

## Safety model (why you can leave this running)

| Layer | What it does |
|---|---|
| **Stub mode** | No `OPENAI_API_KEY` -> nothing leaves the machine. Local dev and CI never spend |
| **Monthly cap** | `OPENAI_MONTHLY_COST_CAP_USD` (default $20). Checked *before* each call; reached -> calls are refused |
| **Per-person daily limit** | `OPENAI_DAILY_TOKEN_LIMIT_PER_USER` (default 50,000 tokens per UTC day) |
| **Failing open for the user** | A provider error returns a friendly message and records no cost; it never raises into a page |
| **Metering** | Every success writes an `AIUsage` row (admin: `/admin/core/aiusage/`) which feeds [cost_monitoring.md](cost_monitoring.md) |

The meter only counts calls made through `core.ai`. **Also set a spend limit on OpenAI's side**
(below) so a leaked key cannot run up a bill.

## Setup (humans)

1. Account at https://platform.openai.com; add a payment method and a small prepaid balance.
2. **Settings -> Limits**: set a monthly budget and an alert threshold. Do this first.
3. **API keys -> Create new secret key**, ideally a *project* key restricted to what you need. Copy it once.
4. Put it in local `.env` as `OPENAI_API_KEY` and on Render (Environment). Never in git, never in chat.
5. Optional: an *admin* key (`sk-admin-...`, scope `api.usage.read`) as `OPENAI_ADMIN_KEY`
   lets the cost report show real organisation-wide spend instead of only what this site metered.

## Practical notes

* Pricing in `core/ai.py` (`PRICES_PER_MTOK`) is approximate; check https://openai.com/api/pricing
  and edit it. Unknown models are costed at the dearest rate so the cap stops early rather than late.
* Models get renamed and retired; if calls start failing, change `OPENAI_DEFAULT_MODEL` in Render.
* Calls are synchronous with a 30 s timeout inside a gunicorn worker (`--timeout 120`). For long
  jobs (batch grading, big documents), run them from a management command, not a request.
* If users can upload images/text for the AI to read, add content moderation first (OpenAI's moderation
  endpoint is free). The reference site gates every upload and chat message that way; see backlog.
* Tests must never reach OpenAI. They don't: the key is empty in tests, and `tests/test_ai.py`
  stubs `requests.post`. Keep it that way.
