from pydantic import BaseModel


class ProviderCapabilityMetadataResponse(BaseModel):
    supports_oauth: bool
    supports_metrics_read: bool
    supports_publish_prepare: bool
    supports_real_publish: bool
    supports_sandbox: bool
    supports_token_refresh: bool
    supports_disconnect: bool
    supports_revoke: bool


class PlatformProviderResponse(BaseModel):
    provider_id: str
    provider_name: str
    provider_type: str
    source_type: str
    implementation_status: str
    connection_status: str
    is_available: bool
    is_real_provider: bool
    requires_user_authorization: bool
    capabilities: ProviderCapabilityMetadataResponse
    boundary_notes: list[str]


class ProviderRegistryListResponse(BaseModel):
    providers: list[PlatformProviderResponse]
