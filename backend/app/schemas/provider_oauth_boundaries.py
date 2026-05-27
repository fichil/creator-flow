from pydantic import BaseModel


class ProviderOAuthBoundaryResponse(BaseModel):
    provider_id: str
    provider_name: str
    source_type: str
    implementation_status: str
    oauth_policy_status: str
    state_policy_status: str
    callback_policy_status: str
    csrf_protection_status: str
    redirect_uri_policy_status: str
    token_exchange_policy_status: str
    token_storage_policy_status: str
    error_redaction_policy_status: str
    audit_event_policy_status: str
    is_available: bool
    is_real_provider: bool
    requires_user_authorization: bool
    can_start_oauth: bool
    can_handle_callback: bool
    can_exchange_token: bool
    can_refresh_token: bool
    can_revoke_token: bool
    safe_status_message: str
    boundary_notes: list[str]
    last_status_change_reason: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class ProviderOAuthBoundaryListResponse(BaseModel):
    oauth_boundaries: list[ProviderOAuthBoundaryResponse]
