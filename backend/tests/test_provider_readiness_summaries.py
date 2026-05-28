import os
import socket
import sqlite3

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.providers.readiness_summary import list_provider_readiness_summaries


SENSITIVE_RESPONSE_FIELD_NAMES = {
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
    "token_expiry_value",
    "token_refresh_response",
    "token_revoke_response",
    "provider_token_response",
}

SENSITIVE_ERROR_TERMS = {
    "token",
    "secret",
    "credential",
    "authorization_code",
    "api_key",
    "client_secret",
    "state_value",
}

EXPECTED_READINESS_BOUNDARIES = {
    "provider_registry",
    "capability_metadata",
    "connection_state",
    "credential_reference",
    "security_audit",
    "oauth_boundary",
    "token_lifecycle_boundary",
}


def test_list_provider_readiness_summaries_returns_stable_metadata(
    client: TestClient,
):
    response = client.get("/api/provider-readiness-summaries")

    assert response.status_code == 200
    body = response.json()
    assert list(body.keys()) == ["readiness_summaries"]
    assert [
        summary["provider_id"] for summary in body["readiness_summaries"]
    ] == [
        "fake_local",
        "douyin_sandbox",
        "douyin_real",
    ]
    for summary in body["readiness_summaries"]:
        assert summary["readiness_items"]
        assert summary["blocking_reasons"]
        assert summary["next_safe_steps"]
        assert summary["safe_summary"]
        assert summary["boundary_notes"]
        assert {
            item["boundary_id"] for item in summary["readiness_items"]
        }.issuperset(EXPECTED_READINESS_BOUNDARIES)
    assert_response_has_no_sensitive_field_names(body)


def test_fake_local_readiness_summary_is_local_fake_only(client: TestClient):
    summary = get_summary_from_list(client, "fake_local")

    assert summary["provider_name"] == "Local Fake Provider"
    assert summary["source_type"] == "fake_local"
    assert summary["implementation_status"] == "available_local_fake"
    assert summary["overall_readiness_status"] == "local_fake_ready"
    assert summary["v0_9_poc_readiness_status"] == "not_applicable_local_fake"
    assert summary["can_use_local_fake_workflow"] is True
    assert summary["is_safe_to_attempt_real_oauth"] is False
    assert summary["is_safe_to_store_tokens"] is False
    assert summary["is_safe_to_fetch_real_metrics"] is False
    assert summary["is_safe_to_publish"] is False
    assert summary["is_ready_for_v0_9_sandbox_poc"] is False
    assert summary["is_ready_for_v0_9_real_poc"] is False
    status_text = build_status_text(summary)
    assert "local fake/demo/test data only" in status_text
    assert "not real Douyin data" in status_text
    assert "no OAuth required" in status_text
    assert "no token stored" in status_text
    assert "no external service call" in status_text
    assert "local fake provider is not a real Douyin provider" in status_text
    assert "no real OAuth" in status_text
    assert "no real metrics" in status_text
    assert "no real publish" in status_text


def test_douyin_sandbox_readiness_summary_is_placeholder_not_ready(
    client: TestClient,
):
    summary = get_summary_from_list(client, "douyin_sandbox")

    assert summary["provider_name"] == "Douyin Sandbox Placeholder"
    assert summary["source_type"] == "sandbox"
    assert summary["implementation_status"] == "planned"
    assert summary["overall_readiness_status"] in {
        "sandbox_placeholder_not_ready",
        "metadata_only",
    }
    assert summary["v0_9_poc_readiness_status"] in {
        "blocked_placeholder_only",
        "metadata_ready_for_review",
    }
    assert summary["can_use_local_fake_workflow"] is False
    assert summary["is_safe_to_attempt_real_oauth"] is False
    assert summary["is_safe_to_store_tokens"] is False
    assert summary["is_safe_to_fetch_real_metrics"] is False
    assert summary["is_safe_to_publish"] is False
    assert summary["is_ready_for_v0_9_sandbox_poc"] is False
    assert summary["is_ready_for_v0_9_real_poc"] is False
    status_text = build_status_text(summary)
    assert "OAuth is not implemented" in status_text
    assert "OAuth callback route is not implemented" in status_text
    assert "OAuth state storage is not implemented" in status_text
    assert "credential storage is not implemented" in status_text
    assert "token lifecycle is not implemented" in status_text
    assert "no real Douyin API call" in status_text
    assert "cannot be treated as douyin_real" in status_text
    assert "placeholder metadata only" in status_text
    assert "tokens are not stored" in status_text
    assert "secrets are not stored" in status_text
    assert "no token exchange" in status_text
    assert "no real metrics fetching" in status_text
    assert "no upload / publish / scheduling" in status_text


