from io import BytesIO

from fastapi.testclient import TestClient


def create_project(client: TestClient) -> int:
    response = client.post("/api/projects", json={"title": "Material project"})
    return response.json()["id"]


def test_add_text_material_success(client: TestClient):
    project_id = create_project(client)

    response = client.post(
        f"/api/projects/{project_id}/materials/text",
        json={"material_type": "summary", "title": "Summary", "text_content": "A user supplied summary."},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["material_type"] == "summary"
    assert body["text_content"] == "A user supplied summary."


def test_add_link_material_success(client: TestClient):
    project_id = create_project(client)

    response = client.post(
        f"/api/projects/{project_id}/materials/link",
        json={"title": "Reference", "source_url": "https://example.com/post"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["material_type"] == "link"
    assert body["source_url"] == "https://example.com/post"


def test_adding_material_marks_project_materials_ready(client: TestClient):
    project_id = create_project(client)

    client.post(
        f"/api/projects/{project_id}/materials/text",
        json={"material_type": "text", "text_content": "A note"},
    )
    response = client.get(f"/api/projects/{project_id}")

    assert response.json()["status"] == "materials_ready"


def test_add_material_to_missing_project_returns_404(client: TestClient):
    response = client.post(
        "/api/projects/999/materials/text",
        json={"material_type": "text", "text_content": "No project"},
    )

    assert response.status_code == 404


def test_upload_rejects_disallowed_file_type(client: TestClient):
    project_id = create_project(client)

    response = client.post(
        f"/api/projects/{project_id}/materials/file",
        data={"material_type": "image"},
        files={"file": ("note.txt", BytesIO(b"plain text"), "text/plain")},
    )

    assert response.status_code == 400
