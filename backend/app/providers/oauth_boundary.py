import sqlite3
from dataclasses import dataclass
from enum import Enum

from app.providers.platform_registry import (
    PlatformProviderDescriptor,
    SourceType,
    get_platform_provider,
    list_platform_providers,
)


class OAuthPolicyStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PLANNED = "planned"
    NOT_IMPLEMENTED = "not_implemented"
    UNAVAILABLE = "unavailable"


class OAuthStatePolicyStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PLANNED = "planned"
    REQUIRED_PLANNED = "required_planned"
    NOT_IMPLEMENTED = "not_implemented"
    UNAVAILABLE = "unavailable"


class OAuthCallbackPolicyStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PLANNED = "planned"
    REQUIRED_PLANNED = "required_planned"
    NOT_IMPLEMENTED = "not_implemented"
    UNAVAILABLE = "unavailable"


class CSRFProtectionStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    REQUIRED_PLANNED = "required_planned"
    ACTIVE_METADATA_ONLY = "active_metadata_only"
    NOT_IMPLEMENTED = "not_implemented"


class RedirectURIPolicyStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    REQUIRED_PLANNED = "required_planned"
    NOT_CONFIGURED = "not_configured"
    NOT_IMPLEMENTED = "not_implemented"


class TokenExchangePolicyStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PLANNED = "planned"
    NOT_IMPLEMENTED = "not_implemented"
    UNAVAILABLE = "unavailable"


class TokenStoragePolicyStatus(str, Enum):
    NONE = "none"
    PLANNED = "planned"
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
class ProviderOAuthBoundary:
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


def list_provider_oauth_boundaries(
    connection: sqlite3.Connection,
) -> list[ProviderOAuthBoundary]:
    boundary_rows = _load_known_oauth_boundary_rows(connection)
    return [
        _merge_provider_oauth_boundary(provider, boundary_rows.get(provider.provider_id))
        for provider in list_platform_providers()
    ]


def get_provider_oauth_boundary(
    connection: sqlite3.Connection, provider_id: str
) -> ProviderOAuthBoundary | None:
    provider = get_platform_provider(provider_id)
    if provider is None:
        return None

    row = connection.execute(
        """
        SELECT provider_id, oauth_policy_status, state_policy_status,
               callback_policy_status, csrf_protection_status,
               redirect_uri_policy_status, token_exchange_policy_status,
               token_storage_policy_status, error_redaction_policy_status,
               audit_event_policy_status, safe_status_message,
               last_status_change_reason, created_at, updated_at
        FROM provider_oauth_boundaries
        WHERE provider_id = ?
        """,
        (provider_id,),
    ).fetchone()
    return _merge_provider_oauth_boundary(provider, row)


