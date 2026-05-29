from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import Any

from app.providers.platform_registry import SourceType, get_platform_provider


class RealProviderCapability(str, Enum):
    OAUTH = "oauth"
    TOKEN_EXCHANGE = "token_exchange"
    CREDENTIAL_STORAGE = "credential_storage"
    PUBLISH = "publish"
    PUBLISH_STATUS = "publish_status"
    METRICS_READ = "metrics_read"
    DISCONNECT = "disconnect"
    REVOKE = "revoke"


class FeatureFlagStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    MISSING = "missing"
    MALFORMED = "malformed"
    REVOKED = "revoked"
    EXPIRED = "expired"
    POLICY_DENIED = "policy_denied"


class KillSwitchStatus(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    MISSING = "missing"
    MALFORMED = "malformed"
    REVOKED = "revoked"
    EXPIRED = "expired"
    POLICY_DENIED = "policy_denied"


class RuntimeEnvironmentStatus(str, Enum):
    ALLOWED = "allowed"
    DISABLED = "disabled"
    MISSING = "missing"
    MALFORMED = "malformed"
    POLICY_DENIED = "policy_denied"


class PlatformPreconditionsStatus(str, Enum):
    ACCEPTED = "accepted"
    MISSING = "missing"
    MALFORMED = "malformed"
    EXPIRED = "expired"
    POLICY_DENIED = "policy_denied"


class RealProviderControlDecisionStatus(str, Enum):
    ALLOWED_FAKE_ONLY = "allowed_fake_only"
    ALLOWED_SANDBOX_ONLY = "allowed_sandbox_only"
    BLOCKED_REAL_PROVIDER = "blocked_real_provider"
    BLOCKED_FEATURE_FLAG_DISABLED = "blocked_feature_flag_disabled"
    BLOCKED_KILL_SWITCH_ACTIVE = "blocked_kill_switch_active"
    BLOCKED_CAPABILITY_DISABLED = "blocked_capability_disabled"
    BLOCKED_PRECONDITIONS_MISSING = "blocked_preconditions_missing"
    BLOCKED_UNSUPPORTED_PROVIDER = "blocked_unsupported_provider"
    BLOCKED_SANDBOX_FALLBACK_FORBIDDEN = "blocked_sandbox_fallback_forbidden"
    BLOCKED_OPERATION_NOT_ALLOWED = "blocked_operation_not_allowed"


@dataclass(frozen=True)
class RealProviderControlPolicy:
    feature_flag_status: str = FeatureFlagStatus.MISSING.value
    kill_switch_status: str = KillSwitchStatus.ACTIVE.value
    allowed_capabilities: frozenset[str] = frozenset()
    environment_status: str = RuntimeEnvironmentStatus.MISSING.value
    platform_preconditions_status: str = PlatformPreconditionsStatus.MISSING.value


@dataclass(frozen=True)
class RealProviderControlDecision:
    status: str
    provider_id: str | None
    source_type: str | None
    capability: str | None
    feature_flag_status: str | None
    kill_switch_status: str | None
    environment_status: str | None
    platform_preconditions_status: str | None
    real_provider_enabled: bool
    external_service_allowed: bool
    sandbox_fallback_performed: bool
    safe_status_message: str


def evaluate_real_provider_control(
    provider_id: str,
    capability: str,
    *,
    control_policy: RealProviderControlPolicy | Mapping[str, Any] | None = None,
    fallback_provider_id: str | None = None,
) -> RealProviderControlDecision:
    provider = get_platform_provider(provider_id)
    if provider is None:
        return _decision(
            RealProviderControlDecisionStatus.BLOCKED_UNSUPPORTED_PROVIDER,
            safe_status_message="Unsupported provider for real provider controls.",
        )

    parsed_capability = _parse_capability(capability)
    if parsed_capability is None:
        return _decision(
            RealProviderControlDecisionStatus.BLOCKED_OPERATION_NOT_ALLOWED,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            capability=None,
            safe_status_message="Requested capability is not allowed by real provider controls.",
        )

    if provider.source_type == SourceType.FAKE_LOCAL:
        return _decision(
            RealProviderControlDecisionStatus.ALLOWED_FAKE_ONLY,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            capability=parsed_capability.value,
            safe_status_message="Real provider controls allow only the fake-local boundary to continue.",
        )

    if provider.source_type == SourceType.SANDBOX:
        return _decision(
            RealProviderControlDecisionStatus.ALLOWED_SANDBOX_ONLY,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            capability=parsed_capability.value,
            safe_status_message="Real provider controls allow only the sandbox boundary to continue.",
        )

    policy = _coerce_policy(control_policy)

    if fallback_provider_id is not None and fallback_provider_id != provider.provider_id:
        return _decision(
            RealProviderControlDecisionStatus.BLOCKED_SANDBOX_FALLBACK_FORBIDDEN,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            capability=parsed_capability.value,
            policy=policy,
            safe_status_message="Real provider cannot fallback to another provider.",
        )

    if policy.kill_switch_status != KillSwitchStatus.INACTIVE.value:
        return _decision(
            RealProviderControlDecisionStatus.BLOCKED_KILL_SWITCH_ACTIVE,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            capability=parsed_capability.value,
            policy=policy,
            safe_status_message="Real provider kill switch blocks the requested capability.",
        )

    if policy.feature_flag_status != FeatureFlagStatus.ENABLED.value:
        return _decision(
            RealProviderControlDecisionStatus.BLOCKED_FEATURE_FLAG_DISABLED,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            capability=parsed_capability.value,
            policy=policy,
            safe_status_message="Real provider feature flag does not explicitly enable runtime behavior.",
        )

    if (
        policy.environment_status != RuntimeEnvironmentStatus.ALLOWED.value
        or policy.platform_preconditions_status != PlatformPreconditionsStatus.ACCEPTED.value
    ):
        return _decision(
            RealProviderControlDecisionStatus.BLOCKED_PRECONDITIONS_MISSING,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            capability=parsed_capability.value,
            policy=policy,
            safe_status_message="Real provider platform preconditions are missing or not accepted.",
        )

    if parsed_capability.value not in policy.allowed_capabilities:
        return _decision(
            RealProviderControlDecisionStatus.BLOCKED_CAPABILITY_DISABLED,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            capability=parsed_capability.value,
            policy=policy,
            safe_status_message="Requested real provider capability is not explicitly allowed.",
        )

    return _decision(
        RealProviderControlDecisionStatus.BLOCKED_REAL_PROVIDER,
        provider_id=provider.provider_id,
        source_type=provider.source_type.value,
        capability=parsed_capability.value,
        policy=policy,
        safe_status_message="Real provider runtime remains blocked in Batch 5.",
    )


def _parse_capability(value: str) -> RealProviderCapability | None:
    try:
        return RealProviderCapability(value)
    except ValueError:
        return None


def _coerce_policy(
    policy: RealProviderControlPolicy | Mapping[str, Any] | None,
) -> RealProviderControlPolicy:
    if policy is None:
        return RealProviderControlPolicy()
    if is_dataclass(policy):
        policy_dict = asdict(policy)
    elif isinstance(policy, Mapping):
        policy_dict = dict(policy)
    else:
        return RealProviderControlPolicy(
            feature_flag_status=FeatureFlagStatus.MALFORMED.value,
            kill_switch_status=KillSwitchStatus.MALFORMED.value,
            environment_status=RuntimeEnvironmentStatus.MALFORMED.value,
            platform_preconditions_status=PlatformPreconditionsStatus.MALFORMED.value,
        )

    return RealProviderControlPolicy(
        feature_flag_status=_coerce_enum_value(
            FeatureFlagStatus,
            policy_dict.get("feature_flag_status"),
            FeatureFlagStatus.MISSING.value,
            FeatureFlagStatus.MALFORMED.value,
        ),
        kill_switch_status=_coerce_enum_value(
            KillSwitchStatus,
            policy_dict.get("kill_switch_status"),
            KillSwitchStatus.MISSING.value,
            KillSwitchStatus.MALFORMED.value,
        ),
        allowed_capabilities=_coerce_allowed_capabilities(policy_dict.get("allowed_capabilities")),
        environment_status=_coerce_enum_value(
            RuntimeEnvironmentStatus,
            policy_dict.get("environment_status"),
            RuntimeEnvironmentStatus.MISSING.value,
            RuntimeEnvironmentStatus.MALFORMED.value,
        ),
        platform_preconditions_status=_coerce_enum_value(
            PlatformPreconditionsStatus,
            policy_dict.get("platform_preconditions_status"),
            PlatformPreconditionsStatus.MISSING.value,
            PlatformPreconditionsStatus.MALFORMED.value,
        ),
    )


def _coerce_enum_value(
    enum_type: type[Enum],
    value: Any,
    missing_value: str,
    malformed_value: str,
) -> str:
    if value is None:
        return missing_value
    if isinstance(value, Enum):
        value = value.value
    if not isinstance(value, str):
        return malformed_value
    normalized_value = value.strip().lower()
    for member in enum_type:
        if member.value == normalized_value:
            return member.value
    return malformed_value


def _coerce_allowed_capabilities(value: Any) -> frozenset[str]:
    if value is None:
        return frozenset()
    if isinstance(value, str):
        values: Iterable[Any] = [value]
    elif isinstance(value, Iterable):
        values = value
    else:
        return frozenset()

    allowed: set[str] = set()
    for item in values:
        if isinstance(item, Enum):
            item = item.value
        if isinstance(item, str):
            capability = _parse_capability(item.strip().lower())
            if capability is not None:
                allowed.add(capability.value)
    return frozenset(allowed)


def _decision(
    status: RealProviderControlDecisionStatus,
    *,
    provider_id: str | None = None,
    source_type: str | None = None,
    capability: str | None = None,
    policy: RealProviderControlPolicy | None = None,
    safe_status_message: str,
) -> RealProviderControlDecision:
    return RealProviderControlDecision(
        status=status.value,
        provider_id=provider_id,
        source_type=source_type,
        capability=capability,
        feature_flag_status=policy.feature_flag_status if policy else None,
        kill_switch_status=policy.kill_switch_status if policy else None,
        environment_status=policy.environment_status if policy else None,
        platform_preconditions_status=policy.platform_preconditions_status if policy else None,
        real_provider_enabled=False,
        external_service_allowed=False,
        sandbox_fallback_performed=False,
        safe_status_message=safe_status_message,
    )
