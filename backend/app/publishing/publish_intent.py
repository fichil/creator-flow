import sqlite3
from dataclasses import dataclass

from fastapi import status

from app.providers.platform_registry import SourceType, get_platform_provider
from app.providers.real_provider_controls import (
    RealProviderCapability,
    RealProviderControlDecisionStatus,
    evaluate_real_provider_control,
)


SENSITIVE_METADATA_MARKERS = (
    "access_token",
    "refresh_token",
    "authorization_code",
    "raw_authorization_code",
    "raw_oauth_state",
    "oauth_state_value",
    "raw_state",
    "state_value",
    "client_secret",
    "api_key",
    "bearer",
    "cookie",
    "session",
    "token",
    "secret",
    "credential",
    "raw_request",
    "raw_response",
    "provider_response",
    "upload_response",
    "publish_response",
    "status_response",
    "external_response",
    "douyin_response",
    "metrics_response",
)


@dataclass(frozen=True)
class PublishIntentWorkflowError(Exception):
    status_code: int
    category: str
    safe_status_message: str


def create_local_publish_intent(
    db: sqlite3.Connection,
    *,
    project_id: int,
    review_draft_id: int,
    provider_id: str,
    title: str,
    caption: str,
    confirm_publish_intent: bool | None,
    fallback_provider_id: str | None = None,
) -> dict:
    provider_id = _required_text(provider_id, "target_platform")
    title = _required_text(title, "title")
    caption = _required_text(caption, "caption")

    if confirm_publish_intent is not True:
        _raise(
            status.HTTP_409_CONFLICT,
            "confirmation_required",
            "Explicit user confirmation is required before creating a publish intent.",
        )

    if _contains_sensitive_marker((title, caption)):
        _raise(
            422,
            "metadata_invalid",
            "Publish intent metadata contains disallowed sensitive markers.",
        )

    provider = get_platform_provider(provider_id)
    if provider is None:
        _raise(
            status.HTTP_409_CONFLICT,
            "unsupported_provider",
            "Unsupported provider for publish intent workflow.",
        )

    if fallback_provider_id is not None and fallback_provider_id != provider.provider_id:
        _raise(
            status.HTTP_409_CONFLICT,
            "sandbox_fallback_forbidden",
            "Provider fallback is forbidden for publish intent workflow.",
        )

    if provider.source_type == SourceType.REAL:
        decision = evaluate_real_provider_control(
            provider.provider_id,
            RealProviderCapability.PUBLISH.value,
            fallback_provider_id=fallback_provider_id,
        )
        if decision.status == RealProviderControlDecisionStatus.BLOCKED_SANDBOX_FALLBACK_FORBIDDEN.value:
            _raise(
                status.HTTP_409_CONFLICT,
                "sandbox_fallback_forbidden",
                "Real provider fallback to sandbox is forbidden.",
            )
        _raise(
            status.HTTP_409_CONFLICT,
            "real_provider_disabled",
            "Real provider publishing remains disabled by feature flag / kill switch controls.",
        )

    review_draft = _get_review_draft(db, project_id, review_draft_id)
    if review_draft["review_status"] != "approved":
        _raise(
            status.HTTP_409_CONFLICT,
            "review_not_ready",
            "Review item must be approved before creating a publish intent.",
        )

    if not _has_ready_media_artifact(db, project_id):
        _raise(
            status.HTTP_409_CONFLICT,
            "media_not_ready",
            "A ready local media artifact is required before creating a publish intent.",
        )

    if _has_active_publish_intent(
        db,
        review_draft_id=review_draft["id"],
        provider_id=provider.provider_id,
        source_type=provider.source_type.value,
    ):
        _raise(
            status.HTTP_409_CONFLICT,
            "duplicate_publish_intent",
            "An active publish intent already exists for this review item and provider.",
        )

    row = db.execute(
        """
        INSERT INTO publish_intents (
            project_id, review_draft_id, target_platform, source_type, title, caption,
            publish_status, confirmation_status, confirmed_at, safe_status_message,
            last_status_change_reason
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, 'confirmed', 'confirmed', CURRENT_TIMESTAMP, ?,
            'user_confirmed_publish_intent_created'
        )
        RETURNING id, project_id, review_draft_id, target_platform, source_type, title, caption,
                  publish_status, confirmation_status, created_at, updated_at, confirmed_at,
                  cancelled_at, safe_status_message, last_status_change_reason
        """,
        (
            project_id,
            review_draft["id"],
            provider.provider_id,
            provider.source_type.value,
            title,
            caption,
            "Publish intent recorded locally after explicit user confirmation; no provider publish was executed.",
        ),
    ).fetchone()
    db.commit()
    return dict(row)


def _get_review_draft(db: sqlite3.Connection, project_id: int, review_draft_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, review_status
        FROM review_drafts
        WHERE id = ? AND project_id = ?
        """,
        (review_draft_id, project_id),
    ).fetchone()
    if row is None:
        _raise(
            status.HTTP_404_NOT_FOUND,
            "review_not_ready",
            "Review item not found for publish intent workflow.",
        )
    return dict(row)


def _has_ready_media_artifact(db: sqlite3.Connection, project_id: int) -> bool:
    row = db.execute(
        """
        SELECT render_artifacts.id
        FROM render_artifacts
        JOIN render_jobs ON render_jobs.id = render_artifacts.render_job_id
        WHERE render_artifacts.project_id = ?
          AND render_jobs.project_id = ?
          AND render_jobs.status = 'succeeded'
          AND render_artifacts.artifact_type IN ('fake_video', 'fake_preview_manifest')
        LIMIT 1
        """,
        (project_id, project_id),
    ).fetchone()
    return row is not None


def _has_active_publish_intent(
    db: sqlite3.Connection,
    *,
    review_draft_id: int,
    provider_id: str,
    source_type: str,
) -> bool:
    row = db.execute(
        """
        SELECT id
        FROM publish_intents
        WHERE review_draft_id = ?
          AND target_platform = ?
          AND source_type = ?
          AND publish_status IN ('pending_confirmation', 'confirmed')
        LIMIT 1
        """,
        (review_draft_id, provider_id, source_type),
    ).fetchone()
    return row is not None


def _required_text(value: str | None, field_name: str) -> str:
    if value is None or not value.strip():
        _raise(
            422,
            "metadata_invalid",
            f"{field_name} is required for publish intent workflow.",
        )
    return value.strip()


def _contains_sensitive_marker(values: tuple[str, ...]) -> bool:
    joined = " ".join(values).lower()
    return any(marker in joined for marker in SENSITIVE_METADATA_MARKERS)


def _raise(status_code: int, category: str, safe_status_message: str) -> None:
    raise PublishIntentWorkflowError(status_code, category, safe_status_message)
