from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.providers.readiness_summary import (
    get_provider_readiness_summary,
    list_provider_readiness_summaries,
)
from app.schemas.provider_readiness import (
    ProviderReadinessSummaryListResponse,
    ProviderReadinessSummaryResponse,
)

router = APIRouter()


@router.get("", response_model=ProviderReadinessSummaryListResponse)
def list_readiness_summaries(db=Depends(get_db)) -> dict[str, list[dict]]:
    return {
        "readiness_summaries": [
            asdict(summary) for summary in list_provider_readiness_summaries(db)
        ]
    }


@router.get("/{provider_id}", response_model=ProviderReadinessSummaryResponse)
def get_readiness_summary(provider_id: str, db=Depends(get_db)) -> dict:
    summary = get_provider_readiness_summary(db, provider_id)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider readiness summary not found",
        )
    return asdict(summary)
