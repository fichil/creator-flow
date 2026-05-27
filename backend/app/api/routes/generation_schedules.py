from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.schemas.generation_schedule import (
    GenerationScheduleCreate,
    GenerationScheduleResponse,
    GenerationScheduleUpdate,
)

router = APIRouter()


@router.get("/{project_id}/generation-schedules", response_model=list[GenerationScheduleResponse])
def list_generation_schedules(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    rows = db.execute(
        """
        SELECT id, project_id, content_plan_id, frequency_per_week, timezone,
               preferred_days, preferred_time, is_enabled, created_at, updated_at
        FROM generation_schedules
        WHERE project_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (project_id,),
    ).fetchall()
    return [dict(row) for row in rows]


@router.post(
    "/{project_id}/content-plans/{content_plan_id}/generation-schedules",
    response_model=GenerationScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_generation_schedule(
    project_id: int,
    content_plan_id: int,
    payload: GenerationScheduleCreate,
    db=Depends(get_db),
):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "create generation schedules")
    content_plan = _get_content_plan(db, project_id, content_plan_id)

    frequency_per_week = payload.frequency_per_week or content_plan["target_frequency_per_week"]
    row = db.execute(
        """
        INSERT INTO generation_schedules (
            project_id, content_plan_id, frequency_per_week, timezone,
            preferred_days, preferred_time, is_enabled
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        RETURNING id, project_id, content_plan_id, frequency_per_week, timezone,
                  preferred_days, preferred_time, is_enabled, created_at, updated_at
        """,
        (
            project_id,
            content_plan_id,
            frequency_per_week,
            _required_text(payload.timezone, "timezone"),
            _optional_text(payload.preferred_days),
            payload.preferred_time,
            1 if payload.is_enabled else 0,
        ),
    ).fetchone()
    db.commit()
    return dict(row)


@router.get("/{project_id}/generation-schedules/{generation_schedule_id}", response_model=GenerationScheduleResponse)
def get_generation_schedule(project_id: int, generation_schedule_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return _get_generation_schedule(db, project_id, generation_schedule_id)


@router.patch("/{project_id}/generation-schedules/{generation_schedule_id}", response_model=GenerationScheduleResponse)
def update_generation_schedule(
    project_id: int,
    generation_schedule_id: int,
    payload: GenerationScheduleUpdate,
    db=Depends(get_db),
):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "update generation schedules")
    current = _get_generation_schedule(db, project_id, generation_schedule_id)
    updates = payload.model_dump(exclude_unset=True)

    frequency_per_week = current["frequency_per_week"]
    timezone_value = current["timezone"]
    preferred_days = current["preferred_days"]
    preferred_time = current["preferred_time"]

    if "frequency_per_week" in updates and updates["frequency_per_week"] is not None:
        frequency_per_week = updates["frequency_per_week"]
    if "timezone" in updates:
        timezone_value = _required_text(updates["timezone"], "timezone")
    if "preferred_days" in updates:
        preferred_days = _optional_text(updates["preferred_days"])
    if "preferred_time" in updates and updates["preferred_time"] is not None:
        preferred_time = updates["preferred_time"]

    db.execute(
        """
        UPDATE generation_schedules
        SET frequency_per_week = ?, timezone = ?, preferred_days = ?,
            preferred_time = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ?
        """,
        (
            frequency_per_week,
            timezone_value,
            preferred_days,
            preferred_time,
            generation_schedule_id,
            project_id,
        ),
    )
    db.commit()
    return _get_generation_schedule(db, project_id, generation_schedule_id)


@router.post("/{project_id}/generation-schedules/{generation_schedule_id}/enable", response_model=GenerationScheduleResponse)
def enable_generation_schedule(project_id: int, generation_schedule_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "enable generation schedules")
    _set_generation_schedule_enabled(db, project_id, generation_schedule_id, True)
    return _get_generation_schedule(db, project_id, generation_schedule_id)


@router.post("/{project_id}/generation-schedules/{generation_schedule_id}/disable", response_model=GenerationScheduleResponse)
def disable_generation_schedule(project_id: int, generation_schedule_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "disable generation schedules")
    _set_generation_schedule_enabled(db, project_id, generation_schedule_id, False)
    return _get_generation_schedule(db, project_id, generation_schedule_id)


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


def _get_content_plan(db, project_id: int, content_plan_id: int):
    content_plan = db.execute(
        """
        SELECT id, project_id, target_frequency_per_week
        FROM content_plans
        WHERE id = ? AND project_id = ?
        """,
        (content_plan_id, project_id),
    ).fetchone()
    if content_plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="content plan not found")
    return content_plan


def _get_generation_schedule(db, project_id: int, generation_schedule_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, content_plan_id, frequency_per_week, timezone,
               preferred_days, preferred_time, is_enabled, created_at, updated_at
        FROM generation_schedules
        WHERE id = ? AND project_id = ?
        """,
        (generation_schedule_id, project_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="generation schedule not found")
    return dict(row)


def _set_generation_schedule_enabled(db, project_id: int, generation_schedule_id: int, is_enabled: bool) -> None:
    _get_generation_schedule(db, project_id, generation_schedule_id)
    db.execute(
        """
        UPDATE generation_schedules
        SET is_enabled = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ?
        """,
        (1 if is_enabled else 0, generation_schedule_id, project_id),
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
