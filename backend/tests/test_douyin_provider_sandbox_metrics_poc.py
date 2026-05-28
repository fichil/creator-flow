import importlib.util
import json
import socket
import urllib.request
from dataclasses import asdict, is_dataclass
from typing import Callable

import pytest

from app.main import app
from app.providers.douyin import (
    create_douyin_provider_adapter,
    list_douyin_provider_descriptors,
    run_douyin_sandbox_dry_run_publish,
    run_douyin_sandbox_metrics_poc,
    run_douyin_sandbox_mock_account_connection,
    run_douyin_sandbox_mock_workflow_poc,
)
from app.providers.douyin.adapter import SANDBOX_OPERATION_REFERENCES


SENSITIVE_EXACT_TERMS = {
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
    "fake-batch4-env-value-001",
    "fake-batch4-env-value-002",
    "fake-batch4-env-value-003",
    "fake-batch4-env-value-004",
    "fake-batch4-env-value-005",
    "fake-batch4-env-value-006",
]


def test_factory_routed_sandbox_adapter_operations_remain_deterministic():
    adapter = create_douyin_provider_adapter("douyin_sandbox")

    for operation_name, operation in iter_adapter_operations(adapter):
        result = operation()

        assert result.provider_id == "douyin_sandbox"
        assert result.source_type == "sandbox"
        assert result.operation == operation_name
        assert result.operation_status == "simulated_success"
        assert result.simulation_reference == SANDBOX_OPERATION_REFERENCES[operation_name]
        assert result.dry_run is True
        assert result.external_call_performed is False
        assert result.credential_read_performed is False
        assert result.token_read_performed is False
        assert result.token_write_performed is False


def test_sandbox_mock_account_connection_returns_deterministic_success():
    result = run_douyin_sandbox_mock_account_connection()

    assert result.provider_id == "douyin_sandbox"
    assert result.source_type == "sandbox"
    assert result.workflow_name == "mock_account_connection"
    assert result.workflow_status == "simulated_success"
    assert result.dry_run is True
    assert result.external_call_performed is False
    assert result.storage_write_performed is False
    assert result.operation_references == (
        "sandbox_oauth_start_001",
        "sandbox_oauth_callback_001",
    )
    assert result.payload == {
        "provider": "douyin_sandbox",
        "source": "sandbox",
        "mode": "sandbox",
        "outcome": "simulated",
        "dry_run": True,
        "connection_id": "sandbox_connection_001",
        "account_id": "sandbox_account_001",
        "account_label": "Sandbox Mock Account",
        "connection_status": "simulated_connected",
    }
    assert_payload_has_no_sensitive_exact_terms(asdict(result))


def test_sandbox_metrics_poc_returns_deterministic_payload():
    result = run_douyin_sandbox_metrics_poc()

    assert result.provider_id == "douyin_sandbox"
    assert result.source_type == "sandbox"
    assert result.workflow_name == "sandbox_metrics_poc"
    assert result.workflow_status == "simulated_success"
    assert result.operation_references == ("sandbox_metrics_001",)
    assert result.payload == {
        "provider": "douyin_sandbox",
        "source": "sandbox",
        "mode": "sandbox",
        "outcome": "simulated",
        "dry_run": True,
        "metrics_id": "sandbox_metrics_snapshot_001",
        "publication_id": "sandbox_publish_001",
        "collected_at": "2026-01-01T00:00:00Z",
        "views": 1200,
        "likes": 128,
        "comments": 16,
        "shares": 9,
        "favorites": 5,
    }
    assert_payload_has_no_sensitive_exact_terms(asdict(result))


def test_sandbox_dry_run_publish_returns_deterministic_simulated_success():
    result = run_douyin_sandbox_dry_run_publish()

    assert result.provider_id == "douyin_sandbox"
    assert result.source_type == "sandbox"
    assert result.workflow_name == "dry_run_publish"
    assert result.workflow_status == "simulated_success"
    assert result.operation_references == (
        "sandbox_prepare_001",
        "sandbox_video_001",
        "sandbox_publish_001",
    )
    assert result.payload == {
        "provider": "douyin_sandbox",
        "source": "sandbox",
        "mode": "sandbox",
        "outcome": "simulated",
        "dry_run": True,
        "video_id": "sandbox_video_001",
        "publish_id": "sandbox_publish_001",
        "publish_status": "simulated_success",
        "scheduled": False,
        "completed_at": "2026-01-01T00:00:00Z",
    }
    assert_payload_has_no_sensitive_exact_terms(asdict(result))


