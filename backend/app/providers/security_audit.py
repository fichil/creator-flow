import json
import re
import sqlite3
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.providers.platform_registry import (
    PlatformProviderDescriptor,
    SourceType,
    get_platform_provider,
    list_platform_providers,
)
from app.security.redaction import (
    REDACTED_VALUE,
    is_sensitive_key,
    redact_sensitive_mapping,
    redact_sensitive_text,
)


class ProviderSecurityAuditEventType(str, Enum):
    BOUNDARY_INITIALIZED = "boundary_initialized"
    CONNECTION_STATUS_CHECKED = "connection_status_checked"
    AUTHORIZATION_STATUS_CHECKED = "authorization_status_checked"
    CREDENTIAL_REFERENCE_CHECKED = "credential_reference_checked"
    REDACTION_APPLIED = "redaction_applied"
    AUTHORIZATION_FAILED = "authorization_failed"
    PERMISSION_DENIED = "permission_denied"
    TOKEN_EXPIRED = "token_expired"
    PROVIDER_ERROR = "provider_error"
    DISCONNECT_REQUESTED = "disconnect_requested"
    REVOKE_REQUESTED = "revoke_requested"
    BOUNDARY_VIOLATION_BLOCKED = "boundary_violation_blocked"


class ProviderSecurityAuditEventStatus(str, Enum):
    RECORDED = "recorded"
    REDACTED = "redacted"
    BLOCKED = "blocked"
    PLANNED = "planned"
    NOT_IMPLEMENTED = "not_implemented"


class ProviderSecurityAuditEventSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SECURITY = "security"


class ProviderSecurityAuditActorType(str, Enum):
    SYSTEM = "system"
    INTERNAL = "internal"
    USER_PLACEHOLDER = "user_placeholder"


class ProviderSecurityAuditRedactionStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    ACTIVE = "active"
    REDACTED = "redacted"


@dataclass(frozen=True)
class ProviderSecurityAuditEvent:
    audit_event_id: str
    provider_id: str
    provider_name: str
    source_type: str
    implementation_status: str
    event_type: str
    event_status: str
    event_severity: str
    actor_type: str
    redaction_status: str
    safe_event_message: str
    safe_metadata: dict[str, Any]
    boundary_notes: list[str]
    created_at: str


def list_provider_security_audit_events(
    connection: sqlite3.Connection,
    provider_id: str | None = None,
    limit: int = 100,
) -> list[ProviderSecurityAuditEvent]:
    known_providers = {provider.provider_id: provider for provider in list_platform_providers()}
    if provider_id is not None and provider_id not in known_providers:
        return []

    clamped_limit = _clamp_limit(limit)
    params: list[Any] = []
    where_clause = ""
    if provider_id is not None:
        where_clause = "WHERE provider_id = ?"
        params.append(provider_id)
    params.append(clamped_limit)

    rows = connection.execute(
        f"""
        SELECT audit_event_id, provider_id, source_type, event_type, event_status,
               event_severity, actor_type, redaction_status, safe_event_message,
               safe_metadata_json, boundary_notes_json, created_at
        FROM provider_security_audit_events
        {where_clause}
        ORDER BY created_at DESC, audit_event_id DESC
        LIMIT ?
        """,
        params,
    ).fetchall()

    events: list[ProviderSecurityAuditEvent] = []
    for row in rows:
        provider = known_providers.get(row["provider_id"])
        if provider is not None:
            events.append(build_provider_security_audit_event(provider, row))
    return events


def get_provider_security_audit_event(
    connection: sqlite3.Connection,
    audit_event_id: str,
) -> ProviderSecurityAuditEvent | None:
    row = connection.execute(
        """
        SELECT audit_event_id, provider_id, source_type, event_type, event_status,
               event_severity, actor_type, redaction_status, safe_event_message,
               safe_metadata_json, boundary_notes_json, created_at
        FROM provider_security_audit_events
        WHERE audit_event_id = ?
        """,
        (audit_event_id,),
    ).fetchone()
    if row is None:
        return None

    provider = get_platform_provider(row["provider_id"])
    if provider is None:
        return None
    return build_provider_security_audit_event(provider, row)


