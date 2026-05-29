import sqlite3
from dataclasses import dataclass
from enum import Enum

from fastapi import status

from app.providers.credential_references import (
    CredentialReferenceStatus,
    CredentialReferenceStorageStatus,
    get_provider_credential_reference,
)
from app.providers.platform_registry import SourceType, get_platform_provider
from app.providers.real_provider_controls import (
    RealProviderCapability,
    RealProviderControlDecisionStatus,
    RealProviderControlPolicy,
    evaluate_real_provider_control,
)
from app.publishing.publish_intent import SENSITIVE_METADATA_MARKERS


class GuardedPublishAttemptStatus(str, Enum):
    PUBLISH_ATTEMPT_CREATED = "publish_attempt_created"
    PUBLISH_BLOCKED = "publish_blocked"
    PUBLISH_INTENT_REQUIRED = "publish_intent_required"
    PUBLISH_INTENT_NOT_READY = "publish_intent_not_ready"
    DUPLICATE_PUBLISH_ATTEMPT = "duplicate_publish_attempt"
    REVIEW_NOT_READY = "review_not_ready"
    MEDIA_NOT_READY = "media_not_ready"
    METADATA_INVALID = "metadata_invalid"
    CREDENTIAL_REFERENCE_MISSING = "credential_reference_missing"
    REAL_PROVIDER_DISABLED = "real_provider_disabled"
    KILL_SWITCH_ACTIVE = "kill_switch_active"
    PLATFORM_PRECONDITIONS_MISSING = "platform_preconditions_missing"
    UNSUPPORTED_PROVIDER = "unsupported_provider"
    SANDBOX_FALLBACK_FORBIDDEN = "sandbox_fallback_forbidden"
    EXTERNAL_PUBLISH_BLOCKED = "external_publish_blocked"


@dataclass(frozen=True)
class GuardedPublishAttemptError(Exception):
    status_code: int
    category: str
    safe_status_message: str


def create_guarded_publish_attempt(
    db: sqlite3.Connection,
    *,
    project_id: int,
    publish_intent_id: int,
    fallback_provider_id: str | None = None,
    real_provider_control_policy: RealProviderControlPolicy | dict | None = None,
) -> dict:
    publish_intent = _get_publish_intent(db, project_id, publish_intent_id)
    provider = get_platform_provider(publish_intent["target_platform"])
    if provider is None:
        _raise(
            status.HTTP_409_CONFLICT,
            GuardedPublishAttemptStatus.UNSUPPORTED_PROVIDER.value,
            "Unsupported provider for guarded publish attempt.",
        )

    if fallback_provider_id is not None and fallback_provider_id != provider.provider_id:
        _raise(
            status.HTTP_409_CONFLICT,
            GuardedPublishAttemptStatus.SANDBOX_FALLBACK_FORBIDDEN.value,
            "Provider fallback is forbidden for guarded publish attempts.",
        )

    if publish_intent["source_type"] != provider.source_type.value:
        _raise(
            status.HTTP_409_CONFLICT,
            GuardedPublishAttemptStatus.SANDBOX_FALLBACK_FORBIDDEN.value,
            "Publish intent provider source mismatch is blocked.",
        )

    if publish_intent["publish_status"] != "confirmed":
        _raise(
            status.HTTP_409_CONFLICT,
            GuardedPublishAttemptStatus.PUBLISH_INTENT_NOT_READY.value,
            "A confirmed publish intent is required before creating a guarded attempt.",
        )

    if provider.source_type == SourceType.REAL:
        _enforce_real_provider_controls(
            provider.provider_id,
            fallback_provider_id=fallback_provider_id,
            real_provider_control_policy=real_provider_control_policy,
        )

    _ensure_review_ready(db, project_id, publish_intent["review_draft_id"])
    _ensure_media_ready(db, project_id)
    _ensure_metadata_safe(publish_intent["title"], publish_intent["caption"])
    _ensure_credential_reference_ready(db, provider.provider_id)
    _ensure_no_active_attempt(db, publish_intent_id)

    row = db.execute(
        """
        INSERT INTO publish_attempts (
            project_id, publish_intent_id, review_draft_id, provider_id, source_type,
            attempt_status, guard_status, external_call_status, safe_status_message,
            last_status_change_reason
        )
        VALUES (?, ?, ?, ?, ?, 'created', 'passed_simulated', 'not_called', ?, ?)
        RETURNING id, project_id, publish_intent_id, review_draft_id, provider_id,
                  source_type, attempt_status, guard_status, external_call_status,
                  created_at, updated_at, completed_at, safe_status_message,
                  last_status_change_reason
        """,
        (
            project_id,
            publish_intent["id"],
            publish_intent["review_draft_id"],
            provider.provider_id,
            provider.source_type.value,
            (
                "Guarded publish attempt recorded locally; no upload, external publish, "
                "scheduled publish, or provider response was executed."
            ),
            "batch7_guarded_publish_attempt_created",
        ),
    ).fetchone()
    db.commit()
    return dict(row)


