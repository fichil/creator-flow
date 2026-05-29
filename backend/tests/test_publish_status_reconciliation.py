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
from app.providers.real_provider_controls import (
    FeatureFlagStatus,
    KillSwitchStatus,
    PlatformPreconditionsStatus,
    RealProviderCapability,
    RealProviderControlPolicy,
    RuntimeEnvironmentStatus,
)
from app.publishers.fake_publisher import FakePublisherProvider
from app.publishing.publish_status_reconciliation import (
    PublishStatusReconciliationError,
    create_publish_status_reconciliation,
)


FAKE_ACCESS_TOKEN_VALUE = "fake-status-access-token-value"
FAKE_REFRESH_TOKEN_VALUE = "fake-status-refresh-token-value"
FAKE_SECRET_VALUE = "fake-status-secret-value"
FAKE_CLIENT_SECRET_VALUE = "fake-status-client-secret-value"
FAKE_CREDENTIAL_VALUE = "fake-status-credential-value"
FAKE_AUTHORIZATION_CODE_VALUE = "fake-status-authorization-code-value"
FAKE_RAW_STATE_VALUE = "fake-status-raw-oauth-state-value"
FAKE_COOKIE_VALUE = "fake-status-cookie-value"
FAKE_SESSION_VALUE = "fake-status-session-value"
FAKE_API_KEY_VALUE = "fake-status-api-key-value"
FAKE_BEARER_VALUE = "fake-status-bearer-value"
FAKE_RAW_REQUEST_VALUE = "fake-status-raw-request-value"
FAKE_RAW_RESPONSE_VALUE = "fake-status-raw-response-value"
FAKE_PROVIDER_RESPONSE_VALUE = "fake-status-provider-response-value"
FAKE_UPLOAD_RESPONSE_VALUE = "fake-status-upload-response-value"
FAKE_PUBLISH_RESPONSE_VALUE = "fake-status-publish-response-value"
FAKE_STATUS_RESPONSE_VALUE = "fake-status-response-value"
FAKE_EXTERNAL_RESPONSE_VALUE = "fake-external-status-response-value"
FAKE_DOUYIN_RESPONSE_VALUE = "fake-douyin-status-response-value"
FAKE_METRICS_RESPONSE_VALUE = "fake-status-metrics-response-value"

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
    "external_response",
    "douyin_response",
    "metrics_response",
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
    FAKE_EXTERNAL_RESPONSE_VALUE,
    FAKE_DOUYIN_RESPONSE_VALUE,
    FAKE_METRICS_RESPONSE_VALUE,
}


def test_publish_status_schema_is_metadata_only(client: TestClient):
    with sqlite3.connect(get_settings().database_path) as connection:
        reconciliation_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(publish_status_reconciliations)").fetchall()
        }
        snapshot_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(publish_status_snapshots)").fetchall()
        }

    assert {
        "reconciliation_id",
        "publish_attempt_id",
        "publish_intent_id",
        "review_item_id",
        "provider_id",
        "source_type",
        "reconciliation_status",
        "local_publish_status",
        "external_query_status",
        "safe_status_message",
        "last_status_change_reason",
    }.issubset(reconciliation_columns)
    assert {
        "status_snapshot_id",
        "publish_attempt_id",
        "reconciliation_id",
        "provider_id",
        "source_type",
        "local_publish_status",
        "status_observed_at",
        "status_source",
        "safe_status_message",
    }.issubset(snapshot_columns)
    assert reconciliation_columns.isdisjoint(FORBIDDEN_DB_COLUMNS)
    assert snapshot_columns.isdisjoint(FORBIDDEN_DB_COLUMNS)


def test_status_reconciliation_requires_existing_publish_attempt(client: TestClient):
    project_id = create_project(client)

    response = client.post(f"/api/projects/{project_id}/publish-attempts/999/status-reconciliations", json={})

    assert response.status_code == 404
    assert response.json()["detail"].startswith("publish_attempt_required:")
    assert_status_reconciliation_count(0)


