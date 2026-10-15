from decimal import Decimal

import pytest
from django.core import mail
from django.core.management import call_command

from core import costs
from core.models import AIUsage, CostRecord

pytestmark = pytest.mark.django_db


def amounts():
    return {r.service: r for r in CostRecord.objects.filter(period=costs.current_period())}


def test_run_all_records_every_service(settings):
    settings.RENDER_MONTHLY_USD = 7.25
    costs.run_all()
    records = amounts()
    assert set(records) == {"render", "openai", "gcs", "domain", "resend"}
    assert records["render"].amount_usd == Decimal("7.25")


def test_openai_cost_comes_from_the_on_site_meter(monkeypatch):
    monkeypatch.delenv("OPENAI_ADMIN_KEY", raising=False)
    AIUsage.objects.create(model="gpt-4o", cost_usd=Decimal("3.456"))
    costs.run_all()
    assert amounts()["openai"].amount_usd == Decimal("3.46")


def test_a_manual_record_is_never_overwritten(settings):
    costs.run_all()
    CostRecord.objects.filter(service="render").update(amount_usd=Decimal("99"), source="manual")
    settings.RENDER_MONTHLY_USD = 1
    costs.run_all()
    assert amounts()["render"].amount_usd == Decimal("99")


def test_one_failing_adapter_does_not_break_the_report(monkeypatch):
    def boom(self, period):
        raise RuntimeError("api down")

    monkeypatch.setattr(costs.RenderAdapter, "fetch", boom)
    costs.run_all()
    assert "unavailable: api down" in amounts()["render"].note
    assert "openai" in amounts()


def test_report_is_idempotent():
    costs.run_all()
    costs.run_all()
    assert CostRecord.objects.count() == 5


def test_over_budget_sends_one_alert_only_with_notify(settings):
    settings.MONTHLY_BUDGET_USD = 1
    settings.ADMINS = [("Owner", "owner@example.com")]
    call_command("report_costs", verbosity=0)
    assert mail.outbox == []
    call_command("report_costs", notify=True, verbosity=0)
    assert len(mail.outbox) == 1
    assert "over the $1 budget" in mail.outbox[0].body


def test_zero_budget_never_alerts(settings):
    settings.MONTHLY_BUDGET_USD = 0
    settings.ADMINS = [("Owner", "owner@example.com")]
    call_command("report_costs", notify=True, verbosity=0)
    assert mail.outbox == []


def test_costs_page_is_staff_only(client, alice, django_user_model):
    assert client.get("/ops/costs/").status_code == 302
    client.force_login(alice)
    assert client.get("/ops/costs/").status_code == 302  # signed in but not staff
    staff = django_user_model.objects.create_user(
        "boss", "b@example.com", "pw-boss-123", is_staff=True
    )
    client.force_login(staff)
    assert client.get("/ops/costs/").status_code == 200
