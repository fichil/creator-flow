import sqlite3

from fastapi.testclient import TestClient

from app.core.config import get_settings


SENSITIVE_RESPONSE_FIELD_NAMES = {
    "access_token",
    "refresh_token",
    "token_value",
    "api_key",
    "secret",
    "secret_value",
    "client_secret",
    "authorization_code",
    "credential_material",
    "encrypted_credential",
    "raw_response",
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
}


def test_list_provider_credential_references_returns_stable_metadata(
    client: TestClient,
):
    response = client.get("/api/provider-credential-references")

    assert response.status_code == 200
    body = response.json()
    assert list(body.keys()) == ["credential_references"]
    assert [
        reference["provider_id"] for reference in body["credential_references"]
    ] == [
        "fake_local",
        "douyin_sandbox",
        "douyin_real",
    ]
    assert_response_has_no_sensitive_field_names(body)


def test_fake_local_credential_reference_is_not_required_and_non_sensitive(
    client: TestClient,
):
    reference = get_reference_from_list(client, "fake_local")

    assert reference["provider_name"] == "Local Fake Provider"
    assert reference["source_type"] == "fake_local"
    assert reference["implementation_status"] == "available_local_fake"
    assert reference["reference_kind"] == "none_required"
    assert reference["reference_status"] == "not_required"
    assert reference["storage_status"] == "none"
    assert reference["redaction_policy_status"] in {"active", "not_required"}
    assert reference["is_available"] is True
    assert reference["is_real_provider"] is False
    assert reference["requires_user_authorization"] is False
    status_text = build_status_text(reference)
    assert "not real Douyin data" in status_text
    assert "no OAuth required" in status_text
    assert "no token stored" in status_text
    assert "no secret stored" in status_text
    assert "no credential material stored" in status_text
    assert "no external service call" in status_text


def test_douyin_sandbox_credential_reference_is_placeholder_only(
    client: TestClient,
):
    reference = get_reference_from_list(client, "douyin_sandbox")

    assert reference["provider_name"] == "Douyin Sandbox Placeholder"
    assert reference["source_type"] == "sandbox"
    assert reference["implementation_status"] == "planned"
    assert reference["reference_kind"] in {
        "oauth_placeholder",
        "credential_reference_placeholder",
    }
    assert reference["reference_status"] == "not_implemented"
    assert reference["storage_status"] == "not_implemented"
    assert reference["redaction_policy_status"] == "active"
    assert reference["is_available"] is False
    assert reference["is_real_provider"] is False
    assert reference["requires_user_authorization"] is True
    status_text = build_status_text(reference)
    assert "placeholder only" in status_text
    assert "OAuth is not implemented" in status_text
    assert "tokens are not stored" in status_text
    assert "secrets are not stored" in status_text
    assert "credential material is not stored" in status_text
    assert "no real Douyin API call" in status_text
    assert "cannot be treated as douyin_real" in status_text


def test_douyin_real_credential_reference_is_future_placeholder_only(
    client: TestClient,
):
    reference = get_reference_from_list(client, "douyin_real")

    assert reference["provider_name"] == "Douyin Real Placeholder"
    assert reference["source_type"] == "real"
    assert reference["implementation_status"] == "planned"
    assert reference["reference_kind"] in {
        "oauth_placeholder",
        "credential_reference_placeholder",
    }
    assert reference["reference_status"] == "not_implemented"
    assert reference["storage_status"] == "not_implemented"
    assert reference["redaction_policy_status"] == "active"
    assert reference["is_available"] is False
    assert reference["is_real_provider"] is True
    assert reference["requires_user_authorization"] is True
    status_text = build_status_text(reference)
    assert "future real provider placeholder only" in status_text
    assert "not real Douyin integration" in status_text
    assert "no OAuth implementation" in status_text
    assert "no token storage" in status_text
    assert "no API key storage" in status_text
    assert "no secret storage" in status_text
    assert "no credential material storage" in status_text
    assert "no real metrics fetching" in status_text
    assert "no upload / publish / scheduling" in status_text


def test_get_each_provider_credential_reference_by_id(client: TestClient):
    for provider_id in ("fake_local", "douyin_sandbox", "douyin_real"):
        response = client.get(f"/api/provider-credential-references/{provider_id}")

        assert response.status_code == 200
        assert response.json()["provider_id"] == provider_id
        assert_response_has_no_sensitive_field_names(response.json())


def test_unknown_provider_credential_reference_returns_404_without_sensitive_terms(
    client: TestClient,
):
    response = client.get("/api/provider-credential-references/unknown")

    assert response.status_code == 404
    assert response.json()["detail"] == "Provider reference metadata not found"
    response_text = response.text.lower()
    for term in SENSITIVE_ERROR_TERMS:
        assert term not in response_text


