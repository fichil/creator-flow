import importlib.util
import json
import socket
import urllib.request
from dataclasses import asdict, is_dataclass
from typing import Callable

import pytest

from app.main import app
from app.providers.douyin import (
    DouyinRealAdapter,
    DouyinSandboxAdapter,
    create_douyin_provider_adapter,
    get_douyin_provider_descriptor,
    list_douyin_provider_descriptors,
)
from app.providers.douyin.adapter import SANDBOX_OPERATION_REFERENCES


SENSITIVE_EXACT_FIELD_NAMES = {
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
    "fake-batch3-douyin-access-value",
    "fake-batch3-douyin-refresh-value",
    "fake-batch3-douyin-client-secret-value",
    "fake-batch3-authorization-code-value",
    "fake-batch3-oauth-state-value",
    "fake-batch3-douyin-api-key-value",
    "fake-batch3-cookie-value",
    "fake-batch3-session-value",
]


def test_douyin_provider_descriptor_listing_is_stable_and_non_sensitive():
    descriptors = list_douyin_provider_descriptors()
    repeated_descriptors = list_douyin_provider_descriptors()

    assert [descriptor.provider_id for descriptor in descriptors] == [
        "douyin_sandbox",
        "douyin_real",
    ]
    assert [asdict(descriptor) for descriptor in repeated_descriptors] == [
        asdict(descriptor) for descriptor in descriptors
    ]

    sandbox, real = descriptors
    assert sandbox.display_name == "Douyin Sandbox Provider"
    assert sandbox.environment == "sandbox"
    assert sandbox.status == "available_for_sandbox"
    assert sandbox.supports_simulation is True
    assert sandbox.supports_real_oauth is False
    assert sandbox.supports_real_publish is False
    assert sandbox.supports_real_metrics is False

    assert real.display_name == "Douyin Real Provider"
    assert real.environment == "real"
    assert real.status == "blocked"
    assert real.supports_simulation is False
    assert real.supports_real_oauth is False
    assert real.supports_real_publish is False
    assert real.supports_real_metrics is False

    assert_payload_has_no_sensitive_exact_keys([asdict(descriptor) for descriptor in descriptors])


def test_douyin_provider_descriptor_lookup_accepts_exact_whitelist_only():
    assert get_douyin_provider_descriptor("douyin_sandbox").environment == "sandbox"
    assert get_douyin_provider_descriptor("douyin_real").environment == "real"

    unsupported_provider_ids = [
        "unknown_provider",
        "",
        None,
        "DOUYIN_SANDBOX",
        " douyin_sandbox ",
        "client_secret",
        "authorization_code",
    ]
    for provider_id in unsupported_provider_ids:
        with pytest.raises(ValueError) as exc_info:
            get_douyin_provider_descriptor(provider_id)  # type: ignore[arg-type]

        error_text = str(exc_info.value).lower()
        assert "unsupported douyin provider id" in error_text
        assert "unknown_provider" in error_text or provider_id != "unknown_provider"
        assert not any(term in error_text for term in SENSITIVE_EXACT_FIELD_NAMES)


def test_douyin_provider_factory_routes_exact_providers_without_fallback():
    sandbox_adapter = create_douyin_provider_adapter("douyin_sandbox")
    real_adapter = create_douyin_provider_adapter("douyin_real")

    assert isinstance(sandbox_adapter, DouyinSandboxAdapter)
    assert sandbox_adapter.provider_id == "douyin_sandbox"
    assert sandbox_adapter.source_type == "sandbox"
    assert isinstance(real_adapter, DouyinRealAdapter)
    assert real_adapter.provider_id == "douyin_real"
    assert real_adapter.source_type == "real"

    for provider_id in ("unknown_provider", "", None, "DOUYIN_REAL", " douyin_real "):
        with pytest.raises(ValueError):
            create_douyin_provider_adapter(provider_id)  # type: ignore[arg-type]


def test_factory_routed_sandbox_operations_keep_deterministic_simulation():
    adapter = create_douyin_provider_adapter("douyin_sandbox")

    for operation_name, operation in iter_adapter_operations(adapter):
        result = operation()
        result_dict = asdict(result)

        assert result.provider_id == "douyin_sandbox"
        assert result.source_type == "sandbox"
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
        assert result.external_call_performed is False
        assert result.credential_read_performed is False
        assert result.token_read_performed is False
        assert result.token_write_performed is False
        assert_payload_has_no_sensitive_exact_keys(result_dict)


def test_factory_routed_real_operations_remain_blocked():
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


def test_registry_factory_and_routed_operations_do_not_trigger_external_calls(monkeypatch):
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

    descriptors = list_douyin_provider_descriptors()
    assert [descriptor.provider_id for descriptor in descriptors] == [
        "douyin_sandbox",
        "douyin_real",
    ]

    for provider_id in ("douyin_sandbox", "douyin_real"):
        adapter = create_douyin_provider_adapter(provider_id)
        for _operation_name, operation in iter_adapter_operations(adapter):
            assert operation().external_call_performed is False


def test_registry_factory_and_routed_operations_do_not_leak_sensitive_values(monkeypatch):
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", FAKE_ENVIRONMENT_VALUES[0])
    monkeypatch.setenv("DOUYIN_REFRESH_TOKEN", FAKE_ENVIRONMENT_VALUES[1])
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", FAKE_ENVIRONMENT_VALUES[2])
    monkeypatch.setenv("AUTHORIZATION_CODE", FAKE_ENVIRONMENT_VALUES[3])
    monkeypatch.setenv("OAUTH_STATE", FAKE_ENVIRONMENT_VALUES[4])
    monkeypatch.setenv("DOUYIN_API_KEY", FAKE_ENVIRONMENT_VALUES[5])
    monkeypatch.setenv("DOUYIN_COOKIE", FAKE_ENVIRONMENT_VALUES[6])
    monkeypatch.setenv("DOUYIN_SESSION", FAKE_ENVIRONMENT_VALUES[7])

    payloads = [
        [asdict(descriptor) for descriptor in list_douyin_provider_descriptors()],
        asdict(get_douyin_provider_descriptor("douyin_sandbox")),
        asdict(get_douyin_provider_descriptor("douyin_real")),
    ]

    for provider_id in ("douyin_sandbox", "douyin_real"):
        adapter = create_douyin_provider_adapter(provider_id)
        payloads.append(build_adapter_public_metadata(adapter))
        for _operation_name, operation in iter_adapter_operations(adapter):
            payloads.append(asdict(operation()))

    for invalid_provider_id in ("unknown_provider", None, "client_secret"):
        with pytest.raises(ValueError) as exc_info:
            create_douyin_provider_adapter(invalid_provider_id)  # type: ignore[arg-type]
        payloads.append({"error": str(exc_info.value)})

    for payload in payloads:
        serialized = json.dumps(payload, sort_keys=True)
        for fake_value in FAKE_ENVIRONMENT_VALUES:
            assert fake_value not in serialized
        assert_payload_has_no_sensitive_exact_keys(payload)


def test_batch3_does_not_add_douyin_oauth_or_token_routes():
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


def assert_payload_has_no_sensitive_exact_keys(payload) -> None:
    assert collect_keys(payload).isdisjoint(SENSITIVE_EXACT_FIELD_NAMES)


def collect_keys(payload) -> set[str]:
    if is_dataclass(payload) and not isinstance(payload, type):
        return collect_keys(asdict(payload))
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
