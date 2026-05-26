from typing import Literal

from pydantic import BaseModel, ConfigDict


class RenderCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requested_format: Literal["mp4"] = "mp4"
    requested_aspect_ratio: Literal["9:16"] = "9:16"
    requested_resolution: Literal["1080x1920"] = "1080x1920"


class RenderArtifactResponse(BaseModel):
    id: int
    project_id: int
    render_job_id: int
    artifact_type: str
    file_name: str
    mime_type: str
    file_size_bytes: int
    duration_seconds: int
    width: int
    height: int
    storage_path: str
    created_at: str


class RenderJobResponse(BaseModel):
    id: int
    project_id: int
    storyboard_draft_id: int
    renderer_name: str
    renderer_version: str
    status: str
    requested_format: str
    requested_aspect_ratio: str
    requested_resolution: str
    error_message: str | None = None
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    updated_at: str
    artifact: RenderArtifactResponse | None = None
