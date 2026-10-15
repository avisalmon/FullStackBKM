import io
from decimal import Decimal

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.crypto import constant_time_compare
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.static import serve
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import ai, costs
from .models import CostRecord


def home(request):
    return render(request, "core/home.html")


def healthz(request):
    """Render's health check. No database, no auth: it answers 'is the process up'."""
    return JsonResponse({"status": "ok"})


def robots_txt(request):
    private = ["/admin/", "/accounts/", "/notes/", "/ops/", "/internal/"]
    body = "User-agent: *\n" + "".join(f"Disallow: {p}\n" for p in private)
    return HttpResponse(body, content_type="text/plain")


def media_serve(request, path):
    """Serve uploaded media.

    Reads MEDIA_ROOT at request time (not import time) so it follows settings overrides,
    and works with DEBUG=False, unlike django.conf.urls.static.static().
    """
    return serve(request, path, document_root=settings.MEDIA_ROOT)


def not_found(request, exception=None):
    return render(request, "404.html", status=404)


def server_error(request):
    return render(request, "500.html", status=500)


# --- machine endpoint for scheduled jobs ------------------------------------------------

# The privileged thing is named here in code, never taken from the request: a caller can only
# pick from this list, and cannot pass arguments (docs/building_an_app.md, "a key, without
# giving it the house").
TASKS = {"backup": "backup_db", "costs": "report_costs"}


@csrf_exempt
@require_POST
def run_task(request, task):
    """POST /internal/run/<task>/ with header X-Task-Token. Called by GitHub Actions cron.

    Runs inside the web service because only it can see the SQLite disk (a separate Render
    cron container cannot). Fails shut: with TASK_TRIGGER_TOKEN unset it answers 403 to all.
    """
    expected = settings.TASK_TRIGGER_TOKEN
    provided = request.headers.get("X-Task-Token", "")
    if not expected or not constant_time_compare(provided, expected):
        return JsonResponse({"ok": False, "error": "forbidden"}, status=403)
    command = TASKS.get(task)
    if command is None:
        return JsonResponse({"ok": False, "error": "unknown task"}, status=404)
    out = io.StringIO()
    try:
        call_command(command, stdout=out, stderr=out)
    except Exception as exc:  # noqa: BLE001 - surface the failure so the Actions run turns red
        return JsonResponse({"ok": False, "error": str(exc), "log": out.getvalue()}, status=500)
    return JsonResponse({"ok": True, "log": out.getvalue()})


# --- AI chat: the smallest useful consumer of core.ai -----------------------------------


@api_view(["POST"])
def ai_chat(request):
    """POST /ai/chat/ {"message": "..."} -> {"reply": "...", "blocked": ""}. Signed-in only."""
    message = str(request.data.get("message", "")).strip()
    if not message or len(message) > 4000:
        return Response({"error": "message is required (max 4000 characters)"}, status=400)
    result = ai.call_openai(
        [{"role": "user", "content": message}],
        user=request.user,
        feature="chat",
        system_prompt="You are a helpful assistant.",
    )
    return Response(
        {"reply": result["content"], "blocked": result["blocked"], "stub": result["stub"]}
    )


# --- staff-only cost page ----------------------------------------------------------------


@staff_member_required
def costs_page(request):
    period = costs.current_period()
    records = list(CostRecord.objects.filter(period=period))
    total = sum((r.amount_usd for r in records), Decimal("0"))
    return render(
        request,
        "core/costs.html",
        {
            "period": period,
            "records": records,
            "total": total,
            "budget": settings.MONTHLY_BUDGET_USD,
            "adapters": costs.ADAPTERS,
        },
    )