def test_missing_publish_attempt_is_rejected(client: TestClient):
    project_id = create_project(client)

    response = client.get(f"/api/projects/{project_id}/publish-attempts/999/status-snapshots")

    assert response.status_code == 404
    assert response.json()["detail"].startswith("publish_attempt_required:")


def test_blocked_cancelled_and_failed_safe_attempts_are_rejected(client: TestClient):
    for attempt_status in ("blocked", "cancelled", "failed_safe"):
        project_id, review_item = prepare_base_project(client)
        attempt_id = insert_publish_attempt(
            project_id,
            review_item["id"],
            provider_id="fake_local",
            source_type="fake_local",
            attempt_status=attempt_status,
        )

        response = client.post(
            f"/api/projects/{project_id}/publish-attempts/{attempt_id}/status-reconciliations",
            json={},
        )

        assert response.status_code == 409
        assert response.json()["detail"].startswith("publish_attempt_not_ready:")


def test_valid_fake_local_attempt_creates_metadata_only_reconciliation(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client)

    response = client.post(
        f"/api/projects/{project_id}/publish-attempts/{attempt['id']}/status-reconciliations",
        json={},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["result_category"] == "status_reconciliation_created"
    assert body["publish_attempt_id"] == attempt["id"]
    assert body["provider_id"] == "fake_local"
    assert body["source_type"] == "fake_local"
    assert body["reconciliation_status"] == "created"
    assert body["local_publish_status"] == "local_status_unknown"
    assert body["external_query_status"] == "not_called"
    assert "no external provider status query" in body["safe_status_message"]
    assert_no_material_values(body)

    snapshots = client.get(
        f"/api/projects/{project_id}/publish-attempts/{attempt['id']}/status-snapshots"
    ).json()
    assert len(snapshots) == 1
    assert snapshots[0]["local_publish_status"] == "local_status_unknown"
    assert snapshots[0]["status_source"] == "local"
    assert_no_material_values(snapshots)


def test_valid_sandbox_safe_attempt_can_create_fixture_snapshot(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client, target_platform="douyin_sandbox")

    response = client.post(
        f"/api/projects/{project_id}/publish-attempts/{attempt['id']}/status-reconciliations",
        json={
            "fake_status_fixture": {
                "local_publish_status": "local_status_reconciled",
                "status_observed_at": "2026-05-29T01:00:00Z",
                "status_source": "sandbox_fixture",
                "safe_status_message": "Sandbox-safe local fixture status; not real Douyin status.",
            }
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["provider_id"] == "douyin_sandbox"
    assert body["source_type"] == "sandbox"
    assert body["local_publish_status"] == "local_status_reconciled"
    snapshots = client.get(
        f"/api/projects/{project_id}/publish-attempts/{attempt['id']}/status-snapshots"
    ).json()
    assert snapshots[0]["status_source"] == "sandbox_fixture"
    assert snapshots[0]["safe_status_message"].endswith("not real Douyin status.")
    assert_no_material_values(body)
    assert_no_material_values(snapshots)


def test_duplicate_active_reconciliation_is_rejected(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client)
    first_response = client.post(
        f"/api/projects/{project_id}/publish-attempts/{attempt['id']}/status-reconciliations",
        json={},
    )

    response = client.post(
        f"/api/projects/{project_id}/publish-attempts/{attempt['id']}/status-reconciliations",
        json={},
    )

    assert first_response.status_code == 201
    assert response.status_code == 409
    assert response.json()["detail"].startswith("duplicate_reconciliation:")
    assert_status_reconciliation_count(1)


def test_stale_status_update_is_ignored_safely(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client)
    first_response = client.post(
        f"/api/projects/{project_id}/publish-attempts/{attempt['id']}/status-reconciliations",
        json={
            "fake_status_fixture": {
                "local_publish_status": "local_status_reconciled",
                "status_observed_at": "2026-05-29T02:00:00Z",
                "status_source": "fake_fixture",
                "safe_status_message": "Fake local status fixture; not real Douyin status.",
            }
        },
    )
    mark_reconciliation_completed(first_response.json()["reconciliation_id"])

    response = client.post(
        f"/api/projects/{project_id}/publish-attempts/{attempt['id']}/status-reconciliations",
        json={
            "fake_status_fixture": {
                "local_publish_status": "local_pending",
                "status_observed_at": "2026-05-29T01:00:00Z",
                "status_source": "fake_fixture",
                "safe_status_message": "Older fake local status fixture; not real Douyin status.",
            }
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result_category"] == "stale_status_ignored"
    assert body["last_status_change_reason"] == "stale_status_ignored"
    snapshots = client.get(
        f"/api/projects/{project_id}/publish-attempts/{attempt['id']}/status-snapshots"
    ).json()
    assert len(snapshots) == 1
    assert snapshots[0]["status_observed_at"] == "2026-05-29T02:00:00Z"
    assert_no_material_values(body)


def test_malformed_fake_status_fixture_is_rejected_safely(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client)

    response = client.post(
        f"/api/projects/{project_id}/publish-attempts/{attempt['id']}/status-reconciliations",
        json={
            "fake_status_fixture": {
                "local_publish_status": "published_on_real_douyin",
                "status_observed_at": "not-a-date",
                "status_source": "provider_response",
                "safe_status_message": FAKE_STATUS_RESPONSE_VALUE,
            }
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"].startswith("status_fixture_invalid:")
    assert_status_reconciliation_count(0)
    assert_no_material_values(response.json())


def test_real_provider_disabled_by_default_and_kill_switch_active_blocks(client: TestClient):
    project_id, review_item = prepare_base_project(client)
    attempt_id = insert_publish_attempt(
        project_id,
        review_item["id"],
        provider_id="douyin_real",
        source_type="real",
    )

    response = client.post(
        f"/api/projects/{project_id}/publish-attempts/{attempt_id}/status-reconciliations",
        json={},
    )

    assert response.status_code == 409
    assert response.json()["detail"].startswith("kill_switch_active:")
    assert_status_reconciliation_count(0)


def test_real_provider_feature_disabled_returns_safe_disabled_result(client: TestClient):
    project_id, review_item = prepare_base_project(client)
    attempt_id = insert_publish_attempt(
        project_id,
        review_item["id"],
        provider_id="douyin_real",
        source_type="real",
    )

    with connect_db(get_settings()) as connection:
        try:
            create_publish_status_reconciliation(
                connection,
                project_id=project_id,
                publish_attempt_id=attempt_id,
                real_provider_control_policy=allowing_policy(
                    feature_flag_status=FeatureFlagStatus.DISABLED.value
                ),
            )
        except PublishStatusReconciliationError as exc:
            assert exc.category == "real_provider_disabled"
            assert_no_material_values(exc)
        else:
            raise AssertionError("feature-disabled real provider status reconciliation must be blocked")


def test_platform_preconditions_missing_blocks_reconciliation(client: TestClient):
    project_id, review_item = prepare_base_project(client)
    attempt_id = insert_publish_attempt(
        project_id,
        review_item["id"],
        provider_id="douyin_real",
        source_type="real",
    )

    with connect_db(get_settings()) as connection:
        try:
            create_publish_status_reconciliation(
                connection,
                project_id=project_id,
                publish_attempt_id=attempt_id,
                real_provider_control_policy=allowing_policy(
                    platform_preconditions_status=PlatformPreconditionsStatus.MISSING.value
                ),
            )
        except PublishStatusReconciliationError as exc:
            assert exc.category == "platform_preconditions_missing"
            assert_no_material_values(exc)
        else:
            raise AssertionError("missing platform preconditions must block status reconciliation")


def test_unsupported_provider_is_rejected(client: TestClient):
    project_id, review_item = prepare_base_project(client)
    attempt_id = insert_publish_attempt(
        project_id,
        review_item["id"],
        provider_id="unknown_provider",
        source_type="fake_local",
    )

    response = client.post(
        f"/api/projects/{project_id}/publish-attempts/{attempt_id}/status-reconciliations",
        json={},
    )

    assert response.status_code == 409
    assert response.json()["detail"].startswith("unsupported_provider:")
    assert_status_reconciliation_count(0)


def test_douyin_real_does_not_fallback_to_sandbox(client: TestClient):
    project_id, review_item = prepare_base_project(client)
    attempt_id = insert_publish_attempt(
        project_id,
        review_item["id"],
        provider_id="douyin_real",
        source_type="real",
    )

    with connect_db(get_settings()) as connection:
        try:
            create_publish_status_reconciliation(
                connection,
                project_id=project_id,
                publish_attempt_id=attempt_id,
                fallback_provider_id="douyin_sandbox",
            )
        except PublishStatusReconciliationError as exc:
            assert exc.category == "sandbox_fallback_forbidden"
            assert_no_material_values(exc)
        else:
            raise AssertionError("real provider fallback to sandbox must be forbidden")


def test_external_status_query_is_blocked_by_default(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client)

    response = client.post(
        f"/api/projects/{project_id}/publish-attempts/{attempt['id']}/status-reconciliations",
        json={"external_status_query_requested": True},
    )

    assert response.status_code == 409
    assert response.json()["detail"].startswith("external_status_query_blocked:")
    assert_status_reconciliation_count(0)


def test_reconciliation_creation_does_not_call_provider_status_query_network_upload_publish_or_metrics(
    client: TestClient,
    monkeypatch,
):
    project_id, attempt = prepare_publish_status_project(client)
    calls: list[tuple[Any, ...]] = []

    def fail_if_called(*args, **kwargs):
        calls.append(args)
        raise AssertionError("status reconciliation must not call external runtime paths")

    monkeypatch.setattr(FakePublisherProvider, "execute", fail_if_called)
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
        result = create_publish_status_reconciliation(
            connection,
            project_id=project_id,
            publish_attempt_id=attempt["id"],
        )

    assert result["external_query_status"] == "not_called"
    assert calls == []


def test_reconciliation_service_does_not_read_or_leak_env_secret(client: TestClient, monkeypatch):
    project_id, attempt = prepare_publish_status_project(client)
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", FAKE_CLIENT_SECRET_VALUE)

    response = client.post(
        f"/api/projects/{project_id}/publish-attempts/{attempt['id']}/status-reconciliations",
        json={},
    )

    assert response.status_code == 201
    assert FAKE_CLIENT_SECRET_VALUE not in repr(response.json())


def test_api_response_contains_safe_metadata_only(client: TestClient):
    project_id, attempt = prepare_publish_status_project(client)

    response = client.post(
        f"/api/projects/{project_id}/publish-attempts/{attempt['id']}/status-reconciliations",
        json={},
    )
    list_response = client.get(f"/api/projects/{project_id}/publish-status-reconciliations")
    get_response = client.get(
        f"/api/projects/{project_id}/publish-status-reconciliations/{response.json()['reconciliation_id']}"
    )
    snapshots_response = client.get(
        f"/api/projects/{project_id}/publish-attempts/{attempt['id']}/status-snapshots"
    )

    assert response.status_code == 201
    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert snapshots_response.status_code == 200
    assert_no_material_values(response.json())
    assert_no_material_values(list_response.json())
    assert_no_material_values(get_response.json())
    assert_no_material_values(snapshots_response.json())


def test_no_real_douyin_metrics_upload_scheduled_publish_oauth_or_token_routes_added():
    route_paths = {getattr(route, "path", "") for route in app.routes}
    rendered = "\n".join(sorted(route_paths)).lower()
    status_paths = "\n".join(path for path in route_paths if "status-reconciliation" in path).lower()

    assert "/api/projects/{project_id}/publish-attempts/{publish_attempt_id}/status-reconciliations" in route_paths
    assert "oauth/start" not in rendered
    assert "oauth/callback" not in rendered
    assert "oauth-url" not in rendered
    assert "authorization-url" not in rendered
    assert "token-exchange" not in rendered
    assert "credential-storage" not in rendered
    assert "douyin-real" not in rendered
    assert "scheduled-publish" not in rendered
    assert "upload" not in status_paths
    assert "metrics" not in status_paths


def prepare_publish_status_project(
    client: TestClient,
    *,
    target_platform: str = "fake_local",
) -> tuple[int, dict]:
    project_id, review_item = prepare_base_project(client)
    if target_platform == "douyin_sandbox":
        insert_metadata_only_credential_reference("douyin_sandbox", "sandbox")
    intent = create_confirmed_intent(
        client,
        project_id,
        review_item["id"],
        target_platform=target_platform,
    ).json()
    attempt = client.post(f"/api/projects/{project_id}/publish-intents/{intent['id']}/attempts").json()
    return project_id, attempt


def prepare_base_project(client: TestClient) -> tuple[int, dict]:
    project_id = create_project(client)
    review_item = create_review_item(client, project_id)
    create_ready_media_artifact(client, project_id)
    return project_id, review_item


def create_project(client: TestClient) -> int:
    response = client.post(
        "/api/projects",
        json={"title": "Batch 8 status reconciliation", "description": "Local status only"},
    )
    return response.json()["id"]


def create_content_plan(client: TestClient, project_id: int) -> int:
    response = client.post(
        f"/api/projects/{project_id}/content-plans",
        json={
            "name": "Weekly AI dev log",
            "account_positioning": "Chinese developer sharing practical AI workflow notes",
            "content_type": "programmer_real_problem",
            "target_frequency_per_week": 3,
            "preferences": '{"tone":"practical","length":"short"}',
        },
    )
    return response.json()["id"]


def create_review_item(client: TestClient, project_id: int) -> dict:
    content_plan_id = create_content_plan(client, project_id)
    client.post(f"/api/projects/{project_id}/content-plans/{content_plan_id}/generation-runs", json={})
    review_item = client.get(f"/api/projects/{project_id}/review-drafts").json()[0]
    return client.post(f"/api/projects/{project_id}/review-drafts/{review_item['id']}/approve").json()


def create_ready_media_artifact(client: TestClient, project_id: int) -> dict:
    client.post(
        f"/api/projects/{project_id}/materials/text",
        json={
            "material_type": "text",
            "title": "Batch 8 local source",
            "text_content": "Obvious local test material for a fake render preview.",
        },
    )
    topic = client.post(f"/api/projects/{project_id}/topic-candidates/generate", json={"candidate_count": 1}).json()
    topic_id = topic["candidates"][0]["id"]
    client.post(f"/api/projects/{project_id}/topic-candidates/{topic_id}/select")
    script = client.post(f"/api/projects/{project_id}/script-drafts/generate", json={"script_count": 1}).json()
    script_id = script["script_drafts"][0]["id"]
    client.post(f"/api/projects/{project_id}/script-drafts/{script_id}/select")
    storyboard = client.post(f"/api/projects/{project_id}/storyboards/generate", json={"storyboard_count": 1}).json()
    storyboard_id = storyboard["storyboards"][0]["id"]
    client.post(f"/api/projects/{project_id}/storyboards/{storyboard_id}/select")
    return client.post(f"/api/projects/{project_id}/renders", json={}).json()["artifact"]


def create_confirmed_intent(
    client: TestClient,
    project_id: int,
    review_item_id: int,
    *,
    target_platform: str = "fake_local",
):
    return client.post(
        f"/api/projects/{project_id}/publish-intents",
        json={
            "review_draft_id": review_item_id,
            "target_platform": target_platform,
            "title": "Batch 8 status reconciliation intent",
            "caption": "Local metadata only; no upload, publish, schedule, status query, or metrics.",
            "confirm_publish_intent": True,
        },
    )


def insert_publish_attempt(
    project_id: int,
    review_item_id: int,
    *,
    provider_id: str,
    source_type: str,
    attempt_status: str = "created",
    guard_status: str = "passed_simulated",
) -> int:
    intent_id = insert_confirmed_publish_intent(
        project_id,
        review_item_id,
        provider_id=provider_id,
        source_type=source_type,
    )
    with sqlite3.connect(get_settings().database_path) as connection:
        row = connection.execute(
            """
            INSERT INTO publish_attempts (
                project_id, publish_intent_id, review_draft_id, provider_id, source_type,
                attempt_status, guard_status, external_call_status, safe_status_message,
                last_status_change_reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'not_called',
                    'Local guarded attempt fixture for status reconciliation tests.',
                    'batch8_status_reconciliation_test_fixture')
            RETURNING id
            """,
            (
                project_id,
                intent_id,
                review_item_id,
                provider_id,
                source_type,
                attempt_status,
                guard_status,
            ),
        ).fetchone()
    return row[0]


def insert_confirmed_publish_intent(
    project_id: int,
    review_item_id: int,
    *,
    provider_id: str,
    source_type: str,
) -> int:
    with sqlite3.connect(get_settings().database_path) as connection:
        row = connection.execute(
            """
            INSERT INTO publish_intents (
                project_id, review_draft_id, target_platform, source_type, title, caption,
                publish_status, confirmation_status, confirmed_at, safe_status_message,
                last_status_change_reason
            )
            VALUES (?, ?, ?, ?, 'Batch 8 status intent fixture',
                    'Local metadata only for status reconciliation.', 'confirmed',
                    'confirmed', CURRENT_TIMESTAMP,
                    'Confirmed local publish intent fixture; no provider publish executed.',
                    'batch8_status_test_fixture')
            RETURNING id
            """,
            (project_id, review_item_id, provider_id, source_type),
        ).fetchone()
    return row[0]


def insert_metadata_only_credential_reference(provider_id: str, source_type: str) -> str:
    reference_id = uuid.uuid4().hex
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            """
            INSERT INTO provider_credential_references (
                reference_id, provider_id, source_type, reference_kind, reference_status,
                storage_status, redaction_policy_status, safe_display_name,
                safe_status_message, last_status_change_reason
            )
            VALUES (?, ?, ?, 'credential_reference_placeholder', 'reference_only',
                    'reference_only', 'active',
                    'Metadata-only credential reference for status reconciliation tests',
                    'Credential reference metadata only; no credential material stored.',
                    'batch8_test_metadata_reference')
            """,
            (reference_id, provider_id, source_type),
        )
    return reference_id


def mark_reconciliation_completed(reconciliation_id: str) -> None:
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            """
            UPDATE publish_status_reconciliations
            SET reconciliation_status = 'completed_safe',
                completed_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP,
                last_status_change_reason = 'test_completed_safe'
            WHERE reconciliation_id = ?
            """,
            (reconciliation_id,),
        )


def allowing_policy(
    *,
    feature_flag_status: str = FeatureFlagStatus.ENABLED.value,
    kill_switch_status: str = KillSwitchStatus.INACTIVE.value,
    environment_status: str = RuntimeEnvironmentStatus.ALLOWED.value,
    platform_preconditions_status: str = PlatformPreconditionsStatus.ACCEPTED.value,
) -> RealProviderControlPolicy:
    return RealProviderControlPolicy(
        feature_flag_status=feature_flag_status,
        kill_switch_status=kill_switch_status,
        allowed_capabilities=frozenset({RealProviderCapability.PUBLISH_STATUS.value}),
        environment_status=environment_status,
        platform_preconditions_status=platform_preconditions_status,
    )


def assert_status_reconciliation_count(expected_count: int) -> None:
    with sqlite3.connect(get_settings().database_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM publish_status_reconciliations").fetchone()[0]
    assert count == expected_count


def assert_no_material_values(value: Any) -> None:
    text = json.dumps(value, default=str, sort_keys=True) if not isinstance(value, str) else value
    for material_value in FORBIDDEN_MATERIAL_VALUES:
        assert material_value not in text
