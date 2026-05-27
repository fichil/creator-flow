from fastapi.testclient import TestClient


def create_project(client: TestClient, title: str = "Plan project") -> int:
    response = client.post("/api/projects", json={"title": title, "description": "Project description"})
    return response.json()["id"]


def create_content_plan(client: TestClient, project_id: int, payload: dict | None = None):
    body = {
        "name": "Weekly AI dev log",
        "account_positioning": "Chinese developer sharing practical AI workflow notes",
        "content_type": "programmer_real_problem",
        "target_frequency_per_week": 3,
        "preferences": '{"tone":"practical","length":"short"}',
    }
    if payload:
        body.update(payload)
    return client.post(f"/api/projects/{project_id}/content-plans", json=body)


def test_create_content_plan_success(client: TestClient):
    project_id = create_project(client)

    response = create_content_plan(client, project_id)

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project_id
    assert body["name"] == "Weekly AI dev log"
    assert body["account_positioning"] == "Chinese developer sharing practical AI workflow notes"
    assert body["content_type"] == "programmer_real_problem"
    assert body["target_frequency_per_week"] == 3
    assert body["preferences"] == '{"tone":"practical","length":"short"}'
    assert body["is_enabled"] is True
    assert body["created_at"]
    assert body["updated_at"]


def test_create_content_plan_trims_text_fields_and_optional_preferences(client: TestClient):
    project_id = create_project(client)

    response = create_content_plan(
        client,
        project_id,
        {
            "name": "  Trimmed plan  ",
            "account_positioning": "  Practical AI creator  ",
            "content_type": "  project_log  ",
            "preferences": "   ",
            "is_enabled": False,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Trimmed plan"
    assert body["account_positioning"] == "Practical AI creator"
    assert body["content_type"] == "project_log"
    assert body["preferences"] is None
    assert body["is_enabled"] is False


def test_create_content_plan_rejects_missing_project(client: TestClient):
    response = create_content_plan(client, 999)

    assert response.status_code == 404
    assert response.json()["detail"] == "project not found"


def test_create_content_plan_rejects_archived_project(client: TestClient):
    project_id = create_project(client)
    client.post(f"/api/projects/{project_id}/archive")

    response = create_content_plan(client, project_id)

    assert response.status_code == 409
    assert response.json()["detail"] == "archived project cannot create content plans"


def test_create_content_plan_rejects_invalid_frequency(client: TestClient):
    project_id = create_project(client)

    too_low = create_content_plan(client, project_id, {"target_frequency_per_week": 0})
    too_high = create_content_plan(client, project_id, {"target_frequency_per_week": 15})

    assert too_low.status_code == 422
    assert too_high.status_code == 422


def test_create_content_plan_rejects_blank_required_text(client: TestClient):
    project_id = create_project(client)

    response = create_content_plan(client, project_id, {"name": "   "})

    assert response.status_code == 422
    assert response.json()["detail"] == "name is required"


def test_list_content_plans_for_project(client: TestClient):
    project_id = create_project(client)
    first = create_content_plan(client, project_id, {"name": "First plan"}).json()
    second = create_content_plan(client, project_id, {"name": "Second plan"}).json()

    response = client.get(f"/api/projects/{project_id}/content-plans")

    assert response.status_code == 200
    body = response.json()
    assert [plan["id"] for plan in body] == [second["id"], first["id"]]
    assert all(plan["project_id"] == project_id for plan in body)


def test_list_content_plans_for_missing_project_returns_404(client: TestClient):
    response = client.get("/api/projects/999/content-plans")

    assert response.status_code == 404
    assert response.json()["detail"] == "project not found"


def test_archived_project_can_list_and_read_existing_content_plans(client: TestClient):
    project_id = create_project(client)
    plan = create_content_plan(client, project_id).json()
    client.post(f"/api/projects/{project_id}/archive")

    list_response = client.get(f"/api/projects/{project_id}/content-plans")
    read_response = client.get(f"/api/projects/{project_id}/content-plans/{plan['id']}")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert read_response.status_code == 200
    assert read_response.json()["id"] == plan["id"]


def test_read_single_content_plan_success(client: TestClient):
    project_id = create_project(client)
    plan = create_content_plan(client, project_id).json()

    response = client.get(f"/api/projects/{project_id}/content-plans/{plan['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == plan["id"]


def test_read_content_plan_from_another_project_returns_404(client: TestClient):
    first_project_id = create_project(client, "First project")
    second_project_id = create_project(client, "Second project")
    plan = create_content_plan(client, first_project_id).json()

    response = client.get(f"/api/projects/{second_project_id}/content-plans/{plan['id']}")

    assert response.status_code == 404
    assert response.json()["detail"] == "content plan not found"


def test_update_content_plan_success(client: TestClient):
    project_id = create_project(client)
    plan = create_content_plan(client, project_id).json()

    response = client.patch(
        f"/api/projects/{project_id}/content-plans/{plan['id']}",
        json={
            "name": "Updated plan",
            "account_positioning": "Updated account positioning",
            "content_type": "updated_type",
            "target_frequency_per_week": 5,
            "preferences": '{"tone":"calm"}',
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Updated plan"
    assert body["account_positioning"] == "Updated account positioning"
    assert body["content_type"] == "updated_type"
    assert body["target_frequency_per_week"] == 5
    assert body["preferences"] == '{"tone":"calm"}'


def test_update_content_plan_rejects_invalid_frequency(client: TestClient):
    project_id = create_project(client)
    plan = create_content_plan(client, project_id).json()

    response = client.patch(
        f"/api/projects/{project_id}/content-plans/{plan['id']}",
        json={"target_frequency_per_week": 99},
    )

    assert response.status_code == 422


def test_update_content_plan_rejects_archived_project(client: TestClient):
    project_id = create_project(client)
    plan = create_content_plan(client, project_id).json()
    client.post(f"/api/projects/{project_id}/archive")

    response = client.patch(f"/api/projects/{project_id}/content-plans/{plan['id']}", json={"name": "Blocked"})

    assert response.status_code == 409
    assert response.json()["detail"] == "archived project cannot update content plans"


def test_update_missing_content_plan_returns_404(client: TestClient):
    project_id = create_project(client)

    response = client.patch(f"/api/projects/{project_id}/content-plans/999", json={"name": "Missing"})

    assert response.status_code == 404
    assert response.json()["detail"] == "content plan not found"


def test_enable_disable_content_plan(client: TestClient):
    project_id = create_project(client)
    plan = create_content_plan(client, project_id).json()

    disabled = client.post(f"/api/projects/{project_id}/content-plans/{plan['id']}/disable")
    enabled = client.post(f"/api/projects/{project_id}/content-plans/{plan['id']}/enable")

    assert disabled.status_code == 200
    assert disabled.json()["is_enabled"] is False
    assert enabled.status_code == 200
    assert enabled.json()["is_enabled"] is True


def test_enable_disable_missing_content_plan_returns_404(client: TestClient):
    project_id = create_project(client)

    disable_response = client.post(f"/api/projects/{project_id}/content-plans/999/disable")
    enable_response = client.post(f"/api/projects/{project_id}/content-plans/999/enable")

    assert disable_response.status_code == 404
    assert enable_response.status_code == 404


def test_archived_project_cannot_enable_or_disable_content_plan(client: TestClient):
    project_id = create_project(client)
    plan = create_content_plan(client, project_id).json()
    client.post(f"/api/projects/{project_id}/archive")

    disable_response = client.post(f"/api/projects/{project_id}/content-plans/{plan['id']}/disable")
    enable_response = client.post(f"/api/projects/{project_id}/content-plans/{plan['id']}/enable")

    assert disable_response.status_code == 409
    assert enable_response.status_code == 409


def test_content_plan_does_not_trigger_generation_or_scheduler_tables(client: TestClient):
    project_id = create_project(client)

    response = create_content_plan(client, project_id)

    assert response.status_code == 201
    detail = client.get(f"/api/projects/{project_id}").json()
    assert detail["status"] == "draft"
