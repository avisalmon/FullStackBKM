from django.conf import settings
from django.db import models


class AIUsage(models.Model):
    """One row per successful AI call: the on-site meter behind the daily per-person token
    limit and the monthly spend cap (core/ai.py)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    feature = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=60)
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.model} {self.prompt_tokens + self.completion_tokens} tokens"


class CostRecord(models.Model):
    """What one service cost in one month (core/costs.py).

    `source` says how much to trust the number: `live` came from the provider's own API,
    `estimate` was computed here, `manual` was typed in by a human in the admin and is
    never overwritten by the automatic run.
    """

    LIVE, ESTIMATE, MANUAL = "live", "estimate", "manual"
    SOURCES = [(LIVE, "Live"), (ESTIMATE, "Estimate"), (MANUAL, "Manual")]

    service = models.CharField(max_length=40)
    period = models.CharField(max_length=7, help_text="YYYY-MM")
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    source = models.CharField(max_length=10, choices=SOURCES, default=ESTIMATE)
    note = models.CharField(max_length=300, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period", "service"]
        constraints = [
            models.UniqueConstraint(fields=["service", "period"], name="one_cost_per_service_month")
        ]

    def __str__(self):
        return f"{self.service} {self.period}: ${self.amount_usd}"
