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


class LimitedMetricsReadResultCategory(str, Enum):
    METRICS_SNAPSHOT_CREATED = "metrics_snapshot_created"
    METRICS_READ_BLOCKED = "metrics_read_blocked"
    PUBLISH_STATUS_REQUIRED = "publish_status_required"
    PUBLISH_NOT_READY_FOR_METRICS = "publish_not_ready_for_metrics"
    METRICS_PERMISSION_MISSING = "metrics_permission_missing"
    METRICS_FRESHNESS_UNKNOWN = "metrics_freshness_unknown"
    REAL_PROVIDER_DISABLED = "real_provider_disabled"
    KILL_SWITCH_ACTIVE = "kill_switch_active"
    PLATFORM_PRECONDITIONS_MISSING = "platform_preconditions_missing"
    UNSUPPORTED_PROVIDER = "unsupported_provider"
    SANDBOX_FALLBACK_FORBIDDEN = "sandbox_fallback_forbidden"
    EXTERNAL_METRICS_QUERY_BLOCKED = "external_metrics_query_blocked"
    METRICS_FIXTURE_INVALID = "metrics_fixture_invalid"


class MetricsSource(str, Enum):
    LOCAL = "local"
    FAKE_FIXTURE = "fake_fixture"
    SANDBOX_FIXTURE = "sandbox_fixture"


class MetricsFreshnessStatus(str, Enum):
    FRESH = "fresh"
    STALE = "stale"
    UNKNOWN = "unknown"
    NOT_AVAILABLE = "not_available"


ELIGIBLE_LOCAL_PUBLISH_STATUSES = {"local_status_reconciled"}

FORBIDDEN_METRICS_MARKERS = SENSITIVE_METADATA_MARKERS + (
    "status_response",
    "metrics_response",
    "external_response",
    "douyin_response",
)


@dataclass(frozen=True)
class LimitedMetricsReadError(Exception):
    status_code: int
    category: str
    safe_status_message: str


@dataclass(frozen=True)
class _MetricsFixture:
    metrics_source: str
    metrics_freshness_status: str
    metrics_observed_at: str | None
    views_count: int | None
    likes_count: int | None
    comments_count: int | None
    shares_count: int | None
    favorites_count: int | None
    completion_rate_basis_points: int | None
    safe_status_message: str


