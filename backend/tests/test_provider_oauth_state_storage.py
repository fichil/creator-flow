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
from app.providers.oauth_state import (
    OAuthStateResultStatus,
    consume_oauth_state_once,
    create_oauth_state_metadata,
    digest_oauth_state,
    mark_expired_oauth_states,
)


SENSITIVE_COLUMN_NAMES = {
    "raw_state",
    "state_value",
    "oauth_state_value",
    "authorization_code",
    "access_token",
    "refresh_token",
    "token",
    "secret",
    "credential",
    "credential_material",
    "cookie",
    "session",
    "raw_request",
    "raw_response",
}

SENSITIVE_VALUE_TERMS = [
    "fake-authorization-code-value",
    "fake-access-token-value",
    "fake-refresh-token-value",
    "fake-secret-value",
    "fake-credential-value",
    "fake-cookie-value",
    "fake-session-value",
]


def test_provider_oauth_states_table_exists_without_sensitive_columns(client):
    with sqlite3.connect(get_settings().database_path) as connection:
        columns = connection.execute("PRAGMA table_info(provider_oauth_states)").fetchall()

    column_names = {column[1] for column in columns}
    assert {
        "oauth_state_id",
        "provider_id",
        "source_type",
        "state_digest",
        "state_status",
        "purpose",
        "created_at",
        "expires_at",
        "consumed_at",
        "updated_at",
        "safe_status_message",
        "last_status_change_reason",
    }.issubset(column_names)
    assert column_names.isdisjoint(SENSITIVE_COLUMN_NAMES)


def test_create_state_persists_digest_only_not_raw_state(client):
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "douyin_real")
        row = fetch_state_row(connection, created.oauth_state_id)

    assert created.status == OAuthStateResultStatus.CREATED.value
    assert created.raw_state is not None
    assert row["provider_id"] == "douyin_real"
    assert row["source_type"] == "real"
    assert row["state_status"] == "pending"
    assert row["purpose"] == "authorization"
    assert row["state_digest"] == digest_oauth_state(created.raw_state)
    serialized = json.dumps(dict(row), sort_keys=True)
    assert created.raw_state not in serialized
    assert len(row["state_digest"]) == 64
    assert row["expires_at"]


def test_state_digest_is_unique(client):
    with connect_db(get_settings()) as connection:
        first = create_oauth_state_metadata(connection, "douyin_real")
        second = create_oauth_state_metadata(connection, "douyin_real")

    assert first.raw_state != second.raw_state
    assert first.state_digest != second.state_digest


def test_pending_state_can_be_consumed_once_then_replay_is_rejected(client):
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "douyin_real")
        assert created.raw_state is not None

        first_consume = consume_oauth_state_once(
            connection, "douyin_real", created.raw_state
        )
        second_consume = consume_oauth_state_once(
            connection, "douyin_real", created.raw_state
        )
        row = fetch_state_row(connection, created.oauth_state_id)

    assert first_consume.status == OAuthStateResultStatus.VALID_CONSUMED.value
    assert second_consume.status == OAuthStateResultStatus.INVALID_REPLAYED_STATE.value
    assert row["state_status"] == "consumed"
    assert row["consumed_at"] is not None


def test_expired_state_is_rejected_and_marked_expired(client):
    now = datetime(2026, 5, 29, 8, 0, 0, tzinfo=timezone.utc)
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(
            connection, "douyin_real", ttl_seconds=60, now=now
        )
        assert created.raw_state is not None

        consumed = consume_oauth_state_once(
            connection,
            "douyin_real",
            created.raw_state,
            now=now + timedelta(minutes=2),
        )
        row = fetch_state_row(connection, created.oauth_state_id)

    assert consumed.status == OAuthStateResultStatus.INVALID_EXPIRED_STATE.value
    assert row["state_status"] == "expired"


def test_mark_expired_states_updates_pending_rows(client):
    now = datetime(2026, 5, 29, 8, 0, 0, tzinfo=timezone.utc)
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(
            connection, "douyin_sandbox", ttl_seconds=60, now=now
        )

        updated_count = mark_expired_oauth_states(
            connection, now=now + timedelta(minutes=2)
        )
        row = fetch_state_row(connection, created.oauth_state_id)

    assert updated_count == 1
    assert row["state_status"] == "expired"


def test_missing_and_malformed_states_are_rejected(client):
    with connect_db(get_settings()) as connection:
        missing = consume_oauth_state_once(connection, "douyin_real", None)
        blank = consume_oauth_state_once(connection, "douyin_real", " ")
        malformed = consume_oauth_state_once(connection, "douyin_real", "bad state!")
        unknown_but_well_formed = consume_oauth_state_once(
            connection, "douyin_real", "fake_state_for_contract_test"
        )

    assert missing.status == OAuthStateResultStatus.INVALID_MISSING_STATE.value
    assert blank.status == OAuthStateResultStatus.INVALID_MISSING_STATE.value
    assert malformed.status == OAuthStateResultStatus.INVALID_MALFORMED_STATE.value
    assert (
        unknown_but_well_formed.status
        == OAuthStateResultStatus.INVALID_MALFORMED_STATE.value
    )


