from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.db.database import get_db
from app.publishing import (
    GuardedPublishAttemptError,
    LimitedMetricsReadError,
    PublishIntentWorkflowError,
    PublishStatusReconciliationError,
    create_guarded_publish_attempt,
    create_limited_metrics_snapshot,
    create_local_publish_intent,
    create_publish_status_reconciliation,
    get_guarded_publish_attempt,
    get_limited_metrics_snapshot,
    get_publish_status_reconciliation,
    list_guarded_publish_attempts,
    list_limited_metrics_snapshots,
    list_publish_status_reconciliations,
    list_publish_status_snapshots,
)
from app.publishers.fake_publisher import FakePublisherProvider
from app.publishers.publisher import PublishExecutionInput
from app.schemas.publishing import (
    MetricsSnapshotCreate,
    PublicationRecordResponse,
    PublishAttemptResponse,
    PublishIntentCreate,
    PublishIntentResponse,
    PublishMetricsSnapshotResponse,
    PublishStatusReconciliationCreate,
    PublishStatusReconciliationResponse,
    PublishStatusSnapshotResponse,
)

router = APIRouter()


@router.post("/{project_id}/publish-intents", response_model=PublishIntentResponse, status_code=status.HTTP_201_CREATED)
def create_publish_intent(project_id: int, payload: PublishIntentCreate, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "create publish intents")
    try:
        return create_local_publish_intent(
            db,
            project_id=project_id,
            review_draft_id=payload.review_draft_id,
            provider_id=payload.target_platform,
            title=payload.title,
            caption=payload.caption,
            confirm_publish_intent=payload.confirm_publish_intent,
        )
    except PublishIntentWorkflowError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=f"{exc.category}: {exc.safe_status_message}",
        ) from exc


