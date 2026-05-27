from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.database import get_db
from app.providers.platform_registry import get_platform_provider
from app.providers.security_audit import (
    get_provider_security_audit_event,
    list_provider_security_audit_events,
)
from app.schemas.provider_security_audit import (
    ProviderSecurityAuditEventListResponse,
    ProviderSecurityAuditEventResponse,
)

router = APIRouter()


@router.get("", response_model=ProviderSecurityAuditEventListResponse)
def list_security_audit_events(
    provider_id: str | None = None,
    limit: int = Query(default=100, ge=1),
    db=Depends(get_db),
) -> dict[str, list[dict]]:
    if provider_id is not None and get_platform_provider(provider_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider security audit provider not found",
        )

    events = list_provider_security_audit_events(
        db,
        provider_id=provider_id,
        limit=min(limit, 100),
    )
    return {"audit_events": [asdict(event) for event in events]}


@router.get("/{audit_event_id}", response_model=ProviderSecurityAuditEventResponse)
def get_security_audit_event(audit_event_id: str, db=Depends(get_db)) -> dict:
    event = get_provider_security_audit_event(db, audit_event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider security audit event not found",
        )
    return asdict(event)
