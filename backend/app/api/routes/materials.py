from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.config import Settings, get_settings
from app.db.database import get_db
from app.schemas.material import LinkMaterialCreate, MaterialResponse, TextMaterialCreate

router = APIRouter()

ALLOWED_FILE_MATERIAL_TYPES = {"image", "screenshot"}
ALLOWED_IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def _ensure_project_exists(db, project_id: int) -> None:
    row = db.execute("SELECT id FROM content_projects WHERE id = ?", (project_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project not found")


def _mark_materials_ready(db, project_id: int) -> None:
    db.execute(
        """
        UPDATE content_projects
        SET status = 'materials_ready', updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND status = 'draft'
        """,
        (project_id,),
    )


def _safe_filename(filename: str) -> str:
    name = Path(filename).name.strip() or "upload"
    return "".join(char if char.isalnum() or char in {".", "-", "_"} else "_" for char in name)


@router.post("/{project_id}/materials/text", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def add_text_material(project_id: int, payload: TextMaterialCreate, db=Depends(get_db)):
    _ensure_project_exists(db, project_id)
    row = db.execute(
        """
        INSERT INTO user_materials (project_id, material_type, title, text_content)
        VALUES (?, ?, ?, ?)
        RETURNING id, project_id, material_type, title, text_content, source_url,
                  stored_file_path, original_file_name, created_at
        """,
        (
            project_id,
            payload.material_type,
            payload.title.strip() if payload.title else None,
            payload.text_content,
        ),
    ).fetchone()
    _mark_materials_ready(db, project_id)
    db.commit()
    return dict(row)


@router.post("/{project_id}/materials/link", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def add_link_material(project_id: int, payload: LinkMaterialCreate, db=Depends(get_db)):
    _ensure_project_exists(db, project_id)
    row = db.execute(
        """
        INSERT INTO user_materials (project_id, material_type, title, source_url)
        VALUES (?, 'link', ?, ?)
        RETURNING id, project_id, material_type, title, text_content, source_url,
                  stored_file_path, original_file_name, created_at
        """,
        (project_id, payload.title.strip() if payload.title else None, str(payload.source_url)),
    ).fetchone()
    _mark_materials_ready(db, project_id)
    db.commit()
    return dict(row)


@router.post("/{project_id}/materials/file", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def add_file_material(
    project_id: int,
    material_type: str = Form(...),
    title: str | None = Form(None),
    file: UploadFile = File(...),
    db=Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    _ensure_project_exists(db, project_id)
    if material_type not in ALLOWED_FILE_MATERIAL_TYPES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="invalid material_type")
    if file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="unsupported file type")

    project_upload_dir = settings.uploads_dir / str(project_id)
    project_upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = _safe_filename(file.filename or "upload")
    stored_name = f"{uuid4().hex}_{original_name}"
    stored_path = project_upload_dir / stored_name
    relative_path = Path("uploads") / str(project_id) / stored_name

    bytes_written = 0
    with stored_path.open("wb") as output:
        while chunk := await file.read(1024 * 1024):
            bytes_written += len(chunk)
            if bytes_written > MAX_UPLOAD_BYTES:
                output.close()
                stored_path.unlink(missing_ok=True)
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="file too large")
            output.write(chunk)

    row = db.execute(
        """
        INSERT INTO user_materials (
            project_id, material_type, title, stored_file_path, original_file_name
        )
        VALUES (?, ?, ?, ?, ?)
        RETURNING id, project_id, material_type, title, text_content, source_url,
                  stored_file_path, original_file_name, created_at
        """,
        (
            project_id,
            material_type,
            title.strip() if title else None,
            relative_path.as_posix(),
            original_name,
        ),
    ).fetchone()
    _mark_materials_ready(db, project_id)
    db.commit()
    return dict(row)
