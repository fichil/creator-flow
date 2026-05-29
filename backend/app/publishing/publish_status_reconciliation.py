import sqlite3
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from fastapi import status

from app.providers.platform_registry import SourceType, get_platform_provider
from app.providers.real_provider_controls import (
    RealProviderCapability,
    RealProviderControlDecisionStatus,
    RealProviderControlPolicy,
    evaluate_real_provider_control,
)
from app.publishing.publish_intent import SENSITIVE_METADATA_MARKERS


class PublishStatusReconciliationResultCategory(str, Enum):
    STATUS_RECONCILIATION_CREATED = "status_reconciliation_created"
    STATUS_RECONCILIATION_BLOCKED = "status_reconciliation_blocked"
    PUBLISH_ATTEMPT_REQUIRED = "publish_attempt_required"
    PUBLISH_ATTEMPT_NOT_READY = "publish_attempt_not_ready"
    DUPLICATE_RECONCILIATION = "duplicate_reconciliation"
    STALE_STATUS_IGNORED = "stale_status_ignored"
    STATUS_SNAPSHOT_CREATED = "status_snapshot_created"
    UNSUPPORTED_PROVIDER = "unsupported_provider"
    REAL_PROVIDER_DISABLED = "real_provider_disabled"
    KILL_SWITCH_ACTIVE = "kill_switch_active"
    PLATFORM_PRECONDITIONS_MISSING = "platform_preconditions_missing"
    SANDBOX_FALLBACK_FORBIDDEN = "sandbox_fallback_forbidden"
    EXTERNAL_STATUS_QUERY_BLOCKED = "external_status_query_blocked"
    STATUS_FIXTURE_INVALID = "status_fixture_invalid"


class LocalPublishStatus(str, Enum):
    LOCAL_PENDING = "local_pending"
    LOCAL_BLOCKED = "local_blocked"
    LOCAL_ATTEMPT_CREATED = "local_attempt_created"
    LOCAL_STATUS_UNKNOWN = "local_status_unknown"
    LOCAL_STATUS_RECONCILED = "local_status_reconciled"
    LOCAL_FAILED_SAFE = "local_failed_safe"
    LOCAL_CANCELLED = "local_cancelled"


class StatusSource(str, Enum):
    LOCAL = "local"
    FAKE_FIXTURE = "fake_fixture"
    SANDBOX_FIXTURE = "sandbox_fixture"


FORBIDDEN_STATUS_MARKERS = SENSITIVE_METADATA_MARKERS + (
    "status_response",
    "external_response",
    "douyin_response",
    "metrics_response",
)


@dataclass(frozen=True)
class PublishStatusReconciliationError(Exception):
    status_code: int
    category: str
    safe_status_message: str


@dataclass(frozen=True)
class _StatusFixture:
    local_publish_status: str
    status_observed_at: str
    status_source: str
    safe_status_message: str


