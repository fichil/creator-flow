from dataclasses import dataclass


BLOCKED_OPERATION_STATUS = "blocked"


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
