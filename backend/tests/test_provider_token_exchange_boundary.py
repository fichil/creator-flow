import importlib.util
import json
import socket
import sqlite3
import urllib.request
from dataclasses import asdict
from datetime import datetime, timedelta, timezone

from app.core.config import get_settings
from app.db.database import connect_db
from app.main import app
from app.providers.oauth_state import create_oauth_state_metadata
from app.providers.token_exchange import (
    TokenExchangeResultStatus,
    simulate_token_exchange_boundary,
)


FAKE_AUTHORIZATION_CODE = "fake_authorization_code_for_token_exchange_test"
FAKE_ACCESS_TOKEN_VALUE = "fake-access-token-value"
FAKE_REFRESH_TOKEN_VALUE = "fake-refresh-token-value"
FAKE_SECRET_VALUE = "fake-secret-value"
FAKE_CREDENTIAL_VALUE = "fake-credential-value"
FAKE_COOKIE_VALUE = "fake-cookie-value"
FAKE_SESSION_VALUE = "fake-session-value"
FAKE_RAW_REQUEST_VALUE = "fake-raw-request-value"
FAKE_RAW_RESPONSE_VALUE = "fake-raw-response-value"

FORBIDDEN_RESULT_FIELDS = {
    "authorization_code",
    "raw_authorization_code",
    "raw_state",
    "state_value",
    "oauth_state_value",
    "access_token",
    "refresh_token",
    "token",
    "token_value",
    "secret",
    "credential",
    "credential_material",
    "cookie",
    "session",
    "raw_request",
    "raw_response",
}

FORBIDDEN_DB_COLUMNS = {
    "authorization_code",
    "raw_authorization_code",
    "access_token",
    "refresh_token",
    "token",
    "token_value",
    "secret",
    "credential",
    "credential_material",
    "cookie",
    "session",
    "raw_state",
    "state_value",
    "raw_request",
    "raw_response",
}


def test_fake_gated_exchange_simulates_metadata_only_for_sandbox(client):
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "douyin_sandbox")
        assert created.raw_state is not None

        result = simulate_token_exchange_boundary(
            connection,
            "douyin_sandbox",
            raw_state=created.raw_state,
            authorization_code=FAKE_AUTHORIZATION_CODE,
        )
        row = fetch_state_row(connection, created.oauth_state_id)

    assert result.status == TokenExchangeResultStatus.EXCHANGE_SIMULATED.value
    assert result.provider_id == "douyin_sandbox"
    assert result.source_type == "sandbox"
    assert result.token_received_boolean is True
    assert result.credential_storage_required_boolean is True
    assert result.external_exchange_performed is False
    assert result.sandbox_fallback_performed is False
    assert row["state_status"] == "consumed"
    assert row["consumed_at"] is not None
    assert_safe_result(result, created.raw_state)


def test_exchange_requires_batch2_state_foundation(client):
    with connect_db(get_settings()) as connection:
        result = simulate_token_exchange_boundary(
            connection,
            "douyin_sandbox",
            raw_state="fake_unknown_state_for_token_exchange",
            authorization_code=FAKE_AUTHORIZATION_CODE,
        )

    assert result.status == TokenExchangeResultStatus.STATE_VALIDATION_FAILED.value
    assert result.state_validation_status == "invalid_malformed_state"
    assert result.exchange_attempted is False
    assert result.token_received_boolean is False


def test_valid_pending_state_is_consumed_once_before_exchange(client):
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "fake_local")
        assert created.raw_state is not None

        result = simulate_token_exchange_boundary(
            connection,
            "fake_local",
            raw_state=created.raw_state,
            authorization_code=FAKE_AUTHORIZATION_CODE,
        )
        row = fetch_state_row(connection, created.oauth_state_id)

    assert result.status == TokenExchangeResultStatus.EXCHANGE_SIMULATED.value
    assert result.state_validation_status == "valid_consumed"
    assert row["state_status"] == "consumed"
    assert row["consumed_at"] is not None


def test_replayed_state_is_rejected_without_exchange(client):
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "douyin_sandbox")
        assert created.raw_state is not None

        first = simulate_token_exchange_boundary(
            connection,
            "douyin_sandbox",
            raw_state=created.raw_state,
            authorization_code=FAKE_AUTHORIZATION_CODE,
        )
        second = simulate_token_exchange_boundary(
            connection,
            "douyin_sandbox",
            raw_state=created.raw_state,
            authorization_code=FAKE_AUTHORIZATION_CODE,
        )

    assert first.status == TokenExchangeResultStatus.EXCHANGE_SIMULATED.value
    assert second.status == TokenExchangeResultStatus.STATE_VALIDATION_FAILED.value
    assert second.state_validation_status == "invalid_replayed_state"
    assert second.exchange_attempted is False
    assert second.token_received_boolean is False


