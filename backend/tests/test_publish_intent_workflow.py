import os
import socket
import sqlite3
from typing import Any

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.publishers.fake_publisher import FakePublisherProvider
from app.publishing.publish_intent import (
    PublishIntentWorkflowError,
    create_local_publish_intent,
)


SENSITIVE_MARKERS = (
    "access_token",
    "refresh_token",
    "authorization_code",
    "raw OAuth state",
    "OAuth state value",
    "cookie",
    "session",
    "API key",
    "bearer",
    "raw request",
    "raw response",
    "provider response",
    "upload response",
    "publish response",
)


def create_project(client: TestClient) -> int:
    response = client.post("/api/projects", json={"title": "Batch 6 publish intent", "description": "Local only"})
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
            "title": "Batch 6 local source",
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


def prepare_publish_intent_ready_project(
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


def publish_intent_payload(review_item_id: int, **overrides: Any) -> dict:
    payload = {
        "review_draft_id": review_item_id,
        "target_platform": "fake_local",
        "title": "Batch 6 user confirmed publish intent",
        "caption": "Local metadata only; no upload, publish, or schedule.",
        "confirm_publish_intent": True,
    }
    payload.update(overrides)
    return payload


def create_publish_intent(client: TestClient, project_id: int, review_item_id: int, **overrides: Any):
    return client.post(
        f"/api/projects/{project_id}/publish-intents",
        json=publish_intent_payload(review_item_id, **overrides),
    )


def assert_no_sensitive_markers(value: Any) -> None:
    rendered = repr(value).lower()
    for marker in SENSITIVE_MARKERS:
        assert marker.lower() not in rendered


def test_publish_intent_schema_is_metadata_only(client: TestClient):
    with sqlite3.connect(get_settings().database_path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(publish_intents)").fetchall()}

    forbidden_columns = {
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
    }
    assert "source_type" in columns
    assert "confirmation_status" in columns
    assert columns.isdisjoint(forbidden_columns)


def test_explicit_confirmation_required(client: TestClient):
    project_id, review_item = prepare_publish_intent_ready_project(client)

    response = create_publish_intent(client, project_id, review_item["id"], confirm_publish_intent=None)

    assert response.status_code == 409
    assert response.json()["detail"].startswith("confirmation_required:")
    assert_publish_intent_count(0)


def test_malformed_confirmation_rejected(client: TestClient):
    project_id, review_item = prepare_publish_intent_ready_project(client)

    response = create_publish_intent(client, project_id, review_item["id"], confirm_publish_intent="yes")

    assert response.status_code == 422
    assert_publish_intent_count(0)


def test_review_item_missing_rejected(client: TestClient):
    project_id = create_project(client)
    create_ready_media_artifact(client, project_id)

    response = create_publish_intent(client, project_id, 999)

    assert response.status_code == 404
    assert response.json()["detail"].startswith("review_not_ready:")
    assert_publish_intent_count(0)


def test_review_item_not_ready_rejected(client: TestClient):
    project_id, review_item = prepare_publish_intent_ready_project(client, approve=False)

    response = create_publish_intent(client, project_id, review_item["id"])

    assert response.status_code == 409
    assert response.json()["detail"].startswith("review_not_ready:")
    assert_publish_intent_count(0)


def test_media_artifact_missing_rejected(client: TestClient):
    project_id, review_item = prepare_publish_intent_ready_project(client, media_ready=False)

    response = create_publish_intent(client, project_id, review_item["id"])

    assert response.status_code == 409
    assert response.json()["detail"].startswith("media_not_ready:")
    assert_publish_intent_count(0)


def test_metadata_with_sensitive_marker_rejected(client: TestClient):
    project_id, review_item = prepare_publish_intent_ready_project(client)

    response = create_publish_intent(client, project_id, review_item["id"], caption="contains access_token marker")

    assert response.status_code == 422
    assert response.json()["detail"].startswith("metadata_invalid:")
    assert_publish_intent_count(0)


def test_valid_fake_local_publish_intent_created_without_publication_record(client: TestClient):
    project_id, review_item = prepare_publish_intent_ready_project(client)

    response = create_publish_intent(client, project_id, review_item["id"])

    assert response.status_code == 201
    body = response.json()
    assert body["target_platform"] == "fake_local"
    assert body["source_type"] == "fake_local"
    assert body["publish_status"] == "confirmed"
    assert body["confirmation_status"] == "confirmed"
    assert body["confirmed_at"]
    assert body["safe_status_message"].endswith("no provider publish was executed.")
    assert_no_sensitive_markers(body)
    records_response = client.get(f"/api/projects/{project_id}/publish-intents/{body['id']}/publication-records")
    assert records_response.json() == []


def test_valid_sandbox_safe_publish_intent_separates_source(client: TestClient):
    project_id, review_item = prepare_publish_intent_ready_project(client)

    response = create_publish_intent(client, project_id, review_item["id"], target_platform="douyin_sandbox")

    assert response.status_code == 201
    body = response.json()
    assert body["target_platform"] == "douyin_sandbox"
    assert body["source_type"] == "sandbox"
    assert_no_sensitive_markers(body)


def test_duplicate_active_publish_intent_rejected(client: TestClient):
    project_id, review_item = prepare_publish_intent_ready_project(client)
    first_response = create_publish_intent(client, project_id, review_item["id"])

    response = create_publish_intent(client, project_id, review_item["id"])

    assert first_response.status_code == 201
    assert response.status_code == 409
    assert response.json()["detail"].startswith("duplicate_publish_intent:")
    assert_publish_intent_count(1)


def test_real_provider_blocked_by_default(client: TestClient):
    project_id, review_item = prepare_publish_intent_ready_project(client)

    response = create_publish_intent(client, project_id, review_item["id"], target_platform="douyin_real")

    assert response.status_code == 409
    assert response.json()["detail"].startswith("real_provider_disabled:")
    assert_publish_intent_count(0)


def test_real_provider_does_not_fallback_to_sandbox(client: TestClient):
    project_id, review_item = prepare_publish_intent_ready_project(client)
    db = sqlite3.connect(get_settings().database_path)
    db.row_factory = sqlite3.Row
    try:
        create_local_publish_intent(
            db,
            project_id=project_id,
            review_draft_id=review_item["id"],
            provider_id="douyin_real",
            title="Fallback attempt",
            caption="Local metadata only.",
            confirm_publish_intent=True,
            fallback_provider_id="douyin_sandbox",
        )
    except PublishIntentWorkflowError as exc:
        assert exc.category == "sandbox_fallback_forbidden"
        assert_no_sensitive_markers(exc)
    else:
        raise AssertionError("real provider fallback attempt must be rejected")
    finally:
        db.close()
    assert_publish_intent_count(0)


def test_unsupported_provider_rejected(client: TestClient):
    project_id, review_item = prepare_publish_intent_ready_project(client)

    response = create_publish_intent(client, project_id, review_item["id"], target_platform="unknown_provider")

    assert response.status_code == 409
    assert response.json()["detail"].startswith("unsupported_provider:")
    assert_publish_intent_count(0)


def test_publish_intent_creation_does_not_call_provider_publish(client: TestClient, monkeypatch):
    project_id, review_item = prepare_publish_intent_ready_project(client)

    def fail_publish(*args, **kwargs):
        raise AssertionError("publish intent creation must not execute provider publish")

    monkeypatch.setattr(FakePublisherProvider, "execute", fail_publish)
    response = create_publish_intent(client, project_id, review_item["id"])

    assert response.status_code == 201


def test_publish_intent_creation_does_not_call_external_network(client: TestClient, monkeypatch):
    project_id, review_item = prepare_publish_intent_ready_project(client)
    calls: list[tuple[Any, ...]] = []

    def fail_create_connection(*args, **kwargs):
        calls.append(args)
        raise AssertionError("publish intent creation must not call external network")

    monkeypatch.setattr(socket, "create_connection", fail_create_connection)
    response = create_publish_intent(client, project_id, review_item["id"])

    assert response.status_code == 201
    assert calls == []


def test_publish_intent_service_does_not_read_or_leak_env_secret(client: TestClient, monkeypatch):
    project_id, review_item = prepare_publish_intent_ready_project(client)
    monkeypatch.setenv("CREATOR_FLOW_FAKE_CLIENT_SECRET", "obvious-fake-env-secret-for-negative-test")

    response = create_publish_intent(client, project_id, review_item["id"])

    assert response.status_code == 201
    assert "obvious-fake-env-secret-for-negative-test" not in repr(response.json())
    assert os.environ["CREATOR_FLOW_FAKE_CLIENT_SECRET"] == "obvious-fake-env-secret-for-negative-test"


def test_no_oauth_upload_or_real_publish_routes_added():
    route_paths = {getattr(route, "path", "") for route in app.routes}
    rendered = "\n".join(sorted(route_paths)).lower()

    assert "oauth/start" not in rendered
    assert "oauth/callback" not in rendered
    assert "oauth-url" not in rendered
    assert "authorization-url" not in rendered
    assert "upload" not in rendered
    assert "token-exchange" not in rendered
    assert "credential-storage" not in rendered
    assert "/api/projects/{project_id}/publish-intents" in route_paths


def assert_publish_intent_count(expected_count: int) -> None:
    with sqlite3.connect(get_settings().database_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM publish_intents").fetchone()[0]
    assert count == expected_count
