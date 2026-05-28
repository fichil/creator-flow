from dataclasses import asdict
from typing import Callable

from fastapi import APIRouter, HTTPException, status

from app.providers.douyin.registry import (
    DouyinProviderDescriptor,
    get_douyin_provider_descriptor,
    list_douyin_provider_descriptors,
)
from app.providers.douyin.workflow import (
    DouyinSandboxWorkflowResult,
    run_douyin_sandbox_dry_run_publish,
    run_douyin_sandbox_metrics_poc,
    run_douyin_sandbox_mock_account_connection,
)
from app.schemas.douyin_sandbox import (
    DouyinProviderDescriptorListResponse,
    DouyinProviderDescriptorResponse,
    DouyinSandboxApiOperationResponse,
)

router = APIRouter()

_SANDBOX_PROVIDER_ID = "douyin_sandbox"
_REAL_PROVIDER_ID = "douyin_real"
_SENSITIVE_PROVIDER_ID_PARTS = (
    "access",
    "refresh",
    "client",
    "authorization",
    "oauth",
    "api",
    "credential",
    "cookie",
    "session",
    "bearer",
    "password",
    "secret",
)


@router.get("", response_model=DouyinProviderDescriptorListResponse)
def list_douyin_providers() -> dict[str, list[dict]]:
    return {
        "providers": [
            _descriptor_to_response(descriptor)
            for descriptor in list_douyin_provider_descriptors()
        ]
    }


@router.post("/sandbox/mock-connection", response_model=DouyinSandboxApiOperationResponse)
def run_sandbox_mock_connection() -> dict:
    return _run_provider_sandbox_operation(
        provider_id=_SANDBOX_PROVIDER_ID,
        operation="sandbox_mock_connection",
        workflow_runner=run_douyin_sandbox_mock_account_connection,
    )


@router.post("/sandbox/metrics-preview", response_model=DouyinSandboxApiOperationResponse)
def run_sandbox_metrics_preview() -> dict:
    return _run_provider_sandbox_operation(
        provider_id=_SANDBOX_PROVIDER_ID,
        operation="sandbox_metrics_preview",
        workflow_runner=run_douyin_sandbox_metrics_poc,
    )


@router.post("/sandbox/publish-dry-run", response_model=DouyinSandboxApiOperationResponse)
def run_sandbox_publish_dry_run() -> dict:
    return _run_provider_sandbox_operation(
        provider_id=_SANDBOX_PROVIDER_ID,
        operation="sandbox_publish_dry_run",
        workflow_runner=run_douyin_sandbox_dry_run_publish,
    )


@router.post(
    "/{provider_id}/sandbox/mock-connection",
    response_model=DouyinSandboxApiOperationResponse,
)
def run_provider_sandbox_mock_connection(provider_id: str) -> dict:
    return _run_provider_sandbox_operation(
        provider_id=provider_id,
        operation="sandbox_mock_connection",
        workflow_runner=run_douyin_sandbox_mock_account_connection,
    )


@router.post(
    "/{provider_id}/sandbox/metrics-preview",
    response_model=DouyinSandboxApiOperationResponse,
)
def run_provider_sandbox_metrics_preview(provider_id: str) -> dict:
    return _run_provider_sandbox_operation(
        provider_id=provider_id,
        operation="sandbox_metrics_preview",
        workflow_runner=run_douyin_sandbox_metrics_poc,
    )


@router.post(
    "/{provider_id}/sandbox/publish-dry-run",
    response_model=DouyinSandboxApiOperationResponse,
)
def run_provider_sandbox_publish_dry_run(provider_id: str) -> dict:
    return _run_provider_sandbox_operation(
        provider_id=provider_id,
        operation="sandbox_publish_dry_run",
        workflow_runner=run_douyin_sandbox_dry_run_publish,
    )


@router.get("/{provider_id}", response_model=DouyinProviderDescriptorResponse)
def get_douyin_provider(provider_id: str) -> dict:
    return _descriptor_to_response(_get_descriptor_or_404(provider_id))


