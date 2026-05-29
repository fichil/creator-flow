import importlib.util
import json
import socket
import sqlite3
import urllib.request
from dataclasses import asdict

import pytest

from app.core.config import get_settings
from app.db.database import connect_db
from app.main import app
from app.providers.credential_storage import (
    CredentialStorageBoundaryStatus,
    create_credential_reference_boundary,
)
from app.providers.oauth_state import create_oauth_state_metadata
from app.providers.token_exchange import simulate_token_exchange_boundary


FAKE_AUTHORIZATION_CODE = "fake_authorization_code_for_credential_test"
FAKE_ACCESS_TOKEN_VALUE = "fake-access-token-value"
FAKE_REFRESH_TOKEN_VALUE = "fake-refresh-token-value"
FAKE_SECRET_VALUE = "fake-secret-value"
FAKE_CREDENTIAL_VALUE = "fake-credential-value"
FAKE_COOKIE_VALUE = "fake-cookie-value"
FAKE_SESSION_VALUE = "fake-session-value"
FAKE_BEARER_VALUE = "fake-bearer-value"
FAKE_RAW_STATE_VALUE = "fake_raw_oauth_state_value"
FAKE_RAW_REQUEST_VALUE = "fake-raw-request-value"
FAKE_RAW_RESPONSE_VALUE = "fake-raw-response-value"

FORBIDDEN_DB_COLUMNS = {
    "authorization_code",
    "raw_authorization_code",
    "raw_state",
    "state_value",
    "oauth_state",
    "access_token",
    "refresh_token",
    "token",
    "secret",
    "credential",
    "client_secret",
    "cookie",
    "session",
    "bearer",
    "raw_request",
    "raw_response",
}

FORBIDDEN_MATERIAL_VALUES = {
    FAKE_AUTHORIZATION_CODE,
    FAKE_ACCESS_TOKEN_VALUE,
    FAKE_REFRESH_TOKEN_VALUE,
    FAKE_SECRET_VALUE,
    FAKE_CREDENTIAL_VALUE,
    FAKE_COOKIE_VALUE,
    FAKE_SESSION_VALUE,
    FAKE_BEARER_VALUE,
    FAKE_RAW_STATE_VALUE,
    FAKE_RAW_REQUEST_VALUE,
    FAKE_RAW_RESPONSE_VALUE,
}


def test_provider_credential_reference_schema_exists_without_sensitive_columns(client):
    with sqlite3.connect(get_settings().database_path) as connection:
        columns = connection.execute(
            "PRAGMA table_info(provider_credential_references)"
        ).fetchall()
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

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
    assert column_names.isdisjoint(FORBIDDEN_DB_COLUMNS)
    assert "provider_credential_payloads" not in tables
    assert "provider_encrypted_credentials" not in tables


def test_valid_fake_gated_exchange_creates_metadata_only_reference(client):
    with connect_db(get_settings()) as connection:
        exchange = create_fake_gated_exchange(connection, "douyin_sandbox")

        result = create_credential_reference_boundary(
            connection,
            "douyin_sandbox",
            token_exchange_result=exchange,
        )
        row = fetch_reference_row(connection, result.credential_reference_id)

    assert result.status == CredentialStorageBoundaryStatus.CREDENTIAL_REFERENCE_CREATED.value
    assert result.provider_id == "douyin_sandbox"
    assert result.source_type == "sandbox"
    assert result.storage_mode == "metadata_reference_only"
    assert result.credential_storage_enabled is False
    assert result.encrypted_payload_stored is False
    assert result.external_storage_performed is False
    assert result.sandbox_fallback_performed is False
    assert row["provider_id"] == "douyin_sandbox"
    assert row["source_type"] == "sandbox"
    assert row["reference_kind"] == "credential_reference_placeholder"
    assert row["reference_status"] == "reference_only"
    assert row["storage_status"] == "reference_only"
    assert_no_material_values(result)
    assert_no_material_values(dict(row))


def test_missing_token_exchange_result_returns_storage_disabled(client):
    with connect_db(get_settings()) as connection:
        result = create_credential_reference_boundary(
            connection,
            "douyin_sandbox",
            token_exchange_result=None,
        )

    assert result.status == CredentialStorageBoundaryStatus.CREDENTIAL_STORAGE_DISABLED.value
    assert result.credential_reference_id is None
    assert result.credential_storage_enabled is False
    assert result.encrypted_payload_stored is False


