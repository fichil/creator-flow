import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.providers.connection_state import (
    ProviderConnectionState,
    list_provider_connection_states,
)
from app.providers.credential_references import (
    ProviderCredentialReference,
    list_provider_credential_references,
)
from app.providers.oauth_boundary import (
    ProviderOAuthBoundary,
    list_provider_oauth_boundaries,
)
from app.providers.platform_registry import (
    PlatformProviderDescriptor,
    SourceType,
    get_platform_provider,
    list_platform_providers,
)
from app.providers.token_lifecycle import (
    ProviderTokenLifecycleBoundary,
    list_provider_token_lifecycle_boundaries,
)


class ProviderOverallReadinessStatus(str, Enum):
    LOCAL_FAKE_READY = "local_fake_ready"
    SANDBOX_PLACEHOLDER_NOT_READY = "sandbox_placeholder_not_ready"
    REAL_PLACEHOLDER_NOT_READY = "real_placeholder_not_ready"
    METADATA_ONLY = "metadata_only"
    BLOCKED = "blocked"


class ProviderV09POCReadinessStatus(str, Enum):
    NOT_APPLICABLE_LOCAL_FAKE = "not_applicable_local_fake"
    BLOCKED_MISSING_REAL_OAUTH = "blocked_missing_real_oauth"
    BLOCKED_MISSING_TOKEN_LIFECYCLE = "blocked_missing_token_lifecycle"
    BLOCKED_MISSING_CREDENTIAL_STORAGE = "blocked_missing_credential_storage"
    BLOCKED_PLACEHOLDER_ONLY = "blocked_placeholder_only"
    METADATA_READY_FOR_REVIEW = "metadata_ready_for_review"


@dataclass(frozen=True)
class ProviderBoundaryReadinessItem:
    boundary_id: str
    boundary_name: str
    readiness_status: str
    is_blocking_real_integration: bool
    safe_status_message: str
    source_metadata: dict[str, Any]


@dataclass(frozen=True)
class ProviderReadinessSummary:
    provider_id: str
    provider_name: str
    source_type: str
    implementation_status: str
    is_available: bool
    is_real_provider: bool
    requires_user_authorization: bool
    overall_readiness_status: str
    v0_9_poc_readiness_status: str
    can_use_local_fake_workflow: bool
    is_safe_to_attempt_real_oauth: bool
    is_safe_to_store_tokens: bool
    is_safe_to_fetch_real_metrics: bool
    is_safe_to_publish: bool
    is_ready_for_v0_9_sandbox_poc: bool
    is_ready_for_v0_9_real_poc: bool
    readiness_items: list[ProviderBoundaryReadinessItem]
    blocking_reasons: list[str]
    next_safe_steps: list[str]
    safe_summary: str
    boundary_notes: list[str]


def list_provider_readiness_summaries(
    connection: sqlite3.Connection,
) -> list[ProviderReadinessSummary]:
    context = _load_readiness_context(connection)
    return [
        build_provider_readiness_summary(
            provider=provider,
            connection_state=context.connection_states[provider.provider_id],
            credential_reference=context.credential_references[provider.provider_id],
            oauth_boundary=context.oauth_boundaries[provider.provider_id],
            token_lifecycle_boundary=context.token_lifecycle_boundaries[provider.provider_id],
            safe_audit_event_count=context.safe_audit_event_counts.get(provider.provider_id, 0),
        )
        for provider in list_platform_providers()
    ]


def get_provider_readiness_summary(
    connection: sqlite3.Connection, provider_id: str
) -> ProviderReadinessSummary | None:
    provider = get_platform_provider(provider_id)
    if provider is None:
        return None

    context = _load_readiness_context(connection)
    return build_provider_readiness_summary(
        provider=provider,
        connection_state=context.connection_states[provider.provider_id],
        credential_reference=context.credential_references[provider.provider_id],
        oauth_boundary=context.oauth_boundaries[provider.provider_id],
        token_lifecycle_boundary=context.token_lifecycle_boundaries[provider.provider_id],
        safe_audit_event_count=context.safe_audit_event_counts.get(provider.provider_id, 0),
    )


