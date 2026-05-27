from pydantic import BaseModel


class ProviderTokenLifecycleBoundaryResponse(BaseModel):
    provider_id: str
    provider_name: str
    source_type: str
    implementation_status: str
    token_lifecycle_policy_status: str
    token_storage_policy_status: str
    refresh_policy_status: str
    expiry_policy_status: str
    revoke_policy_status: str
    disconnect_policy_status: str
    rotation_policy_status: str
    error_redaction_policy_status: str
    audit_event_policy_status: str
    is_available: bool
    is_real_provider: bool
    requires_user_authorization: bool
    can_refresh_token: bool
    can_revoke_token: bool
    can_disconnect: bool
    can_rotate_token: bool
    can_mark_token_expired: bool
    safe_status_message: str
    boundary_notes: list[str]
    last_status_change_reason: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class ProviderTokenLifecycleBoundaryListResponse(BaseModel):
    token_lifecycle_boundaries: list[ProviderTokenLifecycleBoundaryResponse]
