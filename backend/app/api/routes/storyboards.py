from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.providers import (
    SelectedScriptDraft,
    SelectedTopicCandidate,
    StoryboardGenerationInput,
    TopicGenerationMaterial,
    get_llm_provider,
)
from app.schemas.storyboard import StoryboardGenerateRequest, StoryboardGenerationResponse, StoryboardResponse

router = APIRouter()


@router.get("/{project_id}/storyboards", response_model=list[StoryboardResponse])
def list_storyboards(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return _list_storyboards(db, project_id)


@router.post("/{project_id}/storyboards/generate", response_model=StoryboardGenerationResponse)
def generate_storyboards(
    project_id: int,
    payload: StoryboardGenerateRequest | None = None,
    db=Depends(get_db),
):
    payload = payload or StoryboardGenerateRequest()
    project = _get_project(db, project_id)
    if project["status"] == "archived":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="archived project cannot generate storyboards")

    materials = _list_materials(db, project_id)
    if not materials:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="project has no materials")

    topic_candidate = _get_selected_topic_candidate(db, project_id)
    if topic_candidate is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="project has no selected topic candidate")

    script_draft = _get_selected_script_draft(db, project_id)
    if script_draft is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="project has no selected script draft")

    provider = get_llm_provider("fake_llm")
    run = db.execute(
        """
        INSERT INTO storyboard_generation_runs (
            project_id, selected_topic_candidate_id, selected_script_draft_id,
            provider_name, provider_version, status, requested_storyboard_count,
            input_material_count
        )
        VALUES (?, ?, ?, ?, ?, 'running', ?, ?)
        RETURNING id, project_id, selected_topic_candidate_id, selected_script_draft_id,
                  provider_name, provider_version, status, requested_storyboard_count,
                  input_material_count, error_message, created_at, completed_at
        """,
        (
            project_id,
            topic_candidate["id"],
            script_draft["id"],
            provider.provider_name,
            provider.provider_version,
            payload.storyboard_count,
            len(materials),
        ),
    ).fetchone()

    try:
        drafts = provider.generate_storyboard_drafts(
            StoryboardGenerationInput(
                project_title=project["title"],
                project_description=project["description"],
                topic_candidate=SelectedTopicCandidate(
                    id=topic_candidate["id"],
                    title=topic_candidate["title"],
                    angle=topic_candidate["angle"],
                    audience=topic_candidate["audience"],
                    hook=topic_candidate["hook"],
                    rationale=topic_candidate["rationale"],
                ),
                script_draft=SelectedScriptDraft(
                    id=script_draft["id"],
                    title=script_draft["title"],
                    opening_hook=script_draft["opening_hook"],
                    body=script_draft["body"],
                    call_to_action=script_draft["call_to_action"],
                    estimated_duration_seconds=script_draft["estimated_duration_seconds"],
                    rationale=script_draft["rationale"],
                ),
                materials=[
                    TopicGenerationMaterial(
                        id=material["id"],
                        material_type=material["material_type"],
                        title=material["title"],
                        text_content=material["text_content"],
                        source_url=material["source_url"],
                        original_file_name=material["original_file_name"],
                    )
                    for material in materials
                ],
                storyboard_count=payload.storyboard_count,
            )
        )

        storyboard_ids: list[int] = []
        material_ids = [material["id"] for material in materials]
        for draft in drafts:
            if len(draft.scenes) < 2:
                raise ValueError("storyboard draft must include at least two scenes")
            storyboard = db.execute(
                """
                INSERT INTO storyboard_drafts (
                    project_id, generation_run_id, topic_candidate_id, script_draft_id,
                    title, summary, visual_style
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING id
                """,
                (
                    project_id,
                    run["id"],
                    topic_candidate["id"],
                    script_draft["id"],
                    draft.title,
                    draft.summary,
                    draft.visual_style,
                ),
            ).fetchone()
            storyboard_ids.append(storyboard["id"])
            db.executemany(
                """
                INSERT INTO storyboard_scenes (
                    storyboard_draft_id, scene_order, scene_title, narration,
                    visual_description, on_screen_text, estimated_duration_seconds,
                    source_material_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        storyboard["id"],
                        scene_order,
                        scene.scene_title,
                        scene.narration,
                        scene.visual_description,
                        scene.on_screen_text,
                        scene.estimated_duration_seconds,
                        scene.source_material_id,
                    )
                    for scene_order, scene in enumerate(draft.scenes, start=1)
                ],
            )
            db.executemany(
                """
                INSERT INTO storyboard_draft_sources (storyboard_draft_id, material_id)
                VALUES (?, ?)
                """,
                [(storyboard["id"], material_id) for material_id in material_ids],
            )

        run = db.execute(
            """
            UPDATE storyboard_generation_runs
            SET status = 'succeeded', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            RETURNING id, project_id, selected_topic_candidate_id, selected_script_draft_id,
                      provider_name, provider_version, status, requested_storyboard_count,
                      input_material_count, error_message, created_at, completed_at
            """,
            (run["id"],),
        ).fetchone()
        db.commit()
    except Exception as exc:
        db.execute(
            """
            UPDATE storyboard_generation_runs
            SET status = 'failed', error_message = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (str(exc), run["id"]),
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="storyboard generation failed") from exc

    storyboards = _list_storyboards_by_ids(db, storyboard_ids)
    return {"run": dict(run), "storyboards": storyboards}


