---
name: openai-ai-features
description: >
  Add AI features to the site through the metered OpenAI helper (core.ai): account and spend limit, API key, stub
  mode, monthly cap, per-user daily token limit, usage logging, building features on call_openai, testing without
  spending money, and AI privacy. TRIGGER: "openai", "chatgpt", "ai", "gpt", "llm", "chatbot", "ai assistant", "api
  key", "token limit", "ai costs", "summarize with ai", "generate text", "moderation".
---

# AI features with OpenAI

Source of truth: [docs/procedures/openai.md](../../../docs/procedures/openai.md). Re-read it first.

All AI goes through **one function**, `core.ai.call_openai(messages, user=..., feature=..., system_prompt=...)`: it meters every call, enforces the limits, and returns a stub when no key is configured. Never call the OpenAI API directly from a view.
Example consumer: `POST /ai/chat/`.

## Who does what

**The owner (first, before any key exists):** create an OpenAI account, add a small prepaid balance, **set a monthly budget and alert in OpenAI's Limits**, then create a project API key and put it in `.env`. Optional: an `sk-admin-...` key as `OPENAI_ADMIN_KEY` so the cost report reads real org-wide spend.

**You:** set `OPENAI_API_KEY` on Render (`env-set --from-env`), keep the defaults (`OPENAI_MONTHLY_COST_CAP_USD=20`, `OPENAI_DAILY_TOKEN_LIMIT_PER_USER=50000`) unless the owner chooses otherwise, call `/ai/chat/` as a signed-in user, confirm an `AIUsage` row appeared
(`/admin/core/aiusage/`) and that `report_costs` shows it.

## Building a feature

Use `call_openai` and read `result["blocked"]` (`""`, `cap`, `daily`, `error`) and `result["stub"]`; show the human-readable `content` when blocked. Long jobs belong in a management command, not a request (gunicorn timeout 120 s).
**Tests must never reach OpenAI**: the suite blanks the key and stubs `requests.post`. Add a test per feature with a fake response.

## Privacy and safety (advise; the owner decides, [privacy-advisor](../privacy-advisor/SKILL.md))

Don't send secrets or children's personal details to the provider; check OpenAI's current API data-use terms; name OpenAI in the policy (generated automatically when a key is set); consider disabling free-form AI for under-18s; if users upload text or images for the AI to read,
add content moderation (OpenAI's moderation endpoint is free); don't log full prompts; AI conversations you store are personal data (export, erase, retain briefly). Update the price table in `core/ai.py` and `OPENAI_DEFAULT_MODEL` when OpenAI changes models.
