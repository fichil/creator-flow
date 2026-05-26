import sqlite3

from fastapi.testclient import TestClient

from app.core.config import get_settings


def create_project(client: TestClient, title: str = "Subtitle project") -> int:
    response = client.post("/api/projects", json={"title": title, "description": "Project description"})
    return response.json()["id"]


def add_text_material(client: TestClient, project_id: int, text: str = "User supplied subtitle note.") -> int:
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


def create_subtitle_draft(client: TestClient, project_id: int, payload: dict | None = None):
    return client.post(f"/api/projects/{project_id}/subtitle-drafts", json=payload)


def prepare_project_for_subtitles(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)
    script_draft_id = select_script_draft(client, project_id)
    storyboard = select_storyboard(client, project_id)
    return project_id, script_draft_id, storyboard


def test_create_fake_subtitle_draft_success_for_project_with_selected_storyboard(client: TestClient):
    project_id, script_draft_id, storyboard = prepare_project_for_subtitles(client)

    response = create_subtitle_draft(client, project_id)

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == project_id
    assert body["script_draft_id"] == script_draft_id
    assert body["storyboard_draft_id"] == storyboard["id"]
    assert body["generator_name"] == "fake_subtitle_generator"
    assert body["generator_version"] == "0.1"
    assert body["status"] == "draft"
    assert body["selected_at"] is None
    assert len(body["cues"]) == len(storyboard["scenes"])
    assert body["cues"][0]["cue_order"] == 1
    assert body["cues"][0]["start_time_seconds"] == 0
    assert body["cues"][0]["end_time_seconds"] == storyboard["scenes"][0]["estimated_duration_seconds"]
    assert body["cues"][0]["text"] == storyboard["scenes"][0]["narration"]


def test_create_fake_subtitle_draft_persists_draft_and_cues_without_files(client: TestClient):
    project_id, _, storyboard = prepare_project_for_subtitles(client)

    response = create_subtitle_draft(client, project_id)

    assert response.status_code == 200
    with sqlite3.connect(get_settings().database_path) as connection:
        draft_count = connection.execute("SELECT COUNT(*) FROM subtitle_drafts").fetchone()[0]
        cue_count = connection.execute("SELECT COUNT(*) FROM subtitle_cues").fetchone()[0]
        tables = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    assert draft_count == 1
    assert cue_count == len(storyboard["scenes"])
    assert ("subtitle_files",) not in tables


def test_create_fake_subtitle_draft_is_deterministic_for_same_selected_storyboard(client: TestClient):
    project_id, _, _ = prepare_project_for_subtitles(client)

    first = create_subtitle_draft(client, project_id).json()
    second = create_subtitle_draft(client, project_id).json()

    first_cues = [
        (cue["cue_order"], cue["start_time_seconds"], cue["end_time_seconds"], cue["text"])
        for cue in first["cues"]
    ]
    second_cues = [
        (cue["cue_order"], cue["start_time_seconds"], cue["end_time_seconds"], cue["text"])
        for cue in second["cues"]
    ]
    assert first_cues == second_cues


def test_create_fake_subtitle_draft_does_not_modify_project_status(client: TestClient):
    project_id, _, _ = prepare_project_for_subtitles(client)

    before = client.get(f"/api/projects/{project_id}").json()["status"]
    response = create_subtitle_draft(client, project_id)
    after = client.get(f"/api/projects/{project_id}").json()["status"]

    assert response.status_code == 200
    assert after == before


def test_create_fake_subtitle_draft_without_selected_storyboard_returns_409(client: TestClient):
    project_id = create_project(client)
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)
    select_script_draft(client, project_id)

    response = create_subtitle_draft(client, project_id)

    assert response.status_code == 409
    assert response.json()["detail"] == "project has no selected storyboard"


def test_create_fake_subtitle_draft_with_selected_storyboard_without_scenes_returns_409(client: TestClient):
    project_id, _, storyboard = prepare_project_for_subtitles(client)
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute("DELETE FROM storyboard_scenes WHERE storyboard_draft_id = ?", (storyboard["id"],))

    response = create_subtitle_draft(client, project_id)

    assert response.status_code == 409
    assert response.json()["detail"] == "selected storyboard has no scenes"


def test_create_fake_subtitle_draft_for_archived_project_returns_409(client: TestClient):
    project_id, _, _ = prepare_project_for_subtitles(client)
    client.post(f"/api/projects/{project_id}/archive")

    response = create_subtitle_draft(client, project_id)

    assert response.status_code == 409


def test_create_fake_subtitle_draft_for_missing_project_returns_404(client: TestClient):
    response = create_subtitle_draft(client, 999)

    assert response.status_code == 404


