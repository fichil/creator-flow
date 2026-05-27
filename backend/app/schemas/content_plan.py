from pydantic import BaseModel, ConfigDict, Field


class ContentPlanCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    account_positioning: str = Field(..., min_length=1)
    content_type: str = Field(..., min_length=1)
    target_frequency_per_week: int = Field(..., ge=1, le=14)
    preferences: str | None = None
    is_enabled: bool = True


class ContentPlanUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    account_positioning: str | None = Field(default=None, min_length=1)
    content_type: str | None = Field(default=None, min_length=1)
    target_frequency_per_week: int | None = Field(default=None, ge=1, le=14)
    preferences: str | None = None


class ContentPlanResponse(BaseModel):
    id: int
    project_id: int
    name: str
    account_positioning: str
    content_type: str
    target_frequency_per_week: int
    preferences: str | None = None
    is_enabled: bool
    created_at: str
    updated_at: str
