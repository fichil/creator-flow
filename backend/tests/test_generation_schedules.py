import sqlite3

from fastapi.testclient import TestClient

from app.core.config import get_settings


def create_project(client: TestClient, title: str = "Schedule project") -> int:
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
):
    body = {
        "frequency_per_week": 4,
        "timezone": "Asia/Shanghai",
        "preferred_days": '["mon","wed","fri"]',
        "preferred_time": "09:30",
    }
    if payload:
        body.update(payload)
    return client.post(
        f"/api/projects/{project_id}/content-plans/{content_plan_id}/generation-schedules",
        json=body,
    )


def test_create_generation_schedule_success(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)

    response = create_generation_schedule(client, project_id, content_plan["id"])

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project_id
    assert body["content_plan_id"] == content_plan["id"]
    assert body["frequency_per_week"] == 4
    assert body["timezone"] == "Asia/Shanghai"
    assert body["preferred_days"] == '["mon","wed","fri"]'
    assert body["preferred_time"] == "09:30"
    assert body["is_enabled"] is True
    assert body["created_at"]
    assert body["updated_at"]


def test_create_generation_schedule_can_inherit_content_plan_frequency(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id, {"target_frequency_per_week": 6})

    response = create_generation_schedule(client, project_id, content_plan["id"], {"frequency_per_week": None})

    assert response.status_code == 201
    assert response.json()["frequency_per_week"] == 6


