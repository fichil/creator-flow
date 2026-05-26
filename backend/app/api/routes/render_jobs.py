from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import Settings, get_settings
from app.db.database import get_db
from app.renderers import RenderInput, RenderScene, RenderStoryboard, get_renderer
from app.schemas.render_job import RenderCreateRequest, RenderJobResponse

router = APIRouter()


@router.get("/{project_id}/renders", response_model=list[RenderJobResponse])
def list_render_jobs(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return _list_render_jobs(db, project_id)


@router.post("/{project_id}/renders", response_model=RenderJobResponse)
def create_render_job(
    project_id: int,
    payload: RenderCreateRequest | None = None,
    db=Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    payload = payload or RenderCreateRequest()
    project = _get_project(db, project_id)
    if project["status"] == "archived":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="archived project cannot create renders")

    storyboard = _get_selected_storyboard(db, project_id)
    if storyboard is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="project has no selected storyboard")

    scenes = _list_storyboard_scenes(db, storyboard["id"])
    if not scenes:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="selected storyboard has no scenes")

    selected_subtitle_draft = _get_selected_subtitle_draft(db, project_id, storyboard["id"])
    renderer = get_renderer("fake_renderer")
    render_job = db.execute(
        """
        INSERT INTO render_jobs (
            project_id, storyboard_draft_id, renderer_name, renderer_version,
            status, requested_format, requested_aspect_ratio, requested_resolution
        )
        VALUES (?, ?, ?, ?, 'queued', ?, ?, ?)
        RETURNING id, project_id, storyboard_draft_id, renderer_name, renderer_version,
                  status, requested_format, requested_aspect_ratio, requested_resolution,
                  error_message, created_at, started_at, completed_at, updated_at
        """,
        (
            project_id,
            storyboard["id"],
            renderer.renderer_name,
            renderer.renderer_version,
            payload.requested_format,
            payload.requested_aspect_ratio,
            payload.requested_resolution,
        ),
    ).fetchone()

    try:
        render_job = db.execute(
            """
            UPDATE render_jobs
            SET status = 'running', started_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            RETURNING id, project_id, storyboard_draft_id, renderer_name, renderer_version,
                      status, requested_format, requested_aspect_ratio, requested_resolution,
                      error_message, created_at, started_at, completed_at, updated_at
            """,
            (render_job["id"],),
        ).fetchone()
        output = renderer.render(
            RenderInput(
                project_id=project_id,
                render_job_id=render_job["id"],
                selected_subtitle_draft_id=selected_subtitle_draft["id"] if selected_subtitle_draft else None,
                project_title=project["title"],
                project_description=project["description"],
                storyboard=RenderStoryboard(
                    id=storyboard["id"],
                    title=storyboard["title"],
                    summary=storyboard["summary"],
                    visual_style=storyboard["visual_style"],
                ),
                scenes=[
                    RenderScene(
                        id=scene["id"],
                        scene_order=scene["scene_order"],
                        scene_title=scene["scene_title"],
                        narration=scene["narration"],
                        visual_description=scene["visual_description"],
                        on_screen_text=scene["on_screen_text"],
                        estimated_duration_seconds=scene["estimated_duration_seconds"],
                        source_material_id=scene["source_material_id"],
                    )
                    for scene in scenes
                ],
                preview_output_dir=settings.render_previews_dir,
                requested_format=payload.requested_format,
                requested_aspect_ratio=payload.requested_aspect_ratio,
                requested_resolution=payload.requested_resolution,
            )
        )
        db.execute(
            """
            INSERT INTO render_artifacts (
                project_id, render_job_id, subtitle_draft_id, artifact_type, file_name, mime_type,
                file_size_bytes, duration_seconds, width, height, storage_path, checksum_sha256
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                render_job["id"],
                selected_subtitle_draft["id"] if selected_subtitle_draft else None,
                output.artifact_type,
                output.file_name,
                output.mime_type,
                output.file_size_bytes,
                output.duration_seconds,
                output.width,
                output.height,
                output.storage_path,
                output.checksum_sha256,
            ),
        )
        db.execute(
            """
            UPDATE render_jobs
            SET status = 'succeeded', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (render_job["id"],),
        )
        db.commit()
    except Exception as exc:
        db.execute(
            """
            UPDATE render_jobs
            SET status = 'failed', error_message = ?, completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (str(exc), render_job["id"]),
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="render failed") from exc

    return _get_render_job(db, project_id, render_job["id"])


@router.get("/{project_id}/renders/{render_job_id}", response_model=RenderJobResponse)
def get_render_job(project_id: int, render_job_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return _get_render_job(db, project_id, render_job_id)


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


def _get_selected_storyboard(db, project_id: int):
    return db.execute(
        """
        SELECT id, project_id, title, summary, visual_style
        FROM storyboard_drafts
        WHERE project_id = ? AND status = 'selected'
        ORDER BY selected_at DESC, id DESC
        LIMIT 1
        """,
        (project_id,),
    ).fetchone()


def _list_storyboard_scenes(db, storyboard_id: int):
    return db.execute(
        """
        SELECT id, storyboard_draft_id, scene_order, scene_title, narration,
               visual_description, on_screen_text, estimated_duration_seconds,
               source_material_id, created_at
        FROM storyboard_scenes
        WHERE storyboard_draft_id = ?
        ORDER BY scene_order ASC, id ASC
        """,
        (storyboard_id,),
    ).fetchall()


def _get_selected_subtitle_draft(db, project_id: int, storyboard_draft_id: int):
    return db.execute(
        """
        SELECT id, project_id, storyboard_draft_id
        FROM subtitle_drafts
        WHERE project_id = ? AND storyboard_draft_id = ? AND status = 'selected'
        ORDER BY selected_at DESC, id DESC
        LIMIT 1
        """,
        (project_id, storyboard_draft_id),
    ).fetchone()


def _list_render_jobs(db, project_id: int) -> list[dict]:
    rows = db.execute(
        """
        SELECT id, project_id, storyboard_draft_id, renderer_name, renderer_version,
               status, requested_format, requested_aspect_ratio, requested_resolution,
               error_message, created_at, started_at, completed_at, updated_at
        FROM render_jobs
        WHERE project_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (project_id,),
    ).fetchall()
    return _attach_artifacts(db, [dict(row) for row in rows])