@router.post("/{project_id}/storyboards/{storyboard_id}/select", response_model=StoryboardResponse)
def select_storyboard(project_id: int, storyboard_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    if project["status"] == "archived":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="archived project cannot select storyboards")

    storyboard = db.execute(
        """
        SELECT id
        FROM storyboard_drafts
        WHERE id = ? AND project_id = ?
        """,
        (storyboard_id, project_id),
    ).fetchone()
    if storyboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="storyboard not found")

    db.execute(
        """
        UPDATE storyboard_drafts
        SET status = 'draft', selected_at = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE project_id = ? AND status = 'selected'
        """,
        (project_id,),
    )
    db.execute(
        """
        UPDATE storyboard_drafts
        SET status = 'selected', selected_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ?
        """,
        (storyboard_id, project_id),
    )
    db.commit()
    return _get_storyboard(db, project_id, storyboard_id)


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


def _get_selected_topic_candidate(db, project_id: int):
    return db.execute(
        """
        SELECT id, title, angle, audience, hook, rationale
        FROM topic_candidates
        WHERE project_id = ? AND status = 'selected'
        ORDER BY selected_at DESC, id DESC
        LIMIT 1
        """,
        (project_id,),
    ).fetchone()


def _get_selected_script_draft(db, project_id: int):
    return db.execute(
        """
        SELECT id, title, opening_hook, body, call_to_action, estimated_duration_seconds, rationale
        FROM script_drafts
        WHERE project_id = ? AND status = 'selected'
        ORDER BY selected_at DESC, id DESC
        LIMIT 1
        """,
        (project_id,),
    ).fetchone()


def _list_materials(db, project_id: int):
    return db.execute(
        """
        SELECT id, material_type, title, text_content, source_url, original_file_name
        FROM user_materials
        WHERE project_id = ?
        ORDER BY created_at ASC, id ASC
        """,
        (project_id,),
    ).fetchall()


def _list_storyboards(db, project_id: int) -> list[dict]:
    rows = db.execute(
        """
        SELECT id, project_id, generation_run_id, topic_candidate_id, script_draft_id,
               title, summary, visual_style, status, selected_at, created_at, updated_at
        FROM storyboard_drafts
        WHERE project_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (project_id,),
    ).fetchall()
    return _attach_sources_and_scenes(db, [dict(row) for row in rows])


def _list_storyboards_by_ids(db, storyboard_ids: list[int]) -> list[dict]:
    if not storyboard_ids:
        return []
    placeholders = ",".join("?" for _ in storyboard_ids)
    rows = db.execute(
        f"""
        SELECT id, project_id, generation_run_id, topic_candidate_id, script_draft_id,
               title, summary, visual_style, status, selected_at, created_at, updated_at
        FROM storyboard_drafts
        WHERE id IN ({placeholders})
        ORDER BY created_at DESC, id DESC
        """,
        storyboard_ids,
    ).fetchall()
    return _attach_sources_and_scenes(db, [dict(row) for row in rows])


def _get_storyboard(db, project_id: int, storyboard_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, generation_run_id, topic_candidate_id, script_draft_id,
               title, summary, visual_style, status, selected_at, created_at, updated_at
        FROM storyboard_drafts
        WHERE id = ? AND project_id = ?
        """,
        (storyboard_id, project_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="storyboard not found")
    return _attach_sources_and_scenes(db, [dict(row)])[0]


def _attach_sources_and_scenes(db, storyboards: list[dict]) -> list[dict]:
    if not storyboards:
        return []
    storyboard_ids = [storyboard["id"] for storyboard in storyboards]
    placeholders = ",".join("?" for _ in storyboard_ids)
    source_rows = db.execute(
        f"""
        SELECT storyboard_draft_id, material_id
        FROM storyboard_draft_sources
        WHERE storyboard_draft_id IN ({placeholders})
        ORDER BY material_id ASC
        """,
        storyboard_ids,
    ).fetchall()
    scene_rows = db.execute(
        f"""
        SELECT id, storyboard_draft_id, scene_order, scene_title, narration,
               visual_description, on_screen_text, estimated_duration_seconds,
               source_material_id, created_at
        FROM storyboard_scenes
        WHERE storyboard_draft_id IN ({placeholders})
        ORDER BY storyboard_draft_id ASC, scene_order ASC, id ASC
        """,
        storyboard_ids,
    ).fetchall()

    source_map = {storyboard_id: [] for storyboard_id in storyboard_ids}
    scene_map = {storyboard_id: [] for storyboard_id in storyboard_ids}
    for row in source_rows:
        source_map[row["storyboard_draft_id"]].append(row["material_id"])
    for row in scene_rows:
        scene_map[row["storyboard_draft_id"]].append(dict(row))
    for storyboard in storyboards:
        storyboard["source_material_ids"] = source_map[storyboard["id"]]
        storyboard["scenes"] = scene_map[storyboard["id"]]
    return storyboards
