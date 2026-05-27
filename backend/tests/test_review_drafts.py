import sqlite3

from fastapi.testclient import TestClient

from app.core.config import get_settings


def create_project(client: TestClient, title: str = "Review draft project") -> int:
    response = client.post("/api/projects", json={"title": title, "description": "Project description"})
    return response.json()["id"]


def create_content_plan(client: TestClient, project_id: int, payload: dict | None = None) -> dict:
    body = {
        "name": "Weekly AI dev log",
        "account_positioning": "Chinese developer sharing practical AI workflow notes",
        "content_type": "programmer_real_problem",
        "target_frequency_per_week": 3,
        "preferences": '{"tone":"practical","length":"short"}',
    }
    if payload:
        body.update(payload)
    response = client.post(f"/api/projects/{project_id}/content-plans", json=body)
    return response.json()


def create_generation_schedule(client: TestClient, project_id: int, content_plan_id: int) -> dict:
    response = client.post(
        f"/api/projects/{project_id}/content-plans/{content_plan_id}/generation-schedules",
        json={
            "frequency_per_week": 4,
            "timezone": "Asia/Shanghai",
            "preferred_days": '["mon","wed","fri"]',
            "preferred_time": "09:30",
        },
    )
    return response.json()


def create_generation_run(client: TestClient, project_id: int, content_plan_id: int, payload: dict | None = None) -> dict:
    response = client.post(
        f"/api/projects/{project_id}/content-plans/{content_plan_id}/generation-runs",
        json=payload,
    )
    return response.json()


def prepare_review_draft(client: TestClient, with_schedule: bool = False):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    payload = None
    schedule = None
    if with_schedule:
        schedule = create_generation_schedule(client, project_id, content_plan["id"])
        payload = {"generation_schedule_id": schedule["id"]}
    generation_run = create_generation_run(client, project_id, content_plan["id"], payload)
    review_draft = client.get(f"/api/projects/{project_id}/review-drafts").json()[0]
    return project_id, content_plan, schedule, generation_run, review_draft


def test_generation_run_creates_pending_review_draft_placeholder(client: TestClient):
    project_id, content_plan, _, generation_run, review_draft = prepare_review_draft(client)

    assert review_draft["project_id"] == project_id
    assert review_draft["content_plan_id"] == content_plan["id"]
    assert review_draft["generation_schedule_id"] is None
    assert review_draft["generation_run_id"] == generation_run["id"]
    assert review_draft["review_status"] == "pending_review"
    assert review_draft["title"] == f"Fake review draft for {content_plan['name']} run {generation_run['id']}"
    assert "Backend-only fake draft placeholder" in review_draft["draft_summary"]
    assert generation_run["input_summary"] == review_draft["input_source_summary"]
    assert review_draft["hotspot_source_summary"] is None
    assert review_draft["created_at"]
    assert review_draft["updated_at"]


def test_generation_run_with_schedule_carries_schedule_into_review_draft(client: TestClient):
    _, _, schedule, generation_run, review_draft = prepare_review_draft(client, with_schedule=True)

    assert review_draft["generation_schedule_id"] == schedule["id"]
    assert f"GenerationSchedule {schedule['id']}" in review_draft["draft_summary"]
    assert f"generation_schedule_id={schedule['id']}" in generation_run["input_summary"]


