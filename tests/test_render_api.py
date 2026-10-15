import importlib.util
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render_api", ROOT / "scripts" / "render_api.py")
render_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render_api)


def test_logs_query_is_owner_scoped_and_windowed():
    now = datetime(2026, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
    params = render_api.logs_params("tea-1", "srv-1", 15, now=now)
    assert params["ownerId"] == "tea-1"
    assert params["resource"] == "srv-1"
    assert (params["startTime"], params["endTime"]) == (
        "2026-01-02T11:45:00Z",
        "2026-01-02T12:00:00Z",
    )


def test_secrets_are_refused_as_arguments():
    parser = render_api.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["env-set", "--service", "srv-1", "KEY", "--value", "hunter2"])


def test_env_set_without_a_safe_source_exits(monkeypatch):
    args = render_api.build_parser().parse_args(["env-set", "--service", "srv-1", "KEY"])
    with pytest.raises(SystemExit):
        args.func(args)


def test_missing_api_key_is_a_clear_error(monkeypatch, tmp_path):
    monkeypatch.delenv("RENDER_API_KEY", raising=False)
    monkeypatch.setattr(render_api, "__file__", str(tmp_path / "scripts" / "render_api.py"))
    with pytest.raises(SystemExit) as info:
        render_api.load_key()
    assert "RENDER_API_KEY" in str(info.value)


def test_services_lists_the_live_url_so_a_newcomer_can_open_the_site(monkeypatch, capsys):
    fake = [
        {"service": {"id": "srv-1", "name": "my-site", "type": "web_service",
                     "serviceDetails": {"url": "https://my-site-ab12.onrender.com"}}},
        {"service": {"id": "srv-2", "name": "worker", "type": "background_worker"}},
    ]  # fmt: skip
    monkeypatch.setattr(render_api, "call", lambda *a, **k: fake)
    render_api.cmd_services(None)
    out = capsys.readouterr().out
    assert "srv-1" in out and "https://my-site-ab12.onrender.com" in out
    assert "srv-2" in out  # a service with no URL is still listed
