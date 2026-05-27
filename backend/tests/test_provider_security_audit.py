import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.providers.security_audit import record_provider_security_audit_event


SENSITIVE_RESPONSE_FIELD_NAMES = {
    "access_token",
    "refresh_token",
    "token_value",
    "api_key",
    "secret_value",
    "client_secret",
    "authorization_code",
    "oauth_client_secret",
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
}


def test_list_provider_security_audit_events_empty_table_returns_empty_list(
    client: TestClient,
):
    response = client.get("/api/provider-security-audit-events")

    assert response.status_code == 200
    assert response.json() == {"audit_events": []}


def test_provider_security_audit_events_table_exists_without_sensitive_columns(
    client: TestClient,
):
    with sqlite3.connect(get_settings().database_path) as connection:
        columns = connection.execute(
            "PRAGMA table_info(provider_security_audit_events)"
        ).fetchall()

    column_names = {column[1] for column in columns}
    assert {
        "audit_event_id",
        "provider_id",
        "source_type",
        "event_type",
        "event_status",
        "event_severity",
        "actor_type",
        "redaction_status",
        "safe_event_message",
        "safe_metadata_json",
        "boundary_notes_json",
        "created_at",
    }.issubset(column_names)
    assert column_names.isdisjoint(SENSITIVE_RESPONSE_FIELD_NAMES)


def test_record_fake_local_security_audit_event_returns_redacted_metadata(
    client: TestClient,
):
    event = record_event(
        provider_id="fake_local",
        event_type="boundary_initialized",
        event_status="recorded",
        event_severity="info",
        actor_type="system",
        message="fake_local provider boundary initialized",
        metadata={"status": "ready", "source": "local fake"},
    )

    response = client.get("/api/provider-security-audit-events")

    assert response.status_code == 200
    body = response.json()
    assert [item["audit_event_id"] for item in body["audit_events"]] == [
        event.audit_event_id
    ]
    audit_event = body["audit_events"][0]
    assert audit_event["provider_id"] == "fake_local"
    assert audit_event["provider_name"] == "Local Fake Provider"
    assert audit_event["source_type"] == "fake_local"
    assert audit_event["implementation_status"] == "available_local_fake"
    assert audit_event["event_type"] == "boundary_initialized"
    assert audit_event["event_status"] == "recorded"
    assert audit_event["event_severity"] == "info"
    assert audit_event["actor_type"] == "system"
    assert audit_event["redaction_status"] == "active"
    assert audit_event["safe_event_message"] == "fake_local provider boundary initialized"
    assert audit_event["safe_metadata"] == {"source": "local fake", "status": "ready"}
    status_text = build_status_text(audit_event)
    assert "local fake/demo/test audit metadata only" in status_text
    assert "not real Douyin data" in status_text
    assert "no OAuth required" in status_text
    assert "no token stored" in status_text
    assert "no secret stored" in status_text
    assert "no external service call" in status_text
    assert_response_has_no_sensitive_field_names(body)


def test_sandbox_and_real_security_audit_events_keep_source_separation(
    client: TestClient,
):
    sandbox_event = record_event(
        provider_id="douyin_sandbox",
        event_type="credential_reference_checked",
        event_status="planned",
        event_severity="warning",
        actor_type="internal",
        message="sandbox placeholder metadata checked",
    )
    real_event = record_event(
        provider_id="douyin_real",
        event_type="authorization_status_checked",
        event_status="not_implemented",
        event_severity="security",
        actor_type="user_placeholder",
        message="real placeholder authorization boundary checked",
    )

    sandbox_response = client.get(
        f"/api/provider-security-audit-events/{sandbox_event.audit_event_id}"
    )
    real_response = client.get(
        f"/api/provider-security-audit-events/{real_event.audit_event_id}"
    )

    assert sandbox_response.status_code == 200
    sandbox = sandbox_response.json()
    assert sandbox["provider_id"] == "douyin_sandbox"
    assert sandbox["source_type"] == "sandbox"
    sandbox_text = build_status_text(sandbox)
    assert "placeholder audit metadata only" in sandbox_text
    assert "OAuth is not implemented" in sandbox_text
    assert "tokens are not stored" in sandbox_text
    assert "secrets are not stored" in sandbox_text
    assert "no real Douyin API call" in sandbox_text
    assert "cannot be treated as douyin_real" in sandbox_text

    assert real_response.status_code == 200
    real = real_response.json()
    assert real["provider_id"] == "douyin_real"
    assert real["source_type"] == "real"
    real_text = build_status_text(real)
    assert "future real provider placeholder audit metadata only" in real_text
    assert "not real Douyin integration" in real_text
    assert "OAuth is not implemented" in real_text
    assert "no access token or refresh token storage" in real_text
    assert "no API key storage" in real_text
    assert "no secret storage" in real_text
    assert "no real metrics fetching" in real_text
    assert "no upload / publish / scheduling" in real_text


