from pydantic import BaseModel


class ReviewDraftResponse(BaseModel):
    id: int
    project_id: int
    content_plan_id: int
    generation_schedule_id: int | None = None
    generation_run_id: int
    title: str
    draft_summary: str
    input_source_summary: str
    hotspot_source_summary: str | None = None
    review_status: str
    created_at: str
    updated_at: str
