from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.providers.connection_state import (
    get_provider_connection_state,
    list_provider_connection_states,
)
from app.schemas.provider_connections import (
    ProviderConnectionStateListResponse,
    ProviderConnectionStateResponse,
)

router = APIRouter()


@router.get("", response_model=ProviderConnectionStateListResponse)
def list_provider_connections(db=Depends(get_db)) -> dict[str, list[dict]]:
    return {
        "connections": [
            asdict(connection_state)
            for connection_state in list_provider_connection_states(db)
        ]
    }


@router.get("/{provider_id}", response_model=ProviderConnectionStateResponse)
def get_provider_connection(provider_id: str, db=Depends(get_db)) -> dict:
    connection_state = get_provider_connection_state(db, provider_id)
    if connection_state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider connection state not found",
        )
    return asdict(connection_state)
