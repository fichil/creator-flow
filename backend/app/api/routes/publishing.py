from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.publishers.fake_publisher import FakePublisherProvider
from app.publishers.publisher import PublishExecutionInput
from app.schemas.publishing import (
    PublicationRecordResponse,
    PublishIntentCreate,
    PublishIntentResponse,
)

router = APIRouter()


@router.post("/{project_id}/publish-intents", response_model=PublishIntentResponse, status_code=status.HTTP_201_CREATED)
def create_publish_intent(project_id: int, payload: PublishIntentCreate, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "create publish intents")
    review_draft = _get_review_draft(db, project_id, payload.review_draft_id)
    if review_draft["review_status"] != "approved":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="review draft must be approved before creating a publish intent",
        )

    row = db.execute(
        """
        INSERT INTO publish_intents (
            project_id, review_draft_id, target_platform, title, caption, publish_status
        )
        VALUES (?, ?, ?, ?, ?, 'pending_confirmation')
        RETURNING id, project_id, review_draft_id, target_platform, title, caption,
                  publish_status, created_at, updated_at
        """,
        (
            project_id,
            review_draft["id"],
            _required_text(payload.target_platform, "target_platform"),
            _required_text(payload.title, "title"),
            _required_text(payload.caption, "caption"),
        ),
    ).fetchone()
    db.commit()
    return dict(row)


@router.get("/{project_id}/publish-intents", response_model=list[PublishIntentResponse])
def list_publish_intents(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    rows = db.execute(
        """
        SELECT id, project_id, review_draft_id, target_platform, title, caption,
               publish_status, created_at, updated_at
        FROM publish_intents
        WHERE project_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (project_id,),
    ).fetchall()
    return [dict(row) for row in rows]


@router.get("/{project_id}/publish-intents/{publish_intent_id}", response_model=PublishIntentResponse)
def get_publish_intent(project_id: int, publish_intent_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return _get_publish_intent(db, project_id, publish_intent_id)


@router.post("/{project_id}/publish-intents/{publish_intent_id}/cancel", response_model=PublishIntentResponse)
def cancel_publish_intent(project_id: int, publish_intent_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "cancel publish intents")
    publish_intent = _get_publish_intent(db, project_id, publish_intent_id)
    if publish_intent["publish_status"] == "cancelled":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="publish intent is already cancelled")
    if publish_intent["publish_status"] != "pending_confirmation":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="only pending publish intents can be cancelled",
        )

    db.execute(
        """
        UPDATE publish_intents
        SET publish_status = 'cancelled', updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ?
        """,
        (publish_intent_id, project_id),
    )
    db.commit()
    return _get_publish_intent(db, project_id, publish_intent_id)


@router.post("/{project_id}/publish-intents/{publish_intent_id}/confirm", response_model=PublishIntentResponse)
def confirm_publish_intent(project_id: int, publish_intent_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "confirm publish intents")
    publish_intent = _get_publish_intent(db, project_id, publish_intent_id)
    if publish_intent["publish_status"] == "cancelled":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="cancelled publish intent cannot be confirmed")
    if publish_intent["publish_status"] == "confirmed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="publish intent is already confirmed")
    if publish_intent["publish_status"] != "pending_confirmation":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="only pending publish intents can be confirmed",
        )

    db.execute(
        """
        UPDATE publish_intents
        SET publish_status = 'confirmed', updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ?
        """,
        (publish_intent_id, project_id),
    )
    db.execute(
        """
        INSERT INTO publication_records (
            project_id, publish_intent_id, target_platform, provider_name,
            external_publication_id, publication_status, error_message
        )
        VALUES (?, ?, ?, 'placeholder', NULL, 'not_started', NULL)
        """,
        (project_id, publish_intent_id, publish_intent["target_platform"]),
    )
    db.commit()
    return _get_publish_intent(db, project_id, publish_intent_id)


@router.post(
    "/{project_id}/publish-intents/{publish_intent_id}/fake-publish",
    response_model=PublicationRecordResponse,
)
def fake_publish_intent(project_id: int, publish_intent_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "fake publish")
    publish_intent = _get_publish_intent(db, project_id, publish_intent_id)
    if publish_intent["publish_status"] != "confirmed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="only confirmed publish intents can be fake published",
        )

    publication_record = _get_executable_publication_record(db, project_id, publish_intent_id)
    provider = FakePublisherProvider()
    result = provider.execute(
        PublishExecutionInput(
            project_id=project_id,
            publish_intent_id=publish_intent_id,
            publication_record_id=publication_record["id"],
            target_platform=publish_intent["target_platform"],
            title=publish_intent["title"],
            caption=publish_intent["caption"],
        )
    )
    db.execute(
        """
        UPDATE publication_records
        SET provider_name = ?, external_publication_id = ?, publication_status = ?,
            error_message = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ? AND publish_intent_id = ?
        """,
        (
            result.provider_name,
            result.external_publication_id,
            result.publication_status,
            result.error_message,
            publication_record["id"],
            project_id,
            publish_intent_id,
        ),
    )
    db.commit()
    return _get_publication_record(db, project_id, publication_record["id"])


@router.get(
    "/{project_id}/publish-intents/{publish_intent_id}/publication-records",
    response_model=list[PublicationRecordResponse],
)
def list_publication_records(project_id: int, publish_intent_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    _get_publish_intent(db, project_id, publish_intent_id)
    rows = db.execute(
        """
        SELECT id, project_id, publish_intent_id, target_platform, provider_name,
               external_publication_id, publication_status, error_message, created_at, updated_at
        FROM publication_records
        WHERE project_id = ? AND publish_intent_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (project_id, publish_intent_id),
    ).fetchall()
    return [dict(row) for row in rows]


def _get_project(db, project_id: int):
    project = db.execute(
        """
        SELECT id, title, description, status
        FROM content_projects
        WHERE id = ?
        """,
        (project_id,),
    ).fetchone()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project not found")
    return project


def _ensure_project_mutable(project, action: str) -> None:
    if project["status"] == "archived":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"archived project cannot {action}",
        )