def _get_render_job(db, project_id: int, render_job_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, storyboard_draft_id, renderer_name, renderer_version,
               status, requested_format, requested_aspect_ratio, requested_resolution,
               error_message, created_at, started_at, completed_at, updated_at
        FROM render_jobs
        WHERE id = ? AND project_id = ?
        """,
        (render_job_id, project_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="render job not found")
    return _attach_artifacts(db, [dict(row)])[0]


def _attach_artifacts(db, render_jobs: list[dict]) -> list[dict]:
    if not render_jobs:
        return []

    render_job_ids = [render_job["id"] for render_job in render_jobs]
    placeholders = ",".join("?" for _ in render_job_ids)
    artifact_rows = db.execute(
        f"""
        SELECT id, project_id, render_job_id, artifact_type, file_name, mime_type,
               subtitle_draft_id, file_size_bytes, duration_seconds, width, height,
               storage_path, checksum_sha256, created_at
        FROM render_artifacts
        WHERE render_job_id IN ({placeholders})
        ORDER BY id DESC
        """,
        render_job_ids,
    ).fetchall()
    artifact_map = {render_job_id: None for render_job_id in render_job_ids}
    for row in artifact_rows:
        if artifact_map[row["render_job_id"]] is None:
            artifact_map[row["render_job_id"]] = dict(row)

    for render_job in render_jobs:
        render_job["artifact"] = artifact_map[render_job["id"]]
    return render_jobs
