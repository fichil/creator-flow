import sqlite3

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


SENSITIVE_RESPONSE_FIELD_NAMES = {
    "access_token",
    "refresh_token",
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

SENSITIVE_ERROR_TERMS = {
    "token",
    "secret",
    "credential",
    "authorization_code",
    "api_key",
    "client_secret",
    "state_value",
}


def test_list_provider_oauth_boundaries_returns_stable_metadata(client: TestClient):
    response = client.get("/api/provider-oauth-boundaries")

    assert response.status_code == 200
    body = response.json()
    assert list(body.keys()) == ["oauth_boundaries"]
    assert [boundary["provider_id"] for boundary in body["oauth_boundaries"]] == [
        "fake_local",
        "douyin_sandbox",
        "douyin_real",
    ]
    assert_response_has_no_sensitive_field_names(body)


def test_fake_local_oauth_boundary_is_not_required_and_non_sensitive(
    client: TestClient,
):
    boundary = get_boundary_from_list(client, "fake_local")

    assert boundary["provider_name"] == "Local Fake Provider"
    assert boundary["source_type"] == "fake_local"
    assert boundary["implementation_status"] == "available_local_fake"
    assert boundary["oauth_policy_status"] == "not_required"
    assert boundary["state_policy_status"] == "not_required"
    assert boundary["callback_policy_status"] == "not_required"
    assert boundary["csrf_protection_status"] == "not_required"
    assert boundary["redirect_uri_policy_status"] == "not_required"
    assert boundary["token_exchange_policy_status"] == "not_required"
    assert boundary["token_storage_policy_status"] == "none"
    assert boundary["is_available"] is True
    assert boundary["is_real_provider"] is False
    assert boundary["requires_user_authorization"] is False
    assert boundary["can_start_oauth"] is False
    assert boundary["can_handle_callback"] is False
    assert boundary["can_exchange_token"] is False
    assert boundary["can_refresh_token"] is False
    assert boundary["can_revoke_token"] is False
    status_text = build_status_text(boundary)
    assert "not real Douyin data" in status_text
    assert "OAuth is not required" in status_text
    assert "no state value stored" in status_text
    assert "no authorization code stored" in status_text
    assert "no token exchange" in status_text
    assert "no token stored" in status_text
    assert "no secret stored" in status_text
    assert "no external service call" in status_text


def test_douyin_sandbox_oauth_boundary_is_placeholder_only(client: TestClient):
    boundary = get_boundary_from_list(client, "douyin_sandbox")

    assert boundary["provider_name"] == "Douyin Sandbox Placeholder"
    assert boundary["source_type"] == "sandbox"
    assert boundary["implementation_status"] == "planned"
    assert boundary["oauth_policy_status"] == "not_implemented"
    assert boundary["state_policy_status"] in {"required_planned", "not_implemented"}
    assert boundary["callback_policy_status"] in {"required_planned", "not_implemented"}
    assert boundary["csrf_protection_status"] == "required_planned"
    assert boundary["redirect_uri_policy_status"] == "required_planned"
    assert boundary["token_exchange_policy_status"] == "not_implemented"
    assert boundary["token_storage_policy_status"] == "not_implemented"
    assert boundary["error_redaction_policy_status"] == "active"
    assert boundary["audit_event_policy_status"] == "metadata_only"
    assert boundary["is_available"] is False
    assert boundary["is_real_provider"] is False
    assert boundary["requires_user_authorization"] is True
    assert boundary["can_start_oauth"] is False
    assert boundary["can_handle_callback"] is False
    assert boundary["can_exchange_token"] is False
    assert boundary["can_refresh_token"] is False
    assert boundary["can_revoke_token"] is False
    status_text = build_status_text(boundary)
    assert "placeholder OAuth boundary metadata only" in status_text
    assert "OAuth is not implemented" in status_text
    assert "OAuth callback route is not implemented" in status_text
    assert "OAuth state storage is not implemented" in status_text
    assert "authorization code is not stored" in status_text
    assert "tokens are not stored" in status_text
    assert "secrets are not stored" in status_text
    assert "no token exchange" in status_text
    assert "no real Douyin API call" in status_text
    assert "cannot be treated as douyin_real" in status_text


def test_douyin_real_oauth_boundary_is_future_placeholder_only(client: TestClient):
    boundary = get_boundary_from_list(client, "douyin_real")

    assert boundary["provider_name"] == "Douyin Real Placeholder"
    assert boundary["source_type"] == "real"
    assert boundary["implementation_status"] == "planned"
    assert boundary["oauth_policy_status"] == "not_implemented"
    assert boundary["state_policy_status"] in {"required_planned", "not_implemented"}
    assert boundary["callback_policy_status"] in {"required_planned", "not_implemented"}
    assert boundary["csrf_protection_status"] == "required_planned"
    assert boundary["redirect_uri_policy_status"] == "required_planned"
    assert boundary["token_exchange_policy_status"] == "not_implemented"
    assert boundary["token_storage_policy_status"] == "not_implemented"
    assert boundary["error_redaction_policy_status"] == "active"
    assert boundary["audit_event_policy_status"] == "metadata_only"
    assert boundary["is_available"] is False
    assert boundary["is_real_provider"] is True
    assert boundary["requires_user_authorization"] is True
    assert boundary["can_start_oauth"] is False
    assert boundary["can_handle_callback"] is False
    assert boundary["can_exchange_token"] is False
    assert boundary["can_refresh_token"] is False
    assert boundary["can_revoke_token"] is False
    status_text = build_status_text(boundary)
    assert "future real provider OAuth boundary placeholder only" in status_text
    assert "not real Douyin integration" in status_text
    assert "OAuth is not implemented" in status_text
    assert "OAuth callback route is not implemented" in status_text
    assert "OAuth state storage is not implemented" in status_text
    assert "no authorization code storage" in status_text
    assert "no access token or refresh token storage" in status_text
    assert "no API key storage" in status_text
    assert "no secret storage" in status_text
    assert "no token exchange" in status_text
    assert "no real metrics fetching" in status_text
    assert "no upload / publish / scheduling" in status_text


def test_get_each_provider_oauth_boundary_by_id(client: TestClient):
    for provider_id in ("fake_local", "douyin_sandbox", "douyin_real"):
        response = client.get(f"/api/provider-oauth-boundaries/{provider_id}")

        assert response.status_code == 200
        assert response.json()["provider_id"] == provider_id
        assert_response_has_no_sensitive_field_names(response.json())


def test_unknown_provider_oauth_boundary_returns_404_without_sensitive_terms(
    client: TestClient,
):
    response = client.get("/api/provider-oauth-boundaries/unknown")

    assert response.status_code == 404
    assert response.json()["detail"] == "Provider OAuth boundary metadata not found"
    response_text = response.text.lower()
    for term in SENSITIVE_ERROR_TERMS:
        assert term not in response_text


def test_provider_oauth_boundary_response_does_not_leak_environment_values(
    client: TestClient, monkeypatch
):
    environment_values = [
        "fake-access-value-from-env",
        "fake-client-secret-value-from-env",
        "fake-oauth-state-value-from-env",
        "fake-authorization-code-value-from-env",
        "fake-api-key-value-from-env",
        "fake-provider-secret-value-from-env",
    ]
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", environment_values[0])
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", environment_values[1])
    monkeypatch.setenv("OAUTH_STATE", environment_values[2])
    monkeypatch.setenv("AUTHORIZATION_CODE", environment_values[3])
    monkeypatch.setenv("DOUYIN_API_KEY", environment_values[4])
    monkeypatch.setenv("PROVIDER_SECRET", environment_values[5])

    response = client.get("/api/provider-oauth-boundaries")

    assert response.status_code == 200
    for value in environment_values:
        assert value not in response.text


def test_provider_oauth_boundaries_table_exists_without_sensitive_columns(
    client: TestClient,
):
    with sqlite3.connect(get_settings().database_path) as connection:
        columns = connection.execute(
            "PRAGMA table_info(provider_oauth_boundaries)"
        ).fetchall()

    column_names = {column[1] for column in columns}
    assert {
        "provider_id",
        "source_type",
        "oauth_policy_status",
        "state_policy_status",
        "callback_policy_status",
        "csrf_protection_status",
        "redirect_uri_policy_status",
        "token_exchange_policy_status",
        "token_storage_policy_status",
        "error_redaction_policy_status",
        "audit_event_policy_status",
        "safe_status_message",
        "last_status_change_reason",
        "created_at",
        "updated_at",
    }.issubset(column_names)
    assert column_names.isdisjoint(SENSITIVE_RESPONSE_FIELD_NAMES)


def test_unknown_provider_rows_are_not_returned_from_oauth_boundary_list(
    client: TestClient,
):
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            """
            INSERT INTO provider_oauth_boundaries (
                provider_id, source_type, oauth_policy_status, state_policy_status,
                callback_policy_status, csrf_protection_status,
                redirect_uri_policy_status, token_exchange_policy_status,
                token_storage_policy_status, error_redaction_policy_status,
                audit_event_policy_status, safe_status_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "unknown_provider",
                "real",
                "planned",
                "required_planned",
                "required_planned",
                "required_planned",
                "required_planned",
                "planned",
                "planned",
                "active",
                "metadata_only",
                "Unknown provider row should be ignored",
            ),
        )

    response = client.get("/api/provider-oauth-boundaries")

    assert response.status_code == 200
    provider_ids = [
        boundary["provider_id"] for boundary in response.json()["oauth_boundaries"]
    ]
    assert provider_ids == ["fake_local", "douyin_sandbox", "douyin_real"]
    assert "unknown_provider" not in provider_ids
    assert "Unknown provider row should be ignored" not in response.text


def test_known_provider_row_merges_non_sensitive_boundary_without_changing_registry(
    client: TestClient,
):
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            """
            INSERT INTO provider_oauth_boundaries (
                provider_id, source_type, oauth_policy_status, state_policy_status,
                callback_policy_status, csrf_protection_status,
                redirect_uri_policy_status, token_exchange_policy_status,
                token_storage_policy_status, error_redaction_policy_status,
                audit_event_policy_status, safe_status_message,
                last_status_change_reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "fake_local",
                "real",
                "planned",
                "required_planned",
                "required_planned",
                "active_metadata_only",
                "not_configured",
                "planned",
                "planned",
                "planned",
                "planned",
                "Non-sensitive local fake OAuth boundary override",
                "manual_test_metadata",
            ),
        )

    response = client.get("/api/provider-oauth-boundaries/fake_local")

    assert response.status_code == 200
    boundary = response.json()
    assert boundary["provider_id"] == "fake_local"
    assert boundary["provider_name"] == "Local Fake Provider"
    assert boundary["source_type"] == "fake_local"
    assert boundary["is_real_provider"] is False
    assert boundary["oauth_policy_status"] == "planned"
    assert boundary["state_policy_status"] == "required_planned"
    assert boundary["callback_policy_status"] == "required_planned"
    assert boundary["csrf_protection_status"] == "active_metadata_only"
    assert boundary["redirect_uri_policy_status"] == "not_configured"
    assert boundary["token_exchange_policy_status"] == "planned"
    assert boundary["token_storage_policy_status"] == "planned"
    assert boundary["error_redaction_policy_status"] == "planned"
    assert boundary["audit_event_policy_status"] == "planned"
    assert (
        boundary["safe_status_message"]
        == "Non-sensitive local fake OAuth boundary override"
    )
    assert boundary["last_status_change_reason"] == "manual_test_metadata"
    assert "not real Douyin data" in build_status_text(boundary)


