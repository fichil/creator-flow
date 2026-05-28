import importlib.util
import inspect
import json
import socket
import urllib.request

from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import douyin_sandbox as douyin_sandbox_routes


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

FORBIDDEN_RESPONSE_KEYS = {
    "access_token",
    "refresh_token",
    "client_secret",
    "authorization_code",
    "oauth_state",
    "oauth_url",
    "api_key",
    "credential",
    "cookie",
    "session",
    "bearer",
    "password",
    "secret",
}

FAKE_ENVIRONMENT_VALUES = [
    "fake-batch6-env-value-001",
    "fake-batch6-env-value-002",
    "fake-batch6-env-value-003",
    "fake-batch6-env-value-004",
    "fake-batch6-env-value-005",
    "fake-batch6-env-value-006",
]


def test_douyin_provider_list_api_returns_sandbox_and_real_descriptors(client: TestClient):
    response = client.get("/api/providers/douyin")

    assert response.status_code == 200
    body = response.json()
    assert list(body.keys()) == ["providers"]
    assert [provider["provider_id"] for provider in body["providers"]] == [
        "douyin_sandbox",
        "douyin_real",
    ]

    sandbox = get_provider(body, "douyin_sandbox")
    assert sandbox["environment"] == "sandbox"
    assert sandbox["mode"] == "sandbox"
    assert sandbox["status"] == "available_for_sandbox"
    assert sandbox["supports_simulation"] is True
    assert sandbox["supports_real_oauth"] is False
    assert sandbox["supports_real_publish"] is False
    assert sandbox["supports_real_metrics"] is False
    assert sandbox["simulated"] is True
    assert sandbox["dry_run"] is True
    assert "simulation only" in sandbox["boundary_notes"]

    real = get_provider(body, "douyin_real")
    assert real["environment"] == "real"
    assert real["mode"] == "real"
    assert real["status"] in {"blocked", "not_implemented"}
    assert real["supports_simulation"] is False
    assert real["supports_real_oauth"] is False
    assert real["supports_real_publish"] is False
    assert real["supports_real_metrics"] is False
    assert real["simulated"] is False
    assert real["dry_run"] is False
    assert "blocked" in real["boundary_notes"]

    assert_payload_has_no_sensitive_terms(body)


def test_douyin_provider_lookup_api_requires_exact_supported_provider_id(client: TestClient):
    sandbox = client.get("/api/providers/douyin/douyin_sandbox")
    assert sandbox.status_code == 200
    assert sandbox.json()["provider_id"] == "douyin_sandbox"
    assert sandbox.json()["mode"] == "sandbox"
    assert sandbox.json()["simulated"] is True

    real = client.get("/api/providers/douyin/douyin_real")
    assert real.status_code == 200
    assert real.json()["provider_id"] == "douyin_real"
    assert real.json()["status"] in {"blocked", "not_implemented"}
    assert real.json()["simulated"] is False

    for provider_id in ("unknown_provider", "DOUYIN_SANDBOX", "%20douyin_sandbox%20"):
        response = client.get(f"/api/providers/douyin/{provider_id}")

        assert response.status_code == 404
        assert response.json()["detail"]["message"] == "Unsupported Douyin provider id"
        assert response.json()["detail"]["provider_id"] != "douyin_sandbox"
        assert_payload_has_no_sensitive_terms(response.json())

    trailing_slash = client.get("/api/providers/douyin/", follow_redirects=False)
    assert trailing_slash.status_code in {307, 404, 405}


