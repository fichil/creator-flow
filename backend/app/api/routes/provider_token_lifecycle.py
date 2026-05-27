from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.providers.token_lifecycle import (
    get_provider_token_lifecycle_boundary,
    list_provider_token_lifecycle_boundaries,
)
from app.schemas.provider_token_lifecycle import (
    ProviderTokenLifecycleBoundaryListResponse,
    ProviderTokenLifecycleBoundaryResponse,
)

router = APIRouter()


@router.get("", response_model=ProviderTokenLifecycleBoundaryListResponse)
def list_token_lifecycle_boundaries(db=Depends(get_db)) -> dict[str, list[dict]]:
    return {
        "token_lifecycle_boundaries": [
            asdict(boundary)
            for boundary in list_provider_token_lifecycle_boundaries(db)
        ]
    }


@router.get("/{provider_id}", response_model=ProviderTokenLifecycleBoundaryResponse)
def get_token_lifecycle_boundary(provider_id: str, db=Depends(get_db)) -> dict:
    boundary = get_provider_token_lifecycle_boundary(db, provider_id)
    if boundary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider lifecycle boundary metadata not found",
        )
    return asdict(boundary)
