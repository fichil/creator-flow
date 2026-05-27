import sqlite3

from fastapi.testclient import TestClient

from app.core.config import get_settings


SENSITIVE_RESPONSE_FIELD_NAMES = {
    "access_token",
    "refresh_token",
    "token_value",
    "api_key",
    "client_secret",
    "authorization_code",
    "credential_material",
    "encrypted_credential",
    "raw_response",
    "private_key",
    "oauth_code",
    "password",
}

SENSITIVE_ERROR_TERMS = {
    "token",
    "secret",
    "credential",
    "authorization_code",
    "api_key",
    "client_secret",
}


def test_list_provider_connection_states_returns_stable_metadata(client: TestClient):
    response = client.get("/api/provider-connections")

    assert response.status_code == 200
    body = response.json()
    assert list(body.keys()) == ["connections"]
    assert [connection["provider_id"] for connection in body["connections"]] == [
        "fake_local",
        "douyin_sandbox",
        "douyin_real",
    ]
    assert_response_has_no_sensitive_field_names(body)


def test_fake_local_connection_state_is_not_required_and_non_sensitive(client: TestClient):
    connection_state = get_connection_from_list(client, "fake_local")

    assert connection_state["provider_name"] == "Local Fake Provider"
    assert connection_state["source_type"] == "fake_local"
    assert connection_state["implementation_status"] == "available_local_fake"
    assert connection_state["connection_status"] == "not_required"
    assert connection_state["authorization_status"] == "not_required"
    assert connection_state["sensitive_storage_status"] == "none"
    assert connection_state["is_available"] is True
    assert connection_state["is_real_provider"] is False
    assert connection_state["requires_user_authorization"] is False
    assert connection_state["can_connect"] is False
    assert connection_state["can_refresh"] is False
    assert connection_state["can_revoke"] is False
    assert connection_state["can_disconnect"] is False
    status_text = build_status_text(connection_state)
    assert "not real Douyin data" in status_text
    assert "no OAuth required" in status_text
    assert "no tokens stored" in status_text
    assert "no external service call" in status_text


def test_douyin_sandbox_connection_state_is_placeholder_only(client: TestClient):
    connection_state = get_connection_from_list(client, "douyin_sandbox")

    assert connection_state["provider_name"] == "Douyin Sandbox Placeholder"
    assert connection_state["source_type"] == "sandbox"
    assert connection_state["implementation_status"] == "planned"
    assert connection_state["connection_status"] == "not_connected"
    assert connection_state["authorization_status"] in {"not_implemented", "not_authorized"}
    assert connection_state["sensitive_storage_status"] == "not_implemented"
    assert connection_state["is_available"] is False
    assert connection_state["is_real_provider"] is False
    assert connection_state["requires_user_authorization"] is True
    assert connection_state["can_connect"] is False
    assert connection_state["can_refresh"] is False
    assert connection_state["can_revoke"] is False
    assert connection_state["can_disconnect"] is False
    status_text = build_status_text(connection_state)
    assert "placeholder only" in status_text
    assert "OAuth is not implemented" in status_text
    assert "tokens are not stored" in status_text
    assert "no real Douyin API call" in status_text
    assert "cannot be treated as douyin_real" in status_text


def test_douyin_real_connection_state_is_future_placeholder_only(client: TestClient):
    connection_state = get_connection_from_list(client, "douyin_real")

    assert connection_state["provider_name"] == "Douyin Real Placeholder"
    assert connection_state["source_type"] == "real"
    assert connection_state["implementation_status"] == "planned"
    assert connection_state["connection_status"] == "not_connected"
    assert connection_state["authorization_status"] in {"not_implemented", "not_authorized"}
    assert connection_state["sensitive_storage_status"] == "not_implemented"
    assert connection_state["is_available"] is False
    assert connection_state["is_real_provider"] is True
    assert connection_state["requires_user_authorization"] is True
    assert connection_state["can_connect"] is False
    assert connection_state["can_refresh"] is False
    assert connection_state["can_revoke"] is False
    assert connection_state["can_disconnect"] is False
    status_text = build_status_text(connection_state)
    assert "future real provider placeholder only" in status_text
    assert "not real Douyin integration" in status_text
    assert "no OAuth implementation" in status_text
    assert "no token storage" in status_text
    assert "no real metrics fetching" in status_text
    assert "no upload / publish / scheduling" in status_text


def test_get_each_provider_connection_by_id(client: TestClient):
    for provider_id in ("fake_local", "douyin_sandbox", "douyin_real"):
        response = client.get(f"/api/provider-connections/{provider_id}")

        assert response.status_code == 200
        assert response.json()["provider_id"] == provider_id
        assert_response_has_no_sensitive_field_names(response.json())


