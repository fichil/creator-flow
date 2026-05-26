from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.schemas.subtitle import SubtitleDraftCreateRequest, SubtitleDraftResponse
from app.subtitles import SubtitleInput, SubtitleScene, get_subtitle_generator

router = APIRouter()


@router.get("/{project_id}/subtitle-drafts", response_model=list[SubtitleDraftResponse])
def list_subtitle_drafts(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return _list_subtitle_drafts(db, project_id)


@router.post("/{project_id}/subtitle-drafts", response_model=SubtitleDraftResponse)
def create_subtitle_draft(
    project_id: int,
    payload: SubtitleDraftCreateRequest | None = None,
    db=Depends(get_db),
):
    payload = payload or SubtitleDraftCreateRequest()
    project = _get_project(db, project_id)
    if project["status"] == "archived":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="archived project cannot create subtitle drafts")

    storyboard = _get_selected_storyboard(db, project_id)
    if storyboard is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="project has no selected storyboard")

    scenes = _list_storyboard_scenes(db, storyboard["id"])
    if not scenes:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="selected storyboard has no scenes")

    generator = get_subtitle_generator("fake_subtitle_generator")
    cues = generator.generate(
        SubtitleInput(
            project_id=project_id,
            project_title=project["title"],
            project_description=project["description"],
            script_draft_id=storyboard["script_draft_id"],
            storyboard_draft_id=storyboard["id"],
            scenes=[
                SubtitleScene(
                    id=scene["id"],
                    scene_order=scene["scene_order"],
                    narration=scene["narration"],
                    estimated_duration_seconds=scene["estimated_duration_seconds"],
                )
                for scene in scenes
            ],
        )
    )
    if not cues:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="selected storyboard has no subtitle cues")

    subtitle_draft = db.execute(
        """
        INSERT INTO subtitle_drafts (
            project_id, script_draft_id, storyboard_draft_id, generator_name, generator_version
        )
        VALUES (?, ?, ?, ?, ?)
        RETURNING id
        """,
        (
            project_id,
            storyboard["script_draft_id"],
            storyboard["id"],
            generator.generator_name,
            generator.generator_version,
        ),
    ).fetchone()
    db.executemany(
        """
        INSERT INTO subtitle_cues (
            subtitle_draft_id, cue_order, start_time_seconds, end_time_seconds, text
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                subtitle_draft["id"],
                cue.cue_order,
                cue.start_time_seconds,
                cue.end_time_seconds,
                cue.text,
            )
            for cue in cues
        ],
    )
    db.commit()
    return _get_subtitle_draft(db, project_id, subtitle_draft["id"])


@router.get("/{project_id}/subtitle-drafts/{subtitle_draft_id}", response_model=SubtitleDraftResponse)
def get_subtitle_draft(project_id: int, subtitle_draft_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return _get_subtitle_draft(db, project_id, subtitle_draft_id)


@router.post("/{project_id}/subtitle-drafts/{subtitle_draft_id}/select", response_model=SubtitleDraftResponse)
def select_subtitle_draft(project_id: int, subtitle_draft_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    if project["status"] == "archived":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="archived project cannot select subtitle drafts")

    subtitle_draft = db.execute(
        """
        SELECT id
        FROM subtitle_drafts
        WHERE id = ? AND project_id = ?
        """,
        (subtitle_draft_id, project_id),
    ).fetchone()
    if subtitle_draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="subtitle draft not found")

    db.execute(
        """
        UPDATE subtitle_drafts
        SET status = 'draft', selected_at = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE project_id = ? AND status = 'selected'
        """,
        (project_id,),
    )
    db.execute(
        """
        UPDATE subtitle_drafts
        SET status = 'selected', selected_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ?
        """,
        (subtitle_draft_id, project_id),
    )
    db.commit()
    return _get_subtitle_draft(db, project_id, subtitle_draft_id)


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
        SELECT id, project_id, script_draft_id
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
        SELECT id, storyboard_draft_id, scene_order, narration, estimated_duration_seconds
        FROM storyboard_scenes
        WHERE storyboard_draft_id = ?
        ORDER BY scene_order ASC, id ASC
        """,
        (storyboard_id,),
    ).fetchall()


def _list_subtitle_drafts(db, project_id: int) -> list[dict]:
    rows = db.execute(
        """
        SELECT id, project_id, script_draft_id, storyboard_draft_id, generator_name,
               generator_version, status, selected_at, created_at, updated_at
        FROM subtitle_drafts
        WHERE project_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (project_id,),
    ).fetchall()
    return _attach_cues(db, [dict(row) for row in rows])


def _get_subtitle_draft(db, project_id: int, subtitle_draft_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, script_draft_id, storyboard_draft_id, generator_name,
               generator_version, status, selected_at, created_at, updated_at
        FROM subtitle_drafts
        WHERE id = ? AND project_id = ?
        """,
        (subtitle_draft_id, project_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="subtitle draft not found")
    return _attach_cues(db, [dict(row)])[0]


def _attach_cues(db, subtitle_drafts: list[dict]) -> list[dict]:
    if not subtitle_drafts:
        return []

    subtitle_draft_ids = [subtitle_draft["id"] for subtitle_draft in subtitle_drafts]
    placeholders = ",".join("?" for _ in subtitle_draft_ids)
    rows = db.execute(
        f"""
        SELECT id, subtitle_draft_id, cue_order, start_time_seconds,
               end_time_seconds, text, created_at
        FROM subtitle_cues
        WHERE subtitle_draft_id IN ({placeholders})
        ORDER BY subtitle_draft_id ASC, cue_order ASC, id ASC
        """,
        subtitle_draft_ids,
    ).fetchall()

    cue_map = {subtitle_draft_id: [] for subtitle_draft_id in subtitle_draft_ids}
    for row in rows:
        cue_map[row["subtitle_draft_id"]].append(dict(row))
    for subtitle_draft in subtitle_drafts:
        subtitle_draft["cues"] = cue_map[subtitle_draft["id"]]
    return subtitle_drafts
