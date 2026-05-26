from pydantic import BaseModel, ConfigDict, Field


class SubtitleDraftCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SubtitleCueResponse(BaseModel):
    id: int
    subtitle_draft_id: int
    cue_order: int
    start_time_seconds: int
    end_time_seconds: int
    text: str
    created_at: str


class SubtitleDraftResponse(BaseModel):
    id: int
    project_id: int
    script_draft_id: int
    storyboard_draft_id: int
    generator_name: str
    generator_version: str
    status: str
    selected_at: str | None = None
    created_at: str
    updated_at: str
    cues: list[SubtitleCueResponse] = Field(default_factory=list)
