from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.schemas.content_plan import ContentPlanCreate, ContentPlanResponse, ContentPlanUpdate

router = APIRouter()


@router.get("/{project_id}/content-plans", response_model=list[ContentPlanResponse])
def list_content_plans(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    rows = db.execute(
        """
        SELECT id, project_id, name, account_positioning, content_type,
               target_frequency_per_week, preferences, is_enabled, created_at, updated_at
        FROM content_plans
        WHERE project_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (project_id,),
    ).fetchall()
    return [dict(row) for row in rows]


@router.post("/{project_id}/content-plans", response_model=ContentPlanResponse, status_code=status.HTTP_201_CREATED)
def create_content_plan(project_id: int, payload: ContentPlanCreate, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "create content plans")

    row = db.execute(
        """
        INSERT INTO content_plans (
            project_id, name, account_positioning, content_type,
            target_frequency_per_week, preferences, is_enabled
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        RETURNING id, project_id, name, account_positioning, content_type,
                  target_frequency_per_week, preferences, is_enabled, created_at, updated_at
        """,
        (
            project_id,
            _required_text(payload.name, "name"),
            _required_text(payload.account_positioning, "account_positioning"),
            _required_text(payload.content_type, "content_type"),
            payload.target_frequency_per_week,
            _optional_text(payload.preferences),
            1 if payload.is_enabled else 0,
        ),
    ).fetchone()
    db.commit()
    return dict(row)


@router.get("/{project_id}/content-plans/{content_plan_id}", response_model=ContentPlanResponse)
def get_content_plan(project_id: int, content_plan_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return _get_content_plan(db, project_id, content_plan_id)


@router.patch("/{project_id}/content-plans/{content_plan_id}", response_model=ContentPlanResponse)
def update_content_plan(project_id: int, content_plan_id: int, payload: ContentPlanUpdate, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "update content plans")
    current = _get_content_plan(db, project_id, content_plan_id)
    updates = payload.model_dump(exclude_unset=True)

    name = current["name"]
    account_positioning = current["account_positioning"]
    content_type = current["content_type"]
    target_frequency_per_week = current["target_frequency_per_week"]
    preferences = current["preferences"]

    if "name" in updates:
        name = _required_text(updates["name"], "name")
    if "account_positioning" in updates:
        account_positioning = _required_text(updates["account_positioning"], "account_positioning")
    if "content_type" in updates:
        content_type = _required_text(updates["content_type"], "content_type")
    if "target_frequency_per_week" in updates:
        target_frequency_per_week = updates["target_frequency_per_week"]
    if "preferences" in updates:
        preferences = _optional_text(updates["preferences"])

    db.execute(
        """
        UPDATE content_plans
        SET name = ?, account_positioning = ?, content_type = ?,
            target_frequency_per_week = ?, preferences = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ?
        """,
        (
            name,
            account_positioning,
            content_type,
            target_frequency_per_week,
            preferences,
            content_plan_id,
            project_id,
        ),
    )
    db.commit()
    return _get_content_plan(db, project_id, content_plan_id)


@router.post("/{project_id}/content-plans/{content_plan_id}/enable", response_model=ContentPlanResponse)
def enable_content_plan(project_id: int, content_plan_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "enable content plans")
    _set_content_plan_enabled(db, project_id, content_plan_id, True)
    return _get_content_plan(db, project_id, content_plan_id)


@router.post("/{project_id}/content-plans/{content_plan_id}/disable", response_model=ContentPlanResponse)
def disable_content_plan(project_id: int, content_plan_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "disable content plans")
    _set_content_plan_enabled(db, project_id, content_plan_id, False)
    return _get_content_plan(db, project_id, content_plan_id)


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


def _get_content_plan(db, project_id: int, content_plan_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, name, account_positioning, content_type,
               target_frequency_per_week, preferences, is_enabled, created_at, updated_at
        FROM content_plans
        WHERE id = ? AND project_id = ?
        """,
        (content_plan_id, project_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="content plan not found")
    return dict(row)


def _set_content_plan_enabled(db, project_id: int, content_plan_id: int, is_enabled: bool) -> None:
    _get_content_plan(db, project_id, content_plan_id)
    db.execute(
        """
        UPDATE content_plans
        SET is_enabled = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ?
        """,
        (1 if is_enabled else 0, content_plan_id, project_id),
    )
    db.commit()


def _required_text(value: str | None, field_name: str) -> str:
    if value is None or not value.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{field_name} is required")
    return value.strip()


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None