def test_create_fake_subtitle_draft_rejects_generator_override(client: TestClient):
    project_id, _, _ = prepare_project_for_subtitles(client)

    response = create_subtitle_draft(client, project_id, {"generator_name": "real_subtitle_generator"})

    assert response.status_code == 422


def test_list_subtitle_drafts_returns_persisted_data(client: TestClient):
    project_id, _, _ = prepare_project_for_subtitles(client)
    created = create_subtitle_draft(client, project_id).json()

    response = client.get(f"/api/projects/{project_id}/subtitle-drafts")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == created["id"]
    assert body[0]["cues"][0]["subtitle_draft_id"] == created["id"]


def test_get_single_subtitle_draft_success(client: TestClient):
    project_id, _, _ = prepare_project_for_subtitles(client)
    created = create_subtitle_draft(client, project_id).json()

    response = client.get(f"/api/projects/{project_id}/subtitle-drafts/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["cues"]


def test_get_subtitle_draft_from_another_project_returns_404(client: TestClient):
    first_project_id, _, _ = prepare_project_for_subtitles(client)
    second_project_id, _, _ = prepare_project_for_subtitles(client)
    created = create_subtitle_draft(client, first_project_id).json()

    response = client.get(f"/api/projects/{second_project_id}/subtitle-drafts/{created['id']}")

    assert response.status_code == 404


def test_get_missing_subtitle_draft_returns_404(client: TestClient):
    project_id, _, _ = prepare_project_for_subtitles(client)

    response = client.get(f"/api/projects/{project_id}/subtitle-drafts/999")

    assert response.status_code == 404


def test_archived_project_can_list_and_read_existing_subtitle_drafts(client: TestClient):
    project_id, _, _ = prepare_project_for_subtitles(client)
    created = create_subtitle_draft(client, project_id).json()
    client.post(f"/api/projects/{project_id}/archive")

    list_response = client.get(f"/api/projects/{project_id}/subtitle-drafts")
    read_response = client.get(f"/api/projects/{project_id}/subtitle-drafts/{created['id']}")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert read_response.status_code == 200


def test_select_subtitle_draft_success(client: TestClient):
    project_id, _, _ = prepare_project_for_subtitles(client)
    subtitle_draft = create_subtitle_draft(client, project_id).json()

    response = client.post(f"/api/projects/{project_id}/subtitle-drafts/{subtitle_draft['id']}/select")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == subtitle_draft["id"]
    assert body["status"] == "selected"
    assert body["selected_at"] is not None
    assert body["cues"]


def test_only_one_subtitle_draft_can_be_selected_per_project(client: TestClient):
    project_id, _, _ = prepare_project_for_subtitles(client)
    first = create_subtitle_draft(client, project_id).json()
    second = create_subtitle_draft(client, project_id).json()

    client.post(f"/api/projects/{project_id}/subtitle-drafts/{first['id']}/select")
    client.post(f"/api/projects/{project_id}/subtitle-drafts/{second['id']}/select")

    response = client.get(f"/api/projects/{project_id}/subtitle-drafts")
    statuses = {subtitle_draft["id"]: subtitle_draft["status"] for subtitle_draft in response.json()}
    assert statuses[first["id"]] == "draft"
    assert statuses[second["id"]] == "selected"


def test_select_missing_subtitle_draft_returns_404(client: TestClient):
    project_id, _, _ = prepare_project_for_subtitles(client)

    response = client.post(f"/api/projects/{project_id}/subtitle-drafts/999/select")

    assert response.status_code == 404


def test_select_subtitle_draft_from_another_project_returns_404(client: TestClient):
    first_project_id, _, _ = prepare_project_for_subtitles(client)
    second_project_id, _, _ = prepare_project_for_subtitles(client)
    subtitle_draft = create_subtitle_draft(client, first_project_id).json()

    response = client.post(f"/api/projects/{second_project_id}/subtitle-drafts/{subtitle_draft['id']}/select")

    assert response.status_code == 404


def test_archived_project_cannot_select_subtitle_draft(client: TestClient):
    project_id, _, _ = prepare_project_for_subtitles(client)
    subtitle_draft = create_subtitle_draft(client, project_id).json()
    client.post(f"/api/projects/{project_id}/archive")

    response = client.post(f"/api/projects/{project_id}/subtitle-drafts/{subtitle_draft['id']}/select")

    assert response.status_code == 409


def test_list_subtitle_drafts_for_missing_project_returns_404(client: TestClient):
    response = client.get("/api/projects/999/subtitle-drafts")

    assert response.status_code == 404