def record_provider_security_audit_event(
    connection: sqlite3.Connection,
    *,
    provider_id: str,
    event_type: str,
    event_status: str,
    event_severity: str,
    actor_type: str,
    message: str,
    metadata: dict[str, Any] | None = None,
    boundary_notes: list[str] | None = None,
) -> ProviderSecurityAuditEvent:
    provider = get_platform_provider(provider_id)
    if provider is None:
        raise ValueError("Unknown provider")

    event_type_value = ProviderSecurityAuditEventType(event_type).value
    event_status_value = ProviderSecurityAuditEventStatus(event_status).value
    event_severity_value = ProviderSecurityAuditEventSeverity(event_severity).value
    actor_type_value = ProviderSecurityAuditActorType(actor_type).value

    safe_event_message = _build_safe_event_message(message)
    safe_metadata = _build_safe_metadata(metadata or {})
    safe_boundary_notes = _build_boundary_notes(provider, boundary_notes)
    redaction_status = _detect_redaction_status(
        original_message=message,
        safe_event_message=safe_event_message,
        original_metadata=metadata or {},
        safe_metadata=safe_metadata,
    )

    audit_event_id = uuid.uuid4().hex
    connection.execute(
        """
        INSERT INTO provider_security_audit_events (
            audit_event_id, provider_id, source_type, event_type, event_status,
            event_severity, actor_type, redaction_status, safe_event_message,
            safe_metadata_json, boundary_notes_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            audit_event_id,
            provider.provider_id,
            provider.source_type.value,
            event_type_value,
            event_status_value,
            event_severity_value,
            actor_type_value,
            redaction_status.value,
            safe_event_message,
            json.dumps(safe_metadata, sort_keys=True),
            json.dumps(safe_boundary_notes),
        ),
    )
    connection.commit()

    created = get_provider_security_audit_event(connection, audit_event_id)
    if created is None:
        raise RuntimeError("Provider security audit event was not recorded")
    return created


def build_provider_security_audit_event(
    provider: PlatformProviderDescriptor,
    row: sqlite3.Row,
) -> ProviderSecurityAuditEvent:
    return ProviderSecurityAuditEvent(
        audit_event_id=row["audit_event_id"],
        provider_id=provider.provider_id,
        provider_name=provider.provider_name,
        source_type=provider.source_type.value,
        implementation_status=provider.implementation_status.value,
        event_type=row["event_type"],
        event_status=row["event_status"],
        event_severity=row["event_severity"],
        actor_type=row["actor_type"],
        redaction_status=row["redaction_status"],
        safe_event_message=row["safe_event_message"],
        safe_metadata=_load_metadata_json(row["safe_metadata_json"]),
        boundary_notes=_load_boundary_notes_json(row["boundary_notes_json"]),
        created_at=row["created_at"],
    )


def _clamp_limit(limit: int) -> int:
    return max(1, min(int(limit), 100))


def _build_safe_event_message(message: str) -> str:
    return _sanitize_redacted_labels(redact_sensitive_text(message))


def _sanitize_redacted_labels(message: str) -> str:
    pattern = re.compile(
        r"\b("
        r"access_token|refresh_token|token|token_value|api_key|secret|secret_value|"
        r"client_secret|oauth_client_secret|authorization_code|credential|"
        r"credential_material|encrypted_credential|private_key|oauth_code|password|"
        r"bearer_token|session_cookie"
        rf")={re.escape(REDACTED_VALUE)}",
        re.IGNORECASE,
    )
    return pattern.sub(f"redacted_value={REDACTED_VALUE}", message)


def _build_safe_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    redacted = redact_sensitive_mapping(metadata)
    sanitized = _sanitize_sensitive_keys(redacted)
    if not isinstance(sanitized, dict):
        return {}
    return sanitized


def _sanitize_sensitive_keys(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        redacted_key_count = 0
        for key, item in value.items():
            key_text = str(key)
            safe_key = key_text
            if is_sensitive_key(key_text):
                redacted_key_count += 1
                safe_key = "redacted_field"
                if redacted_key_count > 1:
                    safe_key = f"{safe_key}_{redacted_key_count}"
            while safe_key in result:
                redacted_key_count += 1
                safe_key = f"redacted_field_{redacted_key_count}"
            result[safe_key] = _sanitize_sensitive_keys(item)
        return result
    if isinstance(value, list):
        return [_sanitize_sensitive_keys(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize_sensitive_keys(item) for item in value]
    return value


def _build_boundary_notes(
    provider: PlatformProviderDescriptor,
    extra_notes: list[str] | None,
) -> list[str]:
    notes = list(_default_boundary_notes(provider))
    if extra_notes:
        notes.extend(redact_sensitive_text(note) for note in extra_notes)
    return notes


def _default_boundary_notes(provider: PlatformProviderDescriptor) -> list[str]:
    if provider.source_type == SourceType.FAKE_LOCAL:
        return [
            "local fake/demo/test audit metadata only",
            "not real Douyin data",
            "no OAuth required",
            "no token stored",
            "no secret stored",
            "no external service call",
        ]

    if provider.source_type == SourceType.SANDBOX:
        return [
            "placeholder audit metadata only",
            "OAuth is not implemented",
            "tokens are not stored",
            "secrets are not stored",
            "no real Douyin API call",
            "cannot be treated as douyin_real",
        ]

    return [
        "future real provider placeholder audit metadata only",
        "not real Douyin integration",
        "OAuth is not implemented",
        "no access token or refresh token storage",
        "no API key storage",
        "no secret storage",
        "no real metrics fetching",
        "no upload / publish / scheduling",
    ]


def _detect_redaction_status(
    *,
    original_message: str,
    safe_event_message: str,
    original_metadata: dict[str, Any],
    safe_metadata: dict[str, Any],
) -> ProviderSecurityAuditRedactionStatus:
    if safe_event_message != original_message:
        return ProviderSecurityAuditRedactionStatus.REDACTED
    if safe_metadata != original_metadata:
        return ProviderSecurityAuditRedactionStatus.REDACTED
    if original_metadata:
        return ProviderSecurityAuditRedactionStatus.ACTIVE
    return ProviderSecurityAuditRedactionStatus.ACTIVE


def _load_metadata_json(value: str) -> dict[str, Any]:
    parsed = json.loads(value or "{}")
    if isinstance(parsed, dict):
        return parsed
    return {}


def _load_boundary_notes_json(value: str) -> list[str]:
    parsed = json.loads(value or "[]")
    if isinstance(parsed, list):
        return [str(note) for note in parsed]
    return []