def _run_provider_sandbox_operation(
    *,
    provider_id: str,
    operation: str,
    workflow_runner: Callable[[], DouyinSandboxWorkflowResult],
) -> dict:
    descriptor = _get_descriptor_or_404(provider_id)
    if descriptor.provider_id == _REAL_PROVIDER_ID:
        return _blocked_real_provider_response(operation)
    if descriptor.provider_id != _SANDBOX_PROVIDER_ID:
        raise _unsupported_provider_error(provider_id)

    return _workflow_to_response(operation=operation, workflow_result=workflow_runner())


def _get_descriptor_or_404(provider_id: str) -> DouyinProviderDescriptor:
    try:
        return get_douyin_provider_descriptor(provider_id)
    except ValueError as error:
        raise _unsupported_provider_error(provider_id) from error


def _descriptor_to_response(descriptor: DouyinProviderDescriptor) -> dict:
    data = asdict(descriptor)
    data["mode"] = descriptor.environment
    data["simulated"] = descriptor.provider_id == _SANDBOX_PROVIDER_ID
    data["dry_run"] = descriptor.provider_id == _SANDBOX_PROVIDER_ID
    if descriptor.provider_id == _SANDBOX_PROVIDER_ID:
        data["boundary_notes"] = [
            "sandbox descriptor",
            "simulation only",
            "deterministic dry-run API contract",
            "not real platform behavior",
        ]
    else:
        data["boundary_notes"] = [
            "real provider descriptor",
            "blocked",
            "not implemented",
            "not available through sandbox API",
        ]
    return data


def _workflow_to_response(
    *, operation: str, workflow_result: DouyinSandboxWorkflowResult
) -> dict:
    payload = dict(workflow_result.payload)
    return {
        "provider_id": workflow_result.provider_id,
        "source_type": workflow_result.source_type,
        "mode": "sandbox",
        "operation": operation,
        "workflow_name": workflow_result.workflow_name,
        "status": workflow_result.workflow_status,
        "outcome": "simulated",
        "simulated": True,
        "dry_run": workflow_result.dry_run,
        "safe_message": workflow_result.safe_message,
        "boundary_notes": list(workflow_result.boundary_notes),
        "operation_references": list(workflow_result.operation_references),
        "payload": payload,
        "external_call_performed": workflow_result.external_call_performed,
        "storage_write_performed": workflow_result.storage_write_performed,
        "database_write_performed": False,
    }


def _blocked_real_provider_response(operation: str) -> dict:
    return {
        "provider_id": _REAL_PROVIDER_ID,
        "source_type": "real",
        "mode": "real",
        "operation": operation,
        "workflow_name": "sandbox_api_blocked_for_real_provider",
        "status": "blocked",
        "outcome": "blocked",
        "simulated": False,
        "dry_run": True,
        "safe_message": (
            "The real Douyin provider is blocked in the v0.9 sandbox API contract."
        ),
        "boundary_notes": [
            "real provider not implemented",
            "sandbox API cannot execute real provider operations",
            "no platform side effects",
        ],
        "operation_references": [],
        "payload": {
            "provider": _REAL_PROVIDER_ID,
            "source": "real",
            "mode": "real",
            "outcome": "blocked",
            "dry_run": True,
        },
        "external_call_performed": False,
        "storage_write_performed": False,
        "database_write_performed": False,
    }


def _unsupported_provider_error(provider_id: object) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "message": "Unsupported Douyin provider id",
            "provider_id": _safe_provider_id(provider_id),
        },
    )


def _safe_provider_id(provider_id: object) -> str:
    if provider_id is None:
        return "<missing>"
    if provider_id == "":
        return "<empty>"
    provider_text = str(provider_id)
    provider_text_lower = provider_text.lower()
    if any(part in provider_text_lower for part in _SENSITIVE_PROVIDER_ID_PARTS):
        return "<redacted>"
    return provider_text
