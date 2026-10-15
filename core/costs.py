"""Monthly cost monitoring: one adapter per paid service.

    python manage.py report_costs            # print this month, store it, check the budget
    python manage.py report_costs --notify   # also email OWNER_EMAIL when over budget

Each adapter reports one service's spend and says how much to trust it:
  live      from the provider's own API
  estimate  computed here (flat plan price, or metered by this site)
  manual    typed into the admin by a human - never overwritten by this run

An adapter that fails reports 0 with the reason in `note`; one weak adapter never breaks the
report. Add your own service by subclassing CostAdapter and listing it in ADAPTERS.
"""

import logging
import os
from decimal import Decimal

import requests
from django.conf import settings
from django.utils import timezone

from . import ai
from .models import CostRecord

logger = logging.getLogger(__name__)

GCS_FREE_GB = Decimal("5")  # "Always Free" Standard storage (US regions); verify for yours
GCS_USD_PER_GB = Decimal("0.020")


def current_period() -> str:
    return timezone.now().strftime("%Y-%m")


class CostAdapter:
    service = ""
    label = ""
    deep_link = ""

    def fetch(self, period: str) -> tuple[Decimal, str, str]:
        """Return (amount_usd, source, note)."""
        raise NotImplementedError

    def safe_fetch(self, period: str) -> tuple[Decimal, str, str]:
        try:
            amount, source, note = self.fetch(period)
            return Decimal(str(amount)).quantize(Decimal("0.01")), source, note
        except Exception as exc:  # noqa: BLE001
            logger.warning("cost adapter %s failed: %s", self.service, exc)
            return Decimal("0.00"), CostRecord.ESTIMATE, f"unavailable: {exc}"


class RenderAdapter(CostAdapter):
    service, label = "render", "Render"
    deep_link = "https://dashboard.render.com/billing"

    def fetch(self, period):
        amount = Decimal(str(settings.RENDER_MONTHLY_USD))
        return amount, CostRecord.ESTIMATE, "flat plan + disk price (RENDER_MONTHLY_USD)"


class OpenAIAdapter(CostAdapter):
    service, label = "openai", "OpenAI"
    deep_link = "https://platform.openai.com/usage"

    def fetch(self, period):
        admin_key = os.environ.get("OPENAI_ADMIN_KEY", "")
        if admin_key and period == current_period():
            try:
                return self._live(admin_key), CostRecord.LIVE, "OpenAI Costs API (org-wide)"
            except Exception as exc:  # noqa: BLE001 - fall back to the on-site meter
                logger.warning("OpenAI Costs API failed, using on-site meter: %s", exc)
        return ai.month_spend(), CostRecord.ESTIMATE, "metered by this site (core.ai)"

    @staticmethod
    def _live(admin_key):
        start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        response = requests.get(
            "https://api.openai.com/v1/organization/costs",
            headers={"Authorization": f"Bearer {admin_key}"},
            params={"start_time": int(start.timestamp()), "bucket_width": "1d", "limit": 31},
            timeout=20,
        )
        response.raise_for_status()
        total = Decimal("0")
        for bucket in response.json().get("data", []):
            for result in bucket.get("results", []):
                total += Decimal(str((result.get("amount") or {}).get("value") or 0))
        return total


class GCSAdapter(CostAdapter):
    service, label = "gcs", "Google Cloud Storage"
    deep_link = "https://console.cloud.google.com/storage/browser"

    def fetch(self, period):
        from .gcs import Bucket

        bucket = Bucket.from_env()
        if bucket is None:
            return Decimal("0"), CostRecord.ESTIMATE, "not configured"
        gb = Decimal(bucket.total_bytes()) / Decimal(1024**3)
        cost = max(Decimal("0"), gb - GCS_FREE_GB) * GCS_USD_PER_GB
        return cost, CostRecord.ESTIMATE, f"{gb:.2f} GB stored; first {GCS_FREE_GB} GB free"


class DomainAdapter(CostAdapter):
    service, label = "domain", "Domain name"
    deep_link = ""

    def fetch(self, period):
        yearly = Decimal(str(settings.DOMAIN_YEARLY_USD))
        return yearly / 12, CostRecord.ESTIMATE, "DOMAIN_YEARLY_USD / 12"


class ResendAdapter(CostAdapter):
    service, label = "resend", "Resend (email)"
    deep_link = "https://resend.com/overview"

    def fetch(self, period):
        return Decimal("0"), CostRecord.ESTIMATE, "free tier assumed; pin the real figure in admin"


ADAPTERS = [RenderAdapter(), OpenAIAdapter(), GCSAdapter(), DomainAdapter(), ResendAdapter()]


def run_all(period: str | None = None) -> list[CostRecord]:
    """Refresh every adapter's record for `period`, leaving manual records alone."""
    period = period or current_period()
    records = []
    for adapter in ADAPTERS:
        record, _ = CostRecord.objects.get_or_create(service=adapter.service, period=period)
        if record.source != CostRecord.MANUAL:
            record.amount_usd, record.source, record.note = adapter.safe_fetch(period)
            record.save()
        records.append(record)
    return records


def over_budget(records) -> tuple[bool, Decimal]:
    total = sum((r.amount_usd for r in records), Decimal("0"))
    budget = Decimal(str(settings.MONTHLY_BUDGET_USD))
    return (budget > 0 and total > budget), total