def test_provider_oauth_boundary_api_does_not_enable_write_methods(
    client: TestClient,
):
    write_responses = [
        client.post("/api/provider-oauth-boundaries", json={}),
        client.put("/api/provider-oauth-boundaries/fake_local", json={}),
        client.patch("/api/provider-oauth-boundaries/fake_local", json={}),
        client.delete("/api/provider-oauth-boundaries/fake_local"),
    ]

    for response in write_responses:
        assert response.status_code < 200 or response.status_code >= 300


def test_batch_does_not_add_real_oauth_or_lifecycle_routes(client: TestClient):
    forbidden_paths = [
        "/api/oauth/start",
        "/api/auth/douyin",
        "/api/provider-oauth-callback/douyin",
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
    providers_response = client.get("/api/providers")
    connections_response = client.get("/api/provider-connections")
    credential_references_response = client.get("/api/provider-credential-references")
    security_audit_response = client.get("/api/provider-security-audit-events")

    assert providers_response.status_code == 200
    assert connections_response.status_code == 200
    assert credential_references_response.status_code == 200
    assert security_audit_response.status_code == 200
    assert [
        provider["provider_id"] for provider in providers_response.json()["providers"]
    ] == ["fake_local", "douyin_sandbox", "douyin_real"]
    assert [
        connection["provider_id"]
        for connection in connections_response.json()["connections"]
    ] == ["fake_local", "douyin_sandbox", "douyin_real"]
    assert [
        reference["provider_id"]
        for reference in credential_references_response.json()[
            "credential_references"
        ]
    ] == ["fake_local", "douyin_sandbox", "douyin_real"]
    assert list(security_audit_response.json().keys()) == ["audit_events"]


def get_boundary_from_list(client: TestClient, provider_id: str) -> dict:
    response = client.get("/api/provider-oauth-boundaries")
    assert response.status_code == 200
    boundaries = {
        boundary["provider_id"]: boundary
        for boundary in response.json()["oauth_boundaries"]
    }
    return boundaries[provider_id]


def build_status_text(boundary: dict) -> str:
    return " ".join([boundary["safe_status_message"], *boundary["boundary_notes"]])


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