def test_list_review_drafts_for_project(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    first_run = create_generation_run(client, project_id, content_plan["id"])
    second_run = create_generation_run(client, project_id, content_plan["id"])

    response = client.get(f"/api/projects/{project_id}/review-drafts")

    assert response.status_code == 200
    body = response.json()
    assert [draft["generation_run_id"] for draft in body] == [second_run["id"], first_run["id"]]
    assert all(draft["review_status"] == "pending_review" for draft in body)


def test_list_review_drafts_for_missing_project_returns_404(client: TestClient):
    response = client.get("/api/projects/999/review-drafts")

    assert response.status_code == 404
    assert response.json()["detail"] == "project not found"


def test_read_review_draft_success(client: TestClient):
    project_id, _, _, _, review_draft = prepare_review_draft(client)

    response = client.get(f"/api/projects/{project_id}/review-drafts/{review_draft['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == review_draft["id"]


def test_cross_project_review_draft_access_returns_404(client: TestClient):
    first_project_id, _, _, _, review_draft = prepare_review_draft(client)
    second_project_id = create_project(client, "Second project")

    response = client.get(f"/api/projects/{second_project_id}/review-drafts/{review_draft['id']}")

    assert first_project_id != second_project_id
    assert response.status_code == 404
    assert response.json()["detail"] == "review draft not found"


def test_missing_review_draft_returns_404(client: TestClient):
    project_id = create_project(client)

    response = client.get(f"/api/projects/{project_id}/review-drafts/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "review draft not found"


def test_approve_review_draft_changes_status_only(client: TestClient):
    project_id, _, _, _, review_draft = prepare_review_draft(client)

    response = client.post(f"/api/projects/{project_id}/review-drafts/{review_draft['id']}/approve")

    assert response.status_code == 200
    assert response.json()["review_status"] == "approved"
    assert_no_real_output_records()


def test_reject_review_draft_changes_status_only(client: TestClient):
    project_id, _, _, _, review_draft = prepare_review_draft(client)

    response = client.post(f"/api/projects/{project_id}/review-drafts/{review_draft['id']}/reject")

    assert response.status_code == 200
    assert response.json()["review_status"] == "rejected"
    assert_no_real_output_records()


def test_approve_reject_missing_review_draft_returns_404(client: TestClient):
    project_id = create_project(client)

    approve_response = client.post(f"/api/projects/{project_id}/review-drafts/999/approve")
    reject_response = client.post(f"/api/projects/{project_id}/review-drafts/999/reject")

    assert approve_response.status_code == 404
    assert reject_response.status_code == 404


def test_archived_project_can_read_but_cannot_approve_or_reject_review_draft(client: TestClient):
    project_id, _, _, _, review_draft = prepare_review_draft(client)
    client.post(f"/api/projects/{project_id}/archive")

    list_response = client.get(f"/api/projects/{project_id}/review-drafts")
    read_response = client.get(f"/api/projects/{project_id}/review-drafts/{review_draft['id']}")
    approve_response = client.post(f"/api/projects/{project_id}/review-drafts/{review_draft['id']}/approve")
    reject_response = client.post(f"/api/projects/{project_id}/review-drafts/{review_draft['id']}/reject")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert read_response.status_code == 200
    assert approve_response.status_code == 409
    assert approve_response.json()["detail"] == "archived project cannot approve review drafts"
    assert reject_response.status_code == 409
    assert reject_response.json()["detail"] == "archived project cannot reject review drafts"


def test_approve_reject_cross_project_review_draft_returns_404(client: TestClient):
    _, _, _, _, review_draft = prepare_review_draft(client)
    second_project_id = create_project(client, "Second project")

    approve_response = client.post(f"/api/projects/{second_project_id}/review-drafts/{review_draft['id']}/approve")
    reject_response = client.post(f"/api/projects/{second_project_id}/review-drafts/{review_draft['id']}/reject")

    assert approve_response.status_code == 404
    assert reject_response.status_code == 404


def test_approve_reject_do_not_create_render_subtitle_upload_media_or_publication_records(client: TestClient):
    project_id, _, _, _, review_draft = prepare_review_draft(client)

    approve_response = client.post(f"/api/projects/{project_id}/review-drafts/{review_draft['id']}/approve")
    reject_response = client.post(f"/api/projects/{project_id}/review-drafts/{review_draft['id']}/reject")

    assert approve_response.status_code == 200
    assert reject_response.status_code == 200
    assert_no_real_output_records()
    assert not get_settings().uploads_dir.exists() or list(get_settings().uploads_dir.rglob("*")) == []


def assert_no_real_output_records() -> None:
    with sqlite3.connect(get_settings().database_path) as connection:
        counts = {
            "topic_generation_runs": connection.execute("SELECT COUNT(*) FROM topic_generation_runs").fetchone()[0],
            "topic_candidates": connection.execute("SELECT COUNT(*) FROM topic_candidates").fetchone()[0],
            "script_generation_runs": connection.execute("SELECT COUNT(*) FROM script_generation_runs").fetchone()[0],
            "script_drafts": connection.execute("SELECT COUNT(*) FROM script_drafts").fetchone()[0],
            "storyboard_generation_runs": connection.execute("SELECT COUNT(*) FROM storyboard_generation_runs").fetchone()[0],
            "storyboard_drafts": connection.execute("SELECT COUNT(*) FROM storyboard_drafts").fetchone()[0],
            "render_jobs": connection.execute("SELECT COUNT(*) FROM render_jobs").fetchone()[0],
            "render_artifacts": connection.execute("SELECT COUNT(*) FROM render_artifacts").fetchone()[0],
            "subtitle_drafts": connection.execute("SELECT COUNT(*) FROM subtitle_drafts").fetchone()[0],
            "subtitle_cues": connection.execute("SELECT COUNT(*) FROM subtitle_cues").fetchone()[0],
        }
        publication_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name IN ('publish_intents', 'publications')"
        ).fetchall()
    assert counts == {
        "topic_generation_runs": 0,
        "topic_candidates": 0,
        "script_generation_runs": 0,
        "script_drafts": 0,
        "storyboard_generation_runs": 0,
        "storyboard_drafts": 0,
        "render_jobs": 0,
        "render_artifacts": 0,
        "subtitle_drafts": 0,
        "subtitle_cues": 0,
    }
    assert publication_table == []
