from dataclasses import asdict

from fastapi import APIRouter, HTTPException, status

from app.providers.platform_registry import get_platform_provider, list_platform_providers
from app.schemas.provider_registry import PlatformProviderResponse, ProviderRegistryListResponse

router = APIRouter()


@router.get("", response_model=ProviderRegistryListResponse)
def list_providers() -> dict[str, list[dict]]:
    return {"providers": [_provider_to_dict(provider) for provider in list_platform_providers()]}


@router.get("/{provider_id}", response_model=PlatformProviderResponse)
def get_provider(provider_id: str) -> dict:
    provider = get_platform_provider(provider_id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    return _provider_to_dict(provider)


def _provider_to_dict(provider) -> dict:
    data = asdict(provider)
    data["provider_type"] = provider.provider_type.value
    data["source_type"] = provider.source_type.value
    data["implementation_status"] = provider.implementation_status.value
    data["connection_status"] = provider.connection_status.value
    return data
