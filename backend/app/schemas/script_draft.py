from pydantic import BaseModel, ConfigDict, Field


class ScriptDraftGenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    script_count: int = Field(default=2, ge=1, le=3)


class ScriptGenerationRunResponse(BaseModel):
    id: int
    project_id: int
    selected_topic_candidate_id: int
    provider_name: str
    provider_version: str
    status: str
    requested_script_count: int
    input_material_count: int
    error_message: str | None = None
    created_at: str
    completed_at: str | None = None


class ScriptDraftResponse(BaseModel):
    id: int
    project_id: int
    generation_run_id: int
    topic_candidate_id: int
    title: str
    opening_hook: str
    body: str
    call_to_action: str
    estimated_duration_seconds: int
    rationale: str
    status: str
    selected_at: str | None = None
    created_at: str
    updated_at: str
    source_material_ids: list[int] = Field(default_factory=list)


class ScriptDraftGenerationResponse(BaseModel):
    run: ScriptGenerationRunResponse
    script_drafts: list[ScriptDraftResponse]