def build_provider_readiness_summary(
    *,
    provider: PlatformProviderDescriptor,
    connection_state: ProviderConnectionState,
    credential_reference: ProviderCredentialReference,
    oauth_boundary: ProviderOAuthBoundary,
    token_lifecycle_boundary: ProviderTokenLifecycleBoundary,
    safe_audit_event_count: int,
) -> ProviderReadinessSummary:
    readiness_items = build_boundary_readiness_items(
        provider=provider,
        connection_state=connection_state,
        credential_reference=credential_reference,
        oauth_boundary=oauth_boundary,
        token_lifecycle_boundary=token_lifecycle_boundary,
        safe_audit_event_count=safe_audit_event_count,
    )

    if provider.source_type == SourceType.FAKE_LOCAL:
        return ProviderReadinessSummary(
            provider_id=provider.provider_id,
            provider_name=provider.provider_name,
            source_type=provider.source_type.value,
            implementation_status=provider.implementation_status.value,
            is_available=provider.is_available,
            is_real_provider=provider.is_real_provider,
            requires_user_authorization=provider.requires_user_authorization,
            overall_readiness_status=ProviderOverallReadinessStatus.LOCAL_FAKE_READY.value,
            v0_9_poc_readiness_status=(
                ProviderV09POCReadinessStatus.NOT_APPLICABLE_LOCAL_FAKE.value
            ),
            can_use_local_fake_workflow=True,
            is_safe_to_attempt_real_oauth=False,
            is_safe_to_store_tokens=False,
            is_safe_to_fetch_real_metrics=False,
            is_safe_to_publish=False,
            is_ready_for_v0_9_sandbox_poc=False,
            is_ready_for_v0_9_real_poc=False,
            readiness_items=readiness_items,
            blocking_reasons=[
                "local fake provider is not a real Douyin provider",
                "no real OAuth",
                "no real metrics",
                "no real publish",
            ],
            next_safe_steps=[
                "keep fake/local workflow available as fallback",
                "use v0.8 boundaries for review before v0.9 POC",
            ],
            safe_summary=(
                "Local fake provider is ready only for local fake/demo/test workflow; "
                "it is not real Douyin readiness and no real OAuth, real metrics, "
                "upload, publish, or scheduling is available."
            ),
            boundary_notes=[
                "local fake/demo/test data only",
                "not real Douyin data",
                "no OAuth required",
                "no token stored",
                "no external service call",
            ],
        )

    if provider.source_type == SourceType.SANDBOX:
        return ProviderReadinessSummary(
            provider_id=provider.provider_id,
            provider_name=provider.provider_name,
            source_type=provider.source_type.value,
            implementation_status=provider.implementation_status.value,
            is_available=provider.is_available,
            is_real_provider=provider.is_real_provider,
            requires_user_authorization=provider.requires_user_authorization,
            overall_readiness_status=(
                ProviderOverallReadinessStatus.SANDBOX_PLACEHOLDER_NOT_READY.value
            ),
            v0_9_poc_readiness_status=(
                ProviderV09POCReadinessStatus.BLOCKED_PLACEHOLDER_ONLY.value
            ),
            can_use_local_fake_workflow=False,
            is_safe_to_attempt_real_oauth=False,
            is_safe_to_store_tokens=False,
            is_safe_to_fetch_real_metrics=False,
            is_safe_to_publish=False,
            is_ready_for_v0_9_sandbox_poc=False,
            is_ready_for_v0_9_real_poc=False,
            readiness_items=readiness_items,
            blocking_reasons=[
                "OAuth is not implemented",
                "OAuth callback route is not implemented",
                "OAuth state storage is not implemented",
                "credential storage is not implemented",
                "token lifecycle is not implemented",
                "no real Douyin API call",
                "cannot be treated as douyin_real",
            ],
            next_safe_steps=[
                (
                    "review provider registry, OAuth boundary, credential reference, "
                    "token lifecycle and audit metadata"
                ),
                "define v0.9 sandbox/mock callback smoke test separately",
                "do not add real token storage without a separate ADR",
            ],
            safe_summary=(
                "Douyin sandbox readiness is placeholder metadata only; OAuth, "
                "credential storage, token lifecycle, real API calls, metrics fetching, "
                "upload, publish, and scheduling are not ready."
            ),
            boundary_notes=[
                "placeholder metadata only",
                "not connected",
                "tokens are not stored",
                "secrets are not stored",
                "no token exchange",
                "no real metrics fetching",
                "no upload / publish / scheduling",
            ],
        )

    return ProviderReadinessSummary(
        provider_id=provider.provider_id,
        provider_name=provider.provider_name,
        source_type=provider.source_type.value,
        implementation_status=provider.implementation_status.value,
        is_available=provider.is_available,
        is_real_provider=provider.is_real_provider,
        requires_user_authorization=provider.requires_user_authorization,
        overall_readiness_status=(
            ProviderOverallReadinessStatus.REAL_PLACEHOLDER_NOT_READY.value
        ),
        v0_9_poc_readiness_status=(
            ProviderV09POCReadinessStatus.BLOCKED_MISSING_REAL_OAUTH.value
        ),
        can_use_local_fake_workflow=False,
        is_safe_to_attempt_real_oauth=False,
        is_safe_to_store_tokens=False,
        is_safe_to_fetch_real_metrics=False,
        is_safe_to_publish=False,
        is_ready_for_v0_9_sandbox_poc=False,
        is_ready_for_v0_9_real_poc=False,
        readiness_items=readiness_items,
        blocking_reasons=[
            "real OAuth is not implemented",
            "real OAuth callback route is not implemented",
            "real credential storage is not implemented",
            "token storage is not implemented",
            "token refresh / revoke / disconnect is not implemented",
            "no real metrics fetching",
            "no upload / publish / scheduling",
        ],
        next_safe_steps=[
            "complete v0.8 readiness review before v0.9 POC",
            "create separate v0.9 Douyin provider adapter skeleton ADR",
            "create separate sandbox/mock callback smoke test plan",
            (
                "do not store real tokens until encrypted credential storage is "
                "designed and reviewed"
            ),
        ],
        safe_summary=(
            "Douyin real readiness is a future real provider placeholder only; "
            "real OAuth, credential storage, token lifecycle, metrics fetching, "
            "upload, publish, and scheduling are not ready."
        ),
        boundary_notes=[
            "future real provider placeholder only",
            "not real Douyin integration",
            "OAuth is not implemented",
            "no access token or refresh token storage",
            "no token refresh / revoke / disconnect",
            "no API key storage",
            "no secret storage",
            "no real metrics fetching",
            "no upload / publish / scheduling",
        ],
    )