def list_guarded_publish_attempts(db: sqlite3.Connection, *, project_id: int) -> list[dict]:
    rows = db.execute(
        """
        SELECT id, project_id, publish_intent_id, review_draft_id, provider_id,
               source_type, attempt_status, guard_status, external_call_status,
               created_at, updated_at, completed_at, safe_status_message,
               last_status_change_reason
        FROM publish_attempts
        WHERE project_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (project_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def get_guarded_publish_attempt(
    db: sqlite3.Connection,
    *,
    project_id: int,
    publish_attempt_id: int,
) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, publish_intent_id, review_draft_id, provider_id,
               source_type, attempt_status, guard_status, external_call_status,
               created_at, updated_at, completed_at, safe_status_message,
               last_status_change_reason
        FROM publish_attempts
        WHERE id = ? AND project_id = ?
        """,
        (publish_attempt_id, project_id),
    ).fetchone()
    if row is None:
        _raise(
            status.HTTP_404_NOT_FOUND,
            GuardedPublishAttemptStatus.PUBLISH_INTENT_REQUIRED.value,
            "Guarded publish attempt not found.",
        )
    return dict(row)


def _enforce_real_provider_controls(
    provider_id: str,
    *,
    fallback_provider_id: str | None,
    real_provider_control_policy: RealProviderControlPolicy | dict | None,
) -> None:
    decision = evaluate_real_provider_control(
        provider_id,
        RealProviderCapability.PUBLISH.value,
        control_policy=real_provider_control_policy,
        fallback_provider_id=fallback_provider_id,
    )
    if decision.status == RealProviderControlDecisionStatus.BLOCKED_SANDBOX_FALLBACK_FORBIDDEN.value:
        _raise(
            status.HTTP_409_CONFLICT,
            GuardedPublishAttemptStatus.SANDBOX_FALLBACK_FORBIDDEN.value,
            "Real provider fallback to sandbox is forbidden.",
        )
    if decision.status == RealProviderControlDecisionStatus.BLOCKED_KILL_SWITCH_ACTIVE.value:
        _raise(
            status.HTTP_409_CONFLICT,
            GuardedPublishAttemptStatus.KILL_SWITCH_ACTIVE.value,
            "Real provider kill switch blocks guarded publish attempts.",
        )
    if decision.status == RealProviderControlDecisionStatus.BLOCKED_PRECONDITIONS_MISSING.value:
        _raise(
            status.HTTP_409_CONFLICT,
            GuardedPublishAttemptStatus.PLATFORM_PRECONDITIONS_MISSING.value,
            "Real provider platform preconditions are missing or not accepted.",
        )
    if decision.status == RealProviderControlDecisionStatus.BLOCKED_UNSUPPORTED_PROVIDER.value:
        _raise(
            status.HTTP_409_CONFLICT,
            GuardedPublishAttemptStatus.UNSUPPORTED_PROVIDER.value,
            "Unsupported provider for guarded publish attempt.",
        )
    _raise(
        status.HTTP_409_CONFLICT,
        GuardedPublishAttemptStatus.REAL_PROVIDER_DISABLED.value,
        "Real provider publish remains disabled by feature flag / kill switch controls.",
    )


