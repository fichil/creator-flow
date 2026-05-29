import importlib.util
import json
import socket
import sqlite3
import urllib.request
import uuid
from typing import Any

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.db.database import connect_db
from app.main import app
from app.metrics.fake_metrics import FakeMetricsProvider
from app.providers.real_provider_controls import (
    FeatureFlagStatus,
    KillSwitchStatus,
    PlatformPreconditionsStatus,
    RealProviderCapability,
    RealProviderControlPolicy,
    RuntimeEnvironmentStatus,
)
from app.publishers.fake_publisher import FakePublisherProvider
from app.publishing.metrics_read import (
    LimitedMetricsReadError,
    create_limited_metrics_snapshot,
)
from app.publishing.publish_status_reconciliation import create_publish_status_reconciliation

from test_publish_status_reconciliation import (
    insert_publish_attempt,
    prepare_base_project,
    prepare_publish_status_project,
)


FAKE_ACCESS_TOKEN_VALUE = "fake-metrics-access-token-value"
FAKE_REFRESH_TOKEN_VALUE = "fake-metrics-refresh-token-value"
FAKE_SECRET_VALUE = "fake-metrics-secret-value"
FAKE_CLIENT_SECRET_VALUE = "fake-metrics-client-secret-value"
FAKE_CREDENTIAL_VALUE = "fake-metrics-credential-value"
FAKE_AUTHORIZATION_CODE_VALUE = "fake-metrics-authorization-code-value"
FAKE_RAW_STATE_VALUE = "fake-metrics-raw-oauth-state-value"
FAKE_COOKIE_VALUE = "fake-metrics-cookie-value"
FAKE_SESSION_VALUE = "fake-metrics-session-value"
FAKE_API_KEY_VALUE = "fake-metrics-api-key-value"
FAKE_BEARER_VALUE = "fake-metrics-bearer-value"
FAKE_RAW_REQUEST_VALUE = "fake-metrics-raw-request-value"
FAKE_RAW_RESPONSE_VALUE = "fake-metrics-raw-response-value"
FAKE_PROVIDER_RESPONSE_VALUE = "fake-metrics-provider-response-value"
FAKE_UPLOAD_RESPONSE_VALUE = "fake-metrics-upload-response-value"
FAKE_PUBLISH_RESPONSE_VALUE = "fake-metrics-publish-response-value"
FAKE_STATUS_RESPONSE_VALUE = "fake-metrics-status-response-value"
FAKE_METRICS_RESPONSE_VALUE = "fake-metrics-response-value"
FAKE_EXTERNAL_RESPONSE_VALUE = "fake-metrics-external-response-value"
FAKE_DOUYIN_RESPONSE_VALUE = "fake-metrics-douyin-response-value"

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
    "client_secret",
    "credential",
    "api_key",
    "cookie",
    "session",
    "bearer",
    "raw_request",
    "raw_response",
    "provider_response",
    "upload_response",
    "publish_response",
    "status_response",
    "metrics_response",
    "external_response",
    "douyin_response",
}

FORBIDDEN_MATERIAL_VALUES = {
    FAKE_ACCESS_TOKEN_VALUE,
    FAKE_REFRESH_TOKEN_VALUE,
    FAKE_SECRET_VALUE,
    FAKE_CLIENT_SECRET_VALUE,
    FAKE_CREDENTIAL_VALUE,
    FAKE_AUTHORIZATION_CODE_VALUE,
    FAKE_RAW_STATE_VALUE,
    FAKE_COOKIE_VALUE,
    FAKE_SESSION_VALUE,
    FAKE_API_KEY_VALUE,
    FAKE_BEARER_VALUE,
    FAKE_RAW_REQUEST_VALUE,
    FAKE_RAW_RESPONSE_VALUE,
    FAKE_PROVIDER_RESPONSE_VALUE,
    FAKE_UPLOAD_RESPONSE_VALUE,
    FAKE_PUBLISH_RESPONSE_VALUE,
    FAKE_STATUS_RESPONSE_VALUE,
    FAKE_METRICS_RESPONSE_VALUE,
    FAKE_EXTERNAL_RESPONSE_VALUE,
    FAKE_DOUYIN_RESPONSE_VALUE,
}


