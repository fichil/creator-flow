from typing import Any

from pydantic import BaseModel


class ProviderSecurityAuditEventResponse(BaseModel):
    audit_event_id: str
    provider_id: str
    provider_name: str
    source_type: str
    implementation_status: str
    event_type: str
    event_status: str
    event_severity: str
    actor_type: str
    redaction_status: str
    safe_event_message: str
    safe_metadata: dict[str, Any]
    boundary_notes: list[str]
    created_at: str


class ProviderSecurityAuditEventListResponse(BaseModel):
    audit_events: list[ProviderSecurityAuditEventResponse]
