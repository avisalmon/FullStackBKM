from django.contrib import admin

from .models import AIUsage, ConsentRecord, CostRecord


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


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    """History only: records are added, not edited, so the trail stays trustworthy."""

    list_display = ("recorded_at", "user", "kind", "version", "granted", "source", "recorded_by")
    list_filter = ("kind", "granted", "source")
    readonly_fields = ("recorded_at",)