def test_sandbox_mock_connection_api_returns_deterministic_simulated_result(
    client: TestClient,
):
    response = client.post("/api/providers/douyin/sandbox/mock-connection")

    assert response.status_code == 200
    body = response.json()
    assert_sandbox_operation_response(
        body,
        operation="sandbox_mock_connection",
        workflow_name="mock_account_connection",
    )
    assert body["operation_references"] == [
        "sandbox_oauth_start_001",
        "sandbox_oauth_callback_001",
    ]
    assert body["payload"] == {
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
    assert_no_oauth_or_sensitive_payload(body)


def test_sandbox_metrics_preview_api_returns_deterministic_fake_metrics(
    client: TestClient,
):
    response = client.post("/api/providers/douyin/sandbox/metrics-preview")

    assert response.status_code == 200
    body = response.json()
    assert_sandbox_operation_response(
        body,
        operation="sandbox_metrics_preview",
        workflow_name="sandbox_metrics_poc",
    )
    assert body["operation_references"] == ["sandbox_metrics_001"]
    assert body["payload"] == {
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
    assert_no_oauth_or_sensitive_payload(body)


def test_sandbox_publish_dry_run_api_returns_deterministic_fake_publish(
    client: TestClient,
):
    response = client.post("/api/providers/douyin/sandbox/publish-dry-run")

    assert response.status_code == 200
    body = response.json()
    assert_sandbox_operation_response(
        body,
        operation="sandbox_publish_dry_run",
        workflow_name="dry_run_publish",
    )
    assert body["operation_references"] == [
        "sandbox_prepare_001",
        "sandbox_video_001",
        "sandbox_publish_001",
    ]
    assert body["payload"] == {
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
    assert body["storage_write_performed"] is False
    assert body["database_write_performed"] is False
    assert_no_oauth_or_sensitive_payload(body)


def test_provider_specific_sandbox_api_routes_preserve_sandbox_and_real_boundaries(
    client: TestClient,
):
    sandbox = client.post("/api/providers/douyin/douyin_sandbox/sandbox/mock-connection")
    assert sandbox.status_code == 200
    assert_sandbox_operation_response(
        sandbox.json(),
        operation="sandbox_mock_connection",
        workflow_name="mock_account_connection",
    )

    for path in (
        "/api/providers/douyin/douyin_real/sandbox/mock-connection",
        "/api/providers/douyin/douyin_real/sandbox/metrics-preview",
        "/api/providers/douyin/douyin_real/sandbox/publish-dry-run",
    ):
        response = client.post(path)

        assert response.status_code == 200
        body = response.json()
        assert body["provider_id"] == "douyin_real"
        assert body["source_type"] == "real"
        assert body["status"] in {"blocked", "not_implemented"}
        assert body["status"] != "simulated_success"
        assert body["outcome"] == "blocked"
        assert body["simulated"] is False
        assert body["external_call_performed"] is False
        assert body["storage_write_performed"] is False
        assert body["database_write_performed"] is False
        assert_payload_has_no_sensitive_terms(body)


def test_unknown_provider_sandbox_api_does_not_fallback_to_sandbox(client: TestClient):
    for path in (
        "/api/providers/douyin/unknown_provider/sandbox/mock-connection",
        "/api/providers/douyin/DOUYIN_SANDBOX/sandbox/metrics-preview",
        "/api/providers/douyin/%20douyin_sandbox%20/sandbox/publish-dry-run",
    ):
        response = client.post(path)

        assert response.status_code == 404
        assert response.json()["detail"]["message"] == "Unsupported Douyin provider id"
        assert response.json()["detail"]["provider_id"] != "douyin_sandbox"
        assert "fill" not in response.text.lower()
        assert_payload_has_no_sensitive_terms(response.json())


def test_sensitive_provider_id_is_redacted_in_error_payload(client: TestClient):
    response = client.post("/api/providers/douyin/client_secret/sandbox/mock-connection")

    assert response.status_code == 404
    assert response.json()["detail"] == {
        "message": "Unsupported Douyin provider id",
        "provider_id": "<redacted>",
    }
    assert "client_secret" not in response.text


def test_sandbox_api_does_not_trigger_http_or_sdk_calls(client: TestClient, monkeypatch):
    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("unexpected external service call")

    monkeypatch.setattr(socket, "create_connection", fail_if_called)
    monkeypatch.setattr(urllib.request, "urlopen", fail_if_called)

    if importlib.util.find_spec("requests") is not None:
        import requests

        monkeypatch.setattr(requests.sessions.Session, "request", fail_if_called)

    for path in (
        "/api/providers/douyin",
        "/api/providers/douyin/douyin_sandbox",
        "/api/providers/douyin/sandbox/mock-connection",
        "/api/providers/douyin/sandbox/metrics-preview",
        "/api/providers/douyin/sandbox/publish-dry-run",
        "/api/providers/douyin/douyin_real/sandbox/publish-dry-run",
    ):
        if path.endswith("dry-run") or "mock-connection" in path or "metrics-preview" in path:
            response = client.post(path)
        else:
            response = client.get(path)
        assert response.status_code == 200
        assert_payload_has_no_sensitive_terms(response.json())

    route_source = inspect.getsource(douyin_sandbox_routes)
    assert "requests." not in route_source
    assert "httpx." not in route_source


def test_sandbox_api_does_not_read_or_leak_sensitive_environment_values(
    client: TestClient, monkeypatch
):
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", FAKE_ENVIRONMENT_VALUES[0])
    monkeypatch.setenv("DOUYIN_REFRESH_TOKEN", FAKE_ENVIRONMENT_VALUES[1])
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", FAKE_ENVIRONMENT_VALUES[2])
    monkeypatch.setenv("AUTHORIZATION_CODE", FAKE_ENVIRONMENT_VALUES[3])
    monkeypatch.setenv("OAUTH_STATE", FAKE_ENVIRONMENT_VALUES[4])
    monkeypatch.setenv("DOUYIN_SESSION", FAKE_ENVIRONMENT_VALUES[5])

    payloads = [
        client.get("/api/providers/douyin").json(),
        client.get("/api/providers/douyin/douyin_sandbox").json(),
        client.post("/api/providers/douyin/sandbox/mock-connection").json(),
        client.post("/api/providers/douyin/sandbox/metrics-preview").json(),
        client.post("/api/providers/douyin/sandbox/publish-dry-run").json(),
    ]
    serialized = json.dumps(payloads, sort_keys=True)

    for fake_value in FAKE_ENVIRONMENT_VALUES:
        assert fake_value not in serialized
    for payload in payloads:
        assert_payload_has_no_sensitive_terms(payload)


def test_batch6_routes_are_sandbox_contract_only():
    route_paths = {getattr(route, "path", "") for route in app.routes}

    assert "/api/providers/douyin" in route_paths
    assert "/api/providers/douyin/{provider_id}" in route_paths
    assert "/api/providers/douyin/sandbox/mock-connection" in route_paths
    assert "/api/providers/douyin/sandbox/metrics-preview" in route_paths
    assert "/api/providers/douyin/sandbox/publish-dry-run" in route_paths

    assert all(not path.startswith(("/api/douyin", "/api/oauth", "/api/auth")) for path in route_paths)
    assert all("/authorize" not in path for path in route_paths)
    assert all("/callback" not in path for path in route_paths)
    assert all("/refresh" not in path for path in route_paths)
    assert all("/revoke" not in path for path in route_paths)


def get_provider(body: dict, provider_id: str) -> dict:
    providers = {provider["provider_id"]: provider for provider in body["providers"]}
    return providers[provider_id]


def assert_sandbox_operation_response(
    body: dict, *, operation: str, workflow_name: str
) -> None:
    assert body["provider_id"] == "douyin_sandbox"
    assert body["source_type"] == "sandbox"
    assert body["mode"] == "sandbox"
    assert body["operation"] == operation
    assert body["workflow_name"] == workflow_name
    assert body["status"] == "simulated_success"
    assert body["outcome"] == "simulated"
    assert body["simulated"] is True
    assert body["dry_run"] is True
    assert body["external_call_performed"] is False
    assert body["storage_write_performed"] is False
    assert body["database_write_performed"] is False
    assert "sandbox" in json.dumps(body, sort_keys=True)
    assert "simulated" in json.dumps(body, sort_keys=True)
    assert "dry" in json.dumps(body, sort_keys=True)
    assert_payload_has_no_sensitive_terms(body)


def assert_no_oauth_or_sensitive_payload(payload: dict) -> None:
    assert collect_keys(payload).isdisjoint(FORBIDDEN_RESPONSE_KEYS)
    serialized = json.dumps(payload, sort_keys=True).lower()
    assert "oauth_url" not in serialized
    assert "oauth_state" not in serialized
    assert "authorization_code" not in serialized
    assert_payload_has_no_sensitive_terms(payload)


def assert_payload_has_no_sensitive_terms(payload) -> None:
    assert collect_keys(payload).isdisjoint(SENSITIVE_EXACT_TERMS)
    assert collect_string_values(payload).isdisjoint(SENSITIVE_EXACT_TERMS)


def collect_keys(payload) -> set[str]:
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
