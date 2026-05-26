from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class MaterialResponse(BaseModel):
    id: int
    project_id: int
    material_type: str
    title: str | None = None
    text_content: str | None = None
    source_url: str | None = None
    stored_file_path: str | None = None
    original_file_name: str | None = None
    created_at: str


class TextMaterialCreate(BaseModel):
    material_type: Literal["text", "summary", "project_record"]
    title: str | None = None
    text_content: str = Field(..., min_length=1)


class LinkMaterialCreate(BaseModel):
    title: str | None = None
    source_url: HttpUrl