def create_limited_metrics_snapshot(
    db: sqlite3.Connection,
    *,
    project_id: int,
    status_snapshot_id: str,
    external_metrics_query_requested: bool | None = False,
    fallback_provider_id: str | None = None,
    fake_metrics_fixture: Mapping[str, Any] | None = None,
    metrics_permission_status: str | None = "available",
    real_provider_control_policy: RealProviderControlPolicy | Mapping[str, Any] | None = None,
) -> dict:
    status_snapshot = _get_status_snapshot(db, project_id, status_snapshot_id)
    provider = get_platform_provider(status_snapshot["provider_id"])
    if provider is None:
        _raise(
            status.HTTP_409_CONFLICT,
            LimitedMetricsReadResultCategory.UNSUPPORTED_PROVIDER,
            "Unsupported provider for limited metrics read.",
        )

    if fallback_provider_id is not None and fallback_provider_id != provider.provider_id:
        _raise(
            status.HTTP_409_CONFLICT,
            LimitedMetricsReadResultCategory.SANDBOX_FALLBACK_FORBIDDEN,
            "Provider fallback is forbidden for limited metrics read.",
        )

    if status_snapshot["source_type"] != provider.source_type.value:
        _raise(
            status.HTTP_409_CONFLICT,
            LimitedMetricsReadResultCategory.SANDBOX_FALLBACK_FORBIDDEN,
            "Publish status snapshot provider source mismatch is blocked.",
        )

    if external_metrics_query_requested is True:
        _raise(
            status.HTTP_409_CONFLICT,
            LimitedMetricsReadResultCategory.EXTERNAL_METRICS_QUERY_BLOCKED,
            "External provider metrics query is blocked in Batch 9.",
        )

    if status_snapshot["local_publish_status"] not in ELIGIBLE_LOCAL_PUBLISH_STATUSES:
        _raise(
            status.HTTP_409_CONFLICT,
            LimitedMetricsReadResultCategory.PUBLISH_NOT_READY_FOR_METRICS,
            "Publish status snapshot is not eligible for limited metrics foundation.",
        )

    if provider.source_type == SourceType.REAL:
        _enforce_real_provider_controls(
            provider.provider_id,
            fallback_provider_id=fallback_provider_id,
            real_provider_control_policy=real_provider_control_policy,
        )

    if _coerce_permission_status(metrics_permission_status) != "available":
        _raise(
            status.HTTP_409_CONFLICT,
            LimitedMetricsReadResultCategory.METRICS_PERMISSION_MISSING,
            "Metrics permission metadata is missing for limited metrics foundation.",
        )

    fixture = _coerce_metrics_fixture(fake_metrics_fixture, provider.source_type)
    metrics_snapshot_id = f"pms_{uuid.uuid4().hex}"
    db.execute(
        """
        INSERT INTO publish_metrics_snapshots (
            metrics_snapshot_id, status_snapshot_id, publish_attempt_id,
            publish_intent_id, review_item_id, provider_id, source_type,
            metrics_source, metrics_freshness_status, metrics_observed_at,
            views_count, likes_count, comments_count, shares_count,
            favorites_count, completion_rate_basis_points, external_query_status,
            safe_status_message, last_status_change_reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'not_called', ?, ?)
        """,
        (
            metrics_snapshot_id,
            status_snapshot["status_snapshot_id"],
            status_snapshot["publish_attempt_id"],
            status_snapshot["publish_intent_id"],
            status_snapshot["review_item_id"],
            status_snapshot["provider_id"],
            status_snapshot["source_type"],
            fixture.metrics_source,
            fixture.metrics_freshness_status,
            fixture.metrics_observed_at,
            fixture.views_count,
            fixture.likes_count,
            fixture.comments_count,
            fixture.shares_count,
            fixture.favorites_count,
            fixture.completion_rate_basis_points,
            fixture.safe_status_message,
            "batch9_limited_metrics_snapshot_created",
        ),
    )
    db.commit()
    result = get_limited_metrics_snapshot(
        db,
        project_id=project_id,
        metrics_snapshot_id=metrics_snapshot_id,
    )
    result["result_category"] = (
        LimitedMetricsReadResultCategory.METRICS_FRESHNESS_UNKNOWN.value
        if fixture.metrics_freshness_status == MetricsFreshnessStatus.UNKNOWN.value
        else LimitedMetricsReadResultCategory.METRICS_SNAPSHOT_CREATED.value
    )
    return result


