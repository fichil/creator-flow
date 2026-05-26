import sqlite3

from fastapi.testclient import TestClient

from app.core.config import get_settings


def create_project(client: TestClient, title: str = "Storyboard project") -> int:
    response = client.post("/api/projects", json={"title": title, "description": "Project description"})
    return response.json()["id"]


def add_text_material(client: TestClient, project_id: int, text: str = "User supplied storyboard note.") -> int:
    response = client.post(
        f"/api/projects/{project_id}/materials/text",
        json={"material_type": "text", "title": "Material note", "text_content": text},
    )
    return response.json()["id"]


def generate_topic_candidates(client: TestClient, project_id: int, candidate_count: int = 1):
    return client.post(
        f"/api/projects/{project_id}/topic-candidates/generate",
        json={"candidate_count": candidate_count},
    )


def select_topic_candidate(client: TestClient, project_id: int) -> int:
    candidate = generate_topic_candidates(client, project_id).json()["candidates"][0]
    response = client.post(f"/api/projects/{project_id}/topic-candidates/{candidate['id']}/select")
    return response.json()["id"]


def generate_script_drafts(client: TestClient, project_id: int, script_count: int = 1):
    return client.post(
        f"/api/projects/{project_id}/script-drafts/generate",
        json={"script_count": script_count},
    )


def select_script_draft(client: TestClient, project_id: int) -> int:
    script_draft = generate_script_drafts(client, project_id).json()["script_drafts"][0]
    response = client.post(f"/api/projects/{project_id}/script-drafts/{script_draft['id']}/select")
    return response.json()["id"]


def generate_storyboards(client: TestClient, project_id: int, storyboard_count: int = 1):
    return client.post(
        f"/api/projects/{project_id}/storyboards/generate",
        json={"storyboard_count": storyboard_count},
    )


def prepare_project_for_storyboards(client: TestClient):
    project_id = create_project(client)
    material_id = add_text_material(client, project_id)
    topic_candidate_id = select_topic_candidate(client, project_id)
    script_draft_id = select_script_draft(client, project_id)
    return project_id, material_id, topic_candidate_id, script_draft_id


def test_generate_storyboards_success_for_project_with_selected_topic_and_script(client: TestClient):
    project_id, material_id, topic_candidate_id, script_draft_id = prepare_project_for_storyboards(client)

    response = generate_storyboards(client, project_id)

    assert response.status_code == 200
    body = response.json()
    assert body["run"]["provider_name"] == "fake_llm"
    assert body["run"]["provider_version"] == "0.1"
    assert body["run"]["status"] == "succeeded"
    assert body["run"]["requested_storyboard_count"] == 1
    assert body["run"]["input_material_count"] == 1
    assert body["run"]["selected_topic_candidate_id"] == topic_candidate_id
    assert body["run"]["selected_script_draft_id"] == script_draft_id
    assert len(body["storyboards"]) == 1
    storyboard = body["storyboards"][0]
    assert storyboard["status"] == "draft"
    assert storyboard["topic_candidate_id"] == topic_candidate_id
    assert storyboard["script_draft_id"] == script_draft_id
    assert storyboard["source_material_ids"] == [material_id]
    assert len(storyboard["scenes"]) >= 2
    assert storyboard["scenes"][0]["scene_order"] == 1
    assert all(scene["estimated_duration_seconds"] > 0 for scene in storyboard["scenes"])


def test_generate_storyboards_defaults_to_one_storyboard(client: TestClient):
    project_id, _, _, _ = prepare_project_for_storyboards(client)

    response = client.post(f"/api/projects/{project_id}/storyboards/generate")

    assert response.status_code == 200
    assert response.json()["run"]["requested_storyboard_count"] == 1
    assert len(response.json()["storyboards"]) == 1