def test_douyin_real_readiness_summary_is_future_placeholder_not_ready(
    client: TestClient,
):
    summary = get_summary_from_list(client, "douyin_real")

    assert summary["provider_name"] == "Douyin Real Placeholder"
    assert summary["source_type"] == "real"
    assert summary["implementation_status"] == "planned"
    assert summary["overall_readiness_status"] in {
        "real_placeholder_not_ready",
        "metadata_only",
    }
    assert summary["v0_9_poc_readiness_status"] in {
        "blocked_missing_real_oauth",
        "blocked_placeholder_only",
    }
    assert summary["can_use_local_fake_workflow"] is False
    assert summary["is_safe_to_attempt_real_oauth"] is False
    assert summary["is_safe_to_store_tokens"] is False
    assert summary["is_safe_to_fetch_real_metrics"] is False
    assert summary["is_safe_to_publish"] is False
    assert summary["is_ready_for_v0_9_sandbox_poc"] is False
    assert summary["is_ready_for_v0_9_real_poc"] is False
    status_text = build_status_text(summary)
    assert "real OAuth is not implemented" in status_text
    assert "real OAuth callback route is not implemented" in status_text
    assert "real credential storage is not implemented" in status_text
    assert "token storage is not implemented" in status_text
    assert "token refresh / revoke / disconnect is not implemented" in status_text
    assert "no real metrics fetching" in status_text
    assert "no upload / publish / scheduling" in status_text
    assert "future real provider placeholder only" in status_text
    assert "not real Douyin integration" in status_text
    assert "no access token or refresh token storage" in status_text
    assert "no token refresh / revoke / disconnect" in status_text
    assert "no API key storage" in status_text
    assert "no secret storage" in status_text


def test_get_each_provider_readiness_summary_by_id(client: TestClient):
    for provider_id in ("fake_local", "douyin_sandbox", "douyin_real"):
        response = client.get(f"/api/provider-readiness-summaries/{provider_id}")

        assert response.status_code == 200
        assert response.json()["provider_id"] == provider_id
        assert_response_has_no_sensitive_field_names(response.json())


def test_unknown_provider_readiness_summary_returns_404_without_sensitive_terms(
    client: TestClient,
):
    response = client.get("/api/provider-readiness-summaries/unknown")

    assert response.status_code == 404
    assert response.json()["detail"] == "Provider readiness summary not found"
    response_text = response.text.lower()
    for term in SENSITIVE_ERROR_TERMS:
        assert term not in response_text


def test_provider_readiness_summary_response_does_not_leak_environment_values(
    client: TestClient, monkeypatch
):
    environment_values = [
        "fake-access-value-from-env",
        "fake-refresh-value-from-env",
        "fake-client-secret-value-from-env",
        "fake-oauth-state-value-from-env",
        "fake-authorization-code-value-from-env",
        "fake-api-key-value-from-env",
        "fake-provider-secret-value-from-env",
    ]
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", environment_values[0])
    monkeypatch.setenv("DOUYIN_REFRESH_TOKEN", environment_values[1])
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", environment_values[2])
    monkeypatch.setenv("OAUTH_STATE", environment_values[3])
    monkeypatch.setenv("AUTHORIZATION_CODE", environment_values[4])
    monkeypatch.setenv("DOUYIN_API_KEY", environment_values[5])
    monkeypatch.setenv("PROVIDER_SECRET", environment_values[6])

    response = client.get("/api/provider-readiness-summaries")

    assert response.status_code == 200
    for value in environment_values:
        assert value not in response.text