def test_expired_state_is_rejected_without_exchange(client):
    now = datetime(2026, 5, 29, 8, 0, 0, tzinfo=timezone.utc)
    with connect_db(get_settings()) as connection:
        expired_created = create_oauth_state_metadata(
            connection, "douyin_sandbox", ttl_seconds=60, now=now
        )
        assert expired_created.raw_state is not None
        expired_result = simulate_token_exchange_boundary(
            connection,
            "douyin_sandbox",
            raw_state=expired_created.raw_state,
            authorization_code=FAKE_AUTHORIZATION_CODE,
            now=now + timedelta(minutes=2),
        )
        row = fetch_state_row(connection, expired_created.oauth_state_id)

    assert expired_result.status == TokenExchangeResultStatus.STATE_VALIDATION_FAILED.value
    assert expired_result.state_validation_status == "invalid_expired_state"
    assert expired_result.exchange_attempted is False
    assert row["state_status"] == "expired"


def test_missing_and_malformed_state_are_rejected(client):
    with connect_db(get_settings()) as connection:
        missing = simulate_token_exchange_boundary(
            connection,
            "douyin_sandbox",
            raw_state=None,
            authorization_code=FAKE_AUTHORIZATION_CODE,
        )
        malformed = simulate_token_exchange_boundary(
            connection,
            "douyin_sandbox",
            raw_state="bad state!",
            authorization_code=FAKE_AUTHORIZATION_CODE,
        )

    assert missing.status == TokenExchangeResultStatus.STATE_VALIDATION_FAILED.value
    assert missing.state_validation_status == "invalid_missing_state"
    assert malformed.status == TokenExchangeResultStatus.STATE_VALIDATION_FAILED.value
    assert malformed.state_validation_status == "invalid_malformed_state"


def test_provider_mismatch_is_rejected_without_sandbox_fallback(client):
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "douyin_sandbox")
        assert created.raw_state is not None

        result = simulate_token_exchange_boundary(
            connection,
            "fake_local",
            raw_state=created.raw_state,
            authorization_code=FAKE_AUTHORIZATION_CODE,
        )
        row = fetch_state_row(connection, created.oauth_state_id)

    assert result.status == TokenExchangeResultStatus.STATE_VALIDATION_FAILED.value
    assert result.state_validation_status == "invalid_provider_mismatch"
    assert result.provider_id == "fake_local"
    assert result.source_type == "fake_local"
    assert result.sandbox_fallback_performed is False
    assert row["provider_id"] == "douyin_sandbox"
    assert row["source_type"] == "sandbox"
    assert row["state_status"] == "pending"


def test_unsupported_provider_is_rejected(client):
    with connect_db(get_settings()) as connection:
        result = simulate_token_exchange_boundary(
            connection,
            "unknown_provider",
            raw_state="fake_unknown_state_for_token_exchange",
            authorization_code=FAKE_AUTHORIZATION_CODE,
        )

    assert result.status == TokenExchangeResultStatus.UNSUPPORTED_PROVIDER.value
    assert result.provider_id is None
    assert result.source_type is None
    assert result.exchange_attempted is False


def test_missing_authorization_code_is_rejected_without_consuming_state(client):
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "douyin_sandbox")
        assert created.raw_state is not None

        result = simulate_token_exchange_boundary(
            connection,
            "douyin_sandbox",
            raw_state=created.raw_state,
            authorization_code=None,
        )
        blank = simulate_token_exchange_boundary(
            connection,
            "douyin_sandbox",
            raw_state=created.raw_state,
            authorization_code=" ",
        )
        row = fetch_state_row(connection, created.oauth_state_id)

    assert result.status == TokenExchangeResultStatus.AUTHORIZATION_CODE_MISSING.value
    assert blank.status == TokenExchangeResultStatus.AUTHORIZATION_CODE_MISSING.value
    assert row["state_status"] == "pending"


def test_malformed_authorization_code_is_rejected_without_consuming_state(client):
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "douyin_sandbox")
        assert created.raw_state is not None

        result = simulate_token_exchange_boundary(
            connection,
            "douyin_sandbox",
            raw_state=created.raw_state,
            authorization_code="real-looking-code",
        )
        row = fetch_state_row(connection, created.oauth_state_id)

    assert result.status == TokenExchangeResultStatus.AUTHORIZATION_CODE_MALFORMED.value
    assert result.exchange_attempted is False
    assert row["state_status"] == "pending"


def test_douyin_real_is_blocked_by_default_without_sandbox_fallback(client):
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "douyin_real")
        assert created.raw_state is not None

        result = simulate_token_exchange_boundary(
            connection,
            "douyin_real",
            raw_state=created.raw_state,
            authorization_code=FAKE_AUTHORIZATION_CODE,
        )
        row = fetch_state_row(connection, created.oauth_state_id)

    assert result.status == TokenExchangeResultStatus.REAL_PROVIDER_DISABLED.value
    assert result.provider_id == "douyin_real"
    assert result.source_type == "real"
    assert result.exchange_attempted is False
    assert result.external_exchange_performed is False
    assert result.sandbox_fallback_performed is False
    assert row["state_status"] == "pending"


