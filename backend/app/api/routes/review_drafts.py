from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.schemas.review_draft import ReviewDraftResponse

router = APIRouter()


@router.get("/{project_id}/review-drafts", response_model=list[ReviewDraftResponse])
def list_review_drafts(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    rows = db.execute(
        """
        SELECT id, project_id, content_plan_id, generation_schedule_id, generation_run_id,
               title, draft_summary, input_source_summary, hotspot_source_summary,
               review_status, created_at, updated_at
        FROM review_drafts
        WHERE project_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (project_id,),
    ).fetchall()
    return [dict(row) for row in rows]


@router.get("/{project_id}/review-drafts/{review_draft_id}", response_model=ReviewDraftResponse)
def get_review_draft(project_id: int, review_draft_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return _get_review_draft(db, project_id, review_draft_id)


@router.post("/{project_id}/review-drafts/{review_draft_id}/approve", response_model=ReviewDraftResponse)
def approve_review_draft(project_id: int, review_draft_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "approve review drafts")
    return _set_review_status(db, project_id, review_draft_id, "approved")


@router.post("/{project_id}/review-drafts/{review_draft_id}/reject", response_model=ReviewDraftResponse)
def reject_review_draft(project_id: int, review_draft_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "reject review drafts")
    return _set_review_status(db, project_id, review_draft_id, "rejected")


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
        SELECT id, project_id, content_plan_id, generation_schedule_id, generation_run_id,
               title, draft_summary, input_source_summary, hotspot_source_summary,
               review_status, created_at, updated_at
        FROM review_drafts
        WHERE id = ? AND project_id = ?
        """,
        (review_draft_id, project_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="review draft not found")
    return dict(row)


def _set_review_status(db, project_id: int, review_draft_id: int, review_status: str) -> dict:
    _get_review_draft(db, project_id, review_draft_id)
    db.execute(
        """
        UPDATE review_drafts
        SET review_status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ?
        """,
        (review_status, review_draft_id, project_id),
    )
    db.commit()
    return _get_review_draft(db, project_id, review_draft_id)