def test_sandbox_mock_workflow_poc_returns_three_stable_results():
    results = run_douyin_sandbox_mock_workflow_poc()

    assert [result.workflow_name for result in results] == [
        "mock_account_connection",
        "sandbox_metrics_poc",
        "dry_run_publish",
    ]
    assert all(result.provider_id == "douyin_sandbox" for result in results)
    assert all(result.workflow_status == "simulated_success" for result in results)
    assert all(result.dry_run is True for result in results)
    assert all(result.external_call_performed is False for result in results)
    assert all(result.storage_write_performed is False for result in results)
    assert_payload_has_no_sensitive_exact_terms([asdict(result) for result in results])


def test_douyin_real_adapter_remains_blocked_for_batch4():
    adapter = create_douyin_provider_adapter("douyin_real")

    for operation_name, operation in iter_adapter_operations(adapter):
        result = operation()

        assert result.provider_id == "douyin_real"
        assert result.source_type == "real"
        assert result.operation == operation_name
        assert result.operation_status in {"blocked", "not_implemented"}
        assert result.operation_status != "simulated_success"
        assert result.simulation_reference is None
        assert result.simulation_details == {}
        assert result.external_call_performed is False
        assert result.credential_read_performed is False
        assert result.token_read_performed is False
        assert result.token_write_performed is False


def test_unknown_provider_still_does_not_fallback_to_sandbox():
    for provider_id in ("unknown_provider", "", None, "DOUYIN_SANDBOX", " douyin_sandbox "):
        with pytest.raises(ValueError):
            create_douyin_provider_adapter(provider_id)  # type: ignore[arg-type]


def test_sandbox_workflow_does_not_trigger_http_or_sdk_calls(monkeypatch):
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

    results = run_douyin_sandbox_mock_workflow_poc()

    assert all(result.external_call_performed is False for result in results)


def test_sandbox_workflow_does_not_read_or_leak_sensitive_environment_values(monkeypatch):
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", FAKE_ENVIRONMENT_VALUES[0])
    monkeypatch.setenv("DOUYIN_REFRESH_TOKEN", FAKE_ENVIRONMENT_VALUES[1])
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", FAKE_ENVIRONMENT_VALUES[2])
    monkeypatch.setenv("AUTHORIZATION_CODE", FAKE_ENVIRONMENT_VALUES[3])
    monkeypatch.setenv("OAUTH_STATE", FAKE_ENVIRONMENT_VALUES[4])
    monkeypatch.setenv("DOUYIN_SESSION", FAKE_ENVIRONMENT_VALUES[5])

    payloads = [
        [asdict(descriptor) for descriptor in list_douyin_provider_descriptors()],
        build_adapter_public_metadata(create_douyin_provider_adapter("douyin_sandbox")),
        [asdict(result) for result in run_douyin_sandbox_mock_workflow_poc()],
    ]

    for payload in payloads:
        serialized = json.dumps(payload, sort_keys=True)
        for fake_value in FAKE_ENVIRONMENT_VALUES:
            assert fake_value not in serialized
        assert_payload_has_no_sensitive_exact_terms(payload)


def test_batch4_does_not_add_douyin_oauth_or_token_routes():
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


def build_adapter_public_metadata(adapter) -> dict[str, str | bool]:
    return {
        "provider_id": adapter.provider_id,
        "provider_name": adapter.provider_name,
        "source_type": adapter.source_type,
        "is_real_provider": adapter.is_real_provider,
        "supports_oauth": adapter.supports_oauth,
        "supports_metrics_read": adapter.supports_metrics_read,
        "supports_publish_prepare": adapter.supports_publish_prepare,
        "supports_real_publish": adapter.supports_real_publish,
        "supports_token_refresh": adapter.supports_token_refresh,
        "supports_disconnect": adapter.supports_disconnect,
        "supports_revoke": adapter.supports_revoke,
    }


def assert_payload_has_no_sensitive_exact_terms(payload) -> None:
    assert collect_keys(payload).isdisjoint(SENSITIVE_EXACT_TERMS)
    assert collect_string_values(payload).isdisjoint(SENSITIVE_EXACT_TERMS)


def collect_keys(payload) -> set[str]:
    if is_dataclass(payload) and not isinstance(payload, type):
        return collect_keys(asdict(payload))
    if isinstance(payload, dict):
        keys = set(payload)
        for value in payload.values():
            keys.update(collect_keys(value))
        return keys
    if isinstance(payload, list | tuple):
        keys = set()
        for value in payload:
            keys.update(collect_keys(value))
        return keys
    return set()


def collect_string_values(payload) -> set[str]:
    if is_dataclass(payload) and not isinstance(payload, type):
        return collect_string_values(asdict(payload))
    if isinstance(payload, dict):
        values = set()
        for value in payload.values():
            values.update(collect_string_values(value))
        return values
    if isinstance(payload, list | tuple):
        values = set()
        for value in payload:
            values.update(collect_string_values(value))
        return values
    if isinstance(payload, str):
        return {payload.lower()}
    return set()
