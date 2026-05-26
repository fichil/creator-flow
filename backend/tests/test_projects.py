from fastapi.testclient import TestClient


def test_create_project_success(client: TestClient):
    response = client.post("/api/projects", json={"title": "First project", "description": "Local test"})

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "First project"
    assert body["description"] == "Local test"
    assert body["status"] == "draft"


def test_create_project_requires_title(client: TestClient):
    response = client.post("/api/projects", json={"title": ""})

    assert response.status_code == 422


def test_project_detail_returns_materials(client: TestClient):
    project = client.post("/api/projects", json={"title": "Project with material"}).json()
    client.post(
        f"/api/projects/{project['id']}/materials/text",
        json={"material_type": "text", "text_content": "Imported by the user"},
    )

    response = client.get(f"/api/projects/{project['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "materials_ready"
    assert len(body["materials"]) == 1
    assert body["materials"][0]["text_content"] == "Imported by the user"