def _get_review_draft(db, project_id: int, review_draft_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, review_status
        FROM review_drafts
        WHERE id = ? AND project_id = ?
        """,
        (review_draft_id, project_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="review draft not found")
    return dict(row)


def _get_publish_intent(db, project_id: int, publish_intent_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, review_draft_id, target_platform, title, caption,
               publish_status, created_at, updated_at
        FROM publish_intents
        WHERE id = ? AND project_id = ?
        """,
        (publish_intent_id, project_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="publish intent not found")
    return dict(row)


def _get_executable_publication_record(db, project_id: int, publish_intent_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, publish_intent_id, target_platform, provider_name,
               external_publication_id, publication_status, error_message, created_at, updated_at
        FROM publication_records
        WHERE project_id = ? AND publish_intent_id = ? AND publication_status = 'not_started'
        ORDER BY created_at DESC, id DESC
        LIMIT 1
        """,
        (project_id, publish_intent_id),
    ).fetchone()
    if row is not None:
        return dict(row)

    existing = db.execute(
        """
        SELECT publication_status
        FROM publication_records
        WHERE project_id = ? AND publish_intent_id = ?
        ORDER BY created_at DESC, id DESC
        LIMIT 1
        """,
        (project_id, publish_intent_id),
    ).fetchone()
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="publication record not found; confirm publish intent first",
        )
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="publication record has already been executed",
    )


def _get_publication_record(db, project_id: int, publication_record_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, publish_intent_id, target_platform, provider_name,
               external_publication_id, publication_status, error_message, created_at, updated_at
        FROM publication_records
        WHERE id = ? AND project_id = ?
        """,
        (publication_record_id, project_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="publication record not found")
    return dict(row)


def _required_text(value: str | None, field_name: str) -> str:
    if value is None or not value.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{field_name} is required")
    return value.strip()
