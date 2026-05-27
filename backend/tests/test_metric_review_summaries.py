import sqlite3

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.metrics.fake_review_summary import FakeMetricsReviewSummaryGenerator, MetricsReviewSnapshot


def create_project(client: TestClient, title: str = "Metric review project") -> int:
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


def create_fake_metrics_snapshot(client: TestClient, project_id: int, publication_record_id: int) -> dict:
    response = client.post(f"/api/projects/{project_id}/publication-records/{publication_record_id}/metrics/fake")
    assert response.status_code == 201
    return response.json()


def create_fake_metric_review_summary(client: TestClient, project_id: int, publication_record_id: int):
    return client.post(
        f"/api/projects/{project_id}/publication-records/{publication_record_id}/metric-review-summaries/fake"
    )


def test_create_fake_metric_review_summary_from_snapshots(client: TestClient):
    project_id, _, publication_record = prepare_publication_record(client)
    first_snapshot = create_fake_metrics_snapshot(client, project_id, publication_record["id"])
    second_snapshot = create_fake_metrics_snapshot(client, project_id, publication_record["id"])

    response = create_fake_metric_review_summary(client, project_id, publication_record["id"])

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project_id
    assert body["publication_record_id"] == publication_record["id"]
    assert body["source"] == "fake_local"
    assert body["is_fake_local"] is True
    assert body["snapshot_count"] == 2
    assert body["metric_window_start"] == first_snapshot["captured_at"]
    assert body["metric_window_end"] == second_snapshot["captured_at"]
    assert "Fake/local review summary" in body["summary_text"]
    assert "not real platform analysis" in body["summary_text"]
    assert "Latest fake/local snapshot" in body["highlights"]
    assert "Do not auto-modify topics, scripts, or content plans" in body["next_observations"]
    assert_no_metric_review_side_effects(expected_metric_snapshots=2, expected_summaries=1)


def test_create_fake_metric_review_summary_uses_stable_snapshot_window(client: TestClient):
    project_id, _, publication_record = prepare_publication_record(client)
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.executemany(
            """
            INSERT INTO publication_metric_snapshots (
                project_id, publication_record_id, source, captured_at, views, likes,
                comments, shares, favorites, average_watch_time_seconds, completion_rate,
                provider_payload_summary
            )
            VALUES (?, ?, 'fake_local', ?, ?, ?, ?, ?, ?, ?, ?, 'stable fake/local metrics')
            """,
            [
                (project_id, publication_record["id"], "2026-05-27 09:00:00", 100, 8, 1, 1, 2, 9.0, 0.4),
                (project_id, publication_record["id"], "2026-05-27 11:00:00", 230, 30, 6, 4, 9, 16.5, 0.7),
                (project_id, publication_record["id"], "2026-05-27 10:00:00", 180, 18, 4, 2, 5, 13.0, 0.55),
            ],
        )

    response = create_fake_metric_review_summary(client, project_id, publication_record["id"])

    assert response.status_code == 201
    body = response.json()
    assert body["source"] == "fake_local"
    assert body["is_fake_local"] is True
    assert body["snapshot_count"] == 3
    assert body["metric_window_start"] == "2026-05-27 09:00:00"
    assert body["metric_window_end"] == "2026-05-27 11:00:00"
    assert "views +130" in body["highlights"]
    assert "completion_rate +30pp" in body["highlights"]
    assert_no_metric_review_side_effects(expected_metric_snapshots=3, expected_summaries=1)


def test_create_fake_metric_review_summary_allows_missing_metric_fields(client: TestClient):
    project_id, _, publication_record = prepare_publication_record(client)
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            """
            INSERT INTO publication_metric_snapshots (
                project_id, publication_record_id, source, views, likes, comments,
                shares, favorites, average_watch_time_seconds, completion_rate,
                provider_payload_summary
            )
            VALUES (?, ?, 'fake_local', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'partial fake/local metrics')
            """,
            (project_id, publication_record["id"]),
        )

    response = create_fake_metric_review_summary(client, project_id, publication_record["id"])

    assert response.status_code == 201
    body = response.json()
    assert body["snapshot_count"] == 1
    assert "missing views" in body["summary_text"]
    assert "no comparable metric values" in body["highlights"]
    assert_no_metric_review_side_effects(expected_metric_snapshots=1, expected_summaries=1)