def test_provider_security_audit_list_ignores_unknown_provider_rows(
    client: TestClient,
):
    record_event(
        provider_id="fake_local",
        event_type="connection_status_checked",
        event_status="recorded",
        event_severity="info",
        actor_type="system",
        message="known provider event",
    )
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            """
            INSERT INTO provider_security_audit_events (
                audit_event_id, provider_id, source_type, event_type, event_status,
                event_severity, actor_type, redaction_status, safe_event_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "unknown-audit-event",
                "unknown_provider",
                "real",
                "boundary_initialized",
                "recorded",
                "info",
                "system",
                "active",
                "Unknown provider row should be ignored",
            ),
        )

    response = client.get("/api/provider-security-audit-events")

    assert response.status_code == 200
    response_text = response.text
    assert "fake_local" in response_text
    assert "unknown_provider" not in response_text
    assert "Unknown provider row should be ignored" not in response_text


def test_record_provider_security_audit_event_rejects_unknown_provider(
    client: TestClient,
):
    with pytest.raises(ValueError, match="Unknown provider"):
        record_event(
            provider_id="unknown_provider",
            event_type="boundary_initialized",
            event_status="recorded",
            event_severity="info",
            actor_type="system",
            message="should not be written",
        )

    with sqlite3.connect(get_settings().database_path) as connection:
        rows = connection.execute(
            "SELECT provider_id FROM provider_security_audit_events"
        ).fetchall()
    assert rows == []


def test_provider_security_audit_list_supports_provider_filter_and_limit(
    client: TestClient,
):
    fake_event = record_event(
        provider_id="fake_local",
        event_type="connection_status_checked",
        event_status="recorded",
        event_severity="info",
        actor_type="system",
        message="fake event",
    )
    record_event(
        provider_id="douyin_sandbox",
        event_type="credential_reference_checked",
        event_status="planned",
        event_severity="warning",
        actor_type="internal",
        message="sandbox event",
    )
    record_event(
        provider_id="douyin_real",
        event_type="provider_error",
        event_status="not_implemented",
        event_severity="error",
        actor_type="internal",
        message="real event",
    )

    filter_response = client.get(
        "/api/provider-security-audit-events?provider_id=fake_local"
    )
    limited_response = client.get("/api/provider-security-audit-events?limit=2")
    clamped_response = client.get("/api/provider-security-audit-events?limit=500")
    unknown_filter_response = client.get(
        "/api/provider-security-audit-events?provider_id=unknown"
    )

    assert filter_response.status_code == 200
    assert [
        event["audit_event_id"] for event in filter_response.json()["audit_events"]
    ] == [fake_event.audit_event_id]
    assert limited_response.status_code == 200
    assert len(limited_response.json()["audit_events"]) == 2
    assert clamped_response.status_code == 200
    assert len(clamped_response.json()["audit_events"]) == 3
    assert unknown_filter_response.status_code == 404
    assert unknown_filter_response.json()["detail"] == (
        "Provider security audit provider not found"
    )
    for term in SENSITIVE_ERROR_TERMS:
        assert term not in unknown_filter_response.text.lower()


def test_get_provider_security_audit_event_by_id_and_unknown_404(
    client: TestClient,
):
    event = record_event(
        provider_id="fake_local",
        event_type="redaction_applied",
        event_status="redacted",
        event_severity="security",
        actor_type="internal",
        message="redaction helper applied",
    )

    response = client.get(f"/api/provider-security-audit-events/{event.audit_event_id}")
    unknown_response = client.get("/api/provider-security-audit-events/unknown")

    assert response.status_code == 200
    assert response.json()["audit_event_id"] == event.audit_event_id
    assert_response_has_no_sensitive_field_names(response.json())
    assert unknown_response.status_code == 404
    assert unknown_response.json()["detail"] == "Provider security audit event not found"
    for term in SENSITIVE_ERROR_TERMS:
        assert term not in unknown_response.text.lower()


def test_provider_security_audit_redacts_message_and_nested_metadata(
    client: TestClient,
):
    event = record_event(
        provider_id="fake_local",
        event_type="redaction_applied",
        event_status="redacted",
        event_severity="security",
        actor_type="internal",
        message=(
            "access_token=fake-access-token refresh_token=fake-refresh-token "
            "api_key=fake-api-key client_secret=fake-client-secret "
            "authorization_code=fake-auth-code Bearer fake-bearer-token"
        ),
        metadata={
            "access_token": "fake-access-token",
            "nested": {
                "api_key": "fake-api-key",
                "client_secret": "fake-client-secret",
                "credential_material": "fake-credential-material",
                "safe": "visible",
            },
        },
    )

    response = client.get(f"/api/provider-security-audit-events/{event.audit_event_id}")

    assert response.status_code == 200
    audit_event = response.json()
    assert audit_event["redaction_status"] == "redacted"
    assert "redacted_value=[REDACTED]" in audit_event["safe_event_message"]
    assert "Bearer [REDACTED]" in audit_event["safe_event_message"]
    safe_metadata = audit_event["safe_metadata"]
    assert safe_metadata["redacted_field"] == "[REDACTED]"
    assert safe_metadata["nested"]["redacted_field"] == "[REDACTED]"
    assert safe_metadata["nested"]["redacted_field_2"] == "[REDACTED]"
    assert safe_metadata["nested"]["redacted_field_3"] == "[REDACTED]"
    assert safe_metadata["nested"]["safe"] == "visible"
    for leaked_value in (
        "fake-access-token",
        "fake-refresh-token",
        "fake-api-key",
        "fake-client-secret",
        "fake-auth-code",
        "fake-bearer-token",
        "fake-credential-material",
    ):
        assert leaked_value not in response.text
    assert_response_has_no_sensitive_field_names(audit_event)


def test_provider_security_audit_response_does_not_leak_environment_values(
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
    record_event(
        provider_id="fake_local",
        event_type="boundary_initialized",
        event_status="recorded",
        event_severity="info",
        actor_type="system",
        message="safe event without environment reads",
    )

    response = client.get("/api/provider-security-audit-events")

    assert response.status_code == 200
    for value in environment_values:
        assert value not in response.text


def test_provider_security_audit_api_does_not_enable_write_methods(
    client: TestClient,
):
    write_responses = [
        client.post("/api/provider-security-audit-events", json={}),
        client.put("/api/provider-security-audit-events/some-id", json={}),
        client.patch("/api/provider-security-audit-events/some-id", json={}),
        client.delete("/api/provider-security-audit-events/some-id"),
    ]

    for response in write_responses:
        assert response.status_code < 200 or response.status_code >= 300


def test_existing_provider_metadata_routes_still_return_existing_metadata(
    client: TestClient,
):
    providers_response = client.get("/api/providers")
    connections_response = client.get("/api/provider-connections")
    credential_references_response = client.get("/api/provider-credential-references")

    assert providers_response.status_code == 200
    assert connections_response.status_code == 200
    assert credential_references_response.status_code == 200
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
    assert [
        reference["provider_id"]
        for reference in credential_references_response.json()["credential_references"]
    ] == [
        "fake_local",
        "douyin_sandbox",
        "douyin_real",
    ]


def record_event(**kwargs):
    connection = sqlite3.connect(get_settings().database_path)
    connection.row_factory = sqlite3.Row
    try:
        return record_provider_security_audit_event(connection, **kwargs)
    finally:
        connection.close()


def build_status_text(audit_event: dict) -> str:
    return " ".join(
        [
            audit_event["safe_event_message"],
            *audit_event["boundary_notes"],
            str(audit_event["safe_metadata"]),
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
