import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.providers.oauth_state import (
    OAuthStateResultStatus,
    consume_oauth_state_once,
)
from app.providers.platform_registry import SourceType, get_platform_provider


_FAKE_AUTHORIZATION_CODE_PATTERN = re.compile(r"^fake_[A-Za-z0-9_-]{12,256}$")


class TokenExchangeResultStatus(str, Enum):
    EXCHANGE_SIMULATED = "exchange_simulated"
    STATE_VALIDATION_FAILED = "state_validation_failed"
    AUTHORIZATION_CODE_MISSING = "authorization_code_missing"
    AUTHORIZATION_CODE_MALFORMED = "authorization_code_malformed"
    UNSUPPORTED_PROVIDER = "unsupported_provider"
    REAL_PROVIDER_DISABLED = "real_provider_disabled"
    EXTERNAL_EXCHANGE_BLOCKED = "external_exchange_blocked"
    CREDENTIAL_STORAGE_REQUIRED = "credential_storage_required"


@dataclass(frozen=True)
class TokenExchangeBoundaryResult:
    status: str
    provider_id: str | None
    source_type: str | None
    state_validation_status: str | None
    oauth_state_id: str | None
    token_received_boolean: bool
    credential_storage_required_boolean: bool
    external_exchange_performed: bool
    exchange_attempted: bool
    sandbox_fallback_performed: bool
    safe_status_message: str


def simulate_token_exchange_boundary(
    connection: sqlite3.Connection,
    provider_id: str,
    *,
    raw_state: str | None,
    authorization_code: str | None,
    now: datetime | None = None,
) -> TokenExchangeBoundaryResult:
    provider = get_platform_provider(provider_id)
    if provider is None:
        return _result(
            TokenExchangeResultStatus.UNSUPPORTED_PROVIDER,
            safe_status_message="Unsupported provider for token exchange boundary.",
        )

    if authorization_code is None or authorization_code.strip() == "":
        return _result(
            TokenExchangeResultStatus.AUTHORIZATION_CODE_MISSING,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            safe_status_message="Authorization code is missing.",
        )

    if not _is_obvious_fake_authorization_code(authorization_code):
        return _result(
            TokenExchangeResultStatus.AUTHORIZATION_CODE_MALFORMED,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            safe_status_message="Authorization code is malformed for fake-gated exchange.",
        )

    if provider.source_type == SourceType.REAL:
        return _result(
            TokenExchangeResultStatus.REAL_PROVIDER_DISABLED,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            safe_status_message="Real provider token exchange is disabled.",
        )

    state_result = consume_oauth_state_once(
        connection, provider.provider_id, raw_state, now=now
    )
    if state_result.status != OAuthStateResultStatus.VALID_CONSUMED.value:
        return _result(
            TokenExchangeResultStatus.STATE_VALIDATION_FAILED,
            provider_id=state_result.provider_id or provider.provider_id,
            source_type=state_result.source_type or provider.source_type.value,
            state_validation_status=state_result.status,
            oauth_state_id=state_result.oauth_state_id,
            safe_status_message="Token exchange boundary stopped at state validation.",
        )

    if provider.source_type not in {SourceType.FAKE_LOCAL, SourceType.SANDBOX}:
        return _result(
            TokenExchangeResultStatus.EXTERNAL_EXCHANGE_BLOCKED,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            state_validation_status=state_result.status,
            oauth_state_id=state_result.oauth_state_id,
            safe_status_message="External token exchange is blocked.",
        )

    return _result(
        TokenExchangeResultStatus.EXCHANGE_SIMULATED,
        provider_id=provider.provider_id,
        source_type=provider.source_type.value,
        state_validation_status=state_result.status,
        oauth_state_id=state_result.oauth_state_id,
        token_received_boolean=True,
        credential_storage_required_boolean=True,
        exchange_attempted=True,
        safe_status_message=(
            "Fake-gated token exchange simulated with metadata-only result; "
            "credential storage remains required."
        ),
    )


def _is_obvious_fake_authorization_code(value: str) -> bool:
    return bool(_FAKE_AUTHORIZATION_CODE_PATTERN.fullmatch(value))


def _result(
    status: TokenExchangeResultStatus,
    *,
    provider_id: str | None = None,
    source_type: str | None = None,
    state_validation_status: str | None = None,
    oauth_state_id: str | None = None,
    token_received_boolean: bool = False,
    credential_storage_required_boolean: bool = False,
    external_exchange_performed: bool = False,
    exchange_attempted: bool = False,
    sandbox_fallback_performed: bool = False,
    safe_status_message: str,
) -> TokenExchangeBoundaryResult:
    return TokenExchangeBoundaryResult(
        status=status.value,
        provider_id=provider_id,
        source_type=source_type,
        state_validation_status=state_validation_status,
        oauth_state_id=oauth_state_id,
        token_received_boolean=token_received_boolean,
        credential_storage_required_boolean=credential_storage_required_boolean,
        external_exchange_performed=external_exchange_performed,
        exchange_attempted=exchange_attempted,
        sandbox_fallback_performed=sandbox_fallback_performed,
        safe_status_message=safe_status_message,
    )
