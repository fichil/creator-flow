from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.providers.oauth_boundary import (
    get_provider_oauth_boundary,
    list_provider_oauth_boundaries,
)
from app.schemas.provider_oauth_boundaries import (
    ProviderOAuthBoundaryListResponse,
    ProviderOAuthBoundaryResponse,
)

router = APIRouter()


@router.get("", response_model=ProviderOAuthBoundaryListResponse)
def list_oauth_boundaries(db=Depends(get_db)) -> dict[str, list[dict]]:
    return {
        "oauth_boundaries": [
            asdict(boundary) for boundary in list_provider_oauth_boundaries(db)
        ]
    }


@router.get("/{provider_id}", response_model=ProviderOAuthBoundaryResponse)
def get_oauth_boundary(provider_id: str, db=Depends(get_db)) -> dict:
    boundary = get_provider_oauth_boundary(db, provider_id)
    if boundary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider OAuth boundary metadata not found",
        )
    return asdict(boundary)
