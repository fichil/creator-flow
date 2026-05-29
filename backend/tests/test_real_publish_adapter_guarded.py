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
from app.publishing.real_publish_adapter import (
    GuardedPublishAttemptError,
    create_guarded_publish_attempt,
)


FAKE_ACCESS_TOKEN_VALUE = "fake-access-token-value"
FAKE_REFRESH_TOKEN_VALUE = "fake-refresh-token-value"
FAKE_SECRET_VALUE = "fake-secret-value"
FAKE_CLIENT_SECRET_VALUE = "fake-client-secret-value"
FAKE_CREDENTIAL_VALUE = "fake-credential-value"
FAKE_AUTHORIZATION_CODE_VALUE = "fake-authorization-code-value"
FAKE_RAW_STATE_VALUE = "fake-raw-oauth-state-value"
FAKE_COOKIE_VALUE = "fake-cookie-value"
FAKE_SESSION_VALUE = "fake-session-value"
FAKE_API_KEY_VALUE = "fake-api-key-value"
FAKE_BEARER_VALUE = "fake-bearer-value"
FAKE_RAW_REQUEST_VALUE = "fake-raw-request-value"
FAKE_RAW_RESPONSE_VALUE = "fake-raw-response-value"
FAKE_PROVIDER_RESPONSE_VALUE = "fake-provider-response-value"
FAKE_UPLOAD_RESPONSE_VALUE = "fake-upload-response-value"
FAKE_PUBLISH_RESPONSE_VALUE = "fake-publish-response-value"

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
}


def test_publish_attempt_schema_is_metadata_only(client: TestClient):
    with sqlite3.connect(get_settings().database_path) as connection:
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(publish_attempts)").fetchall()
        }

    assert {
        "id",
        "project_id",
        "publish_intent_id",
        "review_draft_id",
        "provider_id",
        "source_type",
        "attempt_status",
        "guard_status",
        "external_call_status",
        "safe_status_message",
        "last_status_change_reason",
    }.issubset(columns)
    assert columns.isdisjoint(FORBIDDEN_DB_COLUMNS)


def test_publish_attempt_requires_confirmed_publish_intent(client: TestClient):
    project_id, _review_item = prepare_publish_attempt_project(client)

    response = client.post(f"/api/projects/{project_id}/publish-intents/999/attempts")

    assert response.status_code == 404
    assert response.json()["detail"].startswith("publish_intent_required:")
    assert_publish_attempt_count(0)


def test_cancelled_publish_intent_is_rejected(client: TestClient):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent = create_confirmed_intent(client, project_id, review_item["id"]).json()
    client.post(f"/api/projects/{project_id}/publish-intents/{intent['id']}/cancel")

    response = client.post(f"/api/projects/{project_id}/publish-intents/{intent['id']}/attempts")

    assert response.status_code == 409
    assert response.json()["detail"].startswith("publish_intent_not_ready:")
    assert_publish_attempt_count(0)


def test_review_item_not_ready_is_rejected(client: TestClient):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent = create_confirmed_intent(client, project_id, review_item["id"]).json()
    set_review_status(review_item["id"], "rejected")

    response = client.post(f"/api/projects/{project_id}/publish-intents/{intent['id']}/attempts")

    assert response.status_code == 409
    assert response.json()["detail"].startswith("review_not_ready:")
    assert_publish_attempt_count(0)


def test_media_artifact_missing_is_rejected(client: TestClient):
    project_id, review_item = prepare_publish_attempt_project(client, media_ready=False)
    intent_id = insert_confirmed_publish_intent(
        project_id,
        review_item["id"],
        provider_id="fake_local",
        source_type="fake_local",
    )

    response = client.post(f"/api/projects/{project_id}/publish-intents/{intent_id}/attempts")

    assert response.status_code == 409
    assert response.json()["detail"].startswith("media_not_ready:")
    assert_publish_attempt_count(0)


