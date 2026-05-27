from typing import Literal

from pydantic import BaseModel, ConfigDict


class GenerationRunCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generation_schedule_id: int | None = None
    trigger_type: Literal["manual"] = "manual"


class GenerationRunResponse(BaseModel):
    id: int
    project_id: int
    content_plan_id: int
    generation_schedule_id: int | None = None
    status: str
    trigger_type: str
    input_summary: str
    result_summary: str | None = None
    error_message: str | None = None
    created_at: str
    updated_at: str