def test_generate_storyboards_persists_run_drafts_scenes_and_sources(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    add_text_material(client, project_id, text="Second explicit material.")
    select_topic_candidate(client, project_id)
    select_script_draft(client, project_id)

    response = generate_storyboards(client, project_id, storyboard_count=2)

    assert response.status_code == 200
    with sqlite3.connect(get_settings().database_path) as connection:
        run_count = connection.execute("SELECT COUNT(*) FROM storyboard_generation_runs").fetchone()[0]
        draft_count = connection.execute("SELECT COUNT(*) FROM storyboard_drafts").fetchone()[0]
        scene_count = connection.execute("SELECT COUNT(*) FROM storyboard_scenes").fetchone()[0]
        source_count = connection.execute("SELECT COUNT(*) FROM storyboard_draft_sources").fetchone()[0]
    assert run_count == 1
    assert draft_count == 2
    assert scene_count >= 4
    assert source_count == 4


def test_generate_storyboards_without_materials_returns_409(client: TestClient):
    project_id = create_project(client)

    response = generate_storyboards(client, project_id)

    assert response.status_code == 409


def test_generate_storyboards_without_selected_topic_returns_409(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)

    response = generate_storyboards(client, project_id)

    assert response.status_code == 409


def test_generate_storyboards_without_selected_script_returns_409(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)
    generate_script_drafts(client, project_id)

    response = generate_storyboards(client, project_id)

    assert response.status_code == 409


def test_generate_storyboards_for_archived_project_returns_409(client: TestClient):
    project_id, _, _, _ = prepare_project_for_storyboards(client)
    client.post(f"/api/projects/{project_id}/archive")

    response = generate_storyboards(client, project_id)

    assert response.status_code == 409


def test_generate_storyboards_for_missing_project_returns_404(client: TestClient):
    response = generate_storyboards(client, 999)

    assert response.status_code == 404


def test_generate_storyboards_rejects_zero_count(client: TestClient):
    project_id, _, _, _ = prepare_project_for_storyboards(client)

    response = generate_storyboards(client, project_id, storyboard_count=0)

    assert response.status_code == 422


def test_generate_storyboards_rejects_count_over_two(client: TestClient):
    project_id, _, _, _ = prepare_project_for_storyboards(client)

    response = generate_storyboards(client, project_id, storyboard_count=3)

    assert response.status_code == 422


def test_generate_storyboards_rejects_provider_override(client: TestClient):
    project_id, _, _, _ = prepare_project_for_storyboards(client)

    response = client.post(
        f"/api/projects/{project_id}/storyboards/generate",
        json={"storyboard_count": 1, "provider_name": "fake_llm"},
    )

    assert response.status_code == 422


def test_list_storyboards_returns_persisted_data_and_ordered_scenes(client: TestClient):
    project_id, _, _, _ = prepare_project_for_storyboards(client)
    generated = generate_storyboards(client, project_id, storyboard_count=1).json()

    response = client.get(f"/api/projects/{project_id}/storyboards")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == generated["storyboards"][0]["id"]
    assert body[0]["source_material_ids"]
    scene_orders = [scene["scene_order"] for scene in body[0]["scenes"]]
    assert scene_orders == sorted(scene_orders)
    assert scene_orders[0] == 1


def test_archived_project_can_list_existing_storyboards(client: TestClient):
    project_id, _, _, _ = prepare_project_for_storyboards(client)
    generate_storyboards(client, project_id, storyboard_count=1)
    client.post(f"/api/projects/{project_id}/archive")

    response = client.get(f"/api/projects/{project_id}/storyboards")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_select_storyboard_success(client: TestClient):
    project_id, _, _, _ = prepare_project_for_storyboards(client)
    storyboard = generate_storyboards(client, project_id, storyboard_count=1).json()["storyboards"][0]

    response = client.post(f"/api/projects/{project_id}/storyboards/{storyboard['id']}/select")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == storyboard["id"]
    assert body["status"] == "selected"
    assert body["selected_at"] is not None
    assert len(body["scenes"]) >= 2


def test_only_one_storyboard_can_be_selected_per_project(client: TestClient):
    project_id, _, _, _ = prepare_project_for_storyboards(client)
    storyboards = generate_storyboards(client, project_id, storyboard_count=2).json()["storyboards"]

    first = storyboards[0]
    second = storyboards[1]
    client.post(f"/api/projects/{project_id}/storyboards/{first['id']}/select")
    client.post(f"/api/projects/{project_id}/storyboards/{second['id']}/select")

    response = client.get(f"/api/projects/{project_id}/storyboards")
    statuses = {storyboard["id"]: storyboard["status"] for storyboard in response.json()}
    assert statuses[first["id"]] == "draft"
    assert statuses[second["id"]] == "selected"


def test_select_missing_storyboard_returns_404(client: TestClient):
    project_id, _, _, _ = prepare_project_for_storyboards(client)

    response = client.post(f"/api/projects/{project_id}/storyboards/999/select")

    assert response.status_code == 404


def test_select_storyboard_from_another_project_returns_404(client: TestClient):
    first_project_id, _, _, _ = prepare_project_for_storyboards(client)
    second_project_id, _, _, _ = prepare_project_for_storyboards(client)
    storyboard = generate_storyboards(client, first_project_id, storyboard_count=1).json()["storyboards"][0]

    response = client.post(f"/api/projects/{second_project_id}/storyboards/{storyboard['id']}/select")

    assert response.status_code == 404


def test_archived_project_cannot_select_storyboard(client: TestClient):
    project_id, _, _, _ = prepare_project_for_storyboards(client)
    storyboard = generate_storyboards(client, project_id, storyboard_count=1).json()["storyboards"][0]
    client.post(f"/api/projects/{project_id}/archive")

    response = client.post(f"/api/projects/{project_id}/storyboards/{storyboard['id']}/select")

    assert response.status_code == 409


def test_list_storyboards_for_missing_project_returns_404(client: TestClient):
    response = client.get("/api/projects/999/storyboards")

    assert response.status_code == 404
