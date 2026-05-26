from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.providers import ScriptGenerationInput, SelectedTopicCandidate, TopicGenerationMaterial, get_llm_provider
from app.schemas.script_draft import ScriptDraftGenerateRequest, ScriptDraftGenerationResponse, ScriptDraftResponse

router = APIRouter()


@router.get("/{project_id}/script-drafts", response_model=list[ScriptDraftResponse])
def list_script_drafts(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return _list_script_drafts(db, project_id)


@router.post("/{project_id}/script-drafts/generate", response_model=ScriptDraftGenerationResponse)
def generate_script_drafts(
    project_id: int,
    payload: ScriptDraftGenerateRequest | None = None,
    db=Depends(get_db),
):
    payload = payload or ScriptDraftGenerateRequest()
    project = _get_project(db, project_id)
    if project["status"] == "archived":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="archived project cannot generate script drafts")

    materials = _list_materials(db, project_id)
    if not materials:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="project has no materials")

    topic_candidate = _get_selected_topic_candidate(db, project_id)
    if topic_candidate is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="project has no selected topic candidate")

    provider = get_llm_provider("fake_llm")
    run = db.execute(
        """
        INSERT INTO script_generation_runs (
            project_id, selected_topic_candidate_id, provider_name, provider_version, status,
            requested_script_count, input_material_count
        )
        VALUES (?, ?, ?, ?, 'running', ?, ?)
        RETURNING id, project_id, selected_topic_candidate_id, provider_name, provider_version,
                  status, requested_script_count, input_material_count, error_message,
                  created_at, completed_at
        """,
        (
            project_id,
            topic_candidate["id"],
            provider.provider_name,
            provider.provider_version,
            payload.script_count,
            len(materials),
        ),
    ).fetchone()

    try:
        drafts = provider.generate_script_drafts(
            ScriptGenerationInput(
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
                script_count=payload.script_count,
            )
        )

        script_draft_ids: list[int] = []
        material_ids = [material["id"] for material in materials]
        for draft in drafts:
            script_draft = db.execute(
                """
                INSERT INTO script_drafts (
                    project_id, generation_run_id, topic_candidate_id, title, opening_hook,
                    body, call_to_action, estimated_duration_seconds, rationale
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
                """,
                (
                    project_id,
                    run["id"],
                    topic_candidate["id"],
                    draft.title,
                    draft.opening_hook,
                    draft.body,
                    draft.call_to_action,
                    draft.estimated_duration_seconds,
                    draft.rationale,
                ),
            ).fetchone()
            script_draft_ids.append(script_draft["id"])
            db.executemany(
                """
                INSERT INTO script_draft_sources (script_draft_id, material_id)
                VALUES (?, ?)
                """,
                [(script_draft["id"], material_id) for material_id in material_ids],
            )

        run = db.execute(
            """
            UPDATE script_generation_runs
            SET status = 'succeeded', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            RETURNING id, project_id, selected_topic_candidate_id, provider_name, provider_version,
                      status, requested_script_count, input_material_count, error_message,
                      created_at, completed_at
            """,
            (run["id"],),
        ).fetchone()
        db.commit()
    except Exception as exc:
        db.execute(
            """
            UPDATE script_generation_runs
            SET status = 'failed', error_message = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (str(exc), run["id"]),
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="script generation failed") from exc

    script_drafts = _list_script_drafts_by_ids(db, script_draft_ids)
    return {"run": dict(run), "script_drafts": script_drafts}


@router.post("/{project_id}/script-drafts/{script_draft_id}/select", response_model=ScriptDraftResponse)
def select_script_draft(project_id: int, script_draft_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    if project["status"] == "archived":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="archived project cannot select script drafts")

    script_draft = db.execute(
        """
        SELECT id
        FROM script_drafts
        WHERE id = ? AND project_id = ?
        """,
        (script_draft_id, project_id),
    ).fetchone()
    if script_draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="script draft not found")

    db.execute(
        """
        UPDATE script_drafts
        SET status = 'draft', selected_at = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE project_id = ? AND status = 'selected'
        """,
        (project_id,),
    )
    db.execute(
        """
        UPDATE script_drafts
        SET status = 'selected', selected_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ?
        """,
        (script_draft_id, project_id),
    )
    db.commit()
    return _get_script_draft(db, project_id, script_draft_id)


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


def _list_script_drafts(db, project_id: int) -> list[dict]:
    rows = db.execute(
        """
        SELECT id, project_id, generation_run_id, topic_candidate_id, title, opening_hook,
               body, call_to_action, estimated_duration_seconds, rationale, status,
               selected_at, created_at, updated_at
        FROM script_drafts
        WHERE project_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (project_id,),
    ).fetchall()
    return _attach_sources(db, [dict(row) for row in rows])


def _list_script_drafts_by_ids(db, script_draft_ids: list[int]) -> list[dict]:
    if not script_draft_ids:
        return []
    placeholders = ",".join("?" for _ in script_draft_ids)
    rows = db.execute(
        f"""
        SELECT id, project_id, generation_run_id, topic_candidate_id, title, opening_hook,
               body, call_to_action, estimated_duration_seconds, rationale, status,
               selected_at, created_at, updated_at
        FROM script_drafts
        WHERE id IN ({placeholders})
        ORDER BY created_at DESC, id DESC
        """,
        script_draft_ids,
    ).fetchall()
    return _attach_sources(db, [dict(row) for row in rows])


def _get_script_draft(db, project_id: int, script_draft_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, generation_run_id, topic_candidate_id, title, opening_hook,
               body, call_to_action, estimated_duration_seconds, rationale, status,
               selected_at, created_at, updated_at
        FROM script_drafts
        WHERE id = ? AND project_id = ?
        """,
        (script_draft_id, project_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="script draft not found")
    return _attach_sources(db, [dict(row)])[0]


def _attach_sources(db, script_drafts: list[dict]) -> list[dict]:
    if not script_drafts:
        return []
    script_draft_ids = [script_draft["id"] for script_draft in script_drafts]
    placeholders = ",".join("?" for _ in script_draft_ids)
    rows = db.execute(
        f"""
        SELECT script_draft_id, material_id
        FROM script_draft_sources
        WHERE script_draft_id IN ({placeholders})
        ORDER BY material_id ASC
        """,
        script_draft_ids,
    ).fetchall()

    source_map = {script_draft_id: [] for script_draft_id in script_draft_ids}
    for row in rows:
        source_map[row["script_draft_id"]].append(row["material_id"])
    for script_draft in script_drafts:
        script_draft["source_material_ids"] = source_map[script_draft["id"]]
    return script_drafts