def test_provider_credential_reference_response_does_not_leak_environment_values(
    client: TestClient, monkeypatch
):
    environment_values = [
        "fake-access-value-from-env",
        "fake-client-secret-value-from-env",
        "fake-api-key-value-from-env",
        "fake-provider-secret-value-from-env",
    ]
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", environment_values[0])
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", environment_values[1])
    monkeypatch.setenv("DOUYIN_API_KEY", environment_values[2])
    monkeypatch.setenv("PROVIDER_SECRET", environment_values[3])

    response = client.get("/api/provider-credential-references")

    assert response.status_code == 200
    for value in environment_values:
        assert value not in response.text


def test_provider_credential_references_table_exists_without_sensitive_columns(
    client: TestClient,
):
    with sqlite3.connect(get_settings().database_path) as connection:
        columns = connection.execute(
            "PRAGMA table_info(provider_credential_references)"
        ).fetchall()

    column_names = {column[1] for column in columns}
    assert {
        "reference_id",
        "provider_id",
        "source_type",
        "reference_kind",
        "reference_status",
        "storage_status",
        "redaction_policy_status",
        "safe_display_name",
        "safe_status_message",
        "last_status_change_reason",
        "created_at",
        "updated_at",
    }.issubset(column_names)
    assert column_names.isdisjoint(SENSITIVE_RESPONSE_FIELD_NAMES)


def test_unknown_provider_rows_are_not_returned_from_credential_reference_list(
    client: TestClient,
):
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            """
            INSERT INTO provider_credential_references (
                reference_id, provider_id, source_type, reference_kind,
                reference_status, storage_status, redaction_policy_status,
                safe_display_name, safe_status_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "unknown-reference",
                "unknown_provider",
                "real",
                "credential_reference_placeholder",
                "reference_only",
                "reference_only",
                "active",
                "Unknown provider reference",
                "Unknown provider row should be ignored",
            ),
        )

    response = client.get("/api/provider-credential-references")

    assert response.status_code == 200
    body = response.json()
    provider_ids = [
        reference["provider_id"] for reference in body["credential_references"]
    ]
    assert provider_ids == ["fake_local", "douyin_sandbox", "douyin_real"]
    assert "unknown_provider" not in provider_ids
    assert "Unknown provider row should be ignored" not in response.text


def test_known_provider_row_merges_non_sensitive_reference_without_changing_registry_boundary(
    client: TestClient,
):
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            """
            INSERT INTO provider_credential_references (
                reference_id, provider_id, source_type, reference_kind,
                reference_status, storage_status, redaction_policy_status,
                safe_display_name, safe_status_message, last_status_change_reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "fake-local-reference",
                "fake_local",
                "real",
                "provider_secret_placeholder",
                "reference_only",
                "reference_only",
                "planned",
                "Non-sensitive local fake reference",
                "Non-sensitive local fake reference override",
                "manual_test_metadata",
            ),
        )

    response = client.get("/api/provider-credential-references/fake_local")

    assert response.status_code == 200
    reference = response.json()
    assert reference["provider_id"] == "fake_local"
    assert reference["provider_name"] == "Local Fake Provider"
    assert reference["source_type"] == "fake_local"
    assert reference["is_real_provider"] is False
    assert reference["reference_kind"] == "provider_secret_placeholder"
    assert reference["reference_status"] == "reference_only"
    assert reference["storage_status"] == "reference_only"
    assert reference["redaction_policy_status"] == "planned"
    assert reference["safe_display_name"] == "Non-sensitive local fake reference"
    assert reference["safe_status_message"] == "Non-sensitive local fake reference override"
    assert reference["last_status_change_reason"] == "manual_test_metadata"
    assert "not real Douyin data" in build_status_text(reference)


def test_provider_credential_reference_api_does_not_enable_write_methods(
    client: TestClient,
):
    write_responses = [
        client.post("/api/provider-credential-references", json={}),
        client.put("/api/provider-credential-references/fake_local", json={}),
        client.patch("/api/provider-credential-references/fake_local", json={}),
        client.delete("/api/provider-credential-references/fake_local"),
    ]

    for response in write_responses:
        assert response.status_code < 200 or response.status_code >= 300


def test_existing_provider_registry_and_connection_state_routes_still_return_metadata(
    client: TestClient,
):
    providers_response = client.get("/api/providers")
    connections_response = client.get("/api/provider-connections")

    assert providers_response.status_code == 200
    assert connections_response.status_code == 200
    assert [
        provider["provider_id"] for provider in providers_response.json()["providers"]
    ] == [
        "fake_local",
        "douyin_sandbox",
        "douyin_real",
    ]
    assert [
        connection["provider_id"]
        for connection in connections_response.json()["connections"]
    ] == [
        "fake_local",
        "douyin_sandbox",
        "douyin_real",
    ]


def get_reference_from_list(client: TestClient, provider_id: str) -> dict:
    response = client.get("/api/provider-credential-references")
    assert response.status_code == 200
    references = {
        reference["provider_id"]: reference
        for reference in response.json()["credential_references"]
    }
    return references[provider_id]


def build_status_text(reference: dict) -> str:
    return " ".join([reference["safe_status_message"], *reference["boundary_notes"]])


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
