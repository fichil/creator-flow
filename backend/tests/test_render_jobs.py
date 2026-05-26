import json
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import get_settings


def create_project(client: TestClient, title: str = "Render project") -> int:
    response = client.post("/api/projects", json={"title": title, "description": "Project description"})
    return response.json()["id"]


def add_text_material(client: TestClient, project_id: int, text: str = "User supplied render note.") -> int:
    response = client.post(
        f"/api/projects/{project_id}/materials/text",
        json={"material_type": "text", "title": "Material note", "text_content": text},
    )
    return response.json()["id"]


def select_topic_candidate(client: TestClient, project_id: int) -> int:
    generated = client.post(
        f"/api/projects/{project_id}/topic-candidates/generate",
        json={"candidate_count": 1},
    ).json()
    candidate_id = generated["candidates"][0]["id"]
    response = client.post(f"/api/projects/{project_id}/topic-candidates/{candidate_id}/select")
    return response.json()["id"]


def select_script_draft(client: TestClient, project_id: int) -> int:
    generated = client.post(
        f"/api/projects/{project_id}/script-drafts/generate",
        json={"script_count": 1},
    ).json()
    script_draft_id = generated["script_drafts"][0]["id"]
    response = client.post(f"/api/projects/{project_id}/script-drafts/{script_draft_id}/select")
    return response.json()["id"]


def select_storyboard(client: TestClient, project_id: int) -> dict:
    generated = client.post(
        f"/api/projects/{project_id}/storyboards/generate",
        json={"storyboard_count": 1},
    ).json()
    storyboard_id = generated["storyboards"][0]["id"]
    response = client.post(f"/api/projects/{project_id}/storyboards/{storyboard_id}/select")
    return response.json()


def create_render(client: TestClient, project_id: int, payload: dict | None = None):
    return client.post(f"/api/projects/{project_id}/renders", json=payload or {})


def create_selected_subtitle_draft(client: TestClient, project_id: int) -> dict:
    subtitle_draft = client.post(f"/api/projects/{project_id}/subtitle-drafts", json={}).json()
    return client.post(f"/api/projects/{project_id}/subtitle-drafts/{subtitle_draft['id']}/select").json()


def prepare_project_for_render(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)
    select_script_draft(client, project_id)
    storyboard = select_storyboard(client, project_id)
    return project_id, storyboard


def test_create_fake_render_success_for_project_with_selected_storyboard(client: TestClient):
    project_id, storyboard = prepare_project_for_render(client)

    response = create_render(client, project_id)

    assert response.status_code == 200
    body = response.json()
    assert body["storyboard_draft_id"] == storyboard["id"]
    assert body["renderer_name"] == "fake_renderer"
    assert body["renderer_version"] == "0.1"
    assert body["status"] == "succeeded"
    assert body["requested_format"] == "mp4"
    assert body["requested_aspect_ratio"] == "9:16"
    assert body["requested_resolution"] == "1080x1920"
    assert body["started_at"] is not None
    assert body["completed_at"] is not None
    artifact = body["artifact"]
    expected_duration = sum(scene["estimated_duration_seconds"] for scene in storyboard["scenes"])
    assert artifact["artifact_type"] == "fake_preview_manifest"
    assert artifact["mime_type"] == "application/json"
    assert artifact["subtitle_draft_id"] is None
    assert artifact["duration_seconds"] == expected_duration
    assert artifact["file_size_bytes"] > 0
    assert artifact["width"] == 1080
    assert artifact["height"] == 1920
    assert artifact["storage_path"] == (
        f"data/local/render_previews/project-{project_id}/"
        f"project-{project_id}-render-{body['id']}-preview-manifest.json"
    )
    assert artifact["checksum_sha256"]


def test_create_fake_render_persists_job_and_artifact(client: TestClient):
    project_id, _ = prepare_project_for_render(client)

    response = create_render(client, project_id)

    assert response.status_code == 200
    with sqlite3.connect(get_settings().database_path) as connection:
        job_count = connection.execute("SELECT COUNT(*) FROM render_jobs").fetchone()[0]
        artifact_count = connection.execute("SELECT COUNT(*) FROM render_artifacts").fetchone()[0]
    assert job_count == 1
    assert artifact_count == 1


