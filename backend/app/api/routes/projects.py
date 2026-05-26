from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.schemas.project import ProjectCreate, ProjectDetailResponse, ProjectResponse

router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
def list_projects(db=Depends(get_db)):
    rows = db.execute(
        """
        SELECT id, title, description, status, created_at, updated_at
        FROM content_projects
        ORDER BY created_at DESC, id DESC
        """
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


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(project_id: int, db=Depends(get_db)):
    project = db.execute(
        """
        SELECT id, title, description, status, created_at, updated_at
        FROM content_projects
        WHERE id = ?
        """,
        (project_id,),
    ).fetchone()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project not found")

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