def test_provider_readiness_summary_does_not_add_database_tables(
    client: TestClient,
):
    with sqlite3.connect(get_settings().database_path) as connection:
        readiness_tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name LIKE '%readiness%'
            """
        ).fetchall()

    assert readiness_tables == []


def test_provider_readiness_summary_service_avoids_environment_and_network_reads(
    client: TestClient, monkeypatch
):
    database_path = get_settings().database_path

    def fail_if_called(*args, **kwargs):
        raise AssertionError("unexpected environment or external service read")

    monkeypatch.setattr(os, "getenv", fail_if_called)
    monkeypatch.setattr(socket, "create_connection", fail_if_called)

    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        summaries = list_provider_readiness_summaries(connection)

    assert [summary.provider_id for summary in summaries] == [
        "fake_local",
        "douyin_sandbox",
        "douyin_real",
    ]


def test_provider_readiness_summary_api_does_not_enable_write_methods(
    client: TestClient,
):
    write_responses = [
        client.post("/api/provider-readiness-summaries", json={}),
        client.put("/api/provider-readiness-summaries/fake_local", json={}),
        client.patch("/api/provider-readiness-summaries/fake_local", json={}),
        client.delete("/api/provider-readiness-summaries/fake_local"),
    ]

    for response in write_responses:
        assert response.status_code < 200 or response.status_code >= 300


def test_batch_does_not_add_real_oauth_or_token_lifecycle_routes(
    client: TestClient,
):
    forbidden_paths = [
        "/api/oauth/start",
        "/api/auth/douyin",
        "/api/token/refresh",
        "/api/provider-token-refresh/douyin",
        "/api/provider-token-revoke/douyin",
        "/api/provider-disconnect/douyin",
        "/api/providers/fake_local/authorize",
        "/api/providers/fake_local/callback",
        "/api/providers/fake_local/connect",
        "/api/providers/fake_local/disconnect",
        "/api/providers/fake_local/refresh",
        "/api/providers/fake_local/revoke",
    ]

    route_paths = {getattr(route, "path", "") for route in app.routes}
    assert all(path not in route_paths for path in forbidden_paths)
    for path in forbidden_paths:
        response = client.post(path, json={})
        assert response.status_code < 200 or response.status_code >= 300


def test_existing_provider_metadata_routes_still_return_existing_metadata(
    client: TestClient,
):
    responses = [
        client.get("/api/providers"),
        client.get("/api/provider-connections"),
        client.get("/api/provider-credential-references"),
        client.get("/api/provider-security-audit-events"),
        client.get("/api/provider-oauth-boundaries"),
        client.get("/api/provider-token-lifecycle-boundaries"),
    ]

    for response in responses:
        assert response.status_code == 200

    assert [
        provider["provider_id"] for provider in responses[0].json()["providers"]
    ] == ["fake_local", "douyin_sandbox", "douyin_real"]
    assert [
        connection["provider_id"] for connection in responses[1].json()["connections"]
    ] == ["fake_local", "douyin_sandbox", "douyin_real"]
    assert [
        reference["provider_id"]
        for reference in responses[2].json()["credential_references"]
    ] == ["fake_local", "douyin_sandbox", "douyin_real"]
    assert list(responses[3].json().keys()) == ["audit_events"]
    assert [
        boundary["provider_id"] for boundary in responses[4].json()["oauth_boundaries"]
    ] == ["fake_local", "douyin_sandbox", "douyin_real"]
    assert [
        boundary["provider_id"]
        for boundary in responses[5].json()["token_lifecycle_boundaries"]
    ] == ["fake_local", "douyin_sandbox", "douyin_real"]


def get_summary_from_list(client: TestClient, provider_id: str) -> dict:
    response = client.get("/api/provider-readiness-summaries")
    assert response.status_code == 200
    summaries = {
        summary["provider_id"]: summary
        for summary in response.json()["readiness_summaries"]
    }
    return summaries[provider_id]


def build_status_text(summary: dict) -> str:
    readiness_item_text = " ".join(
        [
            item["safe_status_message"] + " " + str(item["source_metadata"])
            for item in summary["readiness_items"]
        ]
    )
    return " ".join(
        [
            summary["safe_summary"],
            *summary["blocking_reasons"],
            *summary["next_safe_steps"],
            *summary["boundary_notes"],
            readiness_item_text,
        ]
    )


def assert_response_has_no_sensitive_field_names(payload) -> None:
    for key in collect_keys(payload):
        assert key not in SENSITIVE_RESPONSE_FIELD_NAMES


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