def create_publish_status_reconciliation(
    db: sqlite3.Connection,
    *,
    project_id: int,
    publish_attempt_id: int,
    external_status_query_requested: bool | None = False,
    fallback_provider_id: str | None = None,
    fake_status_fixture: Mapping[str, Any] | None = None,
    real_provider_control_policy: RealProviderControlPolicy | Mapping[str, Any] | None = None,
) -> dict:
    attempt = _get_publish_attempt(db, project_id, publish_attempt_id)
    provider = get_platform_provider(attempt["provider_id"])
    if provider is None:
        _raise(
            status.HTTP_409_CONFLICT,
            PublishStatusReconciliationResultCategory.UNSUPPORTED_PROVIDER,
            "Unsupported provider for publish status reconciliation.",
        )

    if fallback_provider_id is not None and fallback_provider_id != provider.provider_id:
        _raise(
            status.HTTP_409_CONFLICT,
            PublishStatusReconciliationResultCategory.SANDBOX_FALLBACK_FORBIDDEN,
            "Provider fallback is forbidden for publish status reconciliation.",
        )

    if attempt["source_type"] != provider.source_type.value:
        _raise(
            status.HTTP_409_CONFLICT,
            PublishStatusReconciliationResultCategory.SANDBOX_FALLBACK_FORBIDDEN,
            "Publish attempt provider source mismatch is blocked.",
        )

    if external_status_query_requested is True:
        _raise(
            status.HTTP_409_CONFLICT,
            PublishStatusReconciliationResultCategory.EXTERNAL_STATUS_QUERY_BLOCKED,
            "External provider status query is blocked in Batch 8.",
        )

    if attempt["attempt_status"] != "created":
        _raise(
            status.HTTP_409_CONFLICT,
            PublishStatusReconciliationResultCategory.PUBLISH_ATTEMPT_NOT_READY,
            "Publish status reconciliation requires an active metadata-only publish attempt.",
        )

    if attempt["guard_status"] != "passed_simulated":
        _raise(
            status.HTTP_409_CONFLICT,
            PublishStatusReconciliationResultCategory.STATUS_RECONCILIATION_BLOCKED,
            "Publish attempt guard status blocks local status reconciliation.",
        )

    if provider.source_type == SourceType.REAL:
        _enforce_real_provider_controls(
            provider.provider_id,
            fallback_provider_id=fallback_provider_id,
            real_provider_control_policy=real_provider_control_policy,
        )

    _ensure_no_active_reconciliation(db, publish_attempt_id)
    fixture = _coerce_status_fixture(fake_status_fixture, provider.source_type)
    latest_snapshot = _get_latest_snapshot(db, publish_attempt_id)
    if latest_snapshot is not None and fixture.status_observed_at <= latest_snapshot["status_observed_at"]:
        return _record_stale_reconciliation(db, attempt, latest_snapshot)

    reconciliation_id = f"psr_{uuid.uuid4().hex}"
    status_snapshot_id = f"pss_{uuid.uuid4().hex}"
    safe_message = (
        "Local status reconciliation recorded metadata only; no external provider "
        "status query, upload, publish, schedule, or metrics read was executed."
    )
    db.execute(
        """
        INSERT INTO publish_status_reconciliations (
            reconciliation_id, publish_attempt_id, publish_intent_id, review_item_id,
            provider_id, source_type, reconciliation_status, local_publish_status,
            external_query_status, safe_status_message, last_status_change_reason
        )
        VALUES (?, ?, ?, ?, ?, ?, 'created', ?, 'not_called', ?, ?)
        """,
        (
            reconciliation_id,
            attempt["id"],
            attempt["publish_intent_id"],
            attempt["review_draft_id"],
            attempt["provider_id"],
            attempt["source_type"],
            fixture.local_publish_status,
            safe_message,
            "batch8_status_reconciliation_created",
        ),
    )
    db.execute(
        """
        INSERT INTO publish_status_snapshots (
            status_snapshot_id, publish_attempt_id, reconciliation_id, provider_id,
            source_type, local_publish_status, status_observed_at, status_source,
            safe_status_message
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            status_snapshot_id,
            attempt["id"],
            reconciliation_id,
            attempt["provider_id"],
            attempt["source_type"],
            fixture.local_publish_status,
            fixture.status_observed_at,
            fixture.status_source,
            fixture.safe_status_message,
        ),
    )
    db.commit()
    result = get_publish_status_reconciliation(
        db,
        project_id=project_id,
        reconciliation_id=reconciliation_id,
    )
    result["result_category"] = PublishStatusReconciliationResultCategory.STATUS_RECONCILIATION_CREATED.value
    return result


def list_publish_status_reconciliations(db: sqlite3.Connection, *, project_id: int) -> list[dict]:
    rows = db.execute(
        """
        SELECT publish_status_reconciliations.reconciliation_id,
               publish_status_reconciliations.publish_attempt_id,
               publish_status_reconciliations.publish_intent_id,
               publish_status_reconciliations.review_item_id,
               publish_status_reconciliations.provider_id,
               publish_status_reconciliations.source_type,
               publish_status_reconciliations.reconciliation_status,
               publish_status_reconciliations.local_publish_status,
               publish_status_reconciliations.external_query_status,
               publish_status_reconciliations.created_at,
               publish_status_reconciliations.updated_at,
               publish_status_reconciliations.completed_at,
               publish_status_reconciliations.safe_status_message,
               publish_status_reconciliations.last_status_change_reason
        FROM publish_status_reconciliations
        JOIN publish_attempts
          ON publish_attempts.id = publish_status_reconciliations.publish_attempt_id
        WHERE publish_attempts.project_id = ?
        ORDER BY publish_status_reconciliations.created_at DESC,
                 publish_status_reconciliations.reconciliation_id DESC
        """,
        (project_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def get_publish_status_reconciliation(
    db: sqlite3.Connection,
    *,
    project_id: int,
    reconciliation_id: str,
) -> dict:
    row = db.execute(
        """
        SELECT publish_status_reconciliations.reconciliation_id,
               publish_status_reconciliations.publish_attempt_id,
               publish_status_reconciliations.publish_intent_id,
               publish_status_reconciliations.review_item_id,
               publish_status_reconciliations.provider_id,
               publish_status_reconciliations.source_type,
               publish_status_reconciliations.reconciliation_status,
               publish_status_reconciliations.local_publish_status,
               publish_status_reconciliations.external_query_status,
               publish_status_reconciliations.created_at,
               publish_status_reconciliations.updated_at,
               publish_status_reconciliations.completed_at,
               publish_status_reconciliations.safe_status_message,
               publish_status_reconciliations.last_status_change_reason
        FROM publish_status_reconciliations
        JOIN publish_attempts
          ON publish_attempts.id = publish_status_reconciliations.publish_attempt_id
        WHERE publish_status_reconciliations.reconciliation_id = ?
          AND publish_attempts.project_id = ?
        """,
        (reconciliation_id, project_id),
    ).fetchone()
    if row is None:
        _raise(
            status.HTTP_404_NOT_FOUND,
            PublishStatusReconciliationResultCategory.PUBLISH_ATTEMPT_REQUIRED,
            "Publish status reconciliation not found.",
        )
    return dict(row)


def list_publish_status_snapshots(
    db: sqlite3.Connection,
    *,
    project_id: int,
    publish_attempt_id: int,
) -> list[dict]:
    _get_publish_attempt(db, project_id, publish_attempt_id)
    rows = db.execute(
        """
        SELECT status_snapshot_id, publish_attempt_id, reconciliation_id, provider_id,
               source_type, local_publish_status, status_observed_at, status_source,
               created_at, safe_status_message
        FROM publish_status_snapshots
        WHERE publish_attempt_id = ?
        ORDER BY status_observed_at DESC, status_snapshot_id DESC
        """,
        (publish_attempt_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def _enforce_real_provider_controls(
    provider_id: str,
    *,
    fallback_provider_id: str | None,
    real_provider_control_policy: RealProviderControlPolicy | Mapping[str, Any] | None,
) -> None:
    decision = evaluate_real_provider_control(
        provider_id,
        RealProviderCapability.PUBLISH_STATUS.value,
        control_policy=real_provider_control_policy,
        fallback_provider_id=fallback_provider_id,
    )
    if decision.status == RealProviderControlDecisionStatus.BLOCKED_SANDBOX_FALLBACK_FORBIDDEN.value:
        _raise(
            status.HTTP_409_CONFLICT,
            PublishStatusReconciliationResultCategory.SANDBOX_FALLBACK_FORBIDDEN,
            "Real provider fallback to sandbox is forbidden.",
        )
    if decision.status == RealProviderControlDecisionStatus.BLOCKED_KILL_SWITCH_ACTIVE.value:
        _raise(
            status.HTTP_409_CONFLICT,
            PublishStatusReconciliationResultCategory.KILL_SWITCH_ACTIVE,
            "Real provider kill switch blocks publish status reconciliation.",
        )
    if decision.status == RealProviderControlDecisionStatus.BLOCKED_PRECONDITIONS_MISSING.value:
        _raise(
            status.HTTP_409_CONFLICT,
            PublishStatusReconciliationResultCategory.PLATFORM_PRECONDITIONS_MISSING,
            "Real provider platform preconditions are missing or not accepted.",
        )
    if decision.status == RealProviderControlDecisionStatus.BLOCKED_UNSUPPORTED_PROVIDER.value:
        _raise(
            status.HTTP_409_CONFLICT,
            PublishStatusReconciliationResultCategory.UNSUPPORTED_PROVIDER,
            "Unsupported provider for publish status reconciliation.",
        )
    _raise(
        status.HTTP_409_CONFLICT,
        PublishStatusReconciliationResultCategory.REAL_PROVIDER_DISABLED,
        "Real provider publish status reconciliation remains disabled by feature flag / kill switch controls.",
    )


def _get_publish_attempt(db: sqlite3.Connection, project_id: int, publish_attempt_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, publish_intent_id, review_draft_id, provider_id,
               source_type, attempt_status, guard_status, external_call_status,
               safe_status_message, last_status_change_reason
        FROM publish_attempts
        WHERE id = ? AND project_id = ?
        """,
        (publish_attempt_id, project_id),
    ).fetchone()
    if row is None:
        _raise(
            status.HTTP_404_NOT_FOUND,
            PublishStatusReconciliationResultCategory.PUBLISH_ATTEMPT_REQUIRED,
            "Publish status reconciliation requires an existing publish attempt.",
        )
    return dict(row)


