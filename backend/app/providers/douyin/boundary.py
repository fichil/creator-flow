from dataclasses import dataclass, field


BLOCKED_OPERATION_STATUS = "blocked"
SANDBOX_SIMULATED_OPERATION_STATUS = "simulated_success"


@dataclass(frozen=True)
class DouyinAdapterOperationResult:
    provider_id: str
    source_type: str
    operation: str
    operation_status: str
    safe_message: str
    boundary_notes: list[str]
    is_real_provider: bool
    external_call_performed: bool = False
    credential_read_performed: bool = False
    token_read_performed: bool = False
    token_write_performed: bool = False
    simulation_reference: str | None = None
    dry_run: bool = True
    simulation_details: dict[str, str | bool | int] = field(default_factory=dict)


def build_blocked_douyin_operation_result(
    *,
    provider_id: str,
    source_type: str,
    operation: str,
    is_real_provider: bool,
) -> DouyinAdapterOperationResult:
    return DouyinAdapterOperationResult(
        provider_id=provider_id,
        source_type=source_type,
        operation=operation,
        operation_status=BLOCKED_OPERATION_STATUS,
        safe_message=(
            "Douyin provider operation is blocked by the v0.9 Batch 1 adapter "
            "skeleton; no external call, credential read, or token read/write "
            "was performed."
        ),
        boundary_notes=[
            "backend-only Douyin adapter skeleton",
            "operation is not implemented",
            "OAuth is not implemented",
            "OAuth callback route is not implemented",
            "OAuth state storage is not implemented",
            "token exchange is not implemented",
            "tokens are not stored",
            "secrets are not stored",
            "credentials are not stored",
            "no real Douyin API call",
            "no real metrics fetching",
            "no upload / publish / scheduling",
            "sandbox and real sources remain separated",
        ],
        is_real_provider=is_real_provider,
    )


def build_sandbox_douyin_operation_result(
    *,
    provider_id: str,
    source_type: str,
    operation: str,
    is_real_provider: bool,
    simulation_reference: str,
    simulation_details: dict[str, str | bool | int] | None = None,
) -> DouyinAdapterOperationResult:
    return DouyinAdapterOperationResult(
        provider_id=provider_id,
        source_type=source_type,
        operation=operation,
        operation_status=SANDBOX_SIMULATED_OPERATION_STATUS,
        safe_message=(
            "Douyin sandbox operation completed as a deterministic sandbox-only "
            "dry-run; no external call, credential read, or token read/write was "
            "performed."
        ),
        boundary_notes=[
            "sandbox-only simulated operation",
            "deterministic dry-run result",
            "not real Douyin integration",
            "OAuth is not implemented",
            "OAuth callback route is not implemented",
            "OAuth state storage is not implemented",
            "token exchange is not implemented",
            "tokens are not stored",
            "secrets are not stored",
            "no real metrics fetching",
            "no real upload / publish / scheduling",
            "no external service call",
            "cannot be treated as douyin_real",
        ],
        is_real_provider=is_real_provider,
        simulation_reference=simulation_reference,
        dry_run=True,
        simulation_details=simulation_details or {},
    )
