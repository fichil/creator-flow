import sqlite3
from dataclasses import dataclass
from enum import Enum

from app.providers.platform_registry import (
    PlatformProviderDescriptor,
    SourceType,
    get_platform_provider,
    list_platform_providers,
)


class CredentialReferenceKind(str, Enum):
    NONE_REQUIRED = "none_required"
    OAUTH_PLACEHOLDER = "oauth_placeholder"
    PROVIDER_SECRET_PLACEHOLDER = "provider_secret_placeholder"
    API_KEY_PLACEHOLDER = "api_key_placeholder"
    CREDENTIAL_REFERENCE_PLACEHOLDER = "credential_reference_placeholder"


class CredentialReferenceStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    NOT_CONFIGURED = "not_configured"
    NOT_IMPLEMENTED = "not_implemented"
    REFERENCE_ONLY = "reference_only"
    UNAVAILABLE = "unavailable"


class CredentialReferenceStorageStatus(str, Enum):
    NONE = "none"
    NOT_CONFIGURED = "not_configured"
    NOT_IMPLEMENTED = "not_implemented"
    REFERENCE_ONLY = "reference_only"
    ENCRYPTED_STORAGE_PLANNED = "encrypted_storage_planned"


class RedactionPolicyStatus(str, Enum):
    ACTIVE = "active"
    PLANNED = "planned"
    NOT_REQUIRED = "not_required"


@dataclass(frozen=True)
class ProviderCredentialReference:
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


def list_provider_credential_references(
    connection: sqlite3.Connection,
) -> list[ProviderCredentialReference]:
    reference_rows = _load_known_reference_rows(connection)
    return [
        _merge_provider_reference(provider, reference_rows.get(provider.provider_id))
        for provider in list_platform_providers()
    ]


def get_provider_credential_reference(
    connection: sqlite3.Connection, provider_id: str
) -> ProviderCredentialReference | None:
    provider = get_platform_provider(provider_id)
    if provider is None:
        return None

    row = connection.execute(
        """
        SELECT provider_id, reference_kind, reference_status, storage_status,
               redaction_policy_status, safe_display_name, safe_status_message,
               last_status_change_reason, created_at, updated_at
        FROM provider_credential_references
        WHERE provider_id = ?
        ORDER BY created_at DESC, reference_id DESC
        LIMIT 1
        """,
        (provider_id,),
    ).fetchone()
    return _merge_provider_reference(provider, row)


