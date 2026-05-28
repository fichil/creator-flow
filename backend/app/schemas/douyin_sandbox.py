from typing import Any

from pydantic import BaseModel


class DouyinProviderDescriptorResponse(BaseModel):
    provider_id: str
    display_name: str
    environment: str
    mode: str
    status: str
    supports_simulation: bool
    supports_real_oauth: bool
    supports_real_publish: bool
    supports_real_metrics: bool
    simulated: bool
    dry_run: bool
    boundary_notes: list[str]


class DouyinProviderDescriptorListResponse(BaseModel):
    providers: list[DouyinProviderDescriptorResponse]


class DouyinSandboxApiOperationResponse(BaseModel):
    provider_id: str
    source_type: str
    mode: str
    operation: str
    workflow_name: str
    status: str
    outcome: str
    simulated: bool
    dry_run: bool
    safe_message: str
    boundary_notes: list[str]
    operation_references: list[str]
    payload: dict[str, Any]
    external_call_performed: bool
    storage_write_performed: bool
    database_write_performed: bool
