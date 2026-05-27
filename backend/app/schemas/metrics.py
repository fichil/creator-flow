from pydantic import BaseModel


class PublicationMetricSnapshotResponse(BaseModel):
    id: int
    project_id: int
    publication_record_id: int
    source: str
    captured_at: str
    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None
    favorites: int | None = None
    average_watch_time_seconds: float | None = None
    completion_rate: float | None = None
    provider_payload_summary: str | None = None
    created_at: str
    updated_at: str
