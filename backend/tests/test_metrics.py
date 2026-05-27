import sqlite3

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.metrics.fake_metrics import FakeMetricsProvider
from app.metrics.provider import MetricsSnapshotInput


def create_project(client: TestClient, title: str = "Metrics project") -> int:
    response = client.post("/api/projects", json={"title": title, "description": "Project description"})
    return response.json()["id"]


def create_content_plan(client: TestClient, project_id: int) -> dict:
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
    return response.json()


def prepare_review_draft(client: TestClient, project_id: int | None = None) -> tuple[int, dict]:
    if project_id is None:
        project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    client.post(f"/api/projects/{project_id}/content-plans/{content_plan['id']}/generation-runs", json={})
    review_draft = client.get(f"/api/projects/{project_id}/review-drafts").json()[0]
    review_draft = client.post(f"/api/projects/{project_id}/review-drafts/{review_draft['id']}/approve").json()
    return project_id, review_draft


def create_publish_intent(client: TestClient, project_id: int, review_draft_id: int) -> dict:
    response = client.post(
        f"/api/projects/{project_id}/publish-intents",
        json={
            "review_draft_id": review_draft_id,
            "target_platform": "douyin",
            "title": "Human confirmed publishing draft",
            "caption": "Backend-only publish intent metadata.",
        },
    )
    return response.json()


def prepare_publication_record(client: TestClient, project_id: int | None = None) -> tuple[int, dict, dict]:
    project_id, review_draft = prepare_review_draft(client, project_id)
    publish_intent = create_publish_intent(client, project_id, review_draft["id"])
    client.post(f"/api/projects/{project_id}/publish-intents/{publish_intent['id']}/confirm")
    client.post(f"/api/projects/{project_id}/publish-intents/{publish_intent['id']}/fake-publish")
    records = client.get(
        f"/api/projects/{project_id}/publish-intents/{publish_intent['id']}/publication-records"
    ).json()
    return project_id, publish_intent, records[0]


def create_fake_metrics_snapshot(client: TestClient, project_id: int, publication_record_id: int):
    return client.post(f"/api/projects/{project_id}/publication-records/{publication_record_id}/metrics/fake")


def test_create_fake_metrics_snapshot_for_publication_record(client: TestClient):
    project_id, _, publication_record = prepare_publication_record(client)

    response = create_fake_metrics_snapshot(client, project_id, publication_record["id"])

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project_id
    assert body["publication_record_id"] == publication_record["id"]
    assert body["source"] == "fake_local"
    assert body["views"] > 0
    assert body["likes"] >= 0
    assert body["comments"] >= 0
    assert body["shares"] >= 0
    assert body["favorites"] >= 0
    assert body["average_watch_time_seconds"] >= 0
    assert 0 <= body["completion_rate"] <= 1
    assert "fake/local metrics" in body["provider_payload_summary"]
    assert "not real platform performance" in body["provider_payload_summary"]
    assert body["captured_at"]
    assert body["created_at"]
    assert body["updated_at"]
    assert_no_metrics_side_effects(expected_metric_snapshots=1)


def test_list_and_read_metric_snapshots(client: TestClient):
    project_id, _, publication_record = prepare_publication_record(client)
    first = create_fake_metrics_snapshot(client, project_id, publication_record["id"]).json()
    second = create_fake_metrics_snapshot(client, project_id, publication_record["id"]).json()

    list_response = client.get(f"/api/projects/{project_id}/publication-records/{publication_record['id']}/metrics")
    read_response = client.get(
        f"/api/projects/{project_id}/publication-records/{publication_record['id']}/metrics/{first['id']}"
    )

    assert list_response.status_code == 200
    assert [snapshot["id"] for snapshot in list_response.json()] == [second["id"], first["id"]]
    assert read_response.status_code == 200
    assert read_response.json()["id"] == first["id"]
    assert read_response.json()["source"] == "fake_local"
    assert_no_metrics_side_effects(expected_metric_snapshots=2)


def test_create_metrics_for_missing_publication_record_returns_404(client: TestClient):
    project_id = create_project(client)

    response = create_fake_metrics_snapshot(client, project_id, 999)

    assert response.status_code == 404
    assert response.json()["detail"] == "publication record not found"
    assert_no_metrics_side_effects()


def test_metrics_for_missing_project_returns_404(client: TestClient):
    list_response = client.get("/api/projects/999/publication-records/1/metrics")
    create_response = create_fake_metrics_snapshot(client, 999, 1)
    read_response = client.get("/api/projects/999/publication-records/1/metrics/1")

    assert list_response.status_code == 404
    assert list_response.json()["detail"] == "project not found"
    assert create_response.status_code == 404
    assert create_response.json()["detail"] == "project not found"
    assert read_response.status_code == 404
    assert read_response.json()["detail"] == "project not found"
    assert_no_metrics_side_effects()


