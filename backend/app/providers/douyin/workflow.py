from dataclasses import dataclass

from app.providers.douyin.boundary import DouyinAdapterOperationResult
from app.providers.douyin.registry import create_douyin_provider_adapter


SANDBOX_WORKFLOW_STATUS = "simulated_success"
SANDBOX_WORKFLOW_FIXED_TIMESTAMP = "2026-01-01T00:00:00Z"

SANDBOX_MOCK_ACCOUNT_PAYLOAD: dict[str, object] = {
    "provider": "douyin_sandbox",
    "source": "sandbox",
    "mode": "sandbox",
    "outcome": "simulated",
    "dry_run": True,
    "connection_id": "sandbox_connection_001",
    "account_id": "sandbox_account_001",
    "account_label": "Sandbox Mock Account",
    "connection_status": "simulated_connected",
}

SANDBOX_METRICS_POC_PAYLOAD: dict[str, object] = {
    "provider": "douyin_sandbox",
    "source": "sandbox",
    "mode": "sandbox",
    "outcome": "simulated",
    "dry_run": True,
    "metrics_id": "sandbox_metrics_snapshot_001",
    "publication_id": "sandbox_publish_001",
    "collected_at": SANDBOX_WORKFLOW_FIXED_TIMESTAMP,
    "views": 1200,
    "likes": 128,
    "comments": 16,
    "shares": 9,
    "favorites": 5,
}

SANDBOX_DRY_RUN_PUBLISH_PAYLOAD: dict[str, object] = {
    "provider": "douyin_sandbox",
    "source": "sandbox",
    "mode": "sandbox",
    "outcome": "simulated",
    "dry_run": True,
    "video_id": "sandbox_video_001",
    "publish_id": "sandbox_publish_001",
    "publish_status": "simulated_success",
    "scheduled": False,
    "completed_at": SANDBOX_WORKFLOW_FIXED_TIMESTAMP,
}


@dataclass(frozen=True)
class DouyinSandboxWorkflowResult:
    provider_id: str
    source_type: str
    workflow_name: str
    workflow_status: str
    safe_message: str
    boundary_notes: tuple[str, ...]
    operation_references: tuple[str, ...]
    payload: dict[str, object]
    dry_run: bool = True
    external_call_performed: bool = False
    storage_write_performed: bool = False


def run_douyin_sandbox_mock_account_connection() -> DouyinSandboxWorkflowResult:
    adapter = create_douyin_provider_adapter("douyin_sandbox")
    operation_results = (
        adapter.start_oauth(),
        adapter.handle_oauth_callback(),
    )
    return _build_sandbox_workflow_result(
        workflow_name="mock_account_connection",
        safe_message=(
            "Douyin sandbox mock account connection completed as a deterministic "
            "backend-only simulation."
        ),
        operation_results=operation_results,
        payload=SANDBOX_MOCK_ACCOUNT_PAYLOAD,
    )


def run_douyin_sandbox_metrics_poc() -> DouyinSandboxWorkflowResult:
    adapter = create_douyin_provider_adapter("douyin_sandbox")
    operation_results = (adapter.fetch_metrics(),)
    return _build_sandbox_workflow_result(
        workflow_name="sandbox_metrics_poc",
        safe_message=(
            "Douyin sandbox metrics POC returned deterministic mock metrics for "
            "contract testing only."
        ),
        operation_results=operation_results,
        payload=SANDBOX_METRICS_POC_PAYLOAD,
    )


def run_douyin_sandbox_dry_run_publish() -> DouyinSandboxWorkflowResult:
    adapter = create_douyin_provider_adapter("douyin_sandbox")
    operation_results = (
        adapter.prepare_publish(),
        adapter.upload_video(),
        adapter.publish_video(),
    )
    return _build_sandbox_workflow_result(
        workflow_name="dry_run_publish",
        safe_message=(
            "Douyin sandbox dry-run publish completed as deterministic simulation "
            "without platform side effects."
        ),
        operation_results=operation_results,
        payload=SANDBOX_DRY_RUN_PUBLISH_PAYLOAD,
    )


def run_douyin_sandbox_mock_workflow_poc() -> tuple[DouyinSandboxWorkflowResult, ...]:
    return (
        run_douyin_sandbox_mock_account_connection(),
        run_douyin_sandbox_metrics_poc(),
        run_douyin_sandbox_dry_run_publish(),
    )


def _build_sandbox_workflow_result(
    *,
    workflow_name: str,
    safe_message: str,
    operation_results: tuple[DouyinAdapterOperationResult, ...],
    payload: dict[str, object],
) -> DouyinSandboxWorkflowResult:
    _assert_sandbox_operation_results(operation_results)
    return DouyinSandboxWorkflowResult(
        provider_id="douyin_sandbox",
        source_type="sandbox",
        workflow_name=workflow_name,
        workflow_status=SANDBOX_WORKFLOW_STATUS,
        safe_message=safe_message,
        boundary_notes=(
            "sandbox-only mock workflow",
            "deterministic simulated result",
            "factory-routed douyin_sandbox adapter",
            "no external service call",
            "no persistent storage write",
            "not real Douyin integration",
        ),
        operation_references=tuple(
            result.simulation_reference or result.operation for result in operation_results
        ),
        payload=dict(payload),
    )


def _assert_sandbox_operation_results(
    operation_results: tuple[DouyinAdapterOperationResult, ...],
) -> None:
    for result in operation_results:
        if result.provider_id != "douyin_sandbox":
            raise ValueError("Sandbox workflow requires douyin_sandbox operation results.")
        if result.source_type != "sandbox":
            raise ValueError("Sandbox workflow requires sandbox source operation results.")
        if result.operation_status != SANDBOX_WORKFLOW_STATUS:
            raise ValueError("Sandbox workflow requires simulated operation results.")
        if result.external_call_performed:
            raise ValueError("Sandbox workflow operation reported an external call.")
