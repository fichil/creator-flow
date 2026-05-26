from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import get_settings

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02\x00\x00\x00\x0bIDATx\xdac\xfc\xff"
    b"\x1f\x00\x03\x03\x02\x00\xef\xbf\xa7\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
)


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


def test_upload_image_material_success(client: TestClient):
    project_id = create_project(client)

    response = client.post(
        f"/api/projects/{project_id}/materials/file",
        data={"material_type": "image", "title": "Tiny image"},
        files={"file": ("tiny.png", BytesIO(PNG_BYTES), "image/png")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["material_type"] == "image"
    assert body["stored_file_path"]
    stored_relative = Path(body["stored_file_path"]).relative_to("uploads")
    assert (get_settings().uploads_dir / stored_relative).exists()
    assert client.get(f"/api/projects/{project_id}").json()["status"] == "materials_ready"


def test_upload_too_large_file_returns_413_and_removes_partial_file(client: TestClient):
    project_id = create_project(client)

    response = client.post(
        f"/api/projects/{project_id}/materials/file",
        data={"material_type": "image"},
        files={"file": ("large.png", BytesIO(b"0" * (10 * 1024 * 1024 + 1)), "image/png")},
    )

    assert response.status_code == 413
    upload_dir = get_settings().uploads_dir / str(project_id)
    assert not upload_dir.exists() or list(upload_dir.iterdir()) == []


def test_upload_rejects_invalid_material_type(client: TestClient):
    project_id = create_project(client)

    response = client.post(
        f"/api/projects/{project_id}/materials/file",
        data={"material_type": "document"},
        files={"file": ("tiny.png", BytesIO(PNG_BYTES), "image/png")},
    )

    assert response.status_code == 422


def test_archived_project_rejects_text_material(client: TestClient):
    project_id = create_project(client)
    client.post(f"/api/projects/{project_id}/archive")

    response = client.post(
        f"/api/projects/{project_id}/materials/text",
        json={"material_type": "text", "text_content": "Too late"},
    )

    assert response.status_code == 409


def test_archived_project_rejects_link_material(client: TestClient):
    project_id = create_project(client)
    client.post(f"/api/projects/{project_id}/archive")

    response = client.post(
        f"/api/projects/{project_id}/materials/link",
        json={"source_url": "https://example.com/late"},
    )

    assert response.status_code == 409


def test_archived_project_rejects_file_material(client: TestClient):
    project_id = create_project(client)
    client.post(f"/api/projects/{project_id}/archive")

    response = client.post(
        f"/api/projects/{project_id}/materials/file",
        data={"material_type": "image"},
        files={"file": ("tiny.png", BytesIO(PNG_BYTES), "image/png")},
    )

    assert response.status_code == 409