def test_create_fake_metric_review_summary_with_no_snapshots_creates_no_metrics_summary(client: TestClient):
    project_id, _, publication_record = prepare_publication_record(client)

    response = create_fake_metric_review_summary(client, project_id, publication_record["id"])

    assert response.status_code == 201
    body = response.json()
    assert body["source"] == "fake_local"
    assert body["is_fake_local"] is True
    assert body["snapshot_count"] == 0
    assert body["metric_window_start"] is None
    assert body["metric_window_end"] is None
    assert "No fake/local metric snapshots are available yet" in body["summary_text"]
    assert "not real platform analysis" in body["summary_text"]
    assert_no_metric_review_side_effects(expected_summaries=1)


def test_list_and_read_metric_review_summaries(client: TestClient):
    project_id, _, publication_record = prepare_publication_record(client)
    create_fake_metrics_snapshot(client, project_id, publication_record["id"])
    first = create_fake_metric_review_summary(client, project_id, publication_record["id"]).json()
    second = create_fake_metric_review_summary(client, project_id, publication_record["id"]).json()

    list_response = client.get(
        f"/api/projects/{project_id}/publication-records/{publication_record['id']}/metric-review-summaries"
    )
    read_response = client.get(
        f"/api/projects/{project_id}/publication-records/{publication_record['id']}"
        f"/metric-review-summaries/{first['id']}"
    )

    assert list_response.status_code == 200
    assert [summary["id"] for summary in list_response.json()] == [second["id"], first["id"]]
    assert read_response.status_code == 200
    assert read_response.json()["id"] == first["id"]
    assert read_response.json()["source"] == "fake_local"
    assert_no_metric_review_side_effects(expected_metric_snapshots=1, expected_summaries=2)


def test_metric_review_summary_missing_project_returns_404(client: TestClient):
    list_response = client.get("/api/projects/999/publication-records/1/metric-review-summaries")
    create_response = create_fake_metric_review_summary(client, 999, 1)
    read_response = client.get("/api/projects/999/publication-records/1/metric-review-summaries/1")

    assert list_response.status_code == 404
    assert list_response.json()["detail"] == "project not found"
    assert create_response.status_code == 404
    assert create_response.json()["detail"] == "project not found"
    assert read_response.status_code == 404
    assert read_response.json()["detail"] == "project not found"
    assert_no_metric_review_side_effects()


def test_metric_review_summary_missing_publication_record_returns_404(client: TestClient):
    project_id = create_project(client)

    list_response = client.get(f"/api/projects/{project_id}/publication-records/999/metric-review-summaries")
    create_response = create_fake_metric_review_summary(client, project_id, 999)
    read_response = client.get(f"/api/projects/{project_id}/publication-records/999/metric-review-summaries/1")

    assert list_response.status_code == 404
    assert list_response.json()["detail"] == "publication record not found"
    assert create_response.status_code == 404
    assert create_response.json()["detail"] == "publication record not found"
    assert read_response.status_code == 404
    assert read_response.json()["detail"] == "publication record not found"
    assert_no_metric_review_side_effects()


def test_cross_project_publication_record_metric_review_summary_access_returns_404(client: TestClient):
    first_project_id, _, publication_record = prepare_publication_record(client)
    second_project_id = create_project(client, "Second metric review project")

    list_response = client.get(
        f"/api/projects/{second_project_id}/publication-records/{publication_record['id']}"
        "/metric-review-summaries"
    )
    create_response = create_fake_metric_review_summary(client, second_project_id, publication_record["id"])

    assert first_project_id != second_project_id
    assert list_response.status_code == 404
    assert list_response.json()["detail"] == "publication record not found"
    assert create_response.status_code == 404
    assert create_response.json()["detail"] == "publication record not found"
    assert_no_metric_review_side_effects()