def _ensure_no_active_reconciliation(db: sqlite3.Connection, publish_attempt_id: int) -> None:
    row = db.execute(
        """
        SELECT reconciliation_id
        FROM publish_status_reconciliations
        WHERE publish_attempt_id = ?
          AND reconciliation_status = 'created'
        LIMIT 1
        """,
        (publish_attempt_id,),
    ).fetchone()
    if row is not None:
        _raise(
            status.HTTP_409_CONFLICT,
            PublishStatusReconciliationResultCategory.DUPLICATE_RECONCILIATION,
            "An active local status reconciliation already exists for this publish attempt.",
        )


def _get_latest_snapshot(db: sqlite3.Connection, publish_attempt_id: int) -> sqlite3.Row | None:
    return db.execute(
        """
        SELECT status_snapshot_id, local_publish_status, status_observed_at
        FROM publish_status_snapshots
        WHERE publish_attempt_id = ?
        ORDER BY status_observed_at DESC, status_snapshot_id DESC
        LIMIT 1
        """,
        (publish_attempt_id,),
    ).fetchone()


def _record_stale_reconciliation(
    db: sqlite3.Connection,
    attempt: dict,
    latest_snapshot: sqlite3.Row,
) -> dict:
    reconciliation_id = f"psr_{uuid.uuid4().hex}"
    db.execute(
        """
        INSERT INTO publish_status_reconciliations (
            reconciliation_id, publish_attempt_id, publish_intent_id, review_item_id,
            provider_id, source_type, reconciliation_status, local_publish_status,
            external_query_status, completed_at, safe_status_message,
            last_status_change_reason
        )
        VALUES (?, ?, ?, ?, ?, ?, 'completed_safe', ?, 'not_called',
                CURRENT_TIMESTAMP, ?, 'stale_status_ignored')
        """,
        (
            reconciliation_id,
            attempt["id"],
            attempt["publish_intent_id"],
            attempt["review_draft_id"],
            attempt["provider_id"],
            attempt["source_type"],
            latest_snapshot["local_publish_status"],
            "Stale local status update ignored; existing newer metadata-only snapshot retained.",
        ),
    )
    db.commit()
    result = get_publish_status_reconciliation(
        db,
        project_id=attempt["project_id"],
        reconciliation_id=reconciliation_id,
    )
    result["result_category"] = PublishStatusReconciliationResultCategory.STALE_STATUS_IGNORED.value
    return result


