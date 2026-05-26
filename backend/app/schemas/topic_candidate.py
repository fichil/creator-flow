from pydantic import BaseModel, ConfigDict, Field


class TopicCandidateGenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_count: int = Field(default=3, ge=1, le=5)


class TopicGenerationRunResponse(BaseModel):
    id: int
    project_id: int
    provider_name: str
    provider_version: str
    status: str
    requested_candidate_count: int
    input_material_count: int
    error_message: str | None = None
    created_at: str
    completed_at: str | None = None


class TopicCandidateResponse(BaseModel):
    id: int
    project_id: int
    generation_run_id: int
    title: str
    angle: str
    audience: str
    hook: str
    rationale: str
    status: str
    selected_at: str | None = None
    created_at: str
    updated_at: str
    source_material_ids: list[int] = Field(default_factory=list)


class TopicCandidateGenerationResponse(BaseModel):
    run: TopicGenerationRunResponse
    candidates: list[TopicCandidateResponse]
