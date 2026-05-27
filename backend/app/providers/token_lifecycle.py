import sqlite3
from dataclasses import dataclass
from enum import Enum

from app.providers.platform_registry import (
    PlatformProviderDescriptor,
    SourceType,
    get_platform_provider,
    list_platform_providers,
)


class TokenLifecyclePolicyStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PLANNED = "planned"
    NOT_IMPLEMENTED = "not_implemented"
    UNAVAILABLE = "unavailable"


class TokenStoragePolicyStatus(str, Enum):
    NONE = "none"
    PLANNED = "planned"
    NOT_IMPLEMENTED = "not_implemented"
    UNAVAILABLE = "unavailable"


class TokenLifecycleOperationPolicyStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PLANNED = "planned"
    REQUIRED_PLANNED = "required_planned"
    NOT_IMPLEMENTED = "not_implemented"
    UNAVAILABLE = "unavailable"


class ErrorRedactionPolicyStatus(str, Enum):
    ACTIVE = "active"
    PLANNED = "planned"
    NOT_REQUIRED = "not_required"


class AuditEventPolicyStatus(str, Enum):
    METADATA_ONLY = "metadata_only"
    PLANNED = "planned"
    NOT_REQUIRED = "not_required"


@dataclass(frozen=True)
class ProviderTokenLifecycleBoundary:
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


def list_provider_token_lifecycle_boundaries(
    connection: sqlite3.Connection,
) -> list[ProviderTokenLifecycleBoundary]:
    boundary_rows = _load_known_token_lifecycle_boundary_rows(connection)
    return [
        _merge_provider_token_lifecycle_boundary(
            provider, boundary_rows.get(provider.provider_id)
        )
        for provider in list_platform_providers()
    ]


def get_provider_token_lifecycle_boundary(
    connection: sqlite3.Connection, provider_id: str
) -> ProviderTokenLifecycleBoundary | None:
    provider = get_platform_provider(provider_id)
    if provider is None:
        return None

    row = connection.execute(
        """
        SELECT provider_id, token_lifecycle_policy_status,
               token_storage_policy_status, refresh_policy_status,
               expiry_policy_status, revoke_policy_status,
               disconnect_policy_status, rotation_policy_status,
               error_redaction_policy_status, audit_event_policy_status,
               safe_status_message, last_status_change_reason,
               created_at, updated_at
        FROM provider_token_lifecycle_boundaries
        WHERE provider_id = ?
        """,
        (provider_id,),
    ).fetchone()
    return _merge_provider_token_lifecycle_boundary(provider, row)


