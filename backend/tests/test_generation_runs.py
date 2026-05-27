import sqlite3

from fastapi.testclient import TestClient

from app.core.config import get_settings


def create_project(client: TestClient, title: str = "Run project") -> int:
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


def create_generation_schedule(
    client: TestClient,
    project_id: int,
    content_plan_id: int,
    payload: dict | None = None,
) -> dict:
    body = {
        "frequency_per_week": 4,
        "timezone": "Asia/Shanghai",
        "preferred_days": '["mon","wed","fri"]',
        "preferred_time": "09:30",
    }
    if payload:
        body.update(payload)
    response = client.post(
        f"/api/projects/{project_id}/content-plans/{content_plan_id}/generation-schedules",
        json=body,
    )
    return response.json()


def create_generation_run(
    client: TestClient,
    project_id: int,
    content_plan_id: int,
    payload: dict | None = None,
):
    return client.post(
        f"/api/projects/{project_id}/content-plans/{content_plan_id}/generation-runs",
        json=payload,
    )


def test_create_manual_generation_run_success_without_schedule(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)

    response = create_generation_run(client, project_id, content_plan["id"])

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project_id
    assert body["content_plan_id"] == content_plan["id"]
    assert body["generation_schedule_id"] is None
    assert body["status"] == "succeeded"
    assert body["trigger_type"] == "manual"
    assert "manual trigger" in body["input_summary"]
    assert f"content_plan_id={content_plan['id']}" in body["input_summary"]
    assert "frequency_per_week=3" in body["input_summary"]
    assert "deterministic fake manual generation run succeeded" in body["result_summary"]
    assert "no topic candidates" in body["result_summary"]
    assert body["error_message"] is None
    assert body["created_at"]
    assert body["updated_at"]


