from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.schemas.generation_run import GenerationRunCreate, GenerationRunResponse

router = APIRouter()


@router.get("/{project_id}/generation-runs", response_model=list[GenerationRunResponse])
def list_generation_runs(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    rows = db.execute(
        """
        SELECT id, project_id, content_plan_id, generation_schedule_id, status,
               trigger_type, input_summary, result_summary, error_message,
               created_at, updated_at
        FROM generation_runs
        WHERE project_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (project_id,),
    ).fetchall()
    return [dict(row) for row in rows]


@router.post(
    "/{project_id}/content-plans/{content_plan_id}/generation-runs",
    response_model=GenerationRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_generation_run(
    project_id: int,
    content_plan_id: int,
    payload: GenerationRunCreate | None = None,
    db=Depends(get_db),
):
    payload = payload or GenerationRunCreate()
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "create generation runs")
    content_plan = _get_content_plan(db, project_id, content_plan_id)
    generation_schedule = None
    if payload.generation_schedule_id is not None:
        generation_schedule = _get_generation_schedule(
            db,
            project_id,
            content_plan_id,
            payload.generation_schedule_id,
        )

    input_summary = _build_input_summary(project, content_plan, generation_schedule)
    result_summary = _build_result_summary(content_plan, generation_schedule)
    run = db.execute(
        """
        INSERT INTO generation_runs (
            project_id, content_plan_id, generation_schedule_id, status,
            trigger_type, input_summary
        )
        VALUES (?, ?, ?, 'queued', 'manual', ?)
        RETURNING id
        """,
        (
            project_id,
            content_plan_id,
            generation_schedule["id"] if generation_schedule else None,
            input_summary,
        ),
    ).fetchone()
    db.execute(
        """
        UPDATE generation_runs
        SET status = 'running', updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ?
        """,
        (run["id"], project_id),
    )
    db.execute(
        """
        UPDATE generation_runs
        SET status = 'succeeded', result_summary = ?, error_message = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ?
        """,
        (result_summary, run["id"], project_id),
    )
    db.commit()
    return _get_generation_run(db, project_id, run["id"])


@router.get("/{project_id}/generation-runs/{generation_run_id}", response_model=GenerationRunResponse)
def get_generation_run(project_id: int, generation_run_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return _get_generation_run(db, project_id, generation_run_id)


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
        SELECT id, project_id, name, account_positioning, content_type,
               target_frequency_per_week, preferences, is_enabled
        FROM content_plans
        WHERE id = ? AND project_id = ?
        """,
        (content_plan_id, project_id),
    ).fetchone()
    if content_plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="content plan not found")
    return content_plan


def _get_generation_schedule(db, project_id: int, content_plan_id: int, generation_schedule_id: int):
    generation_schedule = db.execute(
        """
        SELECT id, project_id, content_plan_id, frequency_per_week, timezone,
               preferred_days, preferred_time, is_enabled
        FROM generation_schedules
        WHERE id = ? AND project_id = ? AND content_plan_id = ?
        """,
        (generation_schedule_id, project_id, content_plan_id),
    ).fetchone()
    if generation_schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="generation schedule not found")
    return generation_schedule


def _get_generation_run(db, project_id: int, generation_run_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, content_plan_id, generation_schedule_id, status,
               trigger_type, input_summary, result_summary, error_message,
               created_at, updated_at
        FROM generation_runs
        WHERE id = ? AND project_id = ?
        """,
        (generation_run_id, project_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="generation run not found")
    return dict(row)


def _build_input_summary(project, content_plan, generation_schedule) -> str:
    schedule_summary = "manual run without generation schedule"
    frequency = content_plan["target_frequency_per_week"]
    if generation_schedule is not None:
        frequency = generation_schedule["frequency_per_week"]
        schedule_summary = (
            f"generation_schedule_id={generation_schedule['id']}; "
            f"timezone={generation_schedule['timezone']}; "
            f"preferred_days={generation_schedule['preferred_days'] or 'none'}; "
            f"preferred_time={generation_schedule['preferred_time']}"
        )
    return (
        f"manual trigger for project_id={project['id']}; "
        f"content_plan_id={content_plan['id']}; "
        f"content_type={content_plan['content_type']}; "
        f"frequency_per_week={frequency}; "
        f"{schedule_summary}; "
        "source=explicit ContentPlan and optional GenerationSchedule configuration only"
    )


def _build_result_summary(content_plan, generation_schedule) -> str:
    schedule_part = (
        f" using generation_schedule_id={generation_schedule['id']}"
        if generation_schedule is not None
        else " without generation schedule"
    )
    return (
        f"deterministic fake manual generation run succeeded for "
        f"content_plan_id={content_plan['id']}{schedule_part}; "
        "no topic candidates, script drafts, storyboards, render jobs, subtitles, media, uploads, or publications were created"
    )
