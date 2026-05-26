from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.schemas.project import ProjectCreate, ProjectDetailResponse, ProjectResponse, ProjectUpdate

router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
def list_projects(include_archived: bool = False, db=Depends(get_db)):
    rows = db.execute(
        """
        SELECT content_projects.id, content_projects.title, content_projects.description,
               content_projects.status, content_projects.created_at, content_projects.updated_at,
               COUNT(user_materials.id) AS material_count
        FROM content_projects
        LEFT JOIN user_materials ON user_materials.project_id = content_projects.id
        WHERE (? OR content_projects.status != 'archived')
        GROUP BY content_projects.id
        ORDER BY content_projects.created_at DESC, content_projects.id DESC
        """,
        (include_archived,),
    ).fetchall()
    return [dict(row) for row in rows]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db=Depends(get_db)):
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="title is required")

    row = db.execute(
        """
        INSERT INTO content_projects (title, description)
        VALUES (?, ?)
        RETURNING id, title, description, status, created_at, updated_at
        """,
        (title, payload.description.strip() if payload.description else None),
    ).fetchone()
    db.commit()
    return dict(row)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, payload: ProjectUpdate, db=Depends(get_db)):
    project = _get_project(db, project_id)
    updates = payload.model_dump(exclude_unset=True)

    title = project["title"]
    description = project["description"]
    if "title" in updates:
        if updates["title"] is None or not updates["title"].strip():
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="title is required")
        title = updates["title"].strip()
    if "description" in updates:
        description = updates["description"].strip() if updates["description"] else None

    db.execute(
        """
        UPDATE content_projects
        SET title = ?, description = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (title, description, project_id),
    )
    db.commit()
    return _get_project(db, project_id)


@router.post("/{project_id}/archive", response_model=ProjectResponse)
def archive_project(project_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    db.execute(
        """
        UPDATE content_projects
        SET status = 'archived', updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND status != 'archived'
        """,
        (project_id,),
    )
    db.commit()
    return _get_project(db, project_id)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(project_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)

    materials = db.execute(
        """
        SELECT id, project_id, material_type, title, text_content, source_url,
               stored_file_path, original_file_name, created_at
        FROM user_materials
        WHERE project_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (project_id,),
    ).fetchall()

    project_payload = dict(project)
    project_payload["materials"] = [dict(row) for row in materials]
    return project_payload


def _get_project(db, project_id: int):
    project = db.execute(
        """
        SELECT content_projects.id, content_projects.title, content_projects.description,
               content_projects.status, content_projects.created_at, content_projects.updated_at,
               COUNT(user_materials.id) AS material_count
        FROM content_projects
        LEFT JOIN user_materials ON user_materials.project_id = content_projects.id
        WHERE content_projects.id = ?
        GROUP BY content_projects.id
        """,
        (project_id,),
    ).fetchone()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project not found")
    return dict(project)