def build_boundary_readiness_items(
    *,
    provider: PlatformProviderDescriptor,
    connection_state: ProviderConnectionState,
    credential_reference: ProviderCredentialReference,
    oauth_boundary: ProviderOAuthBoundary,
    token_lifecycle_boundary: ProviderTokenLifecycleBoundary,
    safe_audit_event_count: int,
) -> list[ProviderBoundaryReadinessItem]:
    blocks_real = provider.source_type != SourceType.FAKE_LOCAL
    provider_metadata_status = (
        "local_fake_ready"
        if provider.source_type == SourceType.FAKE_LOCAL
        else "placeholder_metadata_only"
    )
    return [
        ProviderBoundaryReadinessItem(
            boundary_id="provider_registry",
            boundary_name="Provider Registry",
            readiness_status=provider_metadata_status,
            is_blocking_real_integration=blocks_real,
            safe_status_message=(
                "Provider registry metadata is available for this known provider."
            ),
            source_metadata={
                "provider_type": provider.provider_type.value,
                "connection_status": provider.connection_status.value,
                "is_registry_known_provider": True,
            },
        ),
        ProviderBoundaryReadinessItem(
            boundary_id="capability_metadata",
            boundary_name="Capability Metadata",
            readiness_status=provider_metadata_status,
            is_blocking_real_integration=blocks_real,
            safe_status_message=(
                "Capability metadata is static, read-only, and does not imply real integration."
            ),
            source_metadata={
                "supports_oauth": provider.capabilities.supports_oauth,
                "supports_metrics_read": provider.capabilities.supports_metrics_read,
                "supports_publish_prepare": provider.capabilities.supports_publish_prepare,
                "supports_real_publish": provider.capabilities.supports_real_publish,
                "supports_sandbox": provider.capabilities.supports_sandbox,
                "supports_token_refresh": provider.capabilities.supports_token_refresh,
                "supports_disconnect": provider.capabilities.supports_disconnect,
                "supports_revoke": provider.capabilities.supports_revoke,
            },
        ),
        ProviderBoundaryReadinessItem(
            boundary_id="connection_state",
            boundary_name="Connection State",
            readiness_status=connection_state.connection_status,
            is_blocking_real_integration=blocks_real,
            safe_status_message=connection_state.safe_status_message,
            source_metadata={
                "authorization_status": connection_state.authorization_status,
                "sensitive_storage_status": connection_state.sensitive_storage_status,
                "can_connect": connection_state.can_connect,
                "can_refresh": connection_state.can_refresh,
                "can_revoke": connection_state.can_revoke,
                "can_disconnect": connection_state.can_disconnect,
            },
        ),
        ProviderBoundaryReadinessItem(
            boundary_id="credential_reference",
            boundary_name="Credential Reference",
            readiness_status=credential_reference.reference_status,
            is_blocking_real_integration=blocks_real,
            safe_status_message=credential_reference.safe_status_message,
            source_metadata={
                "reference_kind": credential_reference.reference_kind,
                "storage_status": credential_reference.storage_status,
                "redaction_policy_status": credential_reference.redaction_policy_status,
            },
        ),
        ProviderBoundaryReadinessItem(
            boundary_id="security_audit",
            boundary_name="Security Audit",
            readiness_status="metadata_only",
            is_blocking_real_integration=False,
            safe_status_message=(
                "Security audit metadata can be read safely; real audit trails are not required."
            ),
            source_metadata={
                "safe_audit_event_count": safe_audit_event_count,
                "audit_boundary_status": "metadata_only",
            },
        ),
        ProviderBoundaryReadinessItem(
            boundary_id="oauth_boundary",
            boundary_name="OAuth Boundary",
            readiness_status=oauth_boundary.oauth_policy_status,
            is_blocking_real_integration=blocks_real,
            safe_status_message=oauth_boundary.safe_status_message,
            source_metadata={
                "state_policy_status": oauth_boundary.state_policy_status,
                "callback_policy_status": oauth_boundary.callback_policy_status,
                "csrf_protection_status": oauth_boundary.csrf_protection_status,
                "redirect_uri_policy_status": oauth_boundary.redirect_uri_policy_status,
                "token_exchange_policy_status": (
                    oauth_boundary.token_exchange_policy_status
                ),
                "token_storage_policy_status": oauth_boundary.token_storage_policy_status,
                "error_redaction_policy_status": (
                    oauth_boundary.error_redaction_policy_status
                ),
                "audit_event_policy_status": oauth_boundary.audit_event_policy_status,
            },
        ),
        ProviderBoundaryReadinessItem(
            boundary_id="token_lifecycle_boundary",
            boundary_name="Token Lifecycle Boundary",
            readiness_status=(
                token_lifecycle_boundary.token_lifecycle_policy_status
            ),
            is_blocking_real_integration=blocks_real,
            safe_status_message=token_lifecycle_boundary.safe_status_message,
            source_metadata={
                "token_storage_policy_status": (
                    token_lifecycle_boundary.token_storage_policy_status
                ),
                "refresh_policy_status": token_lifecycle_boundary.refresh_policy_status,
                "expiry_policy_status": token_lifecycle_boundary.expiry_policy_status,
                "revoke_policy_status": token_lifecycle_boundary.revoke_policy_status,
                "disconnect_policy_status": (
                    token_lifecycle_boundary.disconnect_policy_status
                ),
                "rotation_policy_status": token_lifecycle_boundary.rotation_policy_status,
                "error_redaction_policy_status": (
                    token_lifecycle_boundary.error_redaction_policy_status
                ),
                "audit_event_policy_status": (
                    token_lifecycle_boundary.audit_event_policy_status
                ),
            },
        ),
    ]


