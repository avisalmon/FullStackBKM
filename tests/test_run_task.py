import pytest

URL = "/internal/run/{}/"

pytestmark = pytest.mark.django_db


@pytest.fixture
def armed(settings):
    settings.TASK_TRIGGER_TOKEN = "s3cret-token"
    return {"HTTP_X_TASK_TOKEN": "s3cret-token"}


def test_fails_shut_when_no_token_is_configured(client, settings):
    settings.TASK_TRIGGER_TOKEN = ""
    # The classic bug: an empty expected value equals an empty header.
    assert client.post(URL.format("costs")).status_code == 403
    assert client.post(URL.format("costs"), HTTP_X_TASK_TOKEN="").status_code == 403


def test_wrong_token_is_refused(client, armed):
    assert client.post(URL.format("costs"), HTTP_X_TASK_TOKEN="nope").status_code == 403


def test_get_is_not_allowed(client, armed):
    assert client.get(URL.format("costs"), **armed).status_code == 405


def test_only_listed_tasks_run(client, armed):
    assert client.post(URL.format("migrate"), **armed).status_code == 404
    assert client.post(URL.format("flush"), **armed).status_code == 404


def test_costs_task_runs_and_reports(client, armed):
    response = client.post(URL.format("costs"), **armed)
    assert response.status_code == 200
    assert "TOTAL" in response.json()["log"]


def test_failing_task_is_a_500_so_the_cron_turns_red(client, armed, monkeypatch):
    from core import views

    monkeypatch.setitem(views.TASKS, "costs", "no_such_command")
    assert client.post(URL.format("costs"), **armed).status_code == 500
