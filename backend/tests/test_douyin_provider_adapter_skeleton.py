import importlib.util
import json
import socket
import urllib.request
from dataclasses import asdict
from typing import Callable

from app.main import app
from app.providers.douyin import DouyinRealAdapter, DouyinSandboxAdapter
from app.providers.douyin.boundary import DouyinAdapterOperationResult


SENSITIVE_RESULT_FIELD_NAMES = {
    "access_token",
    "refresh_token",
    "token",
    "token_value",
    "api_key",
    "secret",
    "secret_value",
    "client_secret",
    "oauth_client_secret",
    "authorization_code",
    "state_value",
    "oauth_state_value",
    "callback_payload",
    "credential_material",
    "encrypted_credential",
    "raw_request",
    "raw_response",
    "raw_payload",
    "private_key",
    "oauth_code",
    "password",
    "bearer_token",
    "session_cookie",
}


BLOCKED_STATUSES = {"blocked", "not_implemented"}


def test_douyin_sandbox_adapter_skeleton_metadata_is_blocked():
    adapter = DouyinSandboxAdapter()

    assert adapter.provider_id == "douyin_sandbox"
    assert adapter.source_type == "sandbox"
    assert adapter.is_real_provider is False
    assert adapter.supports_oauth is False
    assert adapter.supports_metrics_read is False
    assert adapter.supports_publish_prepare is False
    assert adapter.supports_real_publish is False
    assert adapter.supports_token_refresh is False
    assert adapter.supports_disconnect is False
    assert adapter.supports_revoke is False


def test_douyin_real_adapter_skeleton_metadata_is_blocked():
    adapter = DouyinRealAdapter()

    assert adapter.provider_id == "douyin_real"
    assert adapter.source_type == "real"
    assert adapter.is_real_provider is True
    assert adapter.supports_oauth is False
    assert adapter.supports_metrics_read is False
    assert adapter.supports_publish_prepare is False
    assert adapter.supports_real_publish is False
    assert adapter.supports_token_refresh is False
    assert adapter.supports_disconnect is False
    assert adapter.supports_revoke is False


def test_douyin_adapter_operations_return_blocked_boundary_results():
    for adapter in (DouyinSandboxAdapter(), DouyinRealAdapter()):
        for operation_name, operation in iter_adapter_operations(adapter):
            result = operation()

            assert isinstance(result, DouyinAdapterOperationResult)
            assert result.provider_id == adapter.provider_id
            assert result.source_type == adapter.source_type
            assert result.operation == operation_name
            assert result.operation_status in BLOCKED_STATUSES
            assert result.safe_message
            assert result.boundary_notes
            assert result.is_real_provider is adapter.is_real_provider
            assert result.external_call_performed is False
            assert result.credential_read_performed is False
            assert result.token_read_performed is False
            assert result.token_write_performed is False
            assert_result_has_no_sensitive_field_names(asdict(result))


def test_douyin_adapter_operations_do_not_read_environment_values(monkeypatch):
    fake_environment_values = [
        "fake-douyin-access-token-env-value",
        "fake-douyin-client-secret-env-value",
        "fake-douyin-api-key-env-value",
        "fake-oauth-state-env-value",
        "fake-authorization-code-env-value",
    ]
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", fake_environment_values[0])
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", fake_environment_values[1])
    monkeypatch.setenv("DOUYIN_API_KEY", fake_environment_values[2])
    monkeypatch.setenv("OAUTH_STATE", fake_environment_values[3])
    monkeypatch.setenv("AUTHORIZATION_CODE", fake_environment_values[4])

    for adapter in (DouyinSandboxAdapter(), DouyinRealAdapter()):
        for _operation_name, operation in iter_adapter_operations(adapter):
            result_text = json.dumps(asdict(operation()), sort_keys=True)
            for fake_value in fake_environment_values:
                assert fake_value not in result_text


def test_douyin_adapter_operations_do_not_trigger_network_calls(monkeypatch):
    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("unexpected external network call")

    monkeypatch.setattr(socket, "create_connection", fail_if_called)
    monkeypatch.setattr(urllib.request, "urlopen", fail_if_called)

    if importlib.util.find_spec("requests") is not None:
        import requests

        monkeypatch.setattr(requests.sessions.Session, "request", fail_if_called)

    if importlib.util.find_spec("httpx") is not None:
        import httpx

        monkeypatch.setattr(httpx.Client, "request", fail_if_called)
        monkeypatch.setattr(httpx.AsyncClient, "request", fail_if_called)

    for adapter in (DouyinSandboxAdapter(), DouyinRealAdapter()):
        for _operation_name, operation in iter_adapter_operations(adapter):
            result = operation()
            assert result.external_call_performed is False


def test_batch_does_not_add_douyin_oauth_or_token_routes():
    route_paths = {getattr(route, "path", "") for route in app.routes}
    forbidden_prefixes = ("/api/douyin", "/api/oauth", "/api/auth")
    forbidden_fragments = (
        "/authorize",
        "/callback",
        "/connect",
        "/refresh",
        "/revoke",
        "/disconnect",
    )

    assert all(
        not path.startswith(forbidden_prefixes)
        and all(fragment not in path for fragment in forbidden_fragments)
        for path in route_paths
    )


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


def assert_result_has_no_sensitive_field_names(payload) -> None:
    assert collect_keys(payload).isdisjoint(SENSITIVE_RESULT_FIELD_NAMES)


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