def _coerce_status_fixture(
    fixture: Mapping[str, Any] | None,
    provider_source_type: SourceType,
) -> _StatusFixture:
    if fixture is None:
        return _StatusFixture(
            local_publish_status=LocalPublishStatus.LOCAL_STATUS_UNKNOWN.value,
            status_observed_at=_now_utc(),
            status_source=StatusSource.LOCAL.value,
            safe_status_message=(
                "Local publish status snapshot created from metadata-only attempt; "
                "no provider status query was called."
            ),
        )
    if not isinstance(fixture, Mapping):
        _invalid_fixture()

    local_publish_status = _coerce_enum_value(LocalPublishStatus, fixture.get("local_publish_status"))
    status_source = _coerce_enum_value(StatusSource, fixture.get("status_source"))
    status_observed_at = _coerce_observed_at(fixture.get("status_observed_at"))
    safe_status_message = fixture.get("safe_status_message")
    if (
        local_publish_status is None
        or status_source is None
        or status_observed_at is None
        or not isinstance(safe_status_message, str)
        or not safe_status_message.strip()
        or _contains_forbidden_marker(safe_status_message)
    ):
        _invalid_fixture()

    if status_source == StatusSource.SANDBOX_FIXTURE.value and provider_source_type != SourceType.SANDBOX:
        _invalid_fixture()
    if status_source == StatusSource.FAKE_FIXTURE.value and provider_source_type == SourceType.REAL:
        _invalid_fixture()

    return _StatusFixture(
        local_publish_status=local_publish_status,
        status_observed_at=status_observed_at,
        status_source=status_source,
        safe_status_message=safe_status_message.strip(),
    )


def _coerce_enum_value(enum_type: type[Enum], value: Any) -> str | None:
    if isinstance(value, Enum):
        value = value.value
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    for item in enum_type:
        if item.value == normalized:
            return item.value
    return None


def _coerce_observed_at(value: Any) -> str | None:
    if value is None:
        return _now_utc()
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _contains_forbidden_marker(value: str) -> bool:
    rendered = value.lower()
    return any(marker in rendered for marker in FORBIDDEN_STATUS_MARKERS)


def _invalid_fixture() -> None:
    _raise(
        422,
        PublishStatusReconciliationResultCategory.STATUS_FIXTURE_INVALID,
        "Fake or sandbox status fixture is invalid for metadata-only reconciliation.",
    )


def _raise(
    status_code: int,
    category: PublishStatusReconciliationResultCategory,
    safe_status_message: str,
) -> None:
    raise PublishStatusReconciliationError(status_code, category.value, safe_status_message)
