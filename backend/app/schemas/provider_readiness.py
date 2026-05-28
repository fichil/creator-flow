from typing import Any

from pydantic import BaseModel


class ProviderBoundaryReadinessItemResponse(BaseModel):
    boundary_id: str
    boundary_name: str
    readiness_status: str
    is_blocking_real_integration: bool
    safe_status_message: str
    source_metadata: dict[str, Any]


class ProviderReadinessSummaryResponse(BaseModel):
    provider_id: str
    provider_name: str
    source_type: str
    implementation_status: str
    is_available: bool
    is_real_provider: bool
    requires_user_authorization: bool
    overall_readiness_status: str
    v0_9_poc_readiness_status: str
    can_use_local_fake_workflow: bool
    is_safe_to_attempt_real_oauth: bool
    is_safe_to_store_tokens: bool
    is_safe_to_fetch_real_metrics: bool
    is_safe_to_publish: bool
    is_ready_for_v0_9_sandbox_poc: bool
    is_ready_for_v0_9_real_poc: bool
    readiness_items: list[ProviderBoundaryReadinessItemResponse]
    blocking_reasons: list[str]
    next_safe_steps: list[str]
    safe_summary: str
    boundary_notes: list[str]


class ProviderReadinessSummaryListResponse(BaseModel):
    readiness_summaries: list[ProviderReadinessSummaryResponse]