def build_default_provider_token_lifecycle_boundary(
    provider: PlatformProviderDescriptor,
) -> ProviderTokenLifecycleBoundary:
    if provider.source_type == SourceType.FAKE_LOCAL:
        return ProviderTokenLifecycleBoundary(
            provider_id=provider.provider_id,
            provider_name=provider.provider_name,
            source_type=provider.source_type.value,
            implementation_status=provider.implementation_status.value,
            token_lifecycle_policy_status=TokenLifecyclePolicyStatus.NOT_REQUIRED.value,
            token_storage_policy_status=TokenStoragePolicyStatus.NONE.value,
            refresh_policy_status=TokenLifecycleOperationPolicyStatus.NOT_REQUIRED.value,
            expiry_policy_status=TokenLifecycleOperationPolicyStatus.NOT_REQUIRED.value,
            revoke_policy_status=TokenLifecycleOperationPolicyStatus.NOT_REQUIRED.value,
            disconnect_policy_status=TokenLifecycleOperationPolicyStatus.NOT_REQUIRED.value,
            rotation_policy_status=TokenLifecycleOperationPolicyStatus.NOT_REQUIRED.value,
            error_redaction_policy_status=ErrorRedactionPolicyStatus.ACTIVE.value,
            audit_event_policy_status=AuditEventPolicyStatus.METADATA_ONLY.value,
            is_available=provider.is_available,
            is_real_provider=provider.is_real_provider,
            requires_user_authorization=provider.requires_user_authorization,
            can_refresh_token=False,
            can_revoke_token=False,
            can_disconnect=False,
            can_rotate_token=False,
            can_mark_token_expired=False,
            safe_status_message=(
                "Local fake provider does not require token storage, refresh, "
                "expiry handling, revoke, disconnect, or rotation."
            ),
            boundary_notes=[
                "local fake/demo/test data only",
                "not real Douyin data",
                "OAuth is not required",
                "no token stored",
                "no refresh token stored",
                "no token refresh",
                "no token expiry handling required",
                "no token revoke",
                "no disconnect operation",
                "no external service call",
            ],
        )

    if provider.source_type == SourceType.SANDBOX:
        return ProviderTokenLifecycleBoundary(
            provider_id=provider.provider_id,
            provider_name=provider.provider_name,
            source_type=provider.source_type.value,
            implementation_status=provider.implementation_status.value,
            token_lifecycle_policy_status=TokenLifecyclePolicyStatus.NOT_IMPLEMENTED.value,
            token_storage_policy_status=TokenStoragePolicyStatus.NOT_IMPLEMENTED.value,
            refresh_policy_status=TokenLifecycleOperationPolicyStatus.REQUIRED_PLANNED.value,
            expiry_policy_status=TokenLifecycleOperationPolicyStatus.REQUIRED_PLANNED.value,
            revoke_policy_status=TokenLifecycleOperationPolicyStatus.REQUIRED_PLANNED.value,
            disconnect_policy_status=TokenLifecycleOperationPolicyStatus.REQUIRED_PLANNED.value,
            rotation_policy_status=TokenLifecycleOperationPolicyStatus.REQUIRED_PLANNED.value,
            error_redaction_policy_status=ErrorRedactionPolicyStatus.ACTIVE.value,
            audit_event_policy_status=AuditEventPolicyStatus.METADATA_ONLY.value,
            is_available=provider.is_available,
            is_real_provider=provider.is_real_provider,
            requires_user_authorization=provider.requires_user_authorization,
            can_refresh_token=False,
            can_revoke_token=False,
            can_disconnect=False,
            can_rotate_token=False,
            can_mark_token_expired=False,
            safe_status_message=(
                "Douyin sandbox token lifecycle boundary is placeholder metadata only; "
                "token storage, refresh, expiry handling, revoke, and disconnect are "
                "not implemented."
            ),
            boundary_notes=[
                "placeholder token lifecycle boundary metadata only",
                "OAuth is not implemented",
                "tokens are not stored",
                "refresh tokens are not stored",
                "token refresh is not implemented",
                "token expiry handling is planned but not active",
                "token revoke is not implemented",
                "disconnect is not implemented",
                "no token exchange",
                "no real Douyin API call",
                "cannot be treated as douyin_real",
            ],
        )

    return ProviderTokenLifecycleBoundary(
        provider_id=provider.provider_id,
        provider_name=provider.provider_name,
        source_type=provider.source_type.value,
        implementation_status=provider.implementation_status.value,
        token_lifecycle_policy_status=TokenLifecyclePolicyStatus.NOT_IMPLEMENTED.value,
        token_storage_policy_status=TokenStoragePolicyStatus.NOT_IMPLEMENTED.value,
        refresh_policy_status=TokenLifecycleOperationPolicyStatus.REQUIRED_PLANNED.value,
        expiry_policy_status=TokenLifecycleOperationPolicyStatus.REQUIRED_PLANNED.value,
        revoke_policy_status=TokenLifecycleOperationPolicyStatus.REQUIRED_PLANNED.value,
        disconnect_policy_status=TokenLifecycleOperationPolicyStatus.REQUIRED_PLANNED.value,
        rotation_policy_status=TokenLifecycleOperationPolicyStatus.REQUIRED_PLANNED.value,
        error_redaction_policy_status=ErrorRedactionPolicyStatus.ACTIVE.value,
        audit_event_policy_status=AuditEventPolicyStatus.METADATA_ONLY.value,
        is_available=provider.is_available,
        is_real_provider=provider.is_real_provider,
        requires_user_authorization=provider.requires_user_authorization,
        can_refresh_token=False,
        can_revoke_token=False,
        can_disconnect=False,
        can_rotate_token=False,
        can_mark_token_expired=False,
        safe_status_message=(
            "Douyin real token lifecycle boundary is a future placeholder only; "
            "token storage, refresh, expiry handling, revoke, disconnect, metrics "
            "fetching, upload, publish, and scheduling are not implemented."
        ),
        boundary_notes=[
            "future real provider token lifecycle boundary placeholder only",
            "not real Douyin integration",
            "OAuth is not implemented",
            "no access token or refresh token storage",
            "token refresh is not implemented",
            "token expiry handling is planned but not active",
            "token revoke is not implemented",
            "disconnect is not implemented",
            "no API key storage",
            "no secret storage",
            "no token exchange",
            "no real metrics fetching",
            "no upload / publish / scheduling",
        ],
    )


def _load_known_token_lifecycle_boundary_rows(
    connection: sqlite3.Connection,
) -> dict[str, sqlite3.Row]:
    known_provider_ids = {provider.provider_id for provider in list_platform_providers()}
    rows = connection.execute(
        """
        SELECT provider_id, token_lifecycle_policy_status,
               token_storage_policy_status, refresh_policy_status,
               expiry_policy_status, revoke_policy_status,
               disconnect_policy_status, rotation_policy_status,
               error_redaction_policy_status, audit_event_policy_status,
               safe_status_message, last_status_change_reason,
               created_at, updated_at
        FROM provider_token_lifecycle_boundaries
        """
    ).fetchall()
    return {row["provider_id"]: row for row in rows if row["provider_id"] in known_provider_ids}


def _merge_provider_token_lifecycle_boundary(
    provider: PlatformProviderDescriptor, row: sqlite3.Row | None
) -> ProviderTokenLifecycleBoundary:
    default = build_default_provider_token_lifecycle_boundary(provider)
    if row is None:
        return default

    return ProviderTokenLifecycleBoundary(
        provider_id=default.provider_id,
        provider_name=default.provider_name,
        source_type=default.source_type,
        implementation_status=default.implementation_status,
        token_lifecycle_policy_status=row["token_lifecycle_policy_status"],
        token_storage_policy_status=row["token_storage_policy_status"],
        refresh_policy_status=row["refresh_policy_status"],
        expiry_policy_status=row["expiry_policy_status"],
        revoke_policy_status=row["revoke_policy_status"],
        disconnect_policy_status=row["disconnect_policy_status"],
        rotation_policy_status=row["rotation_policy_status"],
        error_redaction_policy_status=row["error_redaction_policy_status"],
        audit_event_policy_status=row["audit_event_policy_status"],
        is_available=default.is_available,
        is_real_provider=default.is_real_provider,
        requires_user_authorization=default.requires_user_authorization,
        can_refresh_token=default.can_refresh_token,
        can_revoke_token=default.can_revoke_token,
        can_disconnect=default.can_disconnect,
        can_rotate_token=default.can_rotate_token,
        can_mark_token_expired=default.can_mark_token_expired,
        safe_status_message=row["safe_status_message"],
        boundary_notes=default.boundary_notes,
        last_status_change_reason=row["last_status_change_reason"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
