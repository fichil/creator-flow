from pydantic import BaseModel


class ProviderCredentialReferenceResponse(BaseModel):
    provider_id: str
    provider_name: str
    source_type: str
    implementation_status: str
    reference_kind: str
    reference_status: str
    storage_status: str
    redaction_policy_status: str
    is_available: bool
    is_real_provider: bool
    requires_user_authorization: bool
    safe_display_name: str
    safe_status_message: str
    boundary_notes: list[str]
    last_status_change_reason: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class ProviderCredentialReferenceListResponse(BaseModel):
    credential_references: list[ProviderCredentialReferenceResponse]
