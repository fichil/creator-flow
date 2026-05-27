from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.providers.credential_references import (
    get_provider_credential_reference,
    list_provider_credential_references,
)
from app.schemas.provider_credential_references import (
    ProviderCredentialReferenceListResponse,
    ProviderCredentialReferenceResponse,
)

router = APIRouter()


@router.get("", response_model=ProviderCredentialReferenceListResponse)
def list_credential_references(db=Depends(get_db)) -> dict[str, list[dict]]:
    return {
        "credential_references": [
            asdict(reference)
            for reference in list_provider_credential_references(db)
        ]
    }


@router.get("/{provider_id}", response_model=ProviderCredentialReferenceResponse)
def get_credential_reference(provider_id: str, db=Depends(get_db)) -> dict:
    reference = get_provider_credential_reference(db, provider_id)
    if reference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider reference metadata not found",
        )
    return asdict(reference)
