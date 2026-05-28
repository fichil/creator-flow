import importlib.util
import json
import socket
import urllib.request
from dataclasses import asdict
from typing import Callable

from app.providers.douyin.adapter import SANDBOX_OPERATION_REFERENCES
from app.providers.douyin import DouyinRealAdapter, DouyinSandboxAdapter


SENSITIVE_FIELD_NAMES = {
    "access_token",
    "refresh_token",
    "client_secret",
    "authorization_code",
    "oauth_state",
    "api_key",
    "credential",
    "cookie",
    "session",
    "bearer",
    "password",
    "secret",
}

FAKE_ENVIRONMENT_VALUES = [
    "fake-batch2-douyin-access-value",
    "fake-batch2-douyin-client-secret-value",
    "fake-batch2-douyin-api-key-value",
    "fake-batch2-oauth-state-value",
    "fake-batch2-authorization-code-value",
    "fake-batch2-cookie-value",
    "fake-batch2-session-value",
]


def test_douyin_sandbox_operations_return_deterministic_simulated_success():
    adapter = DouyinSandboxAdapter()

    for operation_name, operation in iter_adapter_operations(adapter):
        result = operation()
        result_dict = asdict(result)
        result_text = json.dumps(result_dict, sort_keys=True)

        assert result.provider_id == "douyin_sandbox"
        assert result.source_type == "sandbox"
        assert result.is_real_provider is False
        assert result.operation == operation_name
        assert result.operation_status == "simulated_success"
        assert result.simulation_reference == SANDBOX_OPERATION_REFERENCES[operation_name]
        assert result.simulation_reference.startswith("sandbox_")
        assert result.dry_run is True
        assert result.simulation_details == {
            "provider": "douyin_sandbox",
            "source": "sandbox",
            "mode": "sandbox",
            "outcome": "simulated",
            "dry_run": True,
            "external_call": False,
        }
        assert "sandbox" in result_text
        assert "simulated" in result_text
        assert "dry-run" in result_text or '"dry_run": true' in result_text
        assert result.external_call_performed is False
        assert result.credential_read_performed is False
        assert result.token_read_performed is False
        assert result.token_write_performed is False
        assert_result_has_no_sensitive_exact_keys(result_dict)


def test_douyin_real_operations_remain_blocked_not_simulated_success():
    adapter = DouyinRealAdapter()

    for operation_name, operation in iter_adapter_operations(adapter):
        result = operation()
        result_dict = asdict(result)

        assert result.provider_id == "douyin_real"
        assert result.source_type == "real"
        assert result.is_real_provider is True
        assert result.operation == operation_name
        assert result.operation_status in {"blocked", "not_implemented"}
        assert result.operation_status != "simulated_success"
        assert result.simulation_reference is None
        assert result.simulation_details == {}
        assert result.external_call_performed is False
        assert result.credential_read_performed is False
        assert result.token_read_performed is False
        assert result.token_write_performed is False
        assert_result_has_no_sensitive_exact_keys(result_dict)


def test_sandbox_operations_do_not_trigger_http_or_sdk_calls(monkeypatch):
    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("unexpected external service call")

    monkeypatch.setattr(socket, "create_connection", fail_if_called)
    monkeypatch.setattr(urllib.request, "urlopen", fail_if_called)

    if importlib.util.find_spec("requests") is not None:
        import requests

        monkeypatch.setattr(requests.sessions.Session, "request", fail_if_called)

    if importlib.util.find_spec("httpx") is not None:
        import httpx

        monkeypatch.setattr(httpx.Client, "request", fail_if_called)
        monkeypatch.setattr(httpx.AsyncClient, "request", fail_if_called)

    for _operation_name, operation in iter_adapter_operations(DouyinSandboxAdapter()):
        result = operation()
        assert result.external_call_performed is False


def test_sandbox_operations_do_not_read_sensitive_environment_values(monkeypatch):
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", FAKE_ENVIRONMENT_VALUES[0])
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", FAKE_ENVIRONMENT_VALUES[1])
    monkeypatch.setenv("DOUYIN_API_KEY", FAKE_ENVIRONMENT_VALUES[2])
    monkeypatch.setenv("OAUTH_STATE", FAKE_ENVIRONMENT_VALUES[3])
    monkeypatch.setenv("AUTHORIZATION_CODE", FAKE_ENVIRONMENT_VALUES[4])
    monkeypatch.setenv("DOUYIN_COOKIE", FAKE_ENVIRONMENT_VALUES[5])
    monkeypatch.setenv("DOUYIN_SESSION", FAKE_ENVIRONMENT_VALUES[6])

    for _operation_name, operation in iter_adapter_operations(DouyinSandboxAdapter()):
        result_text = json.dumps(asdict(operation()), sort_keys=True)
        for fake_value in FAKE_ENVIRONMENT_VALUES:
            assert fake_value not in result_text


def test_sandbox_operation_references_are_stable_fake_values():
    assert SANDBOX_OPERATION_REFERENCES == {
        "start_oauth": "sandbox_oauth_start_001",
        "handle_oauth_callback": "sandbox_oauth_callback_001",
        "exchange_token": "sandbox_exchange_001",
        "refresh_token": "sandbox_refresh_001",
        "revoke_token": "sandbox_revoke_001",
        "disconnect": "sandbox_disconnect_001",
        "fetch_metrics": "sandbox_metrics_001",
        "prepare_publish": "sandbox_prepare_001",
        "upload_video": "sandbox_video_001",
        "publish_video": "sandbox_publish_001",
        "schedule_publish": "sandbox_schedule_001",
    }


def iter_adapter_operations(adapter) -> list[tuple[str, Callable[[], object]]]:
    return [
        ("start_oauth", adapter.start_oauth),
        ("handle_oauth_callback", adapter.handle_oauth_callback),
        ("exchange_token", adapter.exchange_token),
        ("refresh_token", adapter.refresh_token),
        ("revoke_token", adapter.revoke_token),
        ("disconnect", adapter.disconnect),
        ("fetch_metrics", adapter.fetch_metrics),
        ("prepare_publish", adapter.prepare_publish),
        ("upload_video", adapter.upload_video),
        ("publish_video", adapter.publish_video),
        ("schedule_publish", adapter.schedule_publish),
    ]


def assert_result_has_no_sensitive_exact_keys(payload) -> None:
    assert collect_keys(payload).isdisjoint(SENSITIVE_FIELD_NAMES)


def collect_keys(payload) -> set[str]:
    if isinstance(payload, dict):
        keys = set(payload)
        for value in payload.values():
            keys.update(collect_keys(value))
        return keys
    if isinstance(payload, list):
        keys = set()
        for value in payload:
            keys.update(collect_keys(value))
        return keys
    return set()
