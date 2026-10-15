"""OpenAI access with a meter and two safety limits.

    from core.ai import call_openai
    result = call_openai([{"role": "user", "content": "Hi"}], user=request.user, feature="chat")
    result["content"]   # the reply, or an explanation when blocked / not configured

Three behaviours worth knowing before you build on this (docs/procedures/openai.md):

* No OPENAI_API_KEY -> STUB mode: nothing is sent anywhere, a canned reply comes back, and
  the site still works. Local development and CI never spend money.
* A monthly spend cap (OPENAI_MONTHLY_COST_CAP_USD) and a per-person daily token limit
  (OPENAI_DAILY_TOKEN_LIMIT_PER_USER) are checked BEFORE every call. A runaway loop or one
  heavy user hits a wall instead of your credit card. Set the provider-side spend limit
  too: this meter only counts calls made through this function.
* Every successful call is written to AIUsage, which feeds the cost report (core/costs.py).

Calls use plain `requests`, so there is no SDK to pin and tests can stub one function.
"""

import logging
from decimal import Decimal

import requests
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone

from .models import AIUsage

logger = logging.getLogger(__name__)

CHAT_URL = "https://api.openai.com/v1/chat/completions"

# USD per 1M tokens (input, output). APPROXIMATE and will drift - check
# https://openai.com/api/pricing and edit. Unknown models are costed at the most
# expensive entry so the cap errs on the side of stopping early.
PRICES_PER_MTOK = {
    "gpt-4o-mini": (Decimal("0.15"), Decimal("0.60")),
    "gpt-4o": (Decimal("2.50"), Decimal("10.00")),
}

STUB_REPLY = "[AI is in stub mode. Set OPENAI_API_KEY to enable real answers.]"


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> Decimal:
    rate_in, rate_out = PRICES_PER_MTOK.get(model) or max(PRICES_PER_MTOK.values())
    return (rate_in * prompt_tokens + rate_out * completion_tokens) / Decimal(1_000_000)


def _month_start():
    return timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def month_spend() -> Decimal:
    total = AIUsage.objects.filter(created_at__gte=_month_start()).aggregate(t=Sum("cost_usd"))["t"]
    return total or Decimal("0")


def tokens_used_today(user) -> int:
    midnight = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    sums = AIUsage.objects.filter(user=user, created_at__gte=midnight).aggregate(
        p=Sum("prompt_tokens"), c=Sum("completion_tokens")
    )
    return (sums["p"] or 0) + (sums["c"] or 0)


def _result(content, model, prompt=0, completion=0, *, stub=False, blocked=""):
    return {
        "content": content,
        "model": model,
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "stub": stub,
        "blocked": blocked,
    }


def call_openai(messages, *, user=None, feature="", model=None, system_prompt=""):
    model = model or settings.OPENAI_DEFAULT_MODEL

    cap = Decimal(str(settings.OPENAI_MONTHLY_COST_CAP_USD))
    if cap > 0 and month_spend() >= cap:
        logger.warning("OpenAI monthly cap reached (%s); call refused", cap)
        return _result("AI is paused: the monthly budget has been reached.", model, blocked="cap")

    authenticated = user is not None and getattr(user, "is_authenticated", False)
    limit = settings.OPENAI_DAILY_TOKEN_LIMIT_PER_USER
    if authenticated and limit > 0 and tokens_used_today(user) >= limit:
        return _result("Daily AI limit reached. It resets at midnight UTC.", model, blocked="daily")

    if not settings.OPENAI_API_KEY:
        return _result(STUB_REPLY, model, stub=True)

    payload_messages = (
        [{"role": "system", "content": system_prompt}] if system_prompt else []
    ) + list(messages)
    try:
        response = requests.post(
            CHAT_URL,
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            json={"model": model, "messages": payload_messages, "max_tokens": 1024},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"] or ""
        usage = data.get("usage", {})
        prompt, completion = usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
    except Exception:  # noqa: BLE001 - a model having a bad afternoon must not cost a request
        logger.exception("OpenAI call failed")
        return _result(
            "Sorry, the AI service had a problem. Please try again.", model, blocked="error"
        )

    AIUsage.objects.create(
        user=user if authenticated else None,
        feature=feature,
        model=model,
        prompt_tokens=prompt,
        completion_tokens=completion,
        cost_usd=estimate_cost(model, prompt, completion),
    )
    return _result(content, model, prompt, completion)