def test_metadata_invalid_is_rejected(client: TestClient):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent_id = insert_confirmed_publish_intent(
        project_id,
        review_item["id"],
        provider_id="fake_local",
        source_type="fake_local",
        caption="contains access_token marker",
    )

    response = client.post(f"/api/projects/{project_id}/publish-intents/{intent_id}/attempts")

    assert response.status_code == 422
    assert response.json()["detail"].startswith("metadata_invalid:")
    assert_publish_attempt_count(0)


def test_credential_reference_missing_is_rejected_for_sandbox(client: TestClient):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent = create_confirmed_intent(
        client,
        project_id,
        review_item["id"],
        target_platform="douyin_sandbox",
    ).json()

    response = client.post(f"/api/projects/{project_id}/publish-intents/{intent['id']}/attempts")

    assert response.status_code == 409
    assert response.json()["detail"].startswith("credential_reference_missing:")
    assert_publish_attempt_count(0)


def test_valid_fake_local_intent_creates_metadata_only_publish_attempt(client: TestClient):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent = create_confirmed_intent(client, project_id, review_item["id"]).json()

    response = client.post(f"/api/projects/{project_id}/publish-intents/{intent['id']}/attempts")

    assert response.status_code == 201
    body = response.json()
    assert body["publish_intent_id"] == intent["id"]
    assert body["provider_id"] == "fake_local"
    assert body["source_type"] == "fake_local"
    assert body["attempt_status"] == "created"
    assert body["guard_status"] == "passed_simulated"
    assert body["external_call_status"] == "not_called"
    assert "no upload" in body["safe_status_message"]
    assert_no_material_values(body)


def test_valid_sandbox_safe_intent_creates_metadata_only_publish_attempt(client: TestClient):
    project_id, review_item = prepare_publish_attempt_project(client)
    insert_metadata_only_credential_reference("douyin_sandbox", "sandbox")
    intent = create_confirmed_intent(
        client,
        project_id,
        review_item["id"],
        target_platform="douyin_sandbox",
    ).json()

    response = client.post(f"/api/projects/{project_id}/publish-intents/{intent['id']}/attempts")

    assert response.status_code == 201
    body = response.json()
    assert body["provider_id"] == "douyin_sandbox"
    assert body["source_type"] == "sandbox"
    assert body["external_call_status"] == "not_called"
    assert_no_material_values(body)


def test_duplicate_active_publish_attempt_is_rejected(client: TestClient):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent = create_confirmed_intent(client, project_id, review_item["id"]).json()
    first_response = client.post(f"/api/projects/{project_id}/publish-intents/{intent['id']}/attempts")

    response = client.post(f"/api/projects/{project_id}/publish-intents/{intent['id']}/attempts")

    assert first_response.status_code == 201
    assert response.status_code == 409
    assert response.json()["detail"].startswith("duplicate_publish_attempt:")
    assert_publish_attempt_count(1)


def test_real_provider_is_blocked_by_default(client: TestClient):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent_id = insert_confirmed_publish_intent(
        project_id,
        review_item["id"],
        provider_id="douyin_real",
        source_type="real",
    )

    response = client.post(f"/api/projects/{project_id}/publish-intents/{intent_id}/attempts")

    assert response.status_code == 409
    assert response.json()["detail"].startswith("kill_switch_active:")
    assert_publish_attempt_count(0)


def test_kill_switch_active_blocks_attempt(client: TestClient):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent_id = insert_confirmed_publish_intent(
        project_id,
        review_item["id"],
        provider_id="douyin_real",
        source_type="real",
    )

    with connect_db(get_settings()) as connection:
        try:
            create_guarded_publish_attempt(
                connection,
                project_id=project_id,
                publish_intent_id=intent_id,
                real_provider_control_policy=allowing_policy(
                    kill_switch_status=KillSwitchStatus.ACTIVE.value
                ),
            )
        except GuardedPublishAttemptError as exc:
            assert exc.category == "kill_switch_active"
            assert_no_material_values(exc)
        else:
            raise AssertionError("kill switch must block real publish attempts")


