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


def test_update_project_success(client: TestClient):
    project = client.post("/api/projects", json={"title": "Old title", "description": "Old description"}).json()

    response = client.patch(
        f"/api/projects/{project['id']}",
        json={"title": "New title", "description": "New description"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "New title"
    assert body["description"] == "New description"
    assert body["status"] == "draft"


def test_update_project_rejects_blank_title(client: TestClient):
    project = client.post("/api/projects", json={"title": "Keep title"}).json()

    response = client.patch(f"/api/projects/{project['id']}", json={"title": "   "})

    assert response.status_code == 422


def test_update_project_rejects_status_changes(client: TestClient):
    project = client.post("/api/projects", json={"title": "No status patch"}).json()

    response = client.patch(f"/api/projects/{project['id']}", json={"status": "archived"})

    assert response.status_code == 422


def test_archive_project_success(client: TestClient):
    project = client.post("/api/projects", json={"title": "Archive me"}).json()

    response = client.post(f"/api/projects/{project['id']}/archive")

    assert response.status_code == 200
    assert response.json()["status"] == "archived"


def test_archive_project_is_idempotent(client: TestClient):
    project = client.post("/api/projects", json={"title": "Archive twice"}).json()

    first = client.post(f"/api/projects/{project['id']}/archive")
    second = client.post(f"/api/projects/{project['id']}/archive")

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["status"] == "archived"


def test_project_list_excludes_archived_by_default(client: TestClient):
    active = client.post("/api/projects", json={"title": "Active project"}).json()
    archived = client.post("/api/projects", json={"title": "Archived project"}).json()
    client.post(f"/api/projects/{archived['id']}/archive")

    response = client.get("/api/projects")

    assert response.status_code == 200
    ids = [project["id"] for project in response.json()]
    assert active["id"] in ids
    assert archived["id"] not in ids


def test_project_list_includes_archived_when_requested(client: TestClient):
    archived = client.post("/api/projects", json={"title": "Archived project"}).json()
    client.post(f"/api/projects/{archived['id']}/archive")

    response = client.get("/api/projects?include_archived=true")

    assert response.status_code == 200
    projects = response.json()
    assert any(project["id"] == archived["id"] and project["status"] == "archived" for project in projects)


def test_project_list_returns_material_count(client: TestClient):
    project = client.post("/api/projects", json={"title": "Count materials"}).json()
    client.post(
        f"/api/projects/{project['id']}/materials/text",
        json={"material_type": "text", "text_content": "First material"},
    )
    client.post(
        f"/api/projects/{project['id']}/materials/link",
        json={"source_url": "https://example.com/material"},
    )

    response = client.get("/api/projects")

    listed = next(item for item in response.json() if item["id"] == project["id"])
    assert listed["material_count"] == 2


def test_archived_project_detail_returns_existing_materials(client: TestClient):
    project = client.post("/api/projects", json={"title": "Archived detail"}).json()
    client.post(
        f"/api/projects/{project['id']}/materials/text",
        json={"material_type": "text", "text_content": "Keep this material"},
    )
    client.post(f"/api/projects/{project['id']}/archive")

    response = client.get(f"/api/projects/{project['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "archived"
    assert len(body["materials"]) == 1
    assert body["materials"][0]["text_content"] == "Keep this material"