def test_cross_project_metric_review_summary_access_returns_404(client: TestClient):
    first_project_id, _, publication_record = prepare_publication_record(client)
    create_fake_metrics_snapshot(client, first_project_id, publication_record["id"])
    summary = create_fake_metric_review_summary(client, first_project_id, publication_record["id"]).json()
    _, _, second_record = prepare_publication_record(client)

    response = client.get(
        f"/api/projects/{second_record['project_id']}/publication-records/{second_record['id']}"
        f"/metric-review-summaries/{summary['id']}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "metric review summary not found"
    assert_no_metric_review_side_effects(expected_metric_snapshots=1, expected_summaries=1)


def test_archived_project_can_read_but_cannot_create_fake_metric_review_summary(client: TestClient):
    project_id, _, publication_record = prepare_publication_record(client)
    create_fake_metrics_snapshot(client, project_id, publication_record["id"])
    summary = create_fake_metric_review_summary(client, project_id, publication_record["id"]).json()
    client.post(f"/api/projects/{project_id}/archive")

    list_response = client.get(
        f"/api/projects/{project_id}/publication-records/{publication_record['id']}/metric-review-summaries"
    )
    read_response = client.get(
        f"/api/projects/{project_id}/publication-records/{publication_record['id']}"
        f"/metric-review-summaries/{summary['id']}"
    )
    create_response = create_fake_metric_review_summary(client, project_id, publication_record["id"])

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert read_response.status_code == 200
    assert read_response.json()["id"] == summary["id"]
    assert create_response.status_code == 409
    assert create_response.json()["detail"] == "archived project cannot create fake metric review summaries"
    assert_no_metric_review_side_effects(expected_metric_snapshots=1, expected_summaries=1)


def test_fake_metrics_review_summary_generator_is_deterministic_and_local():
    generator = FakeMetricsReviewSummaryGenerator()
    snapshots = [
        MetricsReviewSnapshot(captured_at="2026-05-27 10:00:00", views=120, likes=9, completion_rate=0.45),
        MetricsReviewSnapshot(
            captured_at="2026-05-27 11:00:00",
            views=180,
            likes=21,
            comments=5,
            shares=4,
            favorites=10,
            average_watch_time_seconds=12.5,
            completion_rate=0.62,
        ),
    ]

    first = generator.generate(snapshots)
    second = generator.generate(list(reversed(snapshots)))

    assert generator.generator_name == "fake_metrics_review_summary"
    assert first == second
    assert first.source == "fake_local"
    assert first.is_fake_local is True
    assert first.snapshot_count == 2
    assert "not real platform analysis" in first.summary_text
    assert "Do not auto-modify topics, scripts, or content plans" in first.next_observations


def test_metric_review_summary_workflow_does_not_call_real_platform_or_modify_content(client: TestClient):
    project_id, publish_intent, publication_record = prepare_publication_record(client)
    create_fake_metrics_snapshot(client, project_id, publication_record["id"])

    response = create_fake_metric_review_summary(client, project_id, publication_record["id"])
    review_drafts_response = client.get(f"/api/projects/{project_id}/review-drafts")
    publish_intent_response = client.get(f"/api/projects/{project_id}/publish-intents/{publish_intent['id']}")

    assert response.status_code == 201
    body = response.json()
    assert body["source"] == "fake_local"
    assert body["is_fake_local"] is True
    assert "Douyin API" not in body["summary_text"]
    assert "OAuth" not in body["summary_text"]
    assert "token" not in body["summary_text"].lower()
    assert "upload" not in body["summary_text"].lower()
    assert "publish" not in body["summary_text"].lower()
    assert "schedule" not in body["summary_text"].lower()
    assert review_drafts_response.json()[0]["review_status"] == "approved"
    assert publish_intent_response.json()["publish_status"] == "confirmed"
    assert not get_settings().uploads_dir.exists() or list(get_settings().uploads_dir.rglob("*")) == []
    assert_no_metric_review_side_effects(expected_metric_snapshots=1, expected_summaries=1)


def assert_no_metric_review_side_effects(expected_metric_snapshots: int = 0, expected_summaries: int = 0) -> None:
    with sqlite3.connect(get_settings().database_path) as connection:
        counts = {
            "publication_metric_snapshots": connection.execute(
                "SELECT COUNT(*) FROM publication_metric_snapshots"
            ).fetchone()[0],
            "publication_metric_review_summaries": connection.execute(
                "SELECT COUNT(*) FROM publication_metric_review_summaries"
            ).fetchone()[0],
            "render_jobs": connection.execute("SELECT COUNT(*) FROM render_jobs").fetchone()[0],
            "render_artifacts": connection.execute("SELECT COUNT(*) FROM render_artifacts").fetchone()[0],
            "subtitle_drafts": connection.execute("SELECT COUNT(*) FROM subtitle_drafts").fetchone()[0],
            "subtitle_cues": connection.execute("SELECT COUNT(*) FROM subtitle_cues").fetchone()[0],
            "topic_candidates": connection.execute("SELECT COUNT(*) FROM topic_candidates").fetchone()[0],
            "script_drafts": connection.execute("SELECT COUNT(*) FROM script_drafts").fetchone()[0],
            "content_plans": connection.execute("SELECT COUNT(*) FROM content_plans").fetchone()[0],
        }
    assert counts["publication_metric_snapshots"] == expected_metric_snapshots
    assert counts["publication_metric_review_summaries"] == expected_summaries
    assert counts["render_jobs"] == 0
    assert counts["render_artifacts"] == 0
    assert counts["subtitle_drafts"] == 0
    assert counts["subtitle_cues"] == 0
    assert counts["topic_candidates"] == 0
    assert counts["script_drafts"] == 0