def test_malformed_exchange_metadata_is_rejected(client):
    with connect_db(get_settings()) as connection:
        result = create_credential_reference_boundary(
            connection,
            "douyin_sandbox",
            token_exchange_result={
                "status": "exchange_simulated",
                "provider_id": "douyin_sandbox",
                "source_type": "sandbox",
                "external_exchange_performed": False,
            },
        )

    assert result.status == CredentialStorageBoundaryStatus.CREDENTIAL_STORAGE_REJECTED.value
    assert result.credential_reference_id is None


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("access_token", FAKE_ACCESS_TOKEN_VALUE),
        ("refresh_token", FAKE_REFRESH_TOKEN_VALUE),
        ("authorization_code", FAKE_AUTHORIZATION_CODE),
        ("raw_state", FAKE_RAW_STATE_VALUE),
        ("secret", FAKE_SECRET_VALUE),
        ("credential", FAKE_CREDENTIAL_VALUE),
        ("cookie", FAKE_COOKIE_VALUE),
        ("session", FAKE_SESSION_VALUE),
        ("bearer", FAKE_BEARER_VALUE),
        ("raw_request", FAKE_RAW_REQUEST_VALUE),
        ("raw_response", FAKE_RAW_RESPONSE_VALUE),
    ],
)
def test_raw_credential_material_inputs_are_rejected(client, field_name, field_value):
    with connect_db(get_settings()) as connection:
        exchange = create_fake_gated_exchange(connection, "douyin_sandbox")

        result = create_credential_reference_boundary(
            connection,
            "douyin_sandbox",
            token_exchange_result=exchange,
            attempted_material={field_name: field_value},
        )

    assert result.status == CredentialStorageBoundaryStatus.CREDENTIAL_MATERIAL_REJECTED.value
    assert result.credential_reference_id is None
    assert result.credential_storage_enabled is False
    assert_no_material_values(result)


def test_exchange_metadata_with_raw_material_key_is_rejected(client):
    with connect_db(get_settings()) as connection:
        exchange = asdict(create_fake_gated_exchange(connection, "douyin_sandbox"))
        exchange["access_token"] = FAKE_ACCESS_TOKEN_VALUE

        result = create_credential_reference_boundary(
            connection,
            "douyin_sandbox",
            token_exchange_result=exchange,
        )

    assert result.status == CredentialStorageBoundaryStatus.CREDENTIAL_MATERIAL_REJECTED.value
    assert result.credential_reference_id is None
    assert_no_material_values(result)


def test_unsupported_provider_is_rejected(client):
    with connect_db(get_settings()) as connection:
        result = create_credential_reference_boundary(
            connection,
            "unknown_provider",
            token_exchange_result={"status": "exchange_simulated"},
        )

    assert result.status == CredentialStorageBoundaryStatus.UNSUPPORTED_PROVIDER.value
    assert result.provider_id is None
    assert result.source_type is None


def test_douyin_real_is_blocked_by_default(client):
    with connect_db(get_settings()) as connection:
        result = create_credential_reference_boundary(
            connection,
            "douyin_real",
            token_exchange_result={
                "status": "exchange_simulated",
                "provider_id": "douyin_real",
                "source_type": "real",
                "token_received_boolean": True,
                "credential_storage_required_boolean": True,
                "external_exchange_performed": False,
                "sandbox_fallback_performed": False,
            },
        )

    assert result.status == CredentialStorageBoundaryStatus.REAL_PROVIDER_DISABLED.value
    assert result.provider_id == "douyin_real"
    assert result.source_type == "real"
    assert result.credential_reference_id is None
    assert result.credential_storage_enabled is False


def test_douyin_real_does_not_fallback_to_sandbox(client):
    with connect_db(get_settings()) as connection:
        result = create_credential_reference_boundary(
            connection,
            "douyin_real",
            token_exchange_result=asdict(create_fake_gated_exchange(connection, "douyin_sandbox")),
        )

    assert result.status == CredentialStorageBoundaryStatus.REAL_PROVIDER_DISABLED.value
    assert result.sandbox_fallback_performed is False


def test_provider_mismatch_exchange_metadata_is_rejected_without_fallback(client):
    with connect_db(get_settings()) as connection:
        exchange = asdict(create_fake_gated_exchange(connection, "douyin_sandbox"))
        result = create_credential_reference_boundary(
            connection,
            "fake_local",
            token_exchange_result=exchange,
        )

    assert result.status == CredentialStorageBoundaryStatus.CREDENTIAL_STORAGE_REJECTED.value
    assert result.provider_id == "fake_local"
    assert result.source_type == "fake_local"
    assert result.sandbox_fallback_performed is False


def test_encryption_provider_unavailable_returns_safe_category(client):
    with connect_db(get_settings()) as connection:
        exchange = create_fake_gated_exchange(connection, "douyin_sandbox")

        result = create_credential_reference_boundary(
            connection,
            "douyin_sandbox",
            token_exchange_result=exchange,
            require_encrypted_storage=True,
        )

    assert result.status == CredentialStorageBoundaryStatus.ENCRYPTION_PROVIDER_UNAVAILABLE.value
    assert result.credential_reference_id is None
    assert result.credential_storage_enabled is False
    assert result.encrypted_payload_stored is False
    assert_no_material_values(result)


def test_result_repr_and_safe_messages_do_not_contain_material(client):
    with connect_db(get_settings()) as connection:
        exchange = create_fake_gated_exchange(connection, "douyin_sandbox")

        rejected = create_credential_reference_boundary(
            connection,
            "douyin_sandbox",
            token_exchange_result=exchange,
            attempted_material={
                "access_token": FAKE_ACCESS_TOKEN_VALUE,
                "client_secret": FAKE_SECRET_VALUE,
            },
        )

    payload = json.dumps(asdict(rejected), sort_keys=True)
    assert_no_material_text(payload)
    assert_no_material_text(repr(rejected))
    assert_no_material_text(rejected.safe_status_message)


