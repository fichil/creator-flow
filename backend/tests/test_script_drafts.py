import sqlite3

from fastapi.testclient import TestClient

from app.core.config import get_settings


def create_project(client: TestClient, title: str = "Script project") -> int:
    response = client.post("/api/projects", json={"title": title, "description": "Project description"})
    return response.json()["id"]


def add_text_material(client: TestClient, project_id: int, text: str = "User supplied script note.") -> int:
    response = client.post(
        f"/api/projects/{project_id}/materials/text",
        json={"material_type": "text", "title": "Material note", "text_content": text},
    )
    return response.json()["id"]


def generate_topic_candidates(client: TestClient, project_id: int, candidate_count: int = 2):
    return client.post(
        f"/api/projects/{project_id}/topic-candidates/generate",
        json={"candidate_count": candidate_count},
    )


def select_topic_candidate(client: TestClient, project_id: int) -> int:
    candidate = generate_topic_candidates(client, project_id, candidate_count=1).json()["candidates"][0]
    response = client.post(f"/api/projects/{project_id}/topic-candidates/{candidate['id']}/select")
    return response.json()["id"]


def generate_script_drafts(client: TestClient, project_id: int, script_count: int = 2):
    return client.post(
        f"/api/projects/{project_id}/script-drafts/generate",
        json={"script_count": script_count},
    )


def test_generate_script_drafts_success_for_project_with_materials_and_selected_topic(client: TestClient):
    project_id = create_project(client)
    material_id = add_text_material(client, project_id)
    topic_candidate_id = select_topic_candidate(client, project_id)

    response = generate_script_drafts(client, project_id)

    assert response.status_code == 200
    body = response.json()
    assert body["run"]["provider_name"] == "fake_llm"
    assert body["run"]["provider_version"] == "0.1"
    assert body["run"]["status"] == "succeeded"
    assert body["run"]["requested_script_count"] == 2
    assert body["run"]["input_material_count"] == 1
    assert body["run"]["selected_topic_candidate_id"] == topic_candidate_id
    assert len(body["script_drafts"]) == 2
    assert body["script_drafts"][0]["status"] == "draft"
    assert body["script_drafts"][0]["topic_candidate_id"] == topic_candidate_id
    assert body["script_drafts"][0]["source_material_ids"] == [material_id]


def test_generate_script_drafts_defaults_to_two_drafts(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)

    response = client.post(f"/api/projects/{project_id}/script-drafts/generate")

    assert response.status_code == 200
    assert response.json()["run"]["requested_script_count"] == 2
    assert len(response.json()["script_drafts"]) == 2


def test_generate_script_drafts_persists_run_drafts_and_sources(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    add_text_material(client, project_id, text="Second explicit material.")
    select_topic_candidate(client, project_id)

    response = generate_script_drafts(client, project_id, script_count=3)

    assert response.status_code == 200
    with sqlite3.connect(get_settings().database_path) as connection:
        run_count = connection.execute("SELECT COUNT(*) FROM script_generation_runs").fetchone()[0]
        draft_count = connection.execute("SELECT COUNT(*) FROM script_drafts").fetchone()[0]
        source_count = connection.execute("SELECT COUNT(*) FROM script_draft_sources").fetchone()[0]
    assert run_count == 1
    assert draft_count == 3
    assert source_count == 6


def test_generate_script_drafts_without_materials_returns_409(client: TestClient):
    project_id = create_project(client)

    response = generate_script_drafts(client, project_id)

    assert response.status_code == 409


def test_generate_script_drafts_without_selected_topic_returns_409(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    generate_topic_candidates(client, project_id, candidate_count=1)

    response = generate_script_drafts(client, project_id)

    assert response.status_code == 409


def test_generate_script_drafts_for_archived_project_returns_409(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)
    client.post(f"/api/projects/{project_id}/archive")

    response = generate_script_drafts(client, project_id)

    assert response.status_code == 409


def test_generate_script_drafts_for_missing_project_returns_404(client: TestClient):
    response = generate_script_drafts(client, 999)

    assert response.status_code == 404


def test_generate_script_drafts_rejects_zero_count(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)

    response = generate_script_drafts(client, project_id, script_count=0)

    assert response.status_code == 422


def test_generate_script_drafts_rejects_count_over_three(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)

    response = generate_script_drafts(client, project_id, script_count=4)

    assert response.status_code == 422


def test_generate_script_drafts_rejects_provider_override(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)

    response = client.post(
        f"/api/projects/{project_id}/script-drafts/generate",
        json={"script_count": 2, "provider_name": "fake_llm"},
    )

    assert response.status_code == 422


def test_list_script_drafts_returns_persisted_data(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)
    generated = generate_script_drafts(client, project_id, script_count=2).json()

    response = client.get(f"/api/projects/{project_id}/script-drafts")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {draft["id"] for draft in body} == {draft["id"] for draft in generated["script_drafts"]}
    assert all(draft["source_material_ids"] for draft in body)


def test_archived_project_can_list_existing_script_drafts(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)
    generate_script_drafts(client, project_id, script_count=1)
    client.post(f"/api/projects/{project_id}/archive")

    response = client.get(f"/api/projects/{project_id}/script-drafts")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_select_script_draft_success(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)
    script_draft = generate_script_drafts(client, project_id, script_count=1).json()["script_drafts"][0]

    response = client.post(f"/api/projects/{project_id}/script-drafts/{script_draft['id']}/select")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == script_draft["id"]
    assert body["status"] == "selected"
    assert body["selected_at"] is not None


def test_only_one_script_draft_can_be_selected_per_project(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)
    script_drafts = generate_script_drafts(client, project_id, script_count=2).json()["script_drafts"]

    first = script_drafts[0]
    second = script_drafts[1]
    client.post(f"/api/projects/{project_id}/script-drafts/{first['id']}/select")
    client.post(f"/api/projects/{project_id}/script-drafts/{second['id']}/select")

    response = client.get(f"/api/projects/{project_id}/script-drafts")
    statuses = {script_draft["id"]: script_draft["status"] for script_draft in response.json()}
    assert statuses[first["id"]] == "draft"
    assert statuses[second["id"]] == "selected"


def test_select_missing_script_draft_returns_404(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)

    response = client.post(f"/api/projects/{project_id}/script-drafts/999/select")

    assert response.status_code == 404


def test_select_script_draft_from_another_project_returns_404(client: TestClient):
    first_project_id = create_project(client, title="First")
    second_project_id = create_project(client, title="Second")
    add_text_material(client, first_project_id)
    add_text_material(client, second_project_id)
    select_topic_candidate(client, first_project_id)
    select_topic_candidate(client, second_project_id)
    script_draft = generate_script_drafts(client, first_project_id, script_count=1).json()["script_drafts"][0]

    response = client.post(f"/api/projects/{second_project_id}/script-drafts/{script_draft['id']}/select")

    assert response.status_code == 404


def test_archived_project_cannot_select_script_draft(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)
    script_draft = generate_script_drafts(client, project_id, script_count=1).json()["script_drafts"][0]
    client.post(f"/api/projects/{project_id}/archive")

    response = client.post(f"/api/projects/{project_id}/script-drafts/{script_draft['id']}/select")

    assert response.status_code == 409


def test_list_script_drafts_for_missing_project_returns_404(client: TestClient):
    response = client.get("/api/projects/999/script-drafts")

    assert response.status_code == 404