def test_create_generation_schedule_trims_timezone_and_optional_days(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)

    response = create_generation_schedule(
        client,
        project_id,
        content_plan["id"],
        {"timezone": "  Asia/Shanghai  ", "preferred_days": "   ", "is_enabled": False},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["timezone"] == "Asia/Shanghai"
    assert body["preferred_days"] is None
    assert body["is_enabled"] is False


def test_create_generation_schedule_rejects_missing_project(client: TestClient):
    response = create_generation_schedule(client, 999, 1)

    assert response.status_code == 404
    assert response.json()["detail"] == "project not found"


def test_create_generation_schedule_rejects_missing_content_plan(client: TestClient):
    project_id = create_project(client)

    response = create_generation_schedule(client, project_id, 999)

    assert response.status_code == 404
    assert response.json()["detail"] == "content plan not found"


def test_create_generation_schedule_rejects_cross_project_content_plan(client: TestClient):
    first_project_id = create_project(client, "First project")
    second_project_id = create_project(client, "Second project")
    content_plan = create_content_plan(client, first_project_id)

    response = create_generation_schedule(client, second_project_id, content_plan["id"])

    assert response.status_code == 404
    assert response.json()["detail"] == "content plan not found"


def test_create_generation_schedule_rejects_archived_project(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    client.post(f"/api/projects/{project_id}/archive")

    response = create_generation_schedule(client, project_id, content_plan["id"])

    assert response.status_code == 409
    assert response.json()["detail"] == "archived project cannot create generation schedules"


def test_create_generation_schedule_rejects_invalid_frequency_and_time(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)

    too_low = create_generation_schedule(client, project_id, content_plan["id"], {"frequency_per_week": 0})
    too_high = create_generation_schedule(client, project_id, content_plan["id"], {"frequency_per_week": 15})
    bad_time = create_generation_schedule(client, project_id, content_plan["id"], {"preferred_time": "24:00"})

    assert too_low.status_code == 422
    assert too_high.status_code == 422
    assert bad_time.status_code == 422


def test_create_generation_schedule_rejects_blank_timezone(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)

    response = create_generation_schedule(client, project_id, content_plan["id"], {"timezone": "   "})

    assert response.status_code == 422
    assert response.json()["detail"] == "timezone is required"


def test_list_generation_schedules_for_project(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    first = create_generation_schedule(client, project_id, content_plan["id"], {"preferred_time": "08:00"}).json()
    second = create_generation_schedule(client, project_id, content_plan["id"], {"preferred_time": "18:30"}).json()

    response = client.get(f"/api/projects/{project_id}/generation-schedules")

    assert response.status_code == 200
    body = response.json()
    assert [schedule["id"] for schedule in body] == [second["id"], first["id"]]
    assert all(schedule["project_id"] == project_id for schedule in body)


def test_list_generation_schedules_for_missing_project_returns_404(client: TestClient):
    response = client.get("/api/projects/999/generation-schedules")

    assert response.status_code == 404
    assert response.json()["detail"] == "project not found"


def test_read_single_generation_schedule_success(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    schedule = create_generation_schedule(client, project_id, content_plan["id"]).json()

    response = client.get(f"/api/projects/{project_id}/generation-schedules/{schedule['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == schedule["id"]


def test_read_generation_schedule_from_another_project_returns_404(client: TestClient):
    first_project_id = create_project(client, "First project")
    second_project_id = create_project(client, "Second project")
    content_plan = create_content_plan(client, first_project_id)
    schedule = create_generation_schedule(client, first_project_id, content_plan["id"]).json()

    response = client.get(f"/api/projects/{second_project_id}/generation-schedules/{schedule['id']}")

    assert response.status_code == 404
    assert response.json()["detail"] == "generation schedule not found"


def test_archived_project_can_list_and_read_existing_generation_schedules(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    schedule = create_generation_schedule(client, project_id, content_plan["id"]).json()
    client.post(f"/api/projects/{project_id}/archive")

    list_response = client.get(f"/api/projects/{project_id}/generation-schedules")
    read_response = client.get(f"/api/projects/{project_id}/generation-schedules/{schedule['id']}")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert read_response.status_code == 200
    assert read_response.json()["id"] == schedule["id"]


def test_update_generation_schedule_success(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    schedule = create_generation_schedule(client, project_id, content_plan["id"]).json()

    response = client.patch(
        f"/api/projects/{project_id}/generation-schedules/{schedule['id']}",
        json={
            "frequency_per_week": 5,
            "timezone": "Asia/Tokyo",
            "preferred_days": '["tue","thu"]',
            "preferred_time": "10:45",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["frequency_per_week"] == 5
    assert body["timezone"] == "Asia/Tokyo"
    assert body["preferred_days"] == '["tue","thu"]'
    assert body["preferred_time"] == "10:45"


def test_update_generation_schedule_rejects_invalid_frequency_and_time(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    schedule = create_generation_schedule(client, project_id, content_plan["id"]).json()

    invalid_frequency = client.patch(
        f"/api/projects/{project_id}/generation-schedules/{schedule['id']}",
        json={"frequency_per_week": 99},
    )
    invalid_time = client.patch(
        f"/api/projects/{project_id}/generation-schedules/{schedule['id']}",
        json={"preferred_time": "7:00"},
    )

    assert invalid_frequency.status_code == 422
    assert invalid_time.status_code == 422


def test_update_generation_schedule_rejects_archived_project(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    schedule = create_generation_schedule(client, project_id, content_plan["id"]).json()
    client.post(f"/api/projects/{project_id}/archive")

    response = client.patch(
        f"/api/projects/{project_id}/generation-schedules/{schedule['id']}",
        json={"frequency_per_week": 5},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "archived project cannot update generation schedules"


def test_update_missing_generation_schedule_returns_404(client: TestClient):
    project_id = create_project(client)

    response = client.patch(f"/api/projects/{project_id}/generation-schedules/999", json={"frequency_per_week": 5})

    assert response.status_code == 404
    assert response.json()["detail"] == "generation schedule not found"


def test_enable_disable_generation_schedule(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    schedule = create_generation_schedule(client, project_id, content_plan["id"]).json()

    disabled = client.post(f"/api/projects/{project_id}/generation-schedules/{schedule['id']}/disable")
    enabled = client.post(f"/api/projects/{project_id}/generation-schedules/{schedule['id']}/enable")

    assert disabled.status_code == 200
    assert disabled.json()["is_enabled"] is False
    assert enabled.status_code == 200
    assert enabled.json()["is_enabled"] is True


def test_enable_disable_missing_generation_schedule_returns_404(client: TestClient):
    project_id = create_project(client)

    disable_response = client.post(f"/api/projects/{project_id}/generation-schedules/999/disable")
    enable_response = client.post(f"/api/projects/{project_id}/generation-schedules/999/enable")

    assert disable_response.status_code == 404
    assert enable_response.status_code == 404


def test_archived_project_cannot_enable_or_disable_generation_schedule(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    schedule = create_generation_schedule(client, project_id, content_plan["id"]).json()
    client.post(f"/api/projects/{project_id}/archive")

    disable_response = client.post(f"/api/projects/{project_id}/generation-schedules/{schedule['id']}/disable")
    enable_response = client.post(f"/api/projects/{project_id}/generation-schedules/{schedule['id']}/enable")

    assert disable_response.status_code == 409
    assert enable_response.status_code == 409


def test_generation_schedule_does_not_create_generation_run_or_change_project_status(client: TestClient):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)

    response = create_generation_schedule(client, project_id, content_plan["id"])

    assert response.status_code == 201
    detail = client.get(f"/api/projects/{project_id}").json()
    assert detail["status"] == "draft"
    with sqlite3.connect(get_settings().database_path) as connection:
        generation_run_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'generation_runs'"
        ).fetchone()
    assert generation_run_table is None
