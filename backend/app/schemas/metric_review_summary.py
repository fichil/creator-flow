from pydantic import BaseModel


class PublicationMetricReviewSummaryResponse(BaseModel):
    id: int
    project_id: int
    publication_record_id: int
    source: str
    is_fake_local: bool
    summary_text: str
    highlights: str
    low_performance_signals: str
    next_observations: str
    snapshot_count: int
    metric_window_start: str | None = None
    metric_window_end: str | None = None
    created_at: str
    updated_at: str
