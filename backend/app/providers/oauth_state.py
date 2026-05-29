import hashlib
import re
import secrets
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from app.providers.platform_registry import get_platform_provider


DEFAULT_STATE_TTL_SECONDS = 600

_STATE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{16,512}$")
_STATE_SELECT_COLUMNS = (
    "oauth_state_id",
    "provider_id",
    "source_type",
    "state_digest",
    "state_status",
    "purpose",
    "created_at",
    "expires_at",
    "consumed_at",
    "updated_at",
    "safe_status_message",
    "last_status_change_reason",
)


class OAuthStateStorageStatus(str, Enum):
    PENDING = "pending"
    CONSUMED = "consumed"
    EXPIRED = "expired"
    REVOKED = "revoked"


class OAuthStateResultStatus(str, Enum):
    CREATED = "created"
    VALID_CONSUMED = "valid_consumed"
    INVALID_MISSING_STATE = "invalid_missing_state"
    INVALID_MALFORMED_STATE = "invalid_malformed_state"
    INVALID_PROVIDER_MISMATCH = "invalid_provider_mismatch"
    INVALID_REPLAYED_STATE = "invalid_replayed_state"
    INVALID_EXPIRED_STATE = "invalid_expired_state"
    INVALID_REVOKED_STATE = "invalid_revoked_state"
    UNSUPPORTED_PROVIDER = "unsupported_provider"


@dataclass(frozen=True)
class OAuthStateRecord:
    oauth_state_id: str
    provider_id: str
    source_type: str
    state_digest: str
    state_status: str
    purpose: str
    created_at: str
    expires_at: str
    consumed_at: str | None
    updated_at: str
    safe_status_message: str
    last_status_change_reason: str


@dataclass(frozen=True)
class OAuthStateCreateResult:
    status: str
    provider_id: str | None
    source_type: str | None
    raw_state: str | None
    oauth_state_id: str | None
    state_digest: str | None
    expires_at: str | None
    safe_status_message: str


@dataclass(frozen=True)
class OAuthStateConsumeResult:
    status: str
    provider_id: str | None
    source_type: str | None
    oauth_state_id: str | None
    safe_status_message: str


