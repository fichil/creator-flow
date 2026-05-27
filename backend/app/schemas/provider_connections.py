from pydantic import BaseModel


class ProviderConnectionStateResponse(BaseModel):
    provider_id: str
    provider_name: str
    source_type: str
    implementation_status: str
    connection_status: str
    authorization_status: str
    sensitive_storage_status: str
    is_available: bool
    is_real_provider: bool
    requires_user_authorization: bool
    can_connect: bool
    can_refresh: bool
    can_revoke: bool
    can_disconnect: bool
    safe_status_message: str
    boundary_notes: list[str]
    last_status_change_reason: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class ProviderConnectionStateListResponse(BaseModel):
    connections: list[ProviderConnectionStateResponse]