def list_limited_metrics_snapshots(db: sqlite3.Connection, *, project_id: int) -> list[dict]:
    rows = db.execute(
        """
        SELECT publish_metrics_snapshots.metrics_snapshot_id,
               publish_metrics_snapshots.status_snapshot_id,
               publish_metrics_snapshots.publish_attempt_id,
               publish_metrics_snapshots.publish_intent_id,
               publish_metrics_snapshots.review_item_id,
               publish_metrics_snapshots.provider_id,
               publish_metrics_snapshots.source_type,
               publish_metrics_snapshots.metrics_source,
               publish_metrics_snapshots.metrics_freshness_status,
               publish_metrics_snapshots.metrics_observed_at,
               publish_metrics_snapshots.views_count,
               publish_metrics_snapshots.likes_count,
               publish_metrics_snapshots.comments_count,
               publish_metrics_snapshots.shares_count,
               publish_metrics_snapshots.favorites_count,
               publish_metrics_snapshots.completion_rate_basis_points,
               publish_metrics_snapshots.external_query_status,
               publish_metrics_snapshots.created_at,
               publish_metrics_snapshots.safe_status_message,
               publish_metrics_snapshots.last_status_change_reason,
               'metrics_snapshot_created' AS result_category
        FROM publish_metrics_snapshots
        JOIN publish_attempts
          ON publish_attempts.id = publish_metrics_snapshots.publish_attempt_id
        WHERE publish_attempts.project_id = ?
        ORDER BY publish_metrics_snapshots.created_at DESC,
                 publish_metrics_snapshots.metrics_snapshot_id DESC
        """,
        (project_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def get_limited_metrics_snapshot(
    db: sqlite3.Connection,
    *,
    project_id: int,
    metrics_snapshot_id: str,
) -> dict:
    row = db.execute(
        """
        SELECT publish_metrics_snapshots.metrics_snapshot_id,
               publish_metrics_snapshots.status_snapshot_id,
               publish_metrics_snapshots.publish_attempt_id,
               publish_metrics_snapshots.publish_intent_id,
               publish_metrics_snapshots.review_item_id,
               publish_metrics_snapshots.provider_id,
               publish_metrics_snapshots.source_type,
               publish_metrics_snapshots.metrics_source,
               publish_metrics_snapshots.metrics_freshness_status,
               publish_metrics_snapshots.metrics_observed_at,
               publish_metrics_snapshots.views_count,
               publish_metrics_snapshots.likes_count,
               publish_metrics_snapshots.comments_count,
               publish_metrics_snapshots.shares_count,
               publish_metrics_snapshots.favorites_count,
               publish_metrics_snapshots.completion_rate_basis_points,
               publish_metrics_snapshots.external_query_status,
               publish_metrics_snapshots.created_at,
               publish_metrics_snapshots.safe_status_message,
               publish_metrics_snapshots.last_status_change_reason,
               'metrics_snapshot_created' AS result_category
        FROM publish_metrics_snapshots
        JOIN publish_attempts
          ON publish_attempts.id = publish_metrics_snapshots.publish_attempt_id
        WHERE publish_metrics_snapshots.metrics_snapshot_id = ?
          AND publish_attempts.project_id = ?
        """,
        (metrics_snapshot_id, project_id),
    ).fetchone()
    if row is None:
        _raise(
            status.HTTP_404_NOT_FOUND,
            LimitedMetricsReadResultCategory.PUBLISH_STATUS_REQUIRED,
            "Limited metrics snapshot not found.",
        )
    return dict(row)


def _get_status_snapshot(db: sqlite3.Connection, project_id: int, status_snapshot_id: str) -> dict:
    row = db.execute(
        """
        SELECT publish_status_snapshots.status_snapshot_id,
               publish_status_snapshots.publish_attempt_id,
               publish_status_snapshots.provider_id,
               publish_status_snapshots.source_type,
               publish_status_snapshots.local_publish_status,
               publish_status_snapshots.status_observed_at,
               publish_status_snapshots.status_source,
               publish_attempts.project_id,
               publish_attempts.publish_intent_id,
               publish_attempts.review_draft_id AS review_item_id,
               publish_attempts.attempt_status,
               publish_attempts.guard_status
        FROM publish_status_snapshots
        JOIN publish_attempts
          ON publish_attempts.id = publish_status_snapshots.publish_attempt_id
        JOIN publish_intents
          ON publish_intents.id = publish_attempts.publish_intent_id
        WHERE publish_status_snapshots.status_snapshot_id = ?
          AND publish_attempts.project_id = ?
        """,
        (status_snapshot_id, project_id),
    ).fetchone()
    if row is None:
        _raise(
            status.HTTP_404_NOT_FOUND,
            LimitedMetricsReadResultCategory.PUBLISH_STATUS_REQUIRED,
            "Limited metrics read requires an existing publish status snapshot.",
        )
    return dict(row)


def _enforce_real_provider_controls(
    provider_id: str,
    *,
    fallback_provider_id: str | None,
    real_provider_control_policy: RealProviderControlPolicy | Mapping[str, Any] | None,
) -> None:
    decision = evaluate_real_provider_control(
        provider_id,
        RealProviderCapability.METRICS_READ.value,
        control_policy=real_provider_control_policy,
        fallback_provider_id=fallback_provider_id,
    )
    if decision.status == RealProviderControlDecisionStatus.BLOCKED_SANDBOX_FALLBACK_FORBIDDEN.value:
        _raise(
            status.HTTP_409_CONFLICT,
            LimitedMetricsReadResultCategory.SANDBOX_FALLBACK_FORBIDDEN,
            "Real provider fallback to sandbox is forbidden.",
        )
    if decision.status == RealProviderControlDecisionStatus.BLOCKED_KILL_SWITCH_ACTIVE.value:
        _raise(
            status.HTTP_409_CONFLICT,
            LimitedMetricsReadResultCategory.KILL_SWITCH_ACTIVE,
            "Real provider kill switch blocks limited metrics read.",
        )
    if decision.status == RealProviderControlDecisionStatus.BLOCKED_PRECONDITIONS_MISSING.value:
        _raise(
            status.HTTP_409_CONFLICT,
            LimitedMetricsReadResultCategory.PLATFORM_PRECONDITIONS_MISSING,
            "Real provider platform preconditions are missing or not accepted.",
        )
    if decision.status == RealProviderControlDecisionStatus.BLOCKED_UNSUPPORTED_PROVIDER.value:
        _raise(
            status.HTTP_409_CONFLICT,
            LimitedMetricsReadResultCategory.UNSUPPORTED_PROVIDER,
            "Unsupported provider for limited metrics read.",
        )
    _raise(
        status.HTTP_409_CONFLICT,
        LimitedMetricsReadResultCategory.REAL_PROVIDER_DISABLED,
        "Real provider limited metrics read remains disabled by feature flag / kill switch controls.",
    )


def _coerce_permission_status(value: str | None) -> str:
    if value is None:
        return "available"
    if not isinstance(value, str):
        return "missing"
    normalized = value.strip().lower()
    return normalized if normalized == "available" else "missing"


def _coerce_metrics_fixture(
    fixture: Mapping[str, Any] | None,
    provider_source_type: SourceType,
) -> _MetricsFixture:
    if fixture is None:
        return _MetricsFixture(
            metrics_source=MetricsSource.LOCAL.value,
            metrics_freshness_status=MetricsFreshnessStatus.UNKNOWN.value,
            metrics_observed_at=None,
            views_count=None,
            likes_count=None,
            comments_count=None,
            shares_count=None,
            favorites_count=None,
            completion_rate_basis_points=None,
            safe_status_message=(
                "Local limited metrics snapshot created with freshness unknown; "
                "no external provider metrics query was called."
            ),
        )
    if not isinstance(fixture, Mapping):
        _invalid_fixture()

    metrics_source = _coerce_enum_value(MetricsSource, fixture.get("metrics_source"))
    metrics_freshness_status = _coerce_enum_value(
        MetricsFreshnessStatus,
        fixture.get("metrics_freshness_status"),
    )
    raw_metrics_observed_at = fixture.get("metrics_observed_at")
    metrics_observed_at = _coerce_observed_at(raw_metrics_observed_at)
    safe_status_message = fixture.get("safe_status_message")
    if (
        metrics_source is None
        or metrics_freshness_status is None
        or (raw_metrics_observed_at is not None and metrics_observed_at is None)
        or not isinstance(safe_status_message, str)
        or not safe_status_message.strip()
        or _contains_forbidden_marker(safe_status_message)
    ):
        _invalid_fixture()

    if metrics_source == MetricsSource.SANDBOX_FIXTURE.value and provider_source_type != SourceType.SANDBOX:
        _invalid_fixture()
    if metrics_source == MetricsSource.FAKE_FIXTURE.value and provider_source_type == SourceType.REAL:
        _invalid_fixture()
    if metrics_freshness_status in {MetricsFreshnessStatus.FRESH.value, MetricsFreshnessStatus.STALE.value}:
        if metrics_observed_at is None:
            _invalid_fixture()

    return _MetricsFixture(
        metrics_source=metrics_source,
        metrics_freshness_status=metrics_freshness_status,
        metrics_observed_at=metrics_observed_at,
        views_count=_coerce_optional_non_negative_int(fixture.get("views_count")),
        likes_count=_coerce_optional_non_negative_int(fixture.get("likes_count")),
        comments_count=_coerce_optional_non_negative_int(fixture.get("comments_count")),
        shares_count=_coerce_optional_non_negative_int(fixture.get("shares_count")),
        favorites_count=_coerce_optional_non_negative_int(fixture.get("favorites_count")),
        completion_rate_basis_points=_coerce_completion_rate_basis_points(
            fixture.get("completion_rate_basis_points")
        ),
        safe_status_message=safe_status_message.strip(),
    )


def _coerce_optional_non_negative_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _invalid_fixture()
    return value


def _coerce_completion_rate_basis_points(value: Any) -> int | None:
    coerced = _coerce_optional_non_negative_int(value)
    if coerced is not None and coerced > 10000:
        _invalid_fixture()
    return coerced


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
        return None
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _contains_forbidden_marker(value: str) -> bool:
    rendered = value.lower()
    return any(marker in rendered for marker in FORBIDDEN_METRICS_MARKERS)


def _invalid_fixture() -> None:
    _raise(
        422,
        LimitedMetricsReadResultCategory.METRICS_FIXTURE_INVALID,
        "Fake or sandbox metrics fixture is invalid for metadata-only metrics snapshot.",
    )


def _raise(
    status_code: int,
    category: LimitedMetricsReadResultCategory,
    safe_status_message: str,
) -> None:
    raise LimitedMetricsReadError(status_code, category.value, safe_status_message)