def test_platform_preconditions_missing_blocks_attempt(client: TestClient):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent_id = insert_confirmed_publish_intent(
        project_id,
        review_item["id"],
        provider_id="douyin_real",
        source_type="real",
    )

    with connect_db(get_settings()) as connection:
        try:
            create_guarded_publish_attempt(
                connection,
                project_id=project_id,
                publish_intent_id=intent_id,
                real_provider_control_policy=allowing_policy(
                    platform_preconditions_status=PlatformPreconditionsStatus.MISSING.value
                ),
            )
        except GuardedPublishAttemptError as exc:
            assert exc.category == "platform_preconditions_missing"
            assert_no_material_values(exc)
        else:
            raise AssertionError("missing platform preconditions must block real publish attempts")


def test_unsupported_provider_is_rejected(client: TestClient):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent_id = insert_confirmed_publish_intent(
        project_id,
        review_item["id"],
        provider_id="unknown_provider",
        source_type="fake_local",
    )

    response = client.post(f"/api/projects/{project_id}/publish-intents/{intent_id}/attempts")

    assert response.status_code == 409
    assert response.json()["detail"].startswith("unsupported_provider:")
    assert_publish_attempt_count(0)


def test_douyin_real_does_not_fallback_to_sandbox(client: TestClient):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent_id = insert_confirmed_publish_intent(
        project_id,
        review_item["id"],
        provider_id="douyin_real",
        source_type="real",
    )

    with connect_db(get_settings()) as connection:
        try:
            create_guarded_publish_attempt(
                connection,
                project_id=project_id,
                publish_intent_id=intent_id,
                fallback_provider_id="douyin_sandbox",
            )
        except GuardedPublishAttemptError as exc:
            assert exc.category == "sandbox_fallback_forbidden"
            assert_no_material_values(exc)
        else:
            raise AssertionError("real provider fallback to sandbox must be forbidden")


def test_publish_attempt_creation_does_not_call_provider_publish(client: TestClient, monkeypatch):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent = create_confirmed_intent(client, project_id, review_item["id"]).json()

    def fail_publish(*args, **kwargs):
        raise AssertionError("guarded publish attempt must not execute provider publish")

    monkeypatch.setattr(FakePublisherProvider, "execute", fail_publish)
    response = client.post(f"/api/projects/{project_id}/publish-intents/{intent['id']}/attempts")

    assert response.status_code == 201
    assert response.json()["external_call_status"] == "not_called"


def test_publish_attempt_creation_does_not_call_external_network(client: TestClient, monkeypatch):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent = create_confirmed_intent(client, project_id, review_item["id"]).json()
    calls: list[tuple[Any, ...]] = []

    def fail_if_called(*args, **kwargs):
        calls.append(args)
        raise AssertionError("guarded publish attempt must not call external network")

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
        result = create_guarded_publish_attempt(
            connection,
            project_id=project_id,
            publish_intent_id=intent["id"],
        )

    assert result["external_call_status"] == "not_called"
    assert calls == []


def test_publish_attempt_service_does_not_read_or_leak_env_secret(client: TestClient, monkeypatch):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent = create_confirmed_intent(client, project_id, review_item["id"]).json()
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", FAKE_CLIENT_SECRET_VALUE)

    response = client.post(f"/api/projects/{project_id}/publish-intents/{intent['id']}/attempts")

    assert response.status_code == 201
    assert FAKE_CLIENT_SECRET_VALUE not in repr(response.json())


def test_api_response_contains_safe_metadata_only(client: TestClient):
    project_id, review_item = prepare_publish_attempt_project(client)
    intent = create_confirmed_intent(client, project_id, review_item["id"]).json()

    response = client.post(f"/api/projects/{project_id}/publish-intents/{intent['id']}/attempts")
    list_response = client.get(f"/api/projects/{project_id}/publish-attempts")
    get_response = client.get(f"/api/projects/{project_id}/publish-attempts/{response.json()['id']}")

    assert response.status_code == 201
    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert_no_material_values(response.json())
    assert_no_material_values(list_response.json())
    assert_no_material_values(get_response.json())


