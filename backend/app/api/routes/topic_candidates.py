from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.providers import TopicGenerationInput, TopicGenerationMaterial, get_llm_provider
from app.schemas.topic_candidate import (
    TopicCandidateGenerateRequest,
    TopicCandidateGenerationResponse,
    TopicCandidateResponse,
)

router = APIRouter()


@router.get("/{project_id}/topic-candidates", response_model=list[TopicCandidateResponse])
def list_topic_candidates(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    return _list_candidates(db, project_id)


@router.post("/{project_id}/topic-candidates/generate", response_model=TopicCandidateGenerationResponse)
def generate_topic_candidates(
    project_id: int,
    payload: TopicCandidateGenerateRequest | None = None,
    db=Depends(get_db),
):
    payload = payload or TopicCandidateGenerateRequest()
    project = _get_project(db, project_id)
    if project["status"] == "archived":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="archived project cannot generate candidates")

    materials = _list_materials(db, project_id)
    if not materials:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="project has no materials")

    provider = get_llm_provider("fake_llm")
    run = db.execute(
        """
        INSERT INTO topic_generation_runs (
            project_id, provider_name, provider_version, status,
            requested_candidate_count, input_material_count
        )
        VALUES (?, ?, ?, 'running', ?, ?)
        RETURNING id, project_id, provider_name, provider_version, status,
                  requested_candidate_count, input_material_count, error_message,
                  created_at, completed_at
        """,
        (project_id, provider.provider_name, provider.provider_version, payload.candidate_count, len(materials)),
    ).fetchone()

    try:
        drafts = provider.generate_topic_candidates(
            TopicGenerationInput(
                project_title=project["title"],
                project_description=project["description"],
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
                candidate_count=payload.candidate_count,
            )
        )

        candidate_ids: list[int] = []
        material_ids = [material["id"] for material in materials]
        for draft in drafts:
            candidate = db.execute(
                """
                INSERT INTO topic_candidates (
                    project_id, generation_run_id, title, angle, audience, hook, rationale
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING id
                """,
                (project_id, run["id"], draft.title, draft.angle, draft.audience, draft.hook, draft.rationale),
            ).fetchone()
            candidate_ids.append(candidate["id"])
            db.executemany(
                """
                INSERT INTO topic_candidate_sources (candidate_id, material_id)
                VALUES (?, ?)
                """,
                [(candidate["id"], material_id) for material_id in material_ids],
            )

        run = db.execute(
            """
            UPDATE topic_generation_runs
            SET status = 'succeeded', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            RETURNING id, project_id, provider_name, provider_version, status,
                      requested_candidate_count, input_material_count, error_message,
                      created_at, completed_at
            """,
            (run["id"],),
        ).fetchone()
        db.commit()
    except Exception as exc:
        run = db.execute(
            """
            UPDATE topic_generation_runs
            SET status = 'failed', error_message = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            RETURNING id, project_id, provider_name, provider_version, status,
                      requested_candidate_count, input_material_count, error_message,
                      created_at, completed_at
            """,
            (str(exc), run["id"]),
        ).fetchone()
        db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="topic generation failed") from exc

    candidates = _list_candidates_by_ids(db, candidate_ids)
    return {"run": dict(run), "candidates": candidates}


@router.post("/{project_id}/topic-candidates/{candidate_id}/select", response_model=TopicCandidateResponse)
def select_topic_candidate(project_id: int, candidate_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    if project["status"] == "archived":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="archived project cannot select candidates")

    candidate = db.execute(
        """
        SELECT id
        FROM topic_candidates
        WHERE id = ? AND project_id = ?
        """,
        (candidate_id, project_id),
    ).fetchone()
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="candidate not found")

    db.execute(
        """
        UPDATE topic_candidates
        SET status = 'candidate', selected_at = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE project_id = ? AND status = 'selected'
        """,
        (project_id,),
    )
    db.execute(
        """
        UPDATE topic_candidates
        SET status = 'selected', selected_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND project_id = ?
        """,
        (candidate_id, project_id),
    )
    db.commit()
    return _get_candidate(db, project_id, candidate_id)


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


def _list_candidates(db, project_id: int) -> list[dict]:
    rows = db.execute(
        """
        SELECT id, project_id, generation_run_id, title, angle, audience, hook,
               rationale, status, selected_at, created_at, updated_at
        FROM topic_candidates
        WHERE project_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (project_id,),
    ).fetchall()
    return _attach_sources(db, [dict(row) for row in rows])


def _list_candidates_by_ids(db, candidate_ids: list[int]) -> list[dict]:
    if not candidate_ids:
        return []
    placeholders = ",".join("?" for _ in candidate_ids)
    rows = db.execute(
        f"""
        SELECT id, project_id, generation_run_id, title, angle, audience, hook,
               rationale, status, selected_at, created_at, updated_at
        FROM topic_candidates
        WHERE id IN ({placeholders})
        ORDER BY created_at DESC, id DESC
        """,
        candidate_ids,
    ).fetchall()
    return _attach_sources(db, [dict(row) for row in rows])


def _get_candidate(db, project_id: int, candidate_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, generation_run_id, title, angle, audience, hook,
               rationale, status, selected_at, created_at, updated_at
        FROM topic_candidates
        WHERE id = ? AND project_id = ?
        """,
        (candidate_id, project_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="candidate not found")
    return _attach_sources(db, [dict(row)])[0]


def _attach_sources(db, candidates: list[dict]) -> list[dict]:
    if not candidates:
        return []
    candidate_ids = [candidate["id"] for candidate in candidates]
    placeholders = ",".join("?" for _ in candidate_ids)
    rows = db.execute(
        f"""
        SELECT candidate_id, material_id
        FROM topic_candidate_sources
        WHERE candidate_id IN ({placeholders})
        ORDER BY material_id ASC
        """,
        candidate_ids,
    ).fetchall()

    source_map = {candidate_id: [] for candidate_id in candidate_ids}
    for row in rows:
        source_map[row["candidate_id"]].append(row["material_id"])
    for candidate in candidates:
        candidate["source_material_ids"] = source_map[candidate["id"]]
    return candidates
