from django.contrib import admin

from .models import AIUsage, CostRecord


@admin.register(AIUsage)
class AIUsageAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "user",
        "feature",
        "model",
        "prompt_tokens",
        "completion_tokens",
        "cost_usd",
    )
    list_filter = ("model", "feature")
    date_hierarchy = "created_at"


@admin.register(CostRecord)
class CostRecordAdmin(admin.ModelAdmin):
    """Set `source` to Manual and type the real figure to pin it: the automatic run
    never overwrites a manual record."""

    list_display = ("period", "service", "amount_usd", "source", "note", "updated_at")
    list_filter = ("period", "service", "source")
