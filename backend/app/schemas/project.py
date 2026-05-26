from pydantic import BaseModel, ConfigDict, Field

from app.schemas.material import MaterialResponse


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str | None = None


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    description: str | None = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: str
    created_at: str
    updated_at: str
    material_count: int = 0


class ProjectDetailResponse(ProjectResponse):
    materials: list[MaterialResponse] = Field(default_factory=list)
