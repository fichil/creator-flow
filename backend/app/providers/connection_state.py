import sqlite3
from dataclasses import dataclass
from enum import Enum

from app.providers.platform_registry import (
    PlatformProviderDescriptor,
    ProviderConnectionStatus,
    SourceType,
    get_platform_provider,
    list_platform_providers,
)


class ProviderAuthorizationStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    NOT_AUTHORIZED = "not_authorized"
    AUTHORIZED = "authorized"
    AUTHORIZATION_FAILED = "authorization_failed"
    PERMISSION_DENIED = "permission_denied"
    NOT_IMPLEMENTED = "not_implemented"


class SensitiveStorageStatus(str, Enum):
    NONE = "none"
    NOT_CONFIGURED = "not_configured"
    NOT_IMPLEMENTED = "not_implemented"
    REFERENCE_ONLY = "reference_only"
    ENCRYPTED_STORAGE_PLANNED = "encrypted_storage_planned"


@dataclass(frozen=True)
class ProviderConnectionState:
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


def list_provider_connection_states(connection: sqlite3.Connection) -> list[ProviderConnectionState]:
    state_rows = _load_known_state_rows(connection)
    return [
        _merge_provider_state(provider, state_rows.get(provider.provider_id))
        for provider in list_platform_providers()
    ]


def get_provider_connection_state(
    connection: sqlite3.Connection, provider_id: str
) -> ProviderConnectionState | None:
    provider = get_platform_provider(provider_id)
    if provider is None:
        return None

    row = connection.execute(
        """
        SELECT provider_id, connection_status, authorization_status,
               sensitive_storage_status, safe_status_message,
               last_status_change_reason, created_at, updated_at
        FROM provider_connection_states
        WHERE provider_id = ?
        """,
        (provider_id,),
    ).fetchone()
    return _merge_provider_state(provider, row)


def build_default_provider_connection_state(
    provider: PlatformProviderDescriptor,
) -> ProviderConnectionState:
    if provider.source_type == SourceType.FAKE_LOCAL:
        return ProviderConnectionState(
            provider_id=provider.provider_id,
            provider_name=provider.provider_name,
            source_type=provider.source_type.value,
            implementation_status=provider.implementation_status.value,
            connection_status=ProviderConnectionStatus.NOT_REQUIRED.value,
            authorization_status=ProviderAuthorizationStatus.NOT_REQUIRED.value,
            sensitive_storage_status=SensitiveStorageStatus.NONE.value,
            is_available=provider.is_available,
            is_real_provider=provider.is_real_provider,
            requires_user_authorization=provider.requires_user_authorization,
            can_connect=False,
            can_refresh=False,
            can_revoke=False,
            can_disconnect=False,
            safe_status_message="Local fake provider does not require authorization and stores no tokens.",
            boundary_notes=[
                "local fake/demo/test data only",
                "not real Douyin data",
                "no OAuth required",
                "no tokens stored",
                "no external service call",
            ],
        )

    if provider.source_type == SourceType.SANDBOX:
        return ProviderConnectionState(
            provider_id=provider.provider_id,
            provider_name=provider.provider_name,
            source_type=provider.source_type.value,
            implementation_status=provider.implementation_status.value,
            connection_status=ProviderConnectionStatus.NOT_CONNECTED.value,
            authorization_status=ProviderAuthorizationStatus.NOT_IMPLEMENTED.value,
            sensitive_storage_status=SensitiveStorageStatus.NOT_IMPLEMENTED.value,
            is_available=provider.is_available,
            is_real_provider=provider.is_real_provider,
            requires_user_authorization=provider.requires_user_authorization,
            can_connect=False,
            can_refresh=False,
            can_revoke=False,
            can_disconnect=False,
            safe_status_message=(
                "Douyin sandbox is placeholder metadata only; OAuth is not implemented "
                "and tokens are not stored."
            ),
            boundary_notes=[
                "placeholder only",
                "OAuth is not implemented",
                "tokens are not stored",
                "no real Douyin API call",
                "cannot be treated as douyin_real",
            ],
        )

    return ProviderConnectionState(
        provider_id=provider.provider_id,
        provider_name=provider.provider_name,
        source_type=provider.source_type.value,
        implementation_status=provider.implementation_status.value,
        connection_status=ProviderConnectionStatus.NOT_CONNECTED.value,
        authorization_status=ProviderAuthorizationStatus.NOT_IMPLEMENTED.value,
        sensitive_storage_status=SensitiveStorageStatus.NOT_IMPLEMENTED.value,
        is_available=provider.is_available,
        is_real_provider=provider.is_real_provider,
        requires_user_authorization=provider.requires_user_authorization,
        can_connect=False,
        can_refresh=False,
        can_revoke=False,
        can_disconnect=False,
        safe_status_message=(
            "Douyin real provider is a future placeholder only; no OAuth, token storage, "
            "metrics fetching, upload, publish, or scheduling is implemented."
        ),
        boundary_notes=[
            "future real provider placeholder only",
            "not real Douyin integration",
            "OAuth is not implemented",
            "no OAuth implementation",
            "no access token or refresh token storage",
            "no token storage",
            "no real metrics fetching",
            "no upload / publish / scheduling",
        ],
    )


def _load_known_state_rows(connection: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    known_provider_ids = {provider.provider_id for provider in list_platform_providers()}
    rows = connection.execute(
        """
        SELECT provider_id, connection_status, authorization_status,
               sensitive_storage_status, safe_status_message,
               last_status_change_reason, created_at, updated_at
        FROM provider_connection_states
        """
    ).fetchall()
    return {row["provider_id"]: row for row in rows if row["provider_id"] in known_provider_ids}


def _merge_provider_state(
    provider: PlatformProviderDescriptor, row: sqlite3.Row | None
) -> ProviderConnectionState:
    default = build_default_provider_connection_state(provider)
    if row is None:
        return default

    return ProviderConnectionState(
        provider_id=default.provider_id,
        provider_name=default.provider_name,
        source_type=default.source_type,
        implementation_status=default.implementation_status,
        connection_status=row["connection_status"],
        authorization_status=row["authorization_status"],
        sensitive_storage_status=row["sensitive_storage_status"],
        is_available=default.is_available,
        is_real_provider=default.is_real_provider,
        requires_user_authorization=default.requires_user_authorization,
        can_connect=default.can_connect,
        can_refresh=default.can_refresh,
        can_revoke=default.can_revoke,
        can_disconnect=default.can_disconnect,
        safe_status_message=row["safe_status_message"],
        boundary_notes=default.boundary_notes,
        last_status_change_reason=row["last_status_change_reason"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
