from pydantic import BaseModel, ConfigDict, Field


PREFERRED_TIME_PATTERN = r"^([01][0-9]|2[0-3]):[0-5][0-9]$"


class GenerationScheduleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frequency_per_week: int | None = Field(default=None, ge=1, le=14)
    timezone: str = Field(default="Asia/Shanghai", min_length=1)
    preferred_days: str | None = None
    preferred_time: str = Field(default="09:00", pattern=PREFERRED_TIME_PATTERN)
    is_enabled: bool = True


class GenerationScheduleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frequency_per_week: int | None = Field(default=None, ge=1, le=14)
    timezone: str | None = Field(default=None, min_length=1)
    preferred_days: str | None = None
    preferred_time: str | None = Field(default=None, pattern=PREFERRED_TIME_PATTERN)


class GenerationScheduleResponse(BaseModel):
    id: int
    project_id: int
    content_plan_id: int
    frequency_per_week: int
    timezone: str
    preferred_days: str | None = None
    preferred_time: str
    is_enabled: bool
    created_at: str
    updated_at: str