def test_create_fake_render_writes_preview_manifest_to_ignored_runtime_path(client: TestClient):
    project_id, storyboard = prepare_project_for_render(client)

    body = create_render(client, project_id).json()

    artifact = body["artifact"]
    assert artifact["storage_path"].startswith("data/local/render_previews/")
    manifest_path = get_settings().render_previews_dir / f"project-{project_id}" / artifact["file_name"]
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["artifact_type"] == "fake_preview_manifest"
    assert manifest["project_id"] == project_id
    assert manifest["render_job_id"] == body["id"]
    assert manifest["selected_storyboard_id"] == storyboard["id"]
    assert manifest["selected_subtitle_draft_id"] is None
    assert manifest["duration_seconds"] == artifact["duration_seconds"]


def test_create_fake_render_with_selected_subtitle_draft_records_subtitle_metadata(client: TestClient):
    project_id, _ = prepare_project_for_render(client)
    subtitle_draft = create_selected_subtitle_draft(client, project_id)

    body = create_render(client, project_id).json()

    artifact = body["artifact"]
    manifest_path = get_settings().render_previews_dir / f"project-{project_id}" / artifact["file_name"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert artifact["subtitle_draft_id"] == subtitle_draft["id"]
    assert manifest["selected_subtitle_draft_id"] == subtitle_draft["id"]


def test_create_fake_render_without_selected_subtitle_draft_still_succeeds(client: TestClient):
    project_id, _ = prepare_project_for_render(client)

    response = create_render(client, project_id)

    assert response.status_code == 200
    artifact = response.json()["artifact"]
    manifest_path = get_settings().render_previews_dir / f"project-{project_id}" / artifact["file_name"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert artifact["subtitle_draft_id"] is None
    assert manifest["selected_subtitle_draft_id"] is None


def test_create_fake_render_does_not_create_real_media_or_subtitle_files(client: TestClient):
    project_id, _ = prepare_project_for_render(client)

    response = create_render(client, project_id)

    assert response.status_code == 200
    preview_dir = get_settings().render_previews_dir
    generated_paths = [path for path in preview_dir.rglob("*") if path.is_file()]
    assert generated_paths
    assert all(path.suffix == ".json" for path in generated_paths)
    assert not list(preview_dir.rglob("*.mp4"))
    assert not list(preview_dir.rglob("*.mp3"))
    assert not list(preview_dir.rglob("*.wav"))
    assert not list(preview_dir.rglob("*.srt"))
    assert not list(preview_dir.rglob("*.vtt"))


def test_preview_manifest_storage_path_is_covered_by_gitignore(client: TestClient):
    project_id, _ = prepare_project_for_render(client)

    artifact = create_render(client, project_id).json()["artifact"]

    repo_root = Path(__file__).resolve().parents[2]
    ignore_file = repo_root / ".gitignore"
    ignore_lines = ignore_file.read_text(encoding="utf-8").splitlines()
    assert "data/local/" in ignore_lines
    assert artifact["storage_path"].startswith("data/local/render_previews/")


def test_create_fake_render_without_selected_storyboard_returns_409(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)
    select_script_draft(client, project_id)

    response = create_render(client, project_id)

    assert response.status_code == 409


def test_create_fake_render_with_selected_storyboard_without_scenes_returns_409(client: TestClient):
    project_id, storyboard = prepare_project_for_render(client)
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute("DELETE FROM storyboard_scenes WHERE storyboard_draft_id = ?", (storyboard["id"],))

    response = create_render(client, project_id)

    assert response.status_code == 409


def test_create_fake_render_for_archived_project_returns_409(client: TestClient):
    project_id, _ = prepare_project_for_render(client)
    client.post(f"/api/projects/{project_id}/archive")

    response = create_render(client, project_id)

    assert response.status_code == 409


def test_create_fake_render_for_missing_project_returns_404(client: TestClient):
    response = create_render(client, 999)

    assert response.status_code == 404


def test_list_render_jobs_returns_persisted_data(client: TestClient):
    project_id, _ = prepare_project_for_render(client)
    created = create_render(client, project_id).json()

    response = client.get(f"/api/projects/{project_id}/renders")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == created["id"]
    assert body[0]["artifact"]["id"] == created["artifact"]["id"]
    assert body[0]["artifact"]["artifact_type"] == "fake_preview_manifest"
    assert body[0]["artifact"]["mime_type"] == "application/json"
    assert body[0]["artifact"]["storage_path"] == created["artifact"]["storage_path"]
    assert body[0]["artifact"]["checksum_sha256"] == created["artifact"]["checksum_sha256"]
    assert body[0]["artifact"]["subtitle_draft_id"] is None


def test_get_single_render_job_success(client: TestClient):
    project_id, _ = prepare_project_for_render(client)
    created = create_render(client, project_id).json()

    response = client.get(f"/api/projects/{project_id}/renders/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["artifact"]["render_job_id"] == created["id"]
    assert response.json()["artifact"]["artifact_type"] == "fake_preview_manifest"
    assert response.json()["artifact"]["mime_type"] == "application/json"
    assert response.json()["artifact"]["storage_path"] == created["artifact"]["storage_path"]
    assert response.json()["artifact"]["checksum_sha256"] == created["artifact"]["checksum_sha256"]
    assert response.json()["artifact"]["subtitle_draft_id"] is None


def test_create_fake_render_does_not_modify_project_status(client: TestClient):
    project_id, _ = prepare_project_for_render(client)

    before = client.get(f"/api/projects/{project_id}").json()["status"]
    response = create_render(client, project_id)
    after = client.get(f"/api/projects/{project_id}").json()["status"]

    assert response.status_code == 200
    assert after == before


def test_get_render_job_from_another_project_returns_404(client: TestClient):
    first_project_id, _ = prepare_project_for_render(client)
    second_project_id, _ = prepare_project_for_render(client)
    created = create_render(client, first_project_id).json()

    response = client.get(f"/api/projects/{second_project_id}/renders/{created['id']}")

    assert response.status_code == 404


def test_get_missing_render_job_returns_404(client: TestClient):
    project_id, _ = prepare_project_for_render(client)

    response = client.get(f"/api/projects/{project_id}/renders/999")

    assert response.status_code == 404


def test_get_render_job_for_missing_project_returns_404(client: TestClient):
    response = client.get("/api/projects/999/renders/1")

    assert response.status_code == 404


def test_archived_project_can_list_existing_render_jobs(client: TestClient):
    project_id, _ = prepare_project_for_render(client)
    create_render(client, project_id)
    client.post(f"/api/projects/{project_id}/archive")

    response = client.get(f"/api/projects/{project_id}/renders")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_archived_project_can_get_existing_render_job(client: TestClient):
    project_id, _ = prepare_project_for_render(client)
    created = create_render(client, project_id).json()
    client.post(f"/api/projects/{project_id}/archive")

    response = client.get(f"/api/projects/{project_id}/renders/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_create_fake_render_rejects_invalid_format(client: TestClient):
    project_id, _ = prepare_project_for_render(client)

    response = create_render(client, project_id, {"requested_format": "mov"})

    assert response.status_code == 422


def test_create_fake_render_rejects_invalid_aspect_ratio(client: TestClient):
    project_id, _ = prepare_project_for_render(client)

    response = create_render(client, project_id, {"requested_aspect_ratio": "16:9"})

    assert response.status_code == 422


def test_create_fake_render_rejects_invalid_resolution(client: TestClient):
    project_id, _ = prepare_project_for_render(client)

    response = create_render(client, project_id, {"requested_resolution": "720x1280"})

    assert response.status_code == 422


def test_create_fake_render_rejects_renderer_override(client: TestClient):
    project_id, _ = prepare_project_for_render(client)

    response = create_render(client, project_id, {"renderer_name": "ffmpeg"})

    assert response.status_code == 422


def test_list_render_jobs_for_missing_project_returns_404(client: TestClient):
    response = client.get("/api/projects/999/renders")

    assert response.status_code == 404
