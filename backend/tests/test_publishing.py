import sqlite3

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.publishers.fake_publisher import FakePublisherProvider
from app.publishers.publisher import PublishExecutionInput


def create_project(client: TestClient, title: str = "Publishing project") -> int:
    response = client.post("/api/projects", json={"title": title, "description": "Project description"})
    return response.json()["id"]


def create_content_plan(client: TestClient, project_id: int) -> dict:
    response = client.post(
        f"/api/projects/{project_id}/content-plans",
        json={
            "name": "Weekly AI dev log",
            "account_positioning": "Chinese developer sharing practical AI workflow notes",
            "content_type": "programmer_real_problem",
            "target_frequency_per_week": 3,
            "preferences": '{"tone":"practical","length":"short"}',
        },
    )
    return response.json()


def create_generation_run(client: TestClient, project_id: int, content_plan_id: int) -> dict:
    response = client.post(f"/api/projects/{project_id}/content-plans/{content_plan_id}/generation-runs", json={})
    return response.json()


def add_text_material(client: TestClient, project_id: int) -> int:
    response = client.post(
        f"/api/projects/{project_id}/materials/text",
        json={
            "material_type": "text",
            "title": "Publish intent source material",
            "text_content": "User supplied local material for publish intent tests.",
        },
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


def select_storyboard(client: TestClient, project_id: int) -> int:
    generated = client.post(
        f"/api/projects/{project_id}/storyboards/generate",
        json={"storyboard_count": 1},
    ).json()
    storyboard_id = generated["storyboards"][0]["id"]
    response = client.post(f"/api/projects/{project_id}/storyboards/{storyboard_id}/select")
    return response.json()["id"]


def create_ready_media_artifact(client: TestClient, project_id: int) -> dict:
    add_text_material(client, project_id)
    select_topic_candidate(client, project_id)
    select_script_draft(client, project_id)
    select_storyboard(client, project_id)
    response = client.post(f"/api/projects/{project_id}/renders", json={})
    return response.json()["artifact"]


def prepare_review_draft(client: TestClient, approve: bool = True, media_ready: bool = True):
    project_id = create_project(client)
    content_plan = create_content_plan(client, project_id)
    create_generation_run(client, project_id, content_plan["id"])
    review_draft = client.get(f"/api/projects/{project_id}/review-drafts").json()[0]
    if approve:
        review_draft = client.post(f"/api/projects/{project_id}/review-drafts/{review_draft['id']}/approve").json()
    if media_ready:
        create_ready_media_artifact(client, project_id)
    return project_id, review_draft


def create_publish_intent(
    client: TestClient,
    project_id: int,
    review_draft_id: int,
    payload: dict | None = None,
    *,
    include_confirmation: bool = True,
):
    body = {
        "review_draft_id": review_draft_id,
        "target_platform": "fake_local",
        "title": "Human confirmed publishing draft",
        "caption": "Backend-only publish intent metadata.",
    }
    if include_confirmation:
        body["confirm_publish_intent"] = True
    if payload:
        body.update(payload)
    return client.post(f"/api/projects/{project_id}/publish-intents", json=body)


def insert_legacy_pending_publish_intent(project_id: int, review_draft_id: int, target_platform: str = "fake_local") -> int:
    with sqlite3.connect(get_settings().database_path) as connection:
        row = connection.execute(
            """
            INSERT INTO publish_intents (
                project_id, review_draft_id, target_platform, source_type, title, caption,
                publish_status, confirmation_status, safe_status_message, last_status_change_reason
            )
            VALUES (
                ?, ?, ?, 'fake_local', 'Legacy pending publish intent',
                'Pending local publish intent metadata.', 'pending_confirmation', 'missing',
                'Legacy pending publish intent metadata only.', 'legacy_test_fixture'
            )
            RETURNING id
            """,
            (project_id, review_draft_id, target_platform),
        ).fetchone()
    return row[0]


def confirm_publish_intent(client: TestClient, project_id: int, publish_intent_id: int):
    return client.post(f"/api/projects/{project_id}/publish-intents/{publish_intent_id}/confirm")


def fake_publish_intent(client: TestClient, project_id: int, publish_intent_id: int):
    return client.post(f"/api/projects/{project_id}/publish-intents/{publish_intent_id}/fake-publish")


def test_create_publish_intent_for_approved_review_draft(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)

    response = create_publish_intent(client, project_id, review_draft["id"])

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project_id
    assert body["review_draft_id"] == review_draft["id"]
    assert body["target_platform"] == "fake_local"
    assert body["source_type"] == "fake_local"
    assert body["title"] == "Human confirmed publishing draft"
    assert body["caption"] == "Backend-only publish intent metadata."
    assert body["publish_status"] == "confirmed"
    assert body["confirmation_status"] == "confirmed"
    assert body["confirmed_at"]
    assert body["safe_status_message"] == (
        "Publish intent recorded locally after explicit user confirmation; no provider publish was executed."
    )
    assert body["created_at"]
    assert body["updated_at"]
    assert_no_publication_side_effects(expected_publish_intents=1)


def test_create_publish_intent_rejects_non_approved_review_draft(client: TestClient):
    project_id, review_draft = prepare_review_draft(client, approve=False)

    response = create_publish_intent(client, project_id, review_draft["id"])

    assert response.status_code == 409
    assert response.json()["detail"].startswith("review_not_ready:")
    assert_no_publication_side_effects()


def test_create_publish_intent_rejects_cross_project_review_draft(client: TestClient):
    _, review_draft = prepare_review_draft(client)
    second_project_id = create_project(client, "Second project")

    response = create_publish_intent(client, second_project_id, review_draft["id"])

    assert response.status_code == 404
    assert response.json()["detail"].startswith("review_not_ready:")
    assert_no_publication_side_effects()


def test_archived_project_cannot_create_publish_intent(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    client.post(f"/api/projects/{project_id}/archive")

    response = create_publish_intent(client, project_id, review_draft["id"])

    assert response.status_code == 409
    assert response.json()["detail"] == "archived project cannot create publish intents"
    assert_no_publication_side_effects()


def test_list_and_read_publish_intents(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    first = create_publish_intent(client, project_id, review_draft["id"], {"title": "First publish intent"}).json()

    list_response = client.get(f"/api/projects/{project_id}/publish-intents")
    read_response = client.get(f"/api/projects/{project_id}/publish-intents/{first['id']}")

    assert list_response.status_code == 200
    assert [intent["id"] for intent in list_response.json()] == [first["id"]]
    assert read_response.status_code == 200
    assert read_response.json()["id"] == first["id"]


def test_cross_project_publish_intent_access_returns_404(client: TestClient):
    first_project_id, review_draft = prepare_review_draft(client)
    publish_intent = create_publish_intent(client, first_project_id, review_draft["id"]).json()
    second_project_id = create_project(client, "Second project")

    read_response = client.get(f"/api/projects/{second_project_id}/publish-intents/{publish_intent['id']}")
    cancel_response = client.post(f"/api/projects/{second_project_id}/publish-intents/{publish_intent['id']}/cancel")
    confirm_response = confirm_publish_intent(client, second_project_id, publish_intent["id"])
    records_response = client.get(
        f"/api/projects/{second_project_id}/publish-intents/{publish_intent['id']}/publication-records"
    )

    assert read_response.status_code == 404
    assert read_response.json()["detail"] == "publish intent not found"
    assert cancel_response.status_code == 404
    assert confirm_response.status_code == 404
    assert records_response.status_code == 404


def test_confirm_pending_publish_intent_creates_placeholder_publication_record(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent_id = insert_legacy_pending_publish_intent(project_id, review_draft["id"])

    response = confirm_publish_intent(client, project_id, publish_intent_id)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == publish_intent_id
    assert body["publish_status"] == "confirmed"
    assert body["confirmation_status"] == "confirmed"
    records_response = client.get(
        f"/api/projects/{project_id}/publish-intents/{publish_intent_id}/publication-records"
    )
    assert records_response.status_code == 200
    records = records_response.json()
    assert len(records) == 1
    record = records[0]
    assert record["project_id"] == project_id
    assert record["publish_intent_id"] == publish_intent_id
    assert record["target_platform"] == "fake_local"
    assert record["provider_name"] == "placeholder"
    assert record["external_publication_id"] is None
    assert record["publication_status"] == "not_started"
    assert record["error_message"] is None
    assert_no_publication_side_effects(expected_publish_intents=1, expected_publication_records=1)


def test_confirm_publish_intent_does_not_change_review_draft_status(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent_id = insert_legacy_pending_publish_intent(project_id, review_draft["id"])

    response = confirm_publish_intent(client, project_id, publish_intent_id)
    review_response = client.get(f"/api/projects/{project_id}/review-drafts/{review_draft['id']}")

    assert response.status_code == 200
    assert review_response.status_code == 200
    assert review_response.json()["review_status"] == "approved"
    assert_no_publication_side_effects(expected_publish_intents=1, expected_publication_records=1)


def test_confirmed_publish_intent_cannot_be_confirmed_again(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent = create_publish_intent(client, project_id, review_draft["id"]).json()

    response = confirm_publish_intent(client, project_id, publish_intent["id"])

    assert response.status_code == 409
    assert response.json()["detail"] == "publish intent is already confirmed"
    records = client.get(
        f"/api/projects/{project_id}/publish-intents/{publish_intent['id']}/publication-records"
    ).json()
    assert records == []
    assert_no_publication_side_effects(expected_publish_intents=1)


def test_cancelled_publish_intent_cannot_be_confirmed(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent_id = insert_legacy_pending_publish_intent(project_id, review_draft["id"])
    client.post(f"/api/projects/{project_id}/publish-intents/{publish_intent_id}/cancel")

    response = confirm_publish_intent(client, project_id, publish_intent_id)

    assert response.status_code == 409
    assert response.json()["detail"] == "cancelled publish intent cannot be confirmed"
    assert_no_publication_side_effects(expected_publish_intents=1)


def test_archived_project_cannot_confirm_publish_intent(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent_id = insert_legacy_pending_publish_intent(project_id, review_draft["id"])
    client.post(f"/api/projects/{project_id}/archive")

    response = confirm_publish_intent(client, project_id, publish_intent_id)

    assert response.status_code == 409
    assert response.json()["detail"] == "archived project cannot confirm publish intents"
    assert_no_publication_side_effects(expected_publish_intents=1)


def test_confirm_missing_publish_intent_returns_404(client: TestClient):
    project_id = create_project(client)

    response = confirm_publish_intent(client, project_id, 999)

    assert response.status_code == 404
    assert response.json()["detail"] == "publish intent not found"


def test_fake_publish_confirmed_intent_succeeds_with_local_external_id(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent_id = insert_legacy_pending_publish_intent(project_id, review_draft["id"])
    confirm_publish_intent(client, project_id, publish_intent_id)

    response = fake_publish_intent(client, project_id, publish_intent_id)

    assert response.status_code == 200
    record = response.json()
    assert record["project_id"] == project_id
    assert record["publish_intent_id"] == publish_intent_id
    assert record["target_platform"] == "fake_local"
    assert record["provider_name"] == "fake_publisher"
    assert record["external_publication_id"] == f"fake-publication-{record['id']}"
    assert record["publication_status"] == "succeeded"
    assert record["error_message"] is None
    records = client.get(
        f"/api/projects/{project_id}/publish-intents/{publish_intent_id}/publication-records"
    ).json()
    assert len(records) == 1
    assert records[0]["id"] == record["id"]
    assert records[0]["publication_status"] == "succeeded"
    assert_no_publication_side_effects(expected_publish_intents=1, expected_publication_records=1)


def test_fake_publish_pending_confirmation_intent_is_rejected(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent_id = insert_legacy_pending_publish_intent(project_id, review_draft["id"])

    response = fake_publish_intent(client, project_id, publish_intent_id)

    assert response.status_code == 409
    assert response.json()["detail"] == "only confirmed publish intents can be fake published"
    assert_no_publication_side_effects(expected_publish_intents=1)


def test_fake_publish_cancelled_intent_is_rejected(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent = create_publish_intent(client, project_id, review_draft["id"]).json()
    client.post(f"/api/projects/{project_id}/publish-intents/{publish_intent['id']}/cancel")

    response = fake_publish_intent(client, project_id, publish_intent["id"])

    assert response.status_code == 409
    assert response.json()["detail"] == "only confirmed publish intents can be fake published"
    assert_no_publication_side_effects(expected_publish_intents=1)


def test_fake_publish_succeeded_record_cannot_be_executed_again(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent_id = insert_legacy_pending_publish_intent(project_id, review_draft["id"])
    confirm_publish_intent(client, project_id, publish_intent_id)
    first_response = fake_publish_intent(client, project_id, publish_intent_id)

    response = fake_publish_intent(client, project_id, publish_intent_id)

    assert first_response.status_code == 200
    assert response.status_code == 409
    assert response.json()["detail"] == "publication record has already been executed"
    records = client.get(
        f"/api/projects/{project_id}/publish-intents/{publish_intent_id}/publication-records"
    ).json()
    assert len(records) == 1
    assert records[0]["publication_status"] == "succeeded"
    assert_no_publication_side_effects(expected_publish_intents=1, expected_publication_records=1)


def test_fake_publish_failed_record_cannot_be_executed_again(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent_id = insert_legacy_pending_publish_intent(project_id, review_draft["id"])
    confirm_publish_intent(client, project_id, publish_intent_id)
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            """
            UPDATE publication_records
            SET publication_status = 'failed', error_message = 'local fake failure'
            WHERE publish_intent_id = ?
            """,
            (publish_intent_id,),
        )

    response = fake_publish_intent(client, project_id, publish_intent_id)

    assert response.status_code == 409
    assert response.json()["detail"] == "publication record has already been executed"
    assert_no_publication_side_effects(expected_publish_intents=1, expected_publication_records=1)


def test_archived_project_cannot_fake_publish(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent_id = insert_legacy_pending_publish_intent(project_id, review_draft["id"])
    confirm_publish_intent(client, project_id, publish_intent_id)
    client.post(f"/api/projects/{project_id}/archive")

    response = fake_publish_intent(client, project_id, publish_intent_id)

    assert response.status_code == 409
    assert response.json()["detail"] == "archived project cannot fake publish"
    assert_no_publication_side_effects(expected_publish_intents=1, expected_publication_records=1)


def test_fake_publish_missing_publish_intent_returns_404(client: TestClient):
    project_id = create_project(client)

    response = fake_publish_intent(client, project_id, 999)

    assert response.status_code == 404
    assert response.json()["detail"] == "publish intent not found"


def test_fake_publish_confirmed_intent_without_publication_record_is_rejected(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent = create_publish_intent(client, project_id, review_draft["id"]).json()
    with sqlite3.connect(get_settings().database_path) as connection:
        connection.execute(
            """
            UPDATE publish_intents
            SET publish_status = 'confirmed'
            WHERE id = ?
            """,
            (publish_intent["id"],),
        )

    response = fake_publish_intent(client, project_id, publish_intent["id"])

    assert response.status_code == 409
    assert response.json()["detail"] == "publication record not found; confirm publish intent first"
    assert_no_publication_side_effects(expected_publish_intents=1)


def test_fake_publish_does_not_change_review_draft_status(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent_id = insert_legacy_pending_publish_intent(project_id, review_draft["id"])
    confirm_publish_intent(client, project_id, publish_intent_id)

    response = fake_publish_intent(client, project_id, publish_intent_id)
    review_response = client.get(f"/api/projects/{project_id}/review-drafts/{review_draft['id']}")

    assert response.status_code == 200
    assert review_response.status_code == 200
    assert review_response.json()["review_status"] == "approved"
    assert_no_publication_side_effects(expected_publish_intents=1, expected_publication_records=1)


def test_fake_publisher_provider_is_local_deterministic_and_needs_no_credentials():
    provider = FakePublisherProvider()

    result = provider.execute(
        PublishExecutionInput(
            project_id=1,
            publish_intent_id=2,
            publication_record_id=3,
            target_platform="fake_local",
            title="Local fake title",
            caption="Local fake caption",
        )
    )

    assert provider.provider_name == "fake_publisher"
    assert result.provider_name == "fake_publisher"
    assert result.external_publication_id == "fake-publication-3"
    assert result.publication_status == "succeeded"
    assert result.error_message is None


def test_cancel_publish_intent(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent = create_publish_intent(client, project_id, review_draft["id"]).json()

    response = client.post(f"/api/projects/{project_id}/publish-intents/{publish_intent['id']}/cancel")

    assert response.status_code == 200
    assert response.json()["publish_status"] == "cancelled"
    records_response = client.get(
        f"/api/projects/{project_id}/publish-intents/{publish_intent['id']}/publication-records"
    )
    assert records_response.status_code == 200
    assert records_response.json() == []
    assert_no_publication_side_effects(expected_publish_intents=1)


def test_cancelled_publish_intent_cannot_be_cancelled_again(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent = create_publish_intent(client, project_id, review_draft["id"]).json()
    client.post(f"/api/projects/{project_id}/publish-intents/{publish_intent['id']}/cancel")

    response = client.post(f"/api/projects/{project_id}/publish-intents/{publish_intent['id']}/cancel")

    assert response.status_code == 409
    assert response.json()["detail"] == "publish intent is already cancelled"


def test_archived_project_can_read_but_cannot_cancel_publish_intent(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent = create_publish_intent(client, project_id, review_draft["id"]).json()
    client.post(f"/api/projects/{project_id}/archive")

    list_response = client.get(f"/api/projects/{project_id}/publish-intents")
    read_response = client.get(f"/api/projects/{project_id}/publish-intents/{publish_intent['id']}")
    records_response = client.get(
        f"/api/projects/{project_id}/publish-intents/{publish_intent['id']}/publication-records"
    )
    cancel_response = client.post(f"/api/projects/{project_id}/publish-intents/{publish_intent['id']}/cancel")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert read_response.status_code == 200
    assert records_response.status_code == 200
    assert records_response.json() == []
    assert cancel_response.status_code == 409
    assert cancel_response.json()["detail"] == "archived project cannot cancel publish intents"


def test_publication_records_list_is_empty_for_new_publish_intent(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    publish_intent = create_publish_intent(client, project_id, review_draft["id"]).json()

    response = client.get(f"/api/projects/{project_id}/publish-intents/{publish_intent['id']}/publication-records")

    assert response.status_code == 200
    assert response.json() == []


def test_review_draft_approve_does_not_auto_create_publish_intent(client: TestClient):
    project_id, review_draft = prepare_review_draft(client, approve=False)

    approve_response = client.post(f"/api/projects/{project_id}/review-drafts/{review_draft['id']}/approve")
    publish_intents_response = client.get(f"/api/projects/{project_id}/publish-intents")

    assert approve_response.status_code == 200
    assert approve_response.json()["review_status"] == "approved"
    assert publish_intents_response.status_code == 200
    assert publish_intents_response.json() == []
    assert_no_publication_side_effects()


def test_publish_intent_workflow_does_not_call_real_provider_upload_oauth_or_publish(client: TestClient):
    project_id, review_draft = prepare_review_draft(client)
    create_response = create_publish_intent(client, project_id, review_draft["id"])
    records_response = client.get(
        f"/api/projects/{project_id}/publish-intents/{create_response.json()['id']}/publication-records"
    )

    assert create_response.status_code == 201
    assert create_response.json()["publish_status"] == "confirmed"
    assert records_response.status_code == 200
    assert records_response.json() == []
    assert not get_settings().uploads_dir.exists() or list(get_settings().uploads_dir.rglob("*")) == []
    assert_no_publication_side_effects(expected_publish_intents=1)


def assert_no_publication_side_effects(
    expected_publish_intents: int = 0,
    expected_publication_records: int = 0,
) -> None:
    with sqlite3.connect(get_settings().database_path) as connection:
        counts = {
            "publish_intents": connection.execute("SELECT COUNT(*) FROM publish_intents").fetchone()[0],
            "publication_records": connection.execute("SELECT COUNT(*) FROM publication_records").fetchone()[0],
        }
    assert counts == {
        "publish_intents": expected_publish_intents,
        "publication_records": expected_publication_records,
    }