def test_cross_project_publication_record_metrics_access_returns_404(client: TestClient):
    first_project_id, _, publication_record = prepare_publication_record(client)
    second_project_id = create_project(client, "Second metrics project")

    list_response = client.get(
        f"/api/projects/{second_project_id}/publication-records/{publication_record['id']}/metrics"
    )
    create_response = create_fake_metrics_snapshot(client, second_project_id, publication_record["id"])

    assert first_project_id != second_project_id
    assert list_response.status_code == 404
    assert list_response.json()["detail"] == "publication record not found"
    assert create_response.status_code == 404
    assert create_response.json()["detail"] == "publication record not found"
    assert_no_metrics_side_effects()


def test_metric_snapshot_mismatched_publication_record_returns_404(client: TestClient):
    project_id = create_project(client)
    _, _, first_record = prepare_publication_record(client, project_id)
    _, _, second_record = prepare_publication_record(client, project_id)
    metric_snapshot = create_fake_metrics_snapshot(client, project_id, first_record["id"]).json()

    response = client.get(
        f"/api/projects/{project_id}/publication-records/{second_record['id']}/metrics/{metric_snapshot['id']}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "metric snapshot not found"
    assert_no_metrics_side_effects(expected_metric_snapshots=1)


def test_missing_metric_snapshot_returns_404(client: TestClient):
    project_id, _, publication_record = prepare_publication_record(client)

    response = client.get(f"/api/projects/{project_id}/publication-records/{publication_record['id']}/metrics/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "metric snapshot not found"
    assert_no_metrics_side_effects()


def test_archived_project_can_read_but_cannot_create_fake_metrics(client: TestClient):
    project_id, _, publication_record = prepare_publication_record(client)
    metric_snapshot = create_fake_metrics_snapshot(client, project_id, publication_record["id"]).json()
    client.post(f"/api/projects/{project_id}/archive")

    list_response = client.get(f"/api/projects/{project_id}/publication-records/{publication_record['id']}/metrics")
    read_response = client.get(
        f"/api/projects/{project_id}/publication-records/{publication_record['id']}/metrics/{metric_snapshot['id']}"
    )
    create_response = create_fake_metrics_snapshot(client, project_id, publication_record["id"])

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert read_response.status_code == 200
    assert read_response.json()["id"] == metric_snapshot["id"]
    assert create_response.status_code == 409
    assert create_response.json()["detail"] == "archived project cannot create fake metrics snapshots"
    assert_no_metrics_side_effects(expected_metric_snapshots=1)


def test_fake_metrics_provider_is_local_deterministic_and_needs_no_credentials():
    provider = FakeMetricsProvider()
    input_data = MetricsSnapshotInput(
        project_id=1,
        publish_intent_id=2,
        publication_record_id=3,
        target_platform="douyin",
        provider_name="fake_publisher",
        publication_status="succeeded",
    )

    first = provider.collect(input_data)
    second = provider.collect(input_data)

    assert provider.provider_name == "fake_metrics"
    assert first == second
    assert first.source == "fake_local"
    assert first.views > 0
    assert 0 <= first.completion_rate <= 1
    assert "fake/local metrics" in first.provider_payload_summary
    assert "not real platform performance" in first.provider_payload_summary


def test_metrics_workflow_does_not_call_real_platform_oauth_token_or_external_services(client: TestClient):
    project_id, _, publication_record = prepare_publication_record(client)

    response = create_fake_metrics_snapshot(client, project_id, publication_record["id"])

    assert response.status_code == 201
    body = response.json()
    assert body["source"] == "fake_local"
    assert "Douyin API" not in body["provider_payload_summary"]
    assert "OAuth" not in body["provider_payload_summary"]
    assert "token" not in body["provider_payload_summary"].lower()
    assert not get_settings().uploads_dir.exists() or list(get_settings().uploads_dir.rglob("*")) == []
    assert_no_metrics_side_effects(expected_metric_snapshots=1)


def assert_no_metrics_side_effects(expected_metric_snapshots: int = 0) -> None:
    with sqlite3.connect(get_settings().database_path) as connection:
        counts = {
            "publication_metric_snapshots": connection.execute(
                "SELECT COUNT(*) FROM publication_metric_snapshots"
            ).fetchone()[0],
            "render_jobs": connection.execute("SELECT COUNT(*) FROM render_jobs").fetchone()[0],
            "render_artifacts": connection.execute("SELECT COUNT(*) FROM render_artifacts").fetchone()[0],
            "subtitle_drafts": connection.execute("SELECT COUNT(*) FROM subtitle_drafts").fetchone()[0],
            "subtitle_cues": connection.execute("SELECT COUNT(*) FROM subtitle_cues").fetchone()[0],
        }
    assert counts == {
        "publication_metric_snapshots": expected_metric_snapshots,
        "render_jobs": 0,
        "render_artifacts": 0,
        "subtitle_drafts": 0,
        "subtitle_cues": 0,
    }
