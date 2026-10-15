from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from core import ai
from core.models import AIUsage

pytestmark = pytest.mark.django_db


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


OK = {
    "choices": [{"message": {"content": "hello there"}}],
    "usage": {"prompt_tokens": 100, "completion_tokens": 50},
}


@pytest.fixture
def live(settings, monkeypatch):
    """A configured key and a recorded, never-real network call."""
    settings.OPENAI_API_KEY = "sk-test"
    calls = []

    def fake_post(url, **kwargs):
        calls.append(kwargs)
        return FakeResponse(OK)

    monkeypatch.setattr(ai.requests, "post", fake_post)
    return calls


def test_without_a_key_it_is_stub_mode_and_spends_nothing(settings, alice, monkeypatch):
    settings.OPENAI_API_KEY = ""
    monkeypatch.setattr(
        ai.requests, "post", lambda *a, **k: pytest.fail("network used in stub mode")
    )
    result = ai.call_openai([{"role": "user", "content": "hi"}], user=alice)
    assert result["stub"] is True
    assert AIUsage.objects.count() == 0


def test_a_real_call_is_metered(live, alice):
    result = ai.call_openai([{"role": "user", "content": "hi"}], user=alice, feature="chat")
    assert result["content"] == "hello there"
    row = AIUsage.objects.get()
    assert (row.user, row.feature, row.prompt_tokens, row.completion_tokens) == (
        alice,
        "chat",
        100,
        50,
    )
    assert row.cost_usd > 0
    assert live[0]["headers"]["Authorization"] == "Bearer sk-test"


def test_monthly_cap_stops_calls_before_they_are_made(live, settings, alice):
    settings.OPENAI_MONTHLY_COST_CAP_USD = 1
    AIUsage.objects.create(model="gpt-4o", cost_usd=Decimal("1.5"))
    result = ai.call_openai([{"role": "user", "content": "hi"}], user=alice)
    assert result["blocked"] == "cap"
    assert live == []  # no request left the building


def test_daily_limit_is_per_person(live, settings, alice, bob):
    settings.OPENAI_DAILY_TOKEN_LIMIT_PER_USER = 100
    AIUsage.objects.create(user=alice, model="gpt-4o-mini", prompt_tokens=100)
    assert ai.call_openai([{"role": "user", "content": "x"}], user=alice)["blocked"] == "daily"
    assert ai.call_openai([{"role": "user", "content": "x"}], user=bob)["blocked"] == ""


def test_provider_failure_returns_a_message_and_records_nothing(settings, alice, monkeypatch):
    settings.OPENAI_API_KEY = "sk-test"

    def boom(*a, **k):
        raise ConnectionError("down")

    monkeypatch.setattr(ai.requests, "post", boom)
    result = ai.call_openai([{"role": "user", "content": "x"}], user=alice)
    assert result["blocked"] == "error"
    assert AIUsage.objects.count() == 0


def test_unknown_models_are_costed_at_the_dearest_rate():
    assert ai.estimate_cost("mystery", 1_000_000, 0) == ai.estimate_cost("gpt-4o", 1_000_000, 0)


def test_chat_endpoint_requires_login():
    assert APIClient().post("/ai/chat/", {"message": "hi"}, format="json").status_code == 403


def test_chat_endpoint_works_in_stub_mode(alice, settings):
    settings.OPENAI_API_KEY = ""
    client = APIClient()
    client.force_authenticate(alice)
    response = client.post("/ai/chat/", {"message": "hi"}, format="json")
    assert response.status_code == 200
    assert response.json()["stub"] is True
    assert client.post("/ai/chat/", {"message": ""}, format="json").status_code == 400