def build_default_provider_oauth_boundary(
    provider: PlatformProviderDescriptor,
) -> ProviderOAuthBoundary:
    if provider.source_type == SourceType.FAKE_LOCAL:
        return ProviderOAuthBoundary(
            provider_id=provider.provider_id,
            provider_name=provider.provider_name,
            source_type=provider.source_type.value,
            implementation_status=provider.implementation_status.value,
            oauth_policy_status=OAuthPolicyStatus.NOT_REQUIRED.value,
            state_policy_status=OAuthStatePolicyStatus.NOT_REQUIRED.value,
            callback_policy_status=OAuthCallbackPolicyStatus.NOT_REQUIRED.value,
            csrf_protection_status=CSRFProtectionStatus.NOT_REQUIRED.value,
            redirect_uri_policy_status=RedirectURIPolicyStatus.NOT_REQUIRED.value,
            token_exchange_policy_status=TokenExchangePolicyStatus.NOT_REQUIRED.value,
            token_storage_policy_status=TokenStoragePolicyStatus.NONE.value,
            error_redaction_policy_status=ErrorRedactionPolicyStatus.ACTIVE.value,
            audit_event_policy_status=AuditEventPolicyStatus.METADATA_ONLY.value,
            is_available=provider.is_available,
            is_real_provider=provider.is_real_provider,
            requires_user_authorization=provider.requires_user_authorization,
            can_start_oauth=False,
            can_handle_callback=False,
            can_exchange_token=False,
            can_refresh_token=False,
            can_revoke_token=False,
            safe_status_message=(
                "Local fake provider does not require OAuth state, callback handling, "
                "token exchange, or token storage."
            ),
            boundary_notes=[
                "local fake/demo/test data only",
                "not real Douyin data",
                "OAuth is not required",
                "no state value stored",
                "no authorization code stored",
                "no token exchange",
                "no token stored",
                "no secret stored",
                "no external service call",
            ],
        )

    if provider.source_type == SourceType.SANDBOX:
        return ProviderOAuthBoundary(
            provider_id=provider.provider_id,
            provider_name=provider.provider_name,
            source_type=provider.source_type.value,
            implementation_status=provider.implementation_status.value,
            oauth_policy_status=OAuthPolicyStatus.NOT_IMPLEMENTED.value,
            state_policy_status=OAuthStatePolicyStatus.REQUIRED_PLANNED.value,
            callback_policy_status=OAuthCallbackPolicyStatus.REQUIRED_PLANNED.value,
            csrf_protection_status=CSRFProtectionStatus.REQUIRED_PLANNED.value,
            redirect_uri_policy_status=RedirectURIPolicyStatus.REQUIRED_PLANNED.value,
            token_exchange_policy_status=TokenExchangePolicyStatus.NOT_IMPLEMENTED.value,
            token_storage_policy_status=TokenStoragePolicyStatus.NOT_IMPLEMENTED.value,
            error_redaction_policy_status=ErrorRedactionPolicyStatus.ACTIVE.value,
            audit_event_policy_status=AuditEventPolicyStatus.METADATA_ONLY.value,
            is_available=provider.is_available,
            is_real_provider=provider.is_real_provider,
            requires_user_authorization=provider.requires_user_authorization,
            can_start_oauth=False,
            can_handle_callback=False,
            can_exchange_token=False,
            can_refresh_token=False,
            can_revoke_token=False,
            safe_status_message=(
                "Douyin sandbox OAuth boundary is placeholder metadata only; OAuth "
                "is not implemented and no state value, authorization code, or token "
                "is stored."
            ),
            boundary_notes=[
                "placeholder OAuth boundary metadata only",
                "OAuth is not implemented",
                "OAuth callback route is not implemented",
                "OAuth state storage is not implemented",
                "CSRF state validation is planned but not active",
                "authorization code is not stored",
                "tokens are not stored",
                "secrets are not stored",
                "no token exchange",
                "no real Douyin API call",
                "cannot be treated as douyin_real",
            ],
        )

    return ProviderOAuthBoundary(
        provider_id=provider.provider_id,
        provider_name=provider.provider_name,
        source_type=provider.source_type.value,
        implementation_status=provider.implementation_status.value,
        oauth_policy_status=OAuthPolicyStatus.NOT_IMPLEMENTED.value,
        state_policy_status=OAuthStatePolicyStatus.REQUIRED_PLANNED.value,
        callback_policy_status=OAuthCallbackPolicyStatus.REQUIRED_PLANNED.value,
        csrf_protection_status=CSRFProtectionStatus.REQUIRED_PLANNED.value,
        redirect_uri_policy_status=RedirectURIPolicyStatus.REQUIRED_PLANNED.value,
        token_exchange_policy_status=TokenExchangePolicyStatus.NOT_IMPLEMENTED.value,
        token_storage_policy_status=TokenStoragePolicyStatus.NOT_IMPLEMENTED.value,
        error_redaction_policy_status=ErrorRedactionPolicyStatus.ACTIVE.value,
        audit_event_policy_status=AuditEventPolicyStatus.METADATA_ONLY.value,
        is_available=provider.is_available,
        is_real_provider=provider.is_real_provider,
        requires_user_authorization=provider.requires_user_authorization,
        can_start_oauth=False,
        can_handle_callback=False,
        can_exchange_token=False,
        can_refresh_token=False,
        can_revoke_token=False,
        safe_status_message=(
            "Douyin real OAuth boundary is a future placeholder only; OAuth callback, "
            "state validation, token exchange, token storage, metrics fetching, "
            "upload, publish, and scheduling are not implemented."
        ),
        boundary_notes=[
            "future real provider OAuth boundary placeholder only",
            "not real Douyin integration",
            "OAuth is not implemented",
            "OAuth callback route is not implemented",
            "OAuth state storage is not implemented",
            "CSRF state validation is planned but not active",
            "no authorization code storage",
            "no access token or refresh token storage",
            "no API key storage",
            "no secret storage",
            "no token exchange",
            "no real metrics fetching",
            "no upload / publish / scheduling",
        ],
    )


def _load_known_oauth_boundary_rows(
    connection: sqlite3.Connection,
) -> dict[str, sqlite3.Row]:
    known_provider_ids = {provider.provider_id for provider in list_platform_providers()}
    rows = connection.execute(
        """
        SELECT provider_id, oauth_policy_status, state_policy_status,
               callback_policy_status, csrf_protection_status,
               redirect_uri_policy_status, token_exchange_policy_status,
               token_storage_policy_status, error_redaction_policy_status,
               audit_event_policy_status, safe_status_message,
               last_status_change_reason, created_at, updated_at
        FROM provider_oauth_boundaries
        """
    ).fetchall()
    return {row["provider_id"]: row for row in rows if row["provider_id"] in known_provider_ids}


def _merge_provider_oauth_boundary(
    provider: PlatformProviderDescriptor, row: sqlite3.Row | None
) -> ProviderOAuthBoundary:
    default = build_default_provider_oauth_boundary(provider)
    if row is None:
        return default

    return ProviderOAuthBoundary(
        provider_id=default.provider_id,
        provider_name=default.provider_name,
        source_type=default.source_type,
        implementation_status=default.implementation_status,
        oauth_policy_status=row["oauth_policy_status"],
        state_policy_status=row["state_policy_status"],
        callback_policy_status=row["callback_policy_status"],
        csrf_protection_status=row["csrf_protection_status"],
        redirect_uri_policy_status=row["redirect_uri_policy_status"],
        token_exchange_policy_status=row["token_exchange_policy_status"],
        token_storage_policy_status=row["token_storage_policy_status"],
        error_redaction_policy_status=row["error_redaction_policy_status"],
        audit_event_policy_status=row["audit_event_policy_status"],
        is_available=default.is_available,
        is_real_provider=default.is_real_provider,
        requires_user_authorization=default.requires_user_authorization,
        can_start_oauth=default.can_start_oauth,
        can_handle_callback=default.can_handle_callback,
        can_exchange_token=default.can_exchange_token,
        can_refresh_token=default.can_refresh_token,
        can_revoke_token=default.can_revoke_token,
        safe_status_message=row["safe_status_message"],
        boundary_notes=default.boundary_notes,
        last_status_change_reason=row["last_status_change_reason"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
