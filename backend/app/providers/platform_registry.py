from dataclasses import dataclass
from enum import Enum


class ProviderType(str, Enum):
    PLATFORM = "platform"


class SourceType(str, Enum):
    FAKE_LOCAL = "fake_local"
    SANDBOX = "sandbox"
    REAL = "real"


class ProviderConnectionStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    NOT_CONNECTED = "not_connected"
    CONNECTED = "connected"
    AUTHORIZATION_FAILED = "authorization_failed"
    TOKEN_EXPIRED = "token_expired"
    PERMISSION_DENIED = "permission_denied"
    PROVIDER_ERROR = "provider_error"


class ProviderImplementationStatus(str, Enum):
    AVAILABLE_LOCAL_FAKE = "available_local_fake"
    PLANNED = "planned"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ProviderCapabilityMetadata:
    supports_oauth: bool
    supports_metrics_read: bool
    supports_publish_prepare: bool
    supports_real_publish: bool
    supports_sandbox: bool
    supports_token_refresh: bool
    supports_disconnect: bool
    supports_revoke: bool


@dataclass(frozen=True)
class PlatformProviderDescriptor:
    provider_id: str
    provider_name: str
    provider_type: ProviderType
    source_type: SourceType
    implementation_status: ProviderImplementationStatus
    connection_status: ProviderConnectionStatus
    is_available: bool
    is_real_provider: bool
    requires_user_authorization: bool
    capabilities: ProviderCapabilityMetadata
    boundary_notes: list[str]


_PLATFORM_PROVIDERS: tuple[PlatformProviderDescriptor, ...] = (
    PlatformProviderDescriptor(
        provider_id="fake_local",
        provider_name="Local Fake Provider",
        provider_type=ProviderType.PLATFORM,
        source_type=SourceType.FAKE_LOCAL,
        implementation_status=ProviderImplementationStatus.AVAILABLE_LOCAL_FAKE,
        connection_status=ProviderConnectionStatus.NOT_REQUIRED,
        is_available=True,
        is_real_provider=False,
        requires_user_authorization=False,
        capabilities=ProviderCapabilityMetadata(
            supports_oauth=False,
            supports_metrics_read=True,
            supports_publish_prepare=True,
            supports_real_publish=False,
            supports_sandbox=False,
            supports_token_refresh=False,
            supports_disconnect=False,
            supports_revoke=False,
        ),
        boundary_notes=[
            "local fake/demo/test data only",
            "not real Douyin data",
            "no OAuth required",
            "no token stored",
        ],
    ),
    PlatformProviderDescriptor(
        provider_id="douyin_sandbox",
        provider_name="Douyin Sandbox Placeholder",
        provider_type=ProviderType.PLATFORM,
        source_type=SourceType.SANDBOX,
        implementation_status=ProviderImplementationStatus.PLANNED,
        connection_status=ProviderConnectionStatus.NOT_CONNECTED,
        is_available=False,
        is_real_provider=False,
        requires_user_authorization=True,
        capabilities=ProviderCapabilityMetadata(
            supports_oauth=False,
            supports_metrics_read=False,
            supports_publish_prepare=False,
            supports_real_publish=False,
            supports_sandbox=True,
            supports_token_refresh=False,
            supports_disconnect=False,
            supports_revoke=False,
        ),
        boundary_notes=[
            "placeholder only",
            "OAuth is not implemented",
            "tokens are not stored",
            "no real Douyin API call",
            "cannot be treated as douyin_real",
        ],
    ),
    PlatformProviderDescriptor(
        provider_id="douyin_real",
        provider_name="Douyin Real Placeholder",
        provider_type=ProviderType.PLATFORM,
        source_type=SourceType.REAL,
        implementation_status=ProviderImplementationStatus.PLANNED,
        connection_status=ProviderConnectionStatus.NOT_CONNECTED,
        is_available=False,
        is_real_provider=True,
        requires_user_authorization=True,
        capabilities=ProviderCapabilityMetadata(
            supports_oauth=False,
            supports_metrics_read=False,
            supports_publish_prepare=False,
            supports_real_publish=False,
            supports_sandbox=False,
            supports_token_refresh=False,
            supports_disconnect=False,
            supports_revoke=False,
        ),
        boundary_notes=[
            "future real provider placeholder only",
            "not real Douyin integration",
            "OAuth is not implemented",
            "no access token or refresh token storage",
            "no real metrics fetching",
            "no upload / publish / scheduling",
        ],
    ),
)


def list_platform_providers() -> list[PlatformProviderDescriptor]:
    return list(_PLATFORM_PROVIDERS)


def get_platform_provider(provider_id: str) -> PlatformProviderDescriptor | None:
    for provider in _PLATFORM_PROVIDERS:
        if provider.provider_id == provider_id:
            return provider
    return None