def test_no_upload_schedule_metrics_oauth_or_real_runtime_routes_added(client: TestClient):
    route_paths = {getattr(route, "path", "") for route in app.routes}
    rendered = "\n".join(sorted(route_paths)).lower()

    assert "/api/projects/{project_id}/publish-intents/{publish_intent_id}/attempts" in route_paths
    assert "oauth/start" not in rendered
    assert "oauth/callback" not in rendered
    assert "oauth-url" not in rendered
    assert "authorization-url" not in rendered
    assert "token-exchange" not in rendered
    assert "credential-storage" not in rendered
    assert "douyin-real" not in rendered
    assert "scheduled-publish" not in rendered
    assert "upload" not in "\n".join(path for path in route_paths if "publish" in path).lower()
    assert "metrics" not in "\n".join(path for path in route_paths if "publish-attempt" in path).lower()


def prepare_publish_attempt_project(
    client: TestClient,
    *,
    approve: bool = True,
    media_ready: bool = True,
) -> tuple[int, dict]:
    project_id = create_project(client)
    review_item = create_review_item(client, project_id, approve=approve)
    if media_ready:
        create_ready_media_artifact(client, project_id)
    return project_id, review_item


def create_project(client: TestClient) -> int:
    response = client.post(
        "/api/projects",
        json={"title": "Batch 7 guarded attempt", "description": "Local guarded attempt only"},
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


def create_review_item(client: TestClient, project_id: int, *, approve: bool = True) -> dict:
    content_plan_id = create_content_plan(client, project_id)
    client.post(f"/api/projects/{project_id}/content-plans/{content_plan_id}/generation-runs", json={})
    review_item = client.get(f"/api/projects/{project_id}/review-drafts").json()[0]
    if approve:
        review_item = client.post(f"/api/projects/{project_id}/review-drafts/{review_item['id']}/approve").json()
    return review_item


def create_ready_media_artifact(client: TestClient, project_id: int) -> dict:
    client.post(
        f"/api/projects/{project_id}/materials/text",
        json={
            "material_type": "text",
            "title": "Batch 7 local source",
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
            "title": "Batch 7 guarded publish attempt intent",
            "caption": "Local metadata only; no upload, publish, schedule, or metrics.",
            "confirm_publish_intent": True,
        },
    )


def insert_confirmed_publish_intent(
    project_id: int,
    review_item_id: int,
    *,
    provider_id: str,
    source_type: str,
    caption: str = "Local metadata only for guarded attempt.",
) -> int:
    with sqlite3.connect(get_settings().database_path) as connection:
        row = connection.execute(
            """
            INSERT INTO publish_intents (
                project_id, review_draft_id, target_platform, source_type, title, caption,
                publish_status, confirmation_status, confirmed_at, safe_status_message,
                last_status_change_reason
            )
            VALUES (?, ?, ?, ?, 'Batch 7 guarded intent fixture', ?, 'confirmed',
                    'confirmed', CURRENT_TIMESTAMP,
                    'Confirmed local publish intent fixture; no provider publish executed.',
                    'batch7_guarded_test_fixture')
            RETURNING id
            """,
            (project_id, review_item_id, provider_id, source_type, caption),
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
                    'Metadata-only credential reference for guarded attempt tests',
                    'Credential reference metadata only; no credential material stored.',
                    'batch7_test_metadata_reference')
            """,
            (reference_id, provider_id, source_type),
        )
    return reference_id


def set_review_status(review_item_id: int, review_status: str) -> None:
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            "UPDATE review_drafts SET review_status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (review_status, review_item_id),
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
        allowed_capabilities=frozenset({RealProviderCapability.PUBLISH.value}),
        environment_status=environment_status,
        platform_preconditions_status=platform_preconditions_status,
    )


def assert_publish_attempt_count(expected_count: int) -> None:
    with sqlite3.connect(get_settings().database_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM publish_attempts").fetchone()[0]
    assert count == expected_count


def assert_no_material_values(value: Any) -> None:
    text = json.dumps(value, default=str, sort_keys=True) if not isinstance(value, str) else value
    for material_value in FORBIDDEN_MATERIAL_VALUES:
        assert material_value not in text