def test_service_result_and_repr_do_not_contain_sensitive_values(client):
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "douyin_sandbox")
        assert created.raw_state is not None

        result = simulate_token_exchange_boundary(
            connection,
            "douyin_sandbox",
            raw_state=created.raw_state,
            authorization_code=FAKE_AUTHORIZATION_CODE,
        )

    payload = {
        "result": asdict(result),
        "repr": repr(result),
        "safe_status_message": result.safe_status_message,
    }
    payload_text = json.dumps(payload, sort_keys=True)
    assert created.raw_state not in payload_text
    assert FAKE_AUTHORIZATION_CODE not in payload_text
    assert FORBIDDEN_RESULT_FIELDS.isdisjoint(asdict(result).keys())
    for value in sensitive_values():
        assert value not in payload_text


def test_state_service_does_not_read_or_leak_environment_values(client, monkeypatch):
    environment_values = [
        "fake-env-access-token-value",
        "fake-env-refresh-token-value",
        "fake-env-client-secret-value",
        "fake-env-authorization-code-value",
        "fake-env-oauth-state-value",
        "fake-env-api-key-value",
        "fake-env-cookie-value",
        "fake-env-session-value",
    ]
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", environment_values[0])
    monkeypatch.setenv("DOUYIN_REFRESH_TOKEN", environment_values[1])
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", environment_values[2])
    monkeypatch.setenv("AUTHORIZATION_CODE", environment_values[3])
    monkeypatch.setenv("OAUTH_STATE", environment_values[4])
    monkeypatch.setenv("DOUYIN_API_KEY", environment_values[5])
    monkeypatch.setenv("DOUYIN_COOKIE", environment_values[6])
    monkeypatch.setenv("DOUYIN_SESSION", environment_values[7])

    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "douyin_sandbox")
        assert created.raw_state is not None
        result = simulate_token_exchange_boundary(
            connection,
            "douyin_sandbox",
            raw_state=created.raw_state,
            authorization_code=FAKE_AUTHORIZATION_CODE,
        )

    payload_text = json.dumps(asdict(result), sort_keys=True)
    for value in environment_values:
        assert value not in payload_text


def test_token_exchange_boundary_does_not_call_external_services(client, monkeypatch):
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

    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "douyin_sandbox")
        assert created.raw_state is not None
        result = simulate_token_exchange_boundary(
            connection,
            "douyin_sandbox",
            raw_state=created.raw_state,
            authorization_code=FAKE_AUTHORIZATION_CODE,
        )

    assert result.status == TokenExchangeResultStatus.EXCHANGE_SIMULATED.value
    assert result.external_exchange_performed is False


def test_batch3_does_not_add_oauth_or_token_routes(client):
    route_paths = {getattr(route, "path", "") for route in app.routes}
    forbidden_fragments = (
        "/oauth/start",
        "/oauth/callback",
        "/oauth/url",
        "/authorization-url",
        "/token/exchange",
        "/tokens",
    )

    assert all(
        all(fragment not in path for fragment in forbidden_fragments)
        for path in route_paths
    )


def test_batch3_does_not_add_token_or_credential_storage_schema(client):
    with sqlite3.connect(get_settings().database_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        rows = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()
        column_names_by_table = {
            row[0]: {
                column[1]
                for column in connection.execute(f"PRAGMA table_info({row[0]})").fetchall()
            }
            for row in rows
        }

    assert "provider_token_exchange_attempts" not in table_names
    for column_names in column_names_by_table.values():
        assert FORBIDDEN_DB_COLUMNS.isdisjoint(column_names)


def test_existing_batch1_and_batch2_provider_routes_still_pass(client):
    responses = [
        client.get("/api/provider-oauth-boundaries"),
        client.get("/api/provider-token-lifecycle-boundaries"),
        client.get("/api/provider-credential-references"),
        client.get("/api/provider-security-audit-events"),
    ]

    for response in responses:
        assert response.status_code == 200


def assert_safe_result(result, raw_state: str) -> None:
    payload_text = json.dumps(asdict(result), sort_keys=True)
    assert raw_state not in payload_text
    assert FAKE_AUTHORIZATION_CODE not in payload_text
    for value in sensitive_values():
        assert value not in payload_text
    assert FORBIDDEN_RESULT_FIELDS.isdisjoint(asdict(result).keys())


def sensitive_values() -> list[str]:
    return [
        FAKE_ACCESS_TOKEN_VALUE,
        FAKE_REFRESH_TOKEN_VALUE,
        FAKE_SECRET_VALUE,
        FAKE_CREDENTIAL_VALUE,
        FAKE_COOKIE_VALUE,
        FAKE_SESSION_VALUE,
        FAKE_RAW_REQUEST_VALUE,
        FAKE_RAW_RESPONSE_VALUE,
    ]


def fetch_state_row(connection, oauth_state_id: str | None) -> sqlite3.Row:
    row = connection.execute(
        "SELECT * FROM provider_oauth_states WHERE oauth_state_id = ?",
        (oauth_state_id,),
    ).fetchone()
    assert row is not None
    return row