def test_provider_mismatch_is_rejected_without_sandbox_fallback(client):
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "douyin_sandbox")
        assert created.raw_state is not None

        mismatch = consume_oauth_state_once(
            connection, "douyin_real", created.raw_state
        )
        row = fetch_state_row(connection, created.oauth_state_id)

    assert mismatch.status == OAuthStateResultStatus.INVALID_PROVIDER_MISMATCH.value
    assert mismatch.source_type == "real"
    assert row["provider_id"] == "douyin_sandbox"
    assert row["source_type"] == "sandbox"
    assert row["state_status"] == "pending"


def test_unknown_provider_is_rejected(client):
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "unknown_provider")
        consumed = consume_oauth_state_once(
            connection, "unknown_provider", "fake_state_for_contract_test"
        )

    assert created.status == OAuthStateResultStatus.UNSUPPORTED_PROVIDER.value
    assert created.raw_state is None
    assert consumed.status == OAuthStateResultStatus.UNSUPPORTED_PROVIDER.value


def test_source_types_remain_separated_for_known_providers(client):
    with connect_db(get_settings()) as connection:
        created_by_provider = {
            provider_id: create_oauth_state_metadata(connection, provider_id)
            for provider_id in ("fake_local", "douyin_sandbox", "douyin_real")
        }
        rows = {
            provider_id: fetch_state_row(connection, result.oauth_state_id)
            for provider_id, result in created_by_provider.items()
        }

    assert rows["fake_local"]["source_type"] == "fake_local"
    assert rows["douyin_sandbox"]["source_type"] == "sandbox"
    assert rows["douyin_real"]["source_type"] == "real"


def test_safe_messages_do_not_contain_sensitive_values(client):
    with connect_db(get_settings()) as connection:
        created = create_oauth_state_metadata(connection, "douyin_real")
        assert created.raw_state is not None
        consumed = consume_oauth_state_once(connection, "douyin_real", created.raw_state)
        replayed = consume_oauth_state_once(connection, "douyin_real", created.raw_state)
        row = fetch_state_row(connection, created.oauth_state_id)

    payload_text = json.dumps(
        {
            "created_safe_status_message": created.safe_status_message,
            "consumed": asdict(consumed),
            "replayed": asdict(replayed),
            "row": dict(row),
        },
        sort_keys=True,
    )
    assert created.raw_state not in payload_text
    for value in SENSITIVE_VALUE_TERMS:
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
        created = create_oauth_state_metadata(connection, "douyin_real")
        assert created.raw_state is not None
        consumed = consume_oauth_state_once(connection, "douyin_real", created.raw_state)
        rows = connection.execute("SELECT * FROM provider_oauth_states").fetchall()

    payload_text = json.dumps(
        {
            "created_safe_status_message": created.safe_status_message,
            "consumed": asdict(consumed),
            "rows": [dict(row) for row in rows],
        },
        sort_keys=True,
    )
    for value in environment_values:
        assert value not in payload_text


def test_state_service_does_not_call_external_services(client, monkeypatch):
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
        created = create_oauth_state_metadata(connection, "douyin_real")
        assert created.raw_state is not None
        consumed = consume_oauth_state_once(connection, "douyin_real", created.raw_state)

    assert created.status == OAuthStateResultStatus.CREATED.value
    assert consumed.status == OAuthStateResultStatus.VALID_CONSUMED.value


def test_batch2_does_not_add_oauth_or_token_routes(client):
    route_paths = {getattr(route, "path", "") for route in app.routes}
    forbidden_paths = {
        "/api/oauth/start",
        "/api/oauth/callback",
        "/api/provider-auth/{provider_id}/oauth/start",
        "/api/provider-auth/{provider_id}/oauth/callback",
        "/api/providers/{provider_id}/oauth/start",
        "/api/providers/{provider_id}/oauth/callback",
        "/api/providers/{provider_id}/token/exchange",
    }
    forbidden_fragments = (
        "/oauth/start",
        "/oauth/callback",
        "/token/exchange",
        "/tokens",
    )

    assert route_paths.isdisjoint(forbidden_paths)
    assert all(
        all(fragment not in path for fragment in forbidden_fragments)
        for path in route_paths
    )


def test_existing_provider_metadata_routes_still_pass(client):
    responses = [
        client.get("/api/providers"),
        client.get("/api/provider-connections"),
        client.get("/api/provider-oauth-boundaries"),
        client.get("/api/provider-credential-references"),
        client.get("/api/provider-security-audit-events"),
        client.get("/api/provider-token-lifecycle-boundaries"),
    ]

    for response in responses:
        assert response.status_code == 200


def fetch_state_row(connection, oauth_state_id: str | None) -> sqlite3.Row:
    row = connection.execute(
        "SELECT * FROM provider_oauth_states WHERE oauth_state_id = ?",
        (oauth_state_id,),
    ).fetchone()
    assert row is not None
    return row