def _get_publish_intent(db: sqlite3.Connection, project_id: int, publish_intent_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, review_draft_id, target_platform, source_type, title, caption,
               publish_status, confirmation_status
        FROM publish_intents
        WHERE id = ? AND project_id = ?
        """,
        (publish_intent_id, project_id),
    ).fetchone()
    if row is None:
        _raise(
            status.HTTP_404_NOT_FOUND,
            GuardedPublishAttemptStatus.PUBLISH_INTENT_REQUIRED.value,
            "A confirmed publish intent is required before creating a guarded attempt.",
        )
    return dict(row)


def _ensure_review_ready(
    db: sqlite3.Connection,
    project_id: int,
    review_draft_id: int,
) -> None:
    row = db.execute(
        """
        SELECT review_status
        FROM review_drafts
        WHERE id = ? AND project_id = ?
        """,
        (review_draft_id, project_id),
    ).fetchone()
    if row is None or row["review_status"] != "approved":
        _raise(
            status.HTTP_409_CONFLICT,
            GuardedPublishAttemptStatus.REVIEW_NOT_READY.value,
            "Review item must remain approved before creating a guarded publish attempt.",
        )


def _ensure_media_ready(db: sqlite3.Connection, project_id: int) -> None:
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
    if row is None:
        _raise(
            status.HTTP_409_CONFLICT,
            GuardedPublishAttemptStatus.MEDIA_NOT_READY.value,
            "A ready local media artifact is required before creating a guarded publish attempt.",
        )


def _ensure_metadata_safe(title: str, caption: str) -> None:
    if not title.strip() or not caption.strip():
        _raise(
            422,
            GuardedPublishAttemptStatus.METADATA_INVALID.value,
            "Publish attempt metadata requires a title and caption.",
        )
    rendered = f"{title} {caption}".lower()
    if any(marker in rendered for marker in SENSITIVE_METADATA_MARKERS):
        _raise(
            422,
            GuardedPublishAttemptStatus.METADATA_INVALID.value,
            "Publish attempt metadata contains disallowed sensitive markers.",
        )


def _ensure_credential_reference_ready(db: sqlite3.Connection, provider_id: str) -> None:
    reference = get_provider_credential_reference(db, provider_id)
    if reference is None:
        _raise(
            status.HTTP_409_CONFLICT,
            GuardedPublishAttemptStatus.UNSUPPORTED_PROVIDER.value,
            "Unsupported provider for credential reference validation.",
        )

    if reference.reference_status == CredentialReferenceStatus.NOT_REQUIRED.value:
        return

    if (
        reference.reference_status == CredentialReferenceStatus.REFERENCE_ONLY.value
        and reference.storage_status == CredentialReferenceStorageStatus.REFERENCE_ONLY.value
    ):
        return

    _raise(
        status.HTTP_409_CONFLICT,
        GuardedPublishAttemptStatus.CREDENTIAL_REFERENCE_MISSING.value,
        "A metadata-only credential reference is required before creating a guarded publish attempt.",
    )


def _ensure_no_active_attempt(db: sqlite3.Connection, publish_intent_id: int) -> None:
    row = db.execute(
        """
        SELECT id
        FROM publish_attempts
        WHERE publish_intent_id = ?
          AND attempt_status = 'created'
        LIMIT 1
        """,
        (publish_intent_id,),
    ).fetchone()
    if row is not None:
        _raise(
            status.HTTP_409_CONFLICT,
            GuardedPublishAttemptStatus.DUPLICATE_PUBLISH_ATTEMPT.value,
            "An active guarded publish attempt already exists for this publish intent.",
        )


def _raise(status_code: int, category: str, safe_status_message: str) -> None:
    raise GuardedPublishAttemptError(status_code, category, safe_status_message)
