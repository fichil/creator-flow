import sqlite3
import uuid
from collections.abc import Mapping
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import Any

from app.providers.platform_registry import SourceType, get_platform_provider
from app.providers.token_exchange import TokenExchangeResultStatus


_SAFE_TOKEN_EXCHANGE_FIELDS = {
    "status",
    "provider_id",
    "source_type",
    "state_validation_status",
    "oauth_state_id",
    "token_received_boolean",
    "credential_storage_required_boolean",
    "external_exchange_performed",
    "exchange_attempted",
    "sandbox_fallback_performed",
    "safe_status_message",
}
_SENSITIVE_MATERIAL_KEYS = {
    "authorization_code",
    "raw_authorization_code",
    "raw_state",
    "state_value",
    "oauth_state",
    "oauth_state_value",
    "access_token",
    "refresh_token",
    "token",
    "token_value",
    "secret",
    "secret_value",
    "client_secret",
    "credential",
    "credential_material",
    "encrypted_credential",
    "cookie",
    "session",
    "bearer",
    "bearer_token",
    "raw_request",
    "raw_response",
}


class CredentialStorageBoundaryStatus(str, Enum):
    CREDENTIAL_REFERENCE_CREATED = "credential_reference_created"
    CREDENTIAL_STORAGE_DISABLED = "credential_storage_disabled"
    CREDENTIAL_STORAGE_REJECTED = "credential_storage_rejected"
    CREDENTIAL_MATERIAL_REJECTED = "credential_material_rejected"
    UNSUPPORTED_PROVIDER = "unsupported_provider"
    REAL_PROVIDER_DISABLED = "real_provider_disabled"
    ENCRYPTION_PROVIDER_UNAVAILABLE = "encryption_provider_unavailable"
    EXTERNAL_STORAGE_BLOCKED = "external_storage_blocked"


@dataclass(frozen=True)
class CredentialStorageBoundaryResult:
    status: str
    provider_id: str | None
    source_type: str | None
    credential_reference_id: str | None
    storage_mode: str | None
    credential_storage_enabled: bool
    encrypted_payload_stored: bool
    external_storage_performed: bool
    sandbox_fallback_performed: bool
    safe_status_message: str


def create_credential_reference_boundary(
    connection: sqlite3.Connection,
    provider_id: str,
    *,
    token_exchange_result: Any | None,
    attempted_material: Mapping[str, Any] | None = None,
    require_encrypted_storage: bool = False,
) -> CredentialStorageBoundaryResult:
    provider = get_platform_provider(provider_id)
    if provider is None:
        return _result(
            CredentialStorageBoundaryStatus.UNSUPPORTED_PROVIDER,
            safe_status_message="Unsupported provider for credential storage boundary.",
        )

    if provider.source_type == SourceType.REAL:
        return _result(
            CredentialStorageBoundaryStatus.REAL_PROVIDER_DISABLED,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            safe_status_message="Real provider credential storage is disabled.",
        )

    if attempted_material and _contains_sensitive_material(attempted_material):
        return _result(
            CredentialStorageBoundaryStatus.CREDENTIAL_MATERIAL_REJECTED,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            safe_status_message="Credential material was rejected by the boundary.",
        )

    exchange_metadata = _coerce_exchange_metadata(token_exchange_result)
    if exchange_metadata is None:
        return _result(
            CredentialStorageBoundaryStatus.CREDENTIAL_STORAGE_DISABLED,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            safe_status_message="Credential storage boundary requires safe token exchange metadata.",
        )

    if _contains_sensitive_material(exchange_metadata):
        return _result(
            CredentialStorageBoundaryStatus.CREDENTIAL_MATERIAL_REJECTED,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            safe_status_message="Credential material was rejected by the boundary.",
        )

    if not _is_safe_exchange_metadata(exchange_metadata, provider.provider_id, provider.source_type.value):
        return _result(
            CredentialStorageBoundaryStatus.CREDENTIAL_STORAGE_REJECTED,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            safe_status_message="Credential storage boundary rejected malformed exchange metadata.",
        )

    if require_encrypted_storage:
        return _result(
            CredentialStorageBoundaryStatus.ENCRYPTION_PROVIDER_UNAVAILABLE,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            safe_status_message="Encrypted credential provider is unavailable; real storage remains disabled.",
        )

    credential_reference_id = uuid.uuid4().hex
    connection.execute(
        """
        INSERT INTO provider_credential_references (
            reference_id, provider_id, source_type, reference_kind,
            reference_status, storage_status, redaction_policy_status,
            safe_display_name, safe_status_message, last_status_change_reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            credential_reference_id,
            provider.provider_id,
            provider.source_type.value,
            "credential_reference_placeholder",
            "reference_only",
            "reference_only",
            "active",
            f"{provider.provider_name} metadata-only credential reference",
            "Credential reference metadata created; real credential storage remains disabled.",
            "batch4_metadata_reference_created",
        ),
    )
    connection.commit()

    return _result(
        CredentialStorageBoundaryStatus.CREDENTIAL_REFERENCE_CREATED,
        provider_id=provider.provider_id,
        source_type=provider.source_type.value,
        credential_reference_id=credential_reference_id,
        storage_mode="metadata_reference_only",
        safe_status_message="Credential reference metadata created; real credential storage remains disabled.",
    )


def _coerce_exchange_metadata(value: Any | None) -> dict[str, Any] | None:
    if value is None:
        return None
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    return None


def _contains_sensitive_material(payload: Mapping[str, Any]) -> bool:
    for key, value in payload.items():
        normalized_key = str(key).strip().lower().replace("-", "_")
        if normalized_key in _SENSITIVE_MATERIAL_KEYS:
            return True
        if isinstance(value, Mapping) and _contains_sensitive_material(value):
            return True
    return False


def _is_safe_exchange_metadata(
    metadata: Mapping[str, Any],
    provider_id: str,
    source_type: str,
) -> bool:
    if not set(metadata).issubset(_SAFE_TOKEN_EXCHANGE_FIELDS):
        return False
    if metadata.get("status") != TokenExchangeResultStatus.EXCHANGE_SIMULATED.value:
        return False
    if metadata.get("provider_id") != provider_id:
        return False
    if metadata.get("source_type") != source_type:
        return False
    if metadata.get("external_exchange_performed") is not False:
        return False
    if metadata.get("sandbox_fallback_performed") is not False:
        return False
    if metadata.get("token_received_boolean") is not True:
        return False
    if metadata.get("credential_storage_required_boolean") is not True:
        return False
    return True


def _result(
    status: CredentialStorageBoundaryStatus,
    *,
    provider_id: str | None = None,
    source_type: str | None = None,
    credential_reference_id: str | None = None,
    storage_mode: str | None = None,
    credential_storage_enabled: bool = False,
    encrypted_payload_stored: bool = False,
    external_storage_performed: bool = False,
    sandbox_fallback_performed: bool = False,
    safe_status_message: str,
) -> CredentialStorageBoundaryResult:
    return CredentialStorageBoundaryResult(
        status=status.value,
        provider_id=provider_id,
        source_type=source_type,
        credential_reference_id=credential_reference_id,
        storage_mode=storage_mode,
        credential_storage_enabled=credential_storage_enabled,
        encrypted_payload_stored=encrypted_payload_stored,
        external_storage_performed=external_storage_performed,
        sandbox_fallback_performed=sandbox_fallback_performed,
        safe_status_message=safe_status_message,
    )