def create_oauth_state_metadata(
    connection: sqlite3.Connection,
    provider_id: str,
    *,
    ttl_seconds: int = DEFAULT_STATE_TTL_SECONDS,
    now: datetime | None = None,
) -> OAuthStateCreateResult:
    provider = get_platform_provider(provider_id)
    if provider is None:
        return OAuthStateCreateResult(
            status=OAuthStateResultStatus.UNSUPPORTED_PROVIDER.value,
            provider_id=None,
            source_type=None,
            raw_state=None,
            oauth_state_id=None,
            state_digest=None,
            expires_at=None,
            safe_status_message="Unsupported provider for OAuth state foundation.",
        )

    created_at = _format_timestamp(now or _utc_now())
    expires_at = _format_timestamp((now or _utc_now()) + timedelta(seconds=ttl_seconds))
    raw_state = secrets.token_urlsafe(32)
    state_digest = digest_oauth_state(raw_state)
    oauth_state_id = uuid.uuid4().hex
    safe_status_message = "OAuth state metadata created with digest-only persistence."

    connection.execute(
        """
        INSERT INTO provider_oauth_states (
            oauth_state_id, provider_id, source_type, state_digest, state_status,
            purpose, created_at, expires_at, updated_at, safe_status_message,
            last_status_change_reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            oauth_state_id,
            provider.provider_id,
            provider.source_type.value,
            state_digest,
            OAuthStateStorageStatus.PENDING.value,
            "authorization",
            created_at,
            expires_at,
            created_at,
            safe_status_message,
            "initial_state_created",
        ),
    )
    connection.commit()

    return OAuthStateCreateResult(
        status=OAuthStateResultStatus.CREATED.value,
        provider_id=provider.provider_id,
        source_type=provider.source_type.value,
        raw_state=raw_state,
        oauth_state_id=oauth_state_id,
        state_digest=state_digest,
        expires_at=expires_at,
        safe_status_message=safe_status_message,
    )


def consume_oauth_state_once(
    connection: sqlite3.Connection,
    provider_id: str,
    raw_state: str | None,
    *,
    now: datetime | None = None,
) -> OAuthStateConsumeResult:
    provider = get_platform_provider(provider_id)
    if provider is None:
        return _consume_result(
            OAuthStateResultStatus.UNSUPPORTED_PROVIDER,
            safe_status_message="Unsupported provider for OAuth state validation.",
        )

    if raw_state is None or raw_state.strip() == "":
        return _consume_result(
            OAuthStateResultStatus.INVALID_MISSING_STATE,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            safe_status_message="OAuth state is missing.",
        )

    if not is_well_formed_oauth_state(raw_state):
        return _consume_result(
            OAuthStateResultStatus.INVALID_MALFORMED_STATE,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            safe_status_message="OAuth state is malformed or unknown.",
        )

    state_digest = digest_oauth_state(raw_state)
    record = _get_state_record_by_digest(connection, state_digest)
    if record is None:
        return _consume_result(
            OAuthStateResultStatus.INVALID_MALFORMED_STATE,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            safe_status_message="OAuth state is malformed or unknown.",
        )

    if record.provider_id != provider.provider_id:
        return _consume_result(
            OAuthStateResultStatus.INVALID_PROVIDER_MISMATCH,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            oauth_state_id=record.oauth_state_id,
            safe_status_message="OAuth state does not match the requested provider.",
        )

    checked_at = _format_timestamp(now or _utc_now())
    if record.state_status == OAuthStateStorageStatus.CONSUMED.value:
        return _consume_result(
            OAuthStateResultStatus.INVALID_REPLAYED_STATE,
            provider_id=record.provider_id,
            source_type=record.source_type,
            oauth_state_id=record.oauth_state_id,
            safe_status_message="OAuth state was already consumed.",
        )

    if record.state_status == OAuthStateStorageStatus.REVOKED.value:
        return _consume_result(
            OAuthStateResultStatus.INVALID_REVOKED_STATE,
            provider_id=record.provider_id,
            source_type=record.source_type,
            oauth_state_id=record.oauth_state_id,
            safe_status_message="OAuth state is no longer valid.",
        )

    if record.state_status == OAuthStateStorageStatus.EXPIRED.value or (
        record.state_status == OAuthStateStorageStatus.PENDING.value
        and record.expires_at <= checked_at
    ):
        _mark_state_expired(connection, record.oauth_state_id, checked_at)
        return _consume_result(
            OAuthStateResultStatus.INVALID_EXPIRED_STATE,
            provider_id=record.provider_id,
            source_type=record.source_type,
            oauth_state_id=record.oauth_state_id,
            safe_status_message="OAuth state is expired.",
        )

    cursor = connection.execute(
        """
        UPDATE provider_oauth_states
        SET state_status = ?, consumed_at = ?, updated_at = ?,
            safe_status_message = ?,
            last_status_change_reason = ?
        WHERE state_digest = ?
          AND provider_id = ?
          AND state_status = ?
          AND expires_at > ?
        """,
        (
            OAuthStateStorageStatus.CONSUMED.value,
            checked_at,
            checked_at,
            "OAuth state was consumed once.",
            "state_consumed_once",
            state_digest,
            provider.provider_id,
            OAuthStateStorageStatus.PENDING.value,
            checked_at,
        ),
    )
    connection.commit()

    if cursor.rowcount != 1:
        refreshed = _get_state_record_by_digest(connection, state_digest)
        if refreshed is not None and refreshed.state_status == OAuthStateStorageStatus.CONSUMED.value:
            return _consume_result(
                OAuthStateResultStatus.INVALID_REPLAYED_STATE,
                provider_id=refreshed.provider_id,
                source_type=refreshed.source_type,
                oauth_state_id=refreshed.oauth_state_id,
                safe_status_message="OAuth state was already consumed.",
            )
        return _consume_result(
            OAuthStateResultStatus.INVALID_MALFORMED_STATE,
            provider_id=provider.provider_id,
            source_type=provider.source_type.value,
            safe_status_message="OAuth state could not be consumed.",
        )

    return _consume_result(
        OAuthStateResultStatus.VALID_CONSUMED,
        provider_id=record.provider_id,
        source_type=record.source_type,
        oauth_state_id=record.oauth_state_id,
        safe_status_message="OAuth state was consumed once.",
    )


def mark_expired_oauth_states(
    connection: sqlite3.Connection,
    *,
    now: datetime | None = None,
) -> int:
    checked_at = _format_timestamp(now or _utc_now())
    cursor = connection.execute(
        """
        UPDATE provider_oauth_states
        SET state_status = ?, updated_at = ?, safe_status_message = ?,
            last_status_change_reason = ?
        WHERE state_status = ? AND expires_at <= ?
        """,
        (
            OAuthStateStorageStatus.EXPIRED.value,
            checked_at,
            "OAuth state is expired.",
            "expired_state_marked",
            OAuthStateStorageStatus.PENDING.value,
            checked_at,
        ),
    )
    connection.commit()
    return int(cursor.rowcount)


def digest_oauth_state(raw_state: str) -> str:
    return hashlib.sha256(raw_state.encode("utf-8")).hexdigest()


def is_well_formed_oauth_state(raw_state: str) -> bool:
    return bool(_STATE_PATTERN.fullmatch(raw_state))


def _get_state_record_by_digest(
    connection: sqlite3.Connection,
    state_digest: str,
) -> OAuthStateRecord | None:
    columns = ", ".join(_STATE_SELECT_COLUMNS)
    row = connection.execute(
        f"""
        SELECT {columns}
        FROM provider_oauth_states
        WHERE state_digest = ?
        """,
        (state_digest,),
    ).fetchone()
    if row is None:
        return None
    return _record_from_row(row)


def _mark_state_expired(
    connection: sqlite3.Connection,
    oauth_state_id: str,
    checked_at: str,
) -> None:
    connection.execute(
        """
        UPDATE provider_oauth_states
        SET state_status = ?, updated_at = ?, safe_status_message = ?,
            last_status_change_reason = ?
        WHERE oauth_state_id = ? AND state_status = ?
        """,
        (
            OAuthStateStorageStatus.EXPIRED.value,
            checked_at,
            "OAuth state is expired.",
            "expired_state_rejected",
            oauth_state_id,
            OAuthStateStorageStatus.PENDING.value,
        ),
    )
    connection.commit()


def _consume_result(
    status: OAuthStateResultStatus,
    *,
    provider_id: str | None = None,
    source_type: str | None = None,
    oauth_state_id: str | None = None,
    safe_status_message: str,
) -> OAuthStateConsumeResult:
    return OAuthStateConsumeResult(
        status=status.value,
        provider_id=provider_id,
        source_type=source_type,
        oauth_state_id=oauth_state_id,
        safe_status_message=safe_status_message,
    )


def _record_from_row(row: sqlite3.Row | tuple[Any, ...]) -> OAuthStateRecord:
    values = {
        column: row[column] if isinstance(row, sqlite3.Row) else row[index]
        for index, column in enumerate(_STATE_SELECT_COLUMNS)
    }
    return OAuthStateRecord(**values)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