def test_unknown_provider_connection_returns_404_without_sensitive_terms(client: TestClient):
    response = client.get("/api/provider-connections/unknown")

    assert response.status_code == 404
    assert response.json()["detail"] == "Provider connection state not found"
    response_text = response.text.lower()
    for term in SENSITIVE_ERROR_TERMS:
        assert term not in response_text


def test_provider_connection_state_response_does_not_leak_environment_values(
    client: TestClient, monkeypatch
):
    environment_values = [
        "fake-access-value-from-env",
        "fake-client-secret-value-from-env",
        "fake-api-key-value-from-env",
        "fake-refresh-value-from-env",
    ]
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", environment_values[0])
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", environment_values[1])
    monkeypatch.setenv("DOUYIN_API_KEY", environment_values[2])
    monkeypatch.setenv("DOUYIN_REFRESH_TOKEN", environment_values[3])

    response = client.get("/api/provider-connections")

    assert response.status_code == 200
    for value in environment_values:
        assert value not in response.text


def test_provider_connection_states_table_exists_without_sensitive_columns(client: TestClient):
    with sqlite3.connect(get_settings().database_path) as connection:
        columns = connection.execute("PRAGMA table_info(provider_connection_states)").fetchall()

    column_names = {column[1] for column in columns}
    assert {
        "provider_id",
        "source_type",
        "connection_status",
        "authorization_status",
        "sensitive_storage_status",
        "safe_status_message",
        "last_status_change_reason",
        "created_at",
        "updated_at",
    }.issubset(column_names)
    assert column_names.isdisjoint(SENSITIVE_RESPONSE_FIELD_NAMES)


def test_unknown_provider_rows_are_not_returned_from_connection_state_list(client: TestClient):
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            """
            INSERT INTO provider_connection_states (
                provider_id, source_type, connection_status, authorization_status,
                sensitive_storage_status, safe_status_message
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "unknown_provider",
                "real",
                "connected",
                "authorized",
                "reference_only",
                "Unknown provider row should be ignored",
            ),
        )

    response = client.get("/api/provider-connections")

    assert response.status_code == 200
    body = response.json()
    provider_ids = [connection["provider_id"] for connection in body["connections"]]
    assert provider_ids == ["fake_local", "douyin_sandbox", "douyin_real"]
    assert "unknown_provider" not in provider_ids
    assert "Unknown provider row should be ignored" not in response.text


def test_known_provider_row_merges_non_sensitive_state_without_changing_registry_boundary(
    client: TestClient,
):
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            """
            INSERT INTO provider_connection_states (
                provider_id, source_type, connection_status, authorization_status,
                sensitive_storage_status, safe_status_message, last_status_change_reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "fake_local",
                "real",
                "provider_error",
                "authorization_failed",
                "reference_only",
                "Non-sensitive local fake status override",
                "manual_test_metadata",
            ),
        )

    response = client.get("/api/provider-connections/fake_local")

    assert response.status_code == 200
    connection_state = response.json()
    assert connection_state["provider_id"] == "fake_local"
    assert connection_state["source_type"] == "fake_local"
    assert connection_state["is_real_provider"] is False
    assert connection_state["connection_status"] == "provider_error"
    assert connection_state["authorization_status"] == "authorization_failed"
    assert connection_state["sensitive_storage_status"] == "reference_only"
    assert connection_state["safe_status_message"] == "Non-sensitive local fake status override"
    assert connection_state["last_status_change_reason"] == "manual_test_metadata"
    assert "not real Douyin data" in build_status_text(connection_state)


def test_provider_connection_state_api_does_not_enable_write_methods(client: TestClient):
    write_responses = [
        client.post("/api/provider-connections", json={}),
        client.put("/api/provider-connections/fake_local", json={}),
        client.patch("/api/provider-connections/fake_local", json={}),
        client.delete("/api/provider-connections/fake_local"),
    ]

    for response in write_responses:
        assert response.status_code < 200 or response.status_code >= 300


def test_provider_registry_route_still_returns_existing_metadata(client: TestClient):
    response = client.get("/api/providers")

    assert response.status_code == 200
    assert [provider["provider_id"] for provider in response.json()["providers"]] == [
        "fake_local",
        "douyin_sandbox",
        "douyin_real",
    ]


def get_connection_from_list(client: TestClient, provider_id: str) -> dict:
    response = client.get("/api/provider-connections")
    assert response.status_code == 200
    connections = {
        connection["provider_id"]: connection for connection in response.json()["connections"]
    }
    return connections[provider_id]


def build_status_text(connection_state: dict) -> str:
    return " ".join(
        [connection_state["safe_status_message"], *connection_state["boundary_notes"]]
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
