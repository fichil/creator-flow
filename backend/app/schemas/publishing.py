from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PublishIntentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_draft_id: int
    target_platform: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    caption: str = Field(..., min_length=1)


class PublishIntentResponse(BaseModel):
    id: int
    project_id: int
    review_draft_id: int
    target_platform: str
    title: str
    caption: str
    publish_status: str
    created_at: str
    updated_at: str


class PublicationRecordResponse(BaseModel):
    id: int
    project_id: int
    publish_intent_id: int
    target_platform: str
    provider_name: str
    external_publication_id: str | None = None
    publication_status: Literal["not_started", "succeeded", "failed"]
    error_message: str | None = None
    created_at: str
    updated_at: str
