from pydantic import BaseModel, ConfigDict, Field


class StoryboardGenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    storyboard_count: int = Field(default=1, ge=1, le=2)


class StoryboardGenerationRunResponse(BaseModel):
    id: int
    project_id: int
    selected_topic_candidate_id: int
    selected_script_draft_id: int
    provider_name: str
    provider_version: str
    status: str
    requested_storyboard_count: int
    input_material_count: int
    error_message: str | None = None
    created_at: str
    completed_at: str | None = None


class StoryboardSceneResponse(BaseModel):
    id: int
    storyboard_draft_id: int
    scene_order: int
    scene_title: str
    narration: str
    visual_description: str
    on_screen_text: str
    estimated_duration_seconds: int
    source_material_id: int | None = None
    created_at: str


class StoryboardResponse(BaseModel):
    id: int
    project_id: int
    generation_run_id: int
    topic_candidate_id: int
    script_draft_id: int
    title: str
    summary: str
    visual_style: str
    status: str
    selected_at: str | None = None
    created_at: str
    updated_at: str
    source_material_ids: list[int] = Field(default_factory=list)
    scenes: list[StoryboardSceneResponse] = Field(default_factory=list)


class StoryboardGenerationResponse(BaseModel):
    run: StoryboardGenerationRunResponse
    storyboards: list[StoryboardResponse]