@dataclass(frozen=True)
class _ReadinessContext:
    connection_states: dict[str, ProviderConnectionState]
    credential_references: dict[str, ProviderCredentialReference]
    oauth_boundaries: dict[str, ProviderOAuthBoundary]
    token_lifecycle_boundaries: dict[str, ProviderTokenLifecycleBoundary]
    safe_audit_event_counts: dict[str, int]


def _load_readiness_context(connection: sqlite3.Connection) -> _ReadinessContext:
    return _ReadinessContext(
        connection_states={
            state.provider_id: state
            for state in list_provider_connection_states(connection)
        },
        credential_references={
            reference.provider_id: reference
            for reference in list_provider_credential_references(connection)
        },
        oauth_boundaries={
            boundary.provider_id: boundary
            for boundary in list_provider_oauth_boundaries(connection)
        },
        token_lifecycle_boundaries={
            boundary.provider_id: boundary
            for boundary in list_provider_token_lifecycle_boundaries(connection)
        },
        safe_audit_event_counts=_load_safe_audit_event_counts(connection),
    )


def _load_safe_audit_event_counts(connection: sqlite3.Connection) -> dict[str, int]:
    known_provider_ids = {provider.provider_id for provider in list_platform_providers()}
    rows = connection.execute(
        """
        SELECT provider_id, COUNT(*) AS event_count
        FROM provider_security_audit_events
        GROUP BY provider_id
        """
    ).fetchall()
    return {
        row["provider_id"]: int(row["event_count"])
        for row in rows
        if row["provider_id"] in known_provider_ids
    }