def test_create_manual_generation_run_success_with_schedule(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    schedule = create_generation_schedule(client, project_id, content_plan["id"], {"frequency_per_week": 5})

    response = create_generation_run(
        client,
        project_id,
        content_plan["id"],
        {"generation_schedule_id": schedule["id"]},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["generation_schedule_id"] == schedule["id"]
    assert "frequency_per_week=5" in body["input_summary"]
    assert f"generation_schedule_id={schedule['id']}" in body["input_summary"]
    assert f"using generation_schedule_id={schedule['id']}" in body["result_summary"]


def test_create_manual_generation_run_rejects_scheduled_trigger(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)

    response = create_generation_run(client, project_id, content_plan["id"], {"trigger_type": "scheduled"})

    assert response.status_code == 422


def test_create_generation_run_rejects_missing_project(client: TestClient):
    response = create_generation_run(client, 999, 1)

    assert response.status_code == 404
    assert response.json()["detail"] == "project not found"


def test_create_generation_run_rejects_missing_content_plan(client: TestClient):
    project_id = create_project(client)

    response = create_generation_run(client, project_id, 999)

    assert response.status_code == 404
    assert response.json()["detail"] == "content plan not found"


def test_create_generation_run_rejects_cross_project_content_plan(client: TestClient):
    first_project_id = create_project(client, "First project")
    second_project_id = create_project(client, "Second project")
    content_plan = create_content_plan(client, first_project_id)

    response = create_generation_run(client, second_project_id, content_plan["id"])

    assert response.status_code == 404
    assert response.json()["detail"] == "content plan not found"


def test_create_generation_run_rejects_missing_schedule(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)

    response = create_generation_run(client, project_id, content_plan["id"], {"generation_schedule_id": 999})

    assert response.status_code == 404
    assert response.json()["detail"] == "generation schedule not found"


def test_create_generation_run_rejects_cross_project_schedule(client: TestClient):
    first_project_id = create_project(client, "First project")
    second_project_id = create_project(client, "Second project")
    first_plan = create_content_plan(client, first_project_id)
    second_plan = create_content_plan(client, second_project_id)
    schedule = create_generation_schedule(client, first_project_id, first_plan["id"])

    response = create_generation_run(
        client,
        second_project_id,
        second_plan["id"],
        {"generation_schedule_id": schedule["id"]},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "generation schedule not found"


def test_create_generation_run_rejects_schedule_for_different_content_plan(client: TestClient):
    project_id = create_project(client)
    first_plan = create_content_plan(client, project_id, {"name": "First plan"})
    second_plan = create_content_plan(client, project_id, {"name": "Second plan"})
    schedule = create_generation_schedule(client, project_id, first_plan["id"])

    response = create_generation_run(
        client,
        project_id,
        second_plan["id"],
        {"generation_schedule_id": schedule["id"]},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "generation schedule not found"


def test_create_generation_run_rejects_archived_project(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    client.post(f"/api/projects/{project_id}/archive")

    response = create_generation_run(client, project_id, content_plan["id"])

    assert response.status_code == 409
    assert response.json()["detail"] == "archived project cannot create generation runs"


def test_list_generation_runs_for_project(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    first = create_generation_run(client, project_id, content_plan["id"]).json()
    second = create_generation_run(client, project_id, content_plan["id"]).json()

    response = client.get(f"/api/projects/{project_id}/generation-runs")

    assert response.status_code == 200
    body = response.json()
    assert [run["id"] for run in body] == [second["id"], first["id"]]
    assert all(run["project_id"] == project_id for run in body)


def test_list_generation_runs_for_missing_project_returns_404(client: TestClient):
    response = client.get("/api/projects/999/generation-runs")

    assert response.status_code == 404
    assert response.json()["detail"] == "project not found"


def test_read_single_generation_run_success(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    run = create_generation_run(client, project_id, content_plan["id"]).json()

    response = client.get(f"/api/projects/{project_id}/generation-runs/{run['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == run["id"]


def test_read_generation_run_from_another_project_returns_404(client: TestClient):
    first_project_id = create_project(client, "First project")
    second_project_id = create_project(client, "Second project")
    content_plan = create_content_plan(client, first_project_id)
    run = create_generation_run(client, first_project_id, content_plan["id"]).json()

    response = client.get(f"/api/projects/{second_project_id}/generation-runs/{run['id']}")

    assert response.status_code == 404
    assert response.json()["detail"] == "generation run not found"


def test_archived_project_can_list_and_read_existing_generation_runs(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    run = create_generation_run(client, project_id, content_plan["id"]).json()
    client.post(f"/api/projects/{project_id}/archive")

    list_response = client.get(f"/api/projects/{project_id}/generation-runs")
    read_response = client.get(f"/api/projects/{project_id}/generation-runs/{run['id']}")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert read_response.status_code == 200
    assert read_response.json()["id"] == run["id"]


def test_generation_run_does_not_create_real_drafts_or_media_records(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)

    response = create_generation_run(client, project_id, content_plan["id"])

    assert response.status_code == 201
    detail = client.get(f"/api/projects/{project_id}").json()
    assert detail["status"] == "draft"
    with sqlite3.connect(get_settings().database_path) as connection:
        counts = {
            "generation_runs": connection.execute("SELECT COUNT(*) FROM generation_runs").fetchone()[0],
            "topic_generation_runs": connection.execute("SELECT COUNT(*) FROM topic_generation_runs").fetchone()[0],
            "topic_candidates": connection.execute("SELECT COUNT(*) FROM topic_candidates").fetchone()[0],
            "script_generation_runs": connection.execute("SELECT COUNT(*) FROM script_generation_runs").fetchone()[0],
            "script_drafts": connection.execute("SELECT COUNT(*) FROM script_drafts").fetchone()[0],
            "storyboard_generation_runs": connection.execute("SELECT COUNT(*) FROM storyboard_generation_runs").fetchone()[0],
            "storyboard_drafts": connection.execute("SELECT COUNT(*) FROM storyboard_drafts").fetchone()[0],
            "render_jobs": connection.execute("SELECT COUNT(*) FROM render_jobs").fetchone()[0],
            "subtitle_drafts": connection.execute("SELECT COUNT(*) FROM subtitle_drafts").fetchone()[0],
        }
    assert counts == {
        "generation_runs": 1,
        "topic_generation_runs": 0,
        "topic_candidates": 0,
        "script_generation_runs": 0,
        "script_drafts": 0,
        "storyboard_generation_runs": 0,
        "storyboard_drafts": 0,
        "render_jobs": 0,
        "subtitle_drafts": 0,
    }
