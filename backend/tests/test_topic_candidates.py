import sqlite3

from fastapi.testclient import TestClient

from app.core.config import get_settings


def create_project(client: TestClient, title: str = "Topic project") -> int:
    response = client.post("/api/projects", json={"title": title, "description": "Project description"})
    return response.json()["id"]


def add_text_material(client: TestClient, project_id: int, text: str = "User supplied planning note.") -> int:
    response = client.post(
        f"/api/projects/{project_id}/materials/text",
        json={"material_type": "text", "title": "Material note", "text_content": text},
    )
    return response.json()["id"]


def generate_candidates(client: TestClient, project_id: int, candidate_count: int = 3):
    return client.post(
        f"/api/projects/{project_id}/topic-candidates/generate",
        json={"candidate_count": candidate_count},
    )


def test_generate_topic_candidates_success_for_project_with_materials(client: TestClient):
    project_id = create_project(client)
    material_id = add_text_material(client, project_id)

    response = generate_candidates(client, project_id)

    assert response.status_code == 200
    body = response.json()
    assert body["run"]["provider_name"] == "fake_llm"
    assert body["run"]["provider_version"] == "0.1"
    assert body["run"]["status"] == "succeeded"
    assert body["run"]["requested_candidate_count"] == 3
    assert body["run"]["input_material_count"] == 1
    assert len(body["candidates"]) == 3
    assert body["candidates"][0]["status"] == "candidate"
    assert body["candidates"][0]["source_material_ids"] == [material_id]


def test_generate_topic_candidates_defaults_to_three_candidates(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)

    response = client.post(f"/api/projects/{project_id}/topic-candidates/generate")

    assert response.status_code == 200
    assert response.json()["run"]["requested_candidate_count"] == 3
    assert len(response.json()["candidates"]) == 3


def test_generate_topic_candidates_persists_run_candidates_and_sources(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    add_text_material(client, project_id, text="Second explicit material.")

    response = generate_candidates(client, project_id, candidate_count=2)

    assert response.status_code == 200
    with sqlite3.connect(get_settings().database_path) as connection:
        run_count = connection.execute("SELECT COUNT(*) FROM topic_generation_runs").fetchone()[0]
        candidate_count = connection.execute("SELECT COUNT(*) FROM topic_candidates").fetchone()[0]
        source_count = connection.execute("SELECT COUNT(*) FROM topic_candidate_sources").fetchone()[0]
    assert run_count == 1
    assert candidate_count == 2
    assert source_count == 4


def test_generate_topic_candidates_without_materials_returns_409(client: TestClient):
    project_id = create_project(client)

    response = generate_candidates(client, project_id)

    assert response.status_code == 409


def test_generate_topic_candidates_for_archived_project_returns_409(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    client.post(f"/api/projects/{project_id}/archive")

    response = generate_candidates(client, project_id)

    assert response.status_code == 409


def test_generate_topic_candidates_for_missing_project_returns_404(client: TestClient):
    response = generate_candidates(client, 999)

    assert response.status_code == 404


def test_generate_topic_candidates_rejects_zero_count(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)

    response = generate_candidates(client, project_id, candidate_count=0)

    assert response.status_code == 422


def test_generate_topic_candidates_rejects_count_over_five(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)

    response = generate_candidates(client, project_id, candidate_count=6)

    assert response.status_code == 422


def test_generate_topic_candidates_rejects_provider_override(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)

    response = client.post(
        f"/api/projects/{project_id}/topic-candidates/generate",
        json={"candidate_count": 3, "provider_name": "fake_llm"},
    )

    assert response.status_code == 422


def test_list_topic_candidates_returns_persisted_candidates(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    generated = generate_candidates(client, project_id, candidate_count=2).json()

    response = client.get(f"/api/projects/{project_id}/topic-candidates")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {candidate["id"] for candidate in body} == {candidate["id"] for candidate in generated["candidates"]}
    assert all(candidate["source_material_ids"] for candidate in body)


def test_archived_project_can_list_existing_topic_candidates(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    generate_candidates(client, project_id, candidate_count=1)
    client.post(f"/api/projects/{project_id}/archive")

    response = client.get(f"/api/projects/{project_id}/topic-candidates")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_select_topic_candidate_success(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    candidate = generate_candidates(client, project_id, candidate_count=1).json()["candidates"][0]

    response = client.post(f"/api/projects/{project_id}/topic-candidates/{candidate['id']}/select")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == candidate["id"]
    assert body["status"] == "selected"
    assert body["selected_at"] is not None


def test_only_one_topic_candidate_can_be_selected_per_project(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    candidates = generate_candidates(client, project_id, candidate_count=2).json()["candidates"]

    first = candidates[0]
    second = candidates[1]
    client.post(f"/api/projects/{project_id}/topic-candidates/{first['id']}/select")
    client.post(f"/api/projects/{project_id}/topic-candidates/{second['id']}/select")

    response = client.get(f"/api/projects/{project_id}/topic-candidates")
    statuses = {candidate["id"]: candidate["status"] for candidate in response.json()}
    assert statuses[first["id"]] == "candidate"
    assert statuses[second["id"]] == "selected"


def test_select_missing_topic_candidate_returns_404(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)

    response = client.post(f"/api/projects/{project_id}/topic-candidates/999/select")

    assert response.status_code == 404


def test_select_topic_candidate_from_another_project_returns_404(client: TestClient):
    first_project_id = create_project(client, title="First")
    second_project_id = create_project(client, title="Second")
    add_text_material(client, first_project_id)
    add_text_material(client, second_project_id)
    candidate = generate_candidates(client, first_project_id, candidate_count=1).json()["candidates"][0]

    response = client.post(f"/api/projects/{second_project_id}/topic-candidates/{candidate['id']}/select")

    assert response.status_code == 404


def test_archived_project_cannot_select_topic_candidate(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    candidate = generate_candidates(client, project_id, candidate_count=1).json()["candidates"][0]
    client.post(f"/api/projects/{project_id}/archive")

    response = client.post(f"/api/projects/{project_id}/topic-candidates/{candidate['id']}/select")

    assert response.status_code == 409


def test_list_topic_candidates_for_missing_project_returns_404(client: TestClient):
    response = client.get("/api/projects/999/topic-candidates")

    assert response.status_code == 404
