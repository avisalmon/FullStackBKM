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


class ConsentRecord(models.Model):
    """A recorded decision to agree (or withdraw), kept as history, never edited.

    Infrastructure for consent of any kind: terms of service, a guardian agreeing for a young
    person, opting in to emails. The *gate* (who must consent to what before using what) is a
    product decision per app; see docs/privacy.md. `source` says who actually gave it, because a
    parent's consent and a user's own click are different facts.
    """

    SELF, GUARDIAN, ADMIN = "self", "guardian", "admin"
    SOURCES = [
        (SELF, "The person themselves"),
        (GUARDIAN, "Parent/guardian"),
        (ADMIN, "Entered by staff"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    kind = models.CharField(
        max_length=50, help_text="e.g. terms, privacy, guardian, marketing-email"
    )
    version = models.CharField(max_length=20, blank=True, help_text="Which text they agreed to")
    granted = models.BooleanField(default=True, help_text="False records a withdrawal")
    source = models.CharField(max_length=10, choices=SOURCES, default=SELF)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    note = models.CharField(max_length=300, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-recorded_at", "-id"]

    def __str__(self):
        return f"{self.user_id} {self.kind} {'granted' if self.granted else 'withdrawn'}"