@router.get("/{project_id}/publish-intents", response_model=list[PublishIntentResponse])
def list_publish_intents(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    rows = db.execute(
        """
        SELECT id, project_id, review_draft_id, target_platform, title, caption,
               source_type, publish_status, confirmation_status, created_at, updated_at,
               confirmed_at, cancelled_at, safe_status_message, last_status_change_reason
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
    if publish_intent["publish_status"] not in {"pending_confirmation", "confirmed"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="only active publish intents can be cancelled",
        )

    db.execute(
        """
        UPDATE publish_intents
        SET publish_status = 'cancelled',
            cancelled_at = CURRENT_TIMESTAMP,
            safe_status_message = 'Publish intent cancelled locally; no provider publish was executed.',
            last_status_change_reason = 'publish_intent_cancelled',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ?
        """,
        (publish_intent_id, project_id),
    )
    db.commit()
    return _get_publish_intent(db, project_id, publish_intent_id)


@router.post(
    "/{project_id}/publish-intents/{publish_intent_id}/attempts",
    response_model=PublishAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_publish_attempt(project_id: int, publish_intent_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "create guarded publish attempts")
    try:
        return create_guarded_publish_attempt(
            db,
            project_id=project_id,
            publish_intent_id=publish_intent_id,
        )
    except GuardedPublishAttemptError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=f"{exc.category}: {exc.safe_status_message}",
        ) from exc


@router.get("/{project_id}/publish-attempts", response_model=list[PublishAttemptResponse])
def list_publish_attempts(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return list_guarded_publish_attempts(db, project_id=project_id)


@router.get("/{project_id}/publish-attempts/{publish_attempt_id}", response_model=PublishAttemptResponse)
def get_publish_attempt(project_id: int, publish_attempt_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    try:
        return get_guarded_publish_attempt(
            db,
            project_id=project_id,
            publish_attempt_id=publish_attempt_id,
        )
    except GuardedPublishAttemptError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=f"{exc.category}: {exc.safe_status_message}",
        ) from exc


@router.post(
    "/{project_id}/publish-attempts/{publish_attempt_id}/status-reconciliations",
    response_model=PublishStatusReconciliationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_publish_attempt_status_reconciliation(
    project_id: int,
    publish_attempt_id: int,
    response: Response,
    payload: PublishStatusReconciliationCreate | None = None,
    db=Depends(get_db),
):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "create local publish status reconciliations")
    payload = payload or PublishStatusReconciliationCreate()
    try:
        result = create_publish_status_reconciliation(
            db,
            project_id=project_id,
            publish_attempt_id=publish_attempt_id,
            external_status_query_requested=payload.external_status_query_requested,
            fallback_provider_id=payload.fallback_provider_id,
            fake_status_fixture=payload.fake_status_fixture.model_dump() if payload.fake_status_fixture else None,
        )
    except PublishStatusReconciliationError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=f"{exc.category}: {exc.safe_status_message}",
        ) from exc
    if result.get("result_category") == "stale_status_ignored":
        response.status_code = status.HTTP_200_OK
    return result


@router.get(
    "/{project_id}/publish-status-reconciliations",
    response_model=list[PublishStatusReconciliationResponse],
)
def list_project_publish_status_reconciliations(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return list_publish_status_reconciliations(db, project_id=project_id)


@router.get(
    "/{project_id}/publish-status-reconciliations/{reconciliation_id}",
    response_model=PublishStatusReconciliationResponse,
)
def get_project_publish_status_reconciliation(project_id: int, reconciliation_id: str, db=Depends(get_db)):
    _get_project(db, project_id)
    try:
        return get_publish_status_reconciliation(
            db,
            project_id=project_id,
            reconciliation_id=reconciliation_id,
        )
    except PublishStatusReconciliationError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=f"{exc.category}: {exc.safe_status_message}",
        ) from exc


@router.get(
    "/{project_id}/publish-attempts/{publish_attempt_id}/status-snapshots",
    response_model=list[PublishStatusSnapshotResponse],
)
def list_publish_attempt_status_snapshots(project_id: int, publish_attempt_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    try:
        return list_publish_status_snapshots(
            db,
            project_id=project_id,
            publish_attempt_id=publish_attempt_id,
        )
    except PublishStatusReconciliationError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=f"{exc.category}: {exc.safe_status_message}",
        ) from exc


@router.post(
    "/{project_id}/publish-status-snapshots/{status_snapshot_id}/metrics-snapshots",
    response_model=PublishMetricsSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_publish_status_metrics_snapshot(
    project_id: int,
    status_snapshot_id: str,
    payload: MetricsSnapshotCreate | None = None,
    db=Depends(get_db),
):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "create local limited metrics snapshots")
    payload = payload or MetricsSnapshotCreate()
    try:
        return create_limited_metrics_snapshot(
            db,
            project_id=project_id,
            status_snapshot_id=status_snapshot_id,
            external_metrics_query_requested=payload.external_metrics_query_requested,
            fallback_provider_id=payload.fallback_provider_id,
            metrics_permission_status=payload.metrics_permission_status,
            fake_metrics_fixture=payload.fake_metrics_fixture.model_dump()
            if payload.fake_metrics_fixture
            else None,
        )
    except LimitedMetricsReadError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=f"{exc.category}: {exc.safe_status_message}",
        ) from exc


@router.get(
    "/{project_id}/metrics-snapshots",
    response_model=list[PublishMetricsSnapshotResponse],
)
def list_project_metrics_snapshots(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return list_limited_metrics_snapshots(db, project_id=project_id)


@router.get(
    "/{project_id}/metrics-snapshots/{metrics_snapshot_id}",
    response_model=PublishMetricsSnapshotResponse,
)
def get_project_metrics_snapshot(project_id: int, metrics_snapshot_id: str, db=Depends(get_db)):
    _get_project(db, project_id)
    try:
        return get_limited_metrics_snapshot(
            db,
            project_id=project_id,
            metrics_snapshot_id=metrics_snapshot_id,
        )
    except LimitedMetricsReadError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=f"{exc.category}: {exc.safe_status_message}",
        ) from exc


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
        SET publish_status = 'confirmed',
            confirmation_status = 'confirmed',
            confirmed_at = CURRENT_TIMESTAMP,
            safe_status_message = 'Publish intent confirmed locally; no provider publish was executed.',
            last_status_change_reason = 'legacy_pending_publish_intent_confirmed',
            updated_at = CURRENT_TIMESTAMP
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


def _get_publish_intent(db, project_id: int, publish_intent_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, review_draft_id, target_platform, title, caption,
               source_type, publish_status, confirmation_status, created_at, updated_at,
               confirmed_at, cancelled_at, safe_status_message, last_status_change_reason
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