def test_metrics_snapshot_schema_is_metadata_only(client: TestClient):
    with sqlite3.connect(get_settings().database_path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(publish_metrics_snapshots)").fetchall()}

    assert {
        "metrics_snapshot_id",
        "status_snapshot_id",
        "publish_attempt_id",
        "publish_intent_id",
        "review_item_id",
        "provider_id",
        "source_type",
        "metrics_source",
        "metrics_freshness_status",
        "metrics_observed_at",
        "views_count",
        "likes_count",
        "comments_count",
        "shares_count",
        "favorites_count",
        "completion_rate_basis_points",
        "external_query_status",
        "safe_status_message",
        "last_status_change_reason",
    }.issubset(columns)
    assert columns.isdisjoint(FORBIDDEN_DB_COLUMNS)


def test_metrics_snapshot_requires_existing_publish_status_snapshot(client: TestClient):
    project_id = create_project(client)

    response = client.post(f"/api/projects/{project_id}/publish-status-snapshots/pss_missing/metrics-snapshots", json={})

    assert response.status_code == 404
    assert response.json()["detail"].startswith("publish_status_required:")
    assert_metrics_snapshot_count(0)


def test_publish_status_not_eligible_is_rejected_safely(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client)
    snapshot = create_status_snapshot(
        client,
        project_id,
        attempt["id"],
        local_publish_status="local_blocked",
    )

    response = client.post(
        f"/api/projects/{project_id}/publish-status-snapshots/{snapshot['status_snapshot_id']}/metrics-snapshots",
        json={},
    )

    assert response.status_code == 409
    assert response.json()["detail"].startswith("publish_not_ready_for_metrics:")
    assert_metrics_snapshot_count(0)


def test_valid_fake_local_status_snapshot_creates_metadata_only_metrics_snapshot(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client)
    snapshot = create_status_snapshot(client, project_id, attempt["id"])

    response = client.post(
        f"/api/projects/{project_id}/publish-status-snapshots/{snapshot['status_snapshot_id']}/metrics-snapshots",
        json={
            "fake_metrics_fixture": {
                "metrics_source": "fake_fixture",
                "metrics_freshness_status": "fresh",
                "metrics_observed_at": "2026-05-29T03:00:00Z",
                "views_count": 120,
                "likes_count": 12,
                "comments_count": 4,
                "shares_count": 3,
                "favorites_count": 8,
                "completion_rate_basis_points": 6200,
                "safe_status_message": "Fake fixture metrics for local guarded foundation; not real Douyin metrics.",
            }
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["result_category"] == "metrics_snapshot_created"
    assert body["status_snapshot_id"] == snapshot["status_snapshot_id"]
    assert body["publish_attempt_id"] == attempt["id"]
    assert body["provider_id"] == "fake_local"
    assert body["source_type"] == "fake_local"
    assert body["metrics_source"] == "fake_fixture"
    assert body["metrics_freshness_status"] == "fresh"
    assert body["metrics_observed_at"] == "2026-05-29T03:00:00Z"
    assert body["views_count"] == 120
    assert body["completion_rate_basis_points"] == 6200
    assert body["external_query_status"] == "not_called"
    assert_no_material_values(body)


def test_valid_sandbox_safe_status_snapshot_can_create_metrics_snapshot(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client, target_platform="douyin_sandbox")
    snapshot = create_status_snapshot(client, project_id, attempt["id"], status_source="sandbox_fixture")

    response = client.post(
        f"/api/projects/{project_id}/publish-status-snapshots/{snapshot['status_snapshot_id']}/metrics-snapshots",
        json={
            "fake_metrics_fixture": {
                "metrics_source": "sandbox_fixture",
                "metrics_freshness_status": "stale",
                "metrics_observed_at": "2026-05-29T02:00:00Z",
                "views_count": 88,
                "safe_status_message": "Sandbox-safe fixture metrics; not real Douyin metrics.",
            }
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["provider_id"] == "douyin_sandbox"
    assert body["source_type"] == "sandbox"
    assert body["metrics_source"] == "sandbox_fixture"
    assert body["metrics_freshness_status"] == "stale"
    assert body["views_count"] == 88
    assert_no_material_values(body)


def test_default_metrics_snapshot_exposes_unknown_freshness(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client)
    snapshot = create_status_snapshot(client, project_id, attempt["id"])

    response = client.post(
        f"/api/projects/{project_id}/publish-status-snapshots/{snapshot['status_snapshot_id']}/metrics-snapshots",
        json={},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["result_category"] == "metrics_freshness_unknown"
    assert body["metrics_source"] == "local"
    assert body["metrics_freshness_status"] == "unknown"
    assert body["metrics_observed_at"] is None
    assert body["views_count"] is None
    assert "freshness unknown" in body["safe_status_message"]
    assert_no_material_values(body)


def test_metrics_permission_missing_is_represented_safely(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client)
    snapshot = create_status_snapshot(client, project_id, attempt["id"])

    response = client.post(
        f"/api/projects/{project_id}/publish-status-snapshots/{snapshot['status_snapshot_id']}/metrics-snapshots",
        json={"metrics_permission_status": "missing"},
    )

    assert response.status_code == 409
    assert response.json()["detail"].startswith("metrics_permission_missing:")
    assert_no_material_values(response.json())
    assert_metrics_snapshot_count(0)


def test_malformed_fake_metrics_fixture_is_rejected_safely(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client)
    snapshot = create_status_snapshot(client, project_id, attempt["id"])

    response = client.post(
        f"/api/projects/{project_id}/publish-status-snapshots/{snapshot['status_snapshot_id']}/metrics-snapshots",
        json={
            "fake_metrics_fixture": {
                "metrics_source": "provider_response",
                "metrics_freshness_status": "fresh",
                "metrics_observed_at": "not-a-date",
                "views_count": -1,
                "safe_status_message": FAKE_METRICS_RESPONSE_VALUE,
            }
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"].startswith("metrics_fixture_invalid:")
    assert_no_material_values(response.json())
    assert_metrics_snapshot_count(0)


def test_real_provider_disabled_by_default_and_kill_switch_active_blocks_metrics_read(client: TestClient):
    project_id, review_item = prepare_base_project(client)
    attempt_id = insert_publish_attempt(
        project_id,
        review_item["id"],
        provider_id="douyin_real",
        source_type="real",
    )
    status_snapshot_id = insert_status_snapshot(
        attempt_id,
        provider_id="douyin_real",
        source_type="real",
    )

    response = client.post(
        f"/api/projects/{project_id}/publish-status-snapshots/{status_snapshot_id}/metrics-snapshots",
        json={},
    )

    assert response.status_code == 409
    assert response.json()["detail"].startswith("kill_switch_active:")
    assert_metrics_snapshot_count(0)


def test_real_provider_feature_disabled_returns_safe_disabled_result(client: TestClient):
    project_id, review_item = prepare_base_project(client)
    attempt_id = insert_publish_attempt(
        project_id,
        review_item["id"],
        provider_id="douyin_real",
        source_type="real",
    )
    status_snapshot_id = insert_status_snapshot(attempt_id, provider_id="douyin_real", source_type="real")

    with connect_db(get_settings()) as connection:
        try:
            create_limited_metrics_snapshot(
                connection,
                project_id=project_id,
                status_snapshot_id=status_snapshot_id,
                real_provider_control_policy=metrics_policy(
                    feature_flag_status=FeatureFlagStatus.DISABLED.value
                ),
            )
        except LimitedMetricsReadError as exc:
            assert exc.category == "real_provider_disabled"
            assert_no_material_values(exc)
        else:
            raise AssertionError("feature-disabled real provider metrics read must be blocked")


def test_platform_preconditions_missing_blocks_metrics_read(client: TestClient):
    project_id, review_item = prepare_base_project(client)
    attempt_id = insert_publish_attempt(
        project_id,
        review_item["id"],
        provider_id="douyin_real",
        source_type="real",
    )
    status_snapshot_id = insert_status_snapshot(attempt_id, provider_id="douyin_real", source_type="real")

    with connect_db(get_settings()) as connection:
        try:
            create_limited_metrics_snapshot(
                connection,
                project_id=project_id,
                status_snapshot_id=status_snapshot_id,
                real_provider_control_policy=metrics_policy(
                    platform_preconditions_status=PlatformPreconditionsStatus.MISSING.value
                ),
            )
        except LimitedMetricsReadError as exc:
            assert exc.category == "platform_preconditions_missing"
            assert_no_material_values(exc)
        else:
            raise AssertionError("missing platform preconditions must block metrics read")


def test_unsupported_provider_is_rejected(client: TestClient):
    project_id, review_item = prepare_base_project(client)
    attempt_id = insert_publish_attempt(
        project_id,
        review_item["id"],
        provider_id="unknown_provider",
        source_type="fake_local",
    )
    status_snapshot_id = insert_status_snapshot(attempt_id, provider_id="unknown_provider", source_type="fake_local")

    response = client.post(
        f"/api/projects/{project_id}/publish-status-snapshots/{status_snapshot_id}/metrics-snapshots",
        json={},
    )

    assert response.status_code == 409
    assert response.json()["detail"].startswith("unsupported_provider:")
    assert_metrics_snapshot_count(0)


def test_douyin_real_does_not_fallback_to_sandbox(client: TestClient):
    project_id, review_item = prepare_base_project(client)
    attempt_id = insert_publish_attempt(
        project_id,
        review_item["id"],
        provider_id="douyin_real",
        source_type="real",
    )
    status_snapshot_id = insert_status_snapshot(attempt_id, provider_id="douyin_real", source_type="real")

    response = client.post(
        f"/api/projects/{project_id}/publish-status-snapshots/{status_snapshot_id}/metrics-snapshots",
        json={"fallback_provider_id": "douyin_sandbox"},
    )

    assert response.status_code == 409
    assert response.json()["detail"].startswith("sandbox_fallback_forbidden:")
    assert_metrics_snapshot_count(0)


def test_external_metrics_query_is_blocked(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client)
    snapshot = create_status_snapshot(client, project_id, attempt["id"])

    response = client.post(
        f"/api/projects/{project_id}/publish-status-snapshots/{snapshot['status_snapshot_id']}/metrics-snapshots",
        json={"external_metrics_query_requested": True},
    )

    assert response.status_code == 409
    assert response.json()["detail"].startswith("external_metrics_query_blocked:")
    assert_metrics_snapshot_count(0)


def test_metrics_snapshot_creation_does_not_call_provider_metrics_status_upload_publish_or_network(
    client: TestClient,
    monkeypatch,
):
    project_id, attempt = prepare_publish_status_project(client)
    snapshot = create_status_snapshot(client, project_id, attempt["id"])
    calls: list[str] = []

    def fail_metric_collect(*args, **kwargs):
        calls.append("metrics_provider")
        raise AssertionError("provider metrics query must not be called")

    def fail_status_reconciliation(*args, **kwargs):
        calls.append("status_query")
        raise AssertionError("status query must not be called")

    def fail_publish(*args, **kwargs):
        calls.append("publish")
        raise AssertionError("publish must not be called")

    def fail_socket(*args, **kwargs):
        calls.append("socket")
        raise AssertionError("network must not be called")

    monkeypatch.setattr(FakeMetricsProvider, "collect", fail_metric_collect)
    monkeypatch.setattr(
        "app.publishing.publish_status_reconciliation.create_publish_status_reconciliation",
        fail_status_reconciliation,
    )
    monkeypatch.setattr(FakePublisherProvider, "execute", fail_publish)
    monkeypatch.setattr(socket, "create_connection", fail_socket)
    monkeypatch.setattr(socket.socket, "connect", fail_socket, raising=False)
    monkeypatch.setattr(urllib.request, "urlopen", fail_socket)

    if importlib.util.find_spec("requests") is not None:
        import requests

        monkeypatch.setattr(requests.sessions.Session, "request", fail_socket)
    if importlib.util.find_spec("httpx") is not None:
        import httpx

        monkeypatch.setattr(httpx.Client, "request", fail_socket)
        monkeypatch.setattr(httpx.AsyncClient, "request", fail_socket)

    with connect_db(get_settings()) as connection:
        result = create_limited_metrics_snapshot(
            connection,
            project_id=project_id,
            status_snapshot_id=snapshot["status_snapshot_id"],
        )

    assert result["metrics_snapshot_id"].startswith("pms_")
    assert calls == []


def test_fake_env_secrets_are_not_read_or_leaked(client: TestClient, monkeypatch):
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", FAKE_ACCESS_TOKEN_VALUE)
    monkeypatch.setenv("DOUYIN_REFRESH_TOKEN", FAKE_REFRESH_TOKEN_VALUE)
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", FAKE_CLIENT_SECRET_VALUE)
    monkeypatch.setenv("DOUYIN_API_KEY", FAKE_API_KEY_VALUE)
    project_id, attempt = prepare_publish_status_project(client)
    snapshot = create_status_snapshot(client, project_id, attempt["id"])

    response = client.post(
        f"/api/projects/{project_id}/publish-status-snapshots/{snapshot['status_snapshot_id']}/metrics-snapshots",
        json={},
    )

    assert response.status_code == 201
    assert_no_material_values(response.json())


def test_api_response_contains_safe_metadata_only(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client)
    snapshot = create_status_snapshot(client, project_id, attempt["id"])

    response = client.post(
        f"/api/projects/{project_id}/publish-status-snapshots/{snapshot['status_snapshot_id']}/metrics-snapshots",
        json={},
    )
    list_response = client.get(f"/api/projects/{project_id}/metrics-snapshots")
    get_response = client.get(f"/api/projects/{project_id}/metrics-snapshots/{response.json()['metrics_snapshot_id']}")

    assert response.status_code == 201
    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert_no_material_values(response.json())
    assert_no_material_values(list_response.json())
    assert_no_material_values(get_response.json())
    assert "metrics_freshness_status" in response.json()


def test_no_real_douyin_metrics_upload_scheduled_publish_oauth_or_token_routes_added():
    route_paths = {getattr(route, "path", "") for route in app.routes}
    rendered = "\n".join(sorted(route_paths)).lower()
    metrics_snapshot_paths = "\n".join(path for path in route_paths if "metrics-snapshots" in path).lower()

    assert "/api/projects/{project_id}/publish-status-snapshots/{status_snapshot_id}/metrics-snapshots" in route_paths
    assert "/api/projects/{project_id}/metrics-snapshots" in route_paths
    assert "oauth/start" not in rendered
    assert "oauth/callback" not in rendered
    assert "oauth-url" not in rendered
    assert "authorization-url" not in rendered
    assert "token-exchange" not in rendered
    assert "credential-storage" not in rendered
    assert "douyin-real" not in rendered
    assert "scheduled-publish" not in rendered
    assert "upload" not in metrics_snapshot_paths
    assert "douyin" not in metrics_snapshot_paths
    assert "metrics-query" not in rendered


def create_project(client: TestClient) -> int:
    response = client.post(
        "/api/projects",
        json={"title": "Batch 9 metrics foundation", "description": "Local metrics only"},
    )
    return response.json()["id"]


def create_status_snapshot(
    client: TestClient,
    project_id: int,
    publish_attempt_id: int,
    *,
    local_publish_status: str = "local_status_reconciled",
    status_source: str = "fake_fixture",
) -> dict:
    response = client.post(
        f"/api/projects/{project_id}/publish-attempts/{publish_attempt_id}/status-reconciliations",
        json={
            "fake_status_fixture": {
                "local_publish_status": local_publish_status,
                "status_observed_at": "2026-05-29T01:00:00Z",
                "status_source": status_source,
                "safe_status_message": "Local status fixture for metrics foundation; not real Douyin status.",
            }
        },
    )
    assert response.status_code == 201
    snapshots = client.get(
        f"/api/projects/{project_id}/publish-attempts/{publish_attempt_id}/status-snapshots"
    ).json()
    return snapshots[0]


def insert_status_snapshot(
    publish_attempt_id: int,
    *,
    provider_id: str,
    source_type: str,
    local_publish_status: str = "local_status_reconciled",
) -> str:
    status_snapshot_id = f"pss_{uuid.uuid4().hex}"
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            """
            INSERT INTO publish_status_snapshots (
                status_snapshot_id, publish_attempt_id, reconciliation_id, provider_id,
                source_type, local_publish_status, status_observed_at, status_source,
                safe_status_message
            )
            VALUES (?, ?, NULL, ?, ?, ?, '2026-05-29T01:00:00Z', 'local',
                    'Local status snapshot fixture for metrics read tests.')
            """,
            (status_snapshot_id, publish_attempt_id, provider_id, source_type, local_publish_status),
        )
    return status_snapshot_id


def metrics_policy(
    *,
    feature_flag_status: str = FeatureFlagStatus.ENABLED.value,
    kill_switch_status: str = KillSwitchStatus.INACTIVE.value,
    environment_status: str = RuntimeEnvironmentStatus.ALLOWED.value,
    platform_preconditions_status: str = PlatformPreconditionsStatus.ACCEPTED.value,
) -> RealProviderControlPolicy:
    return RealProviderControlPolicy(
        feature_flag_status=feature_flag_status,
        kill_switch_status=kill_switch_status,
        allowed_capabilities=frozenset({RealProviderCapability.METRICS_READ.value}),
        environment_status=environment_status,
        platform_preconditions_status=platform_preconditions_status,
    )


def assert_metrics_snapshot_count(expected_count: int) -> None:
    with sqlite3.connect(get_settings().database_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM publish_metrics_snapshots").fetchone()[0]
    assert count == expected_count


def assert_no_material_values(value: Any) -> None:
    text = json.dumps(value, default=str, sort_keys=True) if not isinstance(value, str) else value
    for material_value in FORBIDDEN_MATERIAL_VALUES:
        assert material_value not in text