def test_service_does_not_read_or_leak_environment_secrets(client, monkeypatch):
    fake_env_values = [
        "fake-env-access-token-value",
        "fake-env-refresh-token-value",
        "fake-env-client-secret-value",
        "fake-env-cookie-value",
        "fake-env-session-value",
    ]
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", fake_env_values[0])
    monkeypatch.setenv("DOUYIN_REFRESH_TOKEN", fake_env_values[1])
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", fake_env_values[2])
    monkeypatch.setenv("DOUYIN_COOKIE", fake_env_values[3])
    monkeypatch.setenv("DOUYIN_SESSION", fake_env_values[4])

    with connect_db(get_settings()) as connection:
        exchange = create_fake_gated_exchange(connection, "douyin_sandbox")
        result = create_credential_reference_boundary(
            connection,
            "douyin_sandbox",
            token_exchange_result=exchange,
        )

    result_text = json.dumps(asdict(result), sort_keys=True)
    for value in fake_env_values:
        assert value not in result_text


def test_service_does_not_call_external_network(client, monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("credential storage boundary must not call external network")

    monkeypatch.setattr(socket, "create_connection", fail_if_called)
    monkeypatch.setattr(urllib.request, "urlopen", fail_if_called)

    if importlib.util.find_spec("requests") is not None:
        import requests

        monkeypatch.setattr(requests.sessions.Session, "request", fail_if_called)

    if importlib.util.find_spec("httpx") is not None:
        import httpx

        monkeypatch.setattr(httpx.Client, "request", fail_if_called)
        monkeypatch.setattr(httpx.AsyncClient, "request", fail_if_called)

    with connect_db(get_settings()) as connection:
        exchange = create_fake_gated_exchange(connection, "douyin_sandbox")
        result = create_credential_reference_boundary(
            connection,
            "douyin_sandbox",
            token_exchange_result=exchange,
        )

    assert result.status == CredentialStorageBoundaryStatus.CREDENTIAL_REFERENCE_CREATED.value
    assert result.external_storage_performed is False


def test_batch4_does_not_add_oauth_or_storage_routes(client):
    route_paths = {getattr(route, "path", "") for route in app.routes}

    forbidden_paths = {
        "/api/provider-auth/{provider_id}/oauth/start",
        "/api/provider-auth/{provider_id}/oauth/callback",
        "/api/provider-auth/{provider_id}/oauth/url",
        "/api/provider-auth/{provider_id}/token/exchange",
        "/api/provider-credentials",
        "/api/provider-credentials/{provider_id}",
    }
    assert route_paths.isdisjoint(forbidden_paths)
    assert all("/oauth/start" not in path for path in route_paths)
    assert all("/oauth/callback" not in path for path in route_paths)
    assert all("/oauth/url" not in path for path in route_paths)
    assert all("/token/exchange" not in path for path in route_paths)


def test_no_real_token_or_credential_storage_is_enabled(client):
    with sqlite3.connect(get_settings().database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        reference_columns = {
            column[1]
            for column in connection.execute(
                "PRAGMA table_info(provider_credential_references)"
            ).fetchall()
        }

    assert "provider_token_storage" not in tables
    assert "provider_tokens" not in tables
    assert "provider_credential_payloads" not in tables
    assert "provider_encrypted_credentials" not in tables
    assert reference_columns.isdisjoint(FORBIDDEN_DB_COLUMNS)


def test_existing_batch_boundaries_still_expose_metadata_only_routes(client):
    responses = [
        client.get("/api/providers"),
        client.get("/api/provider-oauth-boundaries"),
        client.get("/api/provider-credential-references"),
        client.get("/api/provider-token-lifecycle-boundaries"),
    ]

    for response in responses:
        assert response.status_code == 200
        assert_no_material_text(response.text)


def create_fake_gated_exchange(connection: sqlite3.Connection, provider_id: str):
    created = create_oauth_state_metadata(connection, provider_id)
    assert created.raw_state is not None
    return simulate_token_exchange_boundary(
        connection,
        provider_id,
        raw_state=created.raw_state,
        authorization_code=FAKE_AUTHORIZATION_CODE,
    )


def fetch_reference_row(connection: sqlite3.Connection, reference_id: str | None) -> sqlite3.Row:
    assert reference_id is not None
    row = connection.execute(
        "SELECT * FROM provider_credential_references WHERE reference_id = ?",
        (reference_id,),
    ).fetchone()
    assert row is not None
    return row


def assert_no_material_values(value) -> None:
    assert_no_material_text(json.dumps(asdict(value) if hasattr(value, "__dataclass_fields__") else value, default=str))


def assert_no_material_text(text: str) -> None:
    for material_value in FORBIDDEN_MATERIAL_VALUES:
        assert material_value not in text