def build_default_provider_credential_reference(
    provider: PlatformProviderDescriptor,
) -> ProviderCredentialReference:
    if provider.source_type == SourceType.FAKE_LOCAL:
        return ProviderCredentialReference(
            provider_id=provider.provider_id,
            provider_name=provider.provider_name,
            source_type=provider.source_type.value,
            implementation_status=provider.implementation_status.value,
            reference_kind=CredentialReferenceKind.NONE_REQUIRED.value,
            reference_status=CredentialReferenceStatus.NOT_REQUIRED.value,
            storage_status=CredentialReferenceStorageStatus.NONE.value,
            redaction_policy_status=RedactionPolicyStatus.ACTIVE.value,
            is_available=provider.is_available,
            is_real_provider=provider.is_real_provider,
            requires_user_authorization=provider.requires_user_authorization,
            safe_display_name="Local fake provider credential reference metadata",
            safe_status_message=(
                "Local fake provider does not require credentials, OAuth, tokens, or secrets."
            ),
            boundary_notes=[
                "local fake/demo/test data only",
                "not real Douyin data",
                "no OAuth required",
                "no token stored",
                "no secret stored",
                "no credential material stored",
                "no external service call",
            ],
        )

    if provider.source_type == SourceType.SANDBOX:
        return ProviderCredentialReference(
            provider_id=provider.provider_id,
            provider_name=provider.provider_name,
            source_type=provider.source_type.value,
            implementation_status=provider.implementation_status.value,
            reference_kind=CredentialReferenceKind.OAUTH_PLACEHOLDER.value,
            reference_status=CredentialReferenceStatus.NOT_IMPLEMENTED.value,
            storage_status=CredentialReferenceStorageStatus.NOT_IMPLEMENTED.value,
            redaction_policy_status=RedactionPolicyStatus.ACTIVE.value,
            is_available=provider.is_available,
            is_real_provider=provider.is_real_provider,
            requires_user_authorization=provider.requires_user_authorization,
            safe_display_name="Douyin sandbox credential reference placeholder",
            safe_status_message=(
                "Douyin sandbox credential reference is placeholder metadata only; "
                "OAuth is not implemented and tokens are not stored."
            ),
            boundary_notes=[
                "placeholder only",
                "OAuth is not implemented",
                "tokens are not stored",
                "secrets are not stored",
                "credential material is not stored",
                "no real Douyin API call",
                "cannot be treated as douyin_real",
            ],
        )

    return ProviderCredentialReference(
        provider_id=provider.provider_id,
        provider_name=provider.provider_name,
        source_type=provider.source_type.value,
        implementation_status=provider.implementation_status.value,
        reference_kind=CredentialReferenceKind.OAUTH_PLACEHOLDER.value,
        reference_status=CredentialReferenceStatus.NOT_IMPLEMENTED.value,
        storage_status=CredentialReferenceStorageStatus.NOT_IMPLEMENTED.value,
        redaction_policy_status=RedactionPolicyStatus.ACTIVE.value,
        is_available=provider.is_available,
        is_real_provider=provider.is_real_provider,
        requires_user_authorization=provider.requires_user_authorization,
        safe_display_name="Douyin real credential reference placeholder",
        safe_status_message=(
            "Douyin real credential reference is a future placeholder only; no OAuth, "
            "token storage, metrics fetching, upload, publish, or scheduling is implemented."
        ),
        boundary_notes=[
            "future real provider placeholder only",
            "not real Douyin integration",
            "OAuth is not implemented",
            "no OAuth implementation",
            "no access token or refresh token storage",
            "no token storage",
            "no API key storage",
            "no secret storage",
            "no credential material storage",
            "no real metrics fetching",
            "no upload / publish / scheduling",
        ],
    )


def _load_known_reference_rows(connection: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    known_provider_ids = {provider.provider_id for provider in list_platform_providers()}
    rows = connection.execute(
        """
        SELECT provider_id, reference_kind, reference_status, storage_status,
               redaction_policy_status, safe_display_name, safe_status_message,
               last_status_change_reason, created_at, updated_at
        FROM provider_credential_references
        ORDER BY created_at DESC, reference_id DESC
        """
    ).fetchall()
    reference_rows: dict[str, sqlite3.Row] = {}
    for row in rows:
        provider_id = row["provider_id"]
        if provider_id in known_provider_ids and provider_id not in reference_rows:
            reference_rows[provider_id] = row
    return reference_rows


def _merge_provider_reference(
    provider: PlatformProviderDescriptor, row: sqlite3.Row | None
) -> ProviderCredentialReference:
    default = build_default_provider_credential_reference(provider)
    if row is None:
        return default

    return ProviderCredentialReference(
        provider_id=default.provider_id,
        provider_name=default.provider_name,
        source_type=default.source_type,
        implementation_status=default.implementation_status,
        reference_kind=row["reference_kind"],
        reference_status=row["reference_status"],
        storage_status=row["storage_status"],
        redaction_policy_status=row["redaction_policy_status"],
        is_available=default.is_available,
        is_real_provider=default.is_real_provider,
        requires_user_authorization=default.requires_user_authorization,
        safe_display_name=row["safe_display_name"],
        safe_status_message=row["safe_status_message"],
        boundary_notes=default.boundary_notes,
        last_status_change_reason=row["last_status_change_reason"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
