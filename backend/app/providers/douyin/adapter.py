from dataclasses import dataclass

from app.providers.douyin.boundary import (
    DouyinAdapterOperationResult,
    build_blocked_douyin_operation_result,
    build_sandbox_douyin_operation_result,
)


SANDBOX_OPERATION_REFERENCES = {
    "start_oauth": "sandbox_oauth_start_001",
    "handle_oauth_callback": "sandbox_oauth_callback_001",
    "exchange_token": "sandbox_exchange_001",
    "refresh_token": "sandbox_refresh_001",
    "revoke_token": "sandbox_revoke_001",
    "disconnect": "sandbox_disconnect_001",
    "fetch_metrics": "sandbox_metrics_001",
    "prepare_publish": "sandbox_prepare_001",
    "upload_video": "sandbox_video_001",
    "publish_video": "sandbox_publish_001",
    "schedule_publish": "sandbox_schedule_001",
}


@dataclass(frozen=True)
class DouyinProviderAdapter:
    provider_id: str
    provider_name: str
    source_type: str
    is_real_provider: bool
    supports_oauth: bool = False
    supports_metrics_read: bool = False
    supports_publish_prepare: bool = False
    supports_real_publish: bool = False
    supports_token_refresh: bool = False
    supports_disconnect: bool = False
    supports_revoke: bool = False

    def start_oauth(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._blocked("start_oauth")

    def handle_oauth_callback(
        self, *_args: object, **_kwargs: object
    ) -> DouyinAdapterOperationResult:
        return self._blocked("handle_oauth_callback")

    def exchange_token(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._blocked("exchange_token")

    def refresh_token(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._blocked("refresh_token")

    def revoke_token(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._blocked("revoke_token")

    def disconnect(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._blocked("disconnect")

    def fetch_metrics(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._blocked("fetch_metrics")

    def prepare_publish(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._blocked("prepare_publish")

    def upload_video(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._blocked("upload_video")

    def publish_video(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._blocked("publish_video")

    def schedule_publish(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._blocked("schedule_publish")

    def _blocked(self, operation: str) -> DouyinAdapterOperationResult:
        return build_blocked_douyin_operation_result(
            provider_id=self.provider_id,
            source_type=self.source_type,
            operation=operation,
            is_real_provider=self.is_real_provider,
        )


class DouyinSandboxAdapter(DouyinProviderAdapter):
    def __init__(self) -> None:
        super().__init__(
            provider_id="douyin_sandbox",
            provider_name="Douyin Sandbox Adapter Skeleton",
            source_type="sandbox",
            is_real_provider=False,
        )

    def start_oauth(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._simulated("start_oauth")

    def handle_oauth_callback(
        self, *_args: object, **_kwargs: object
    ) -> DouyinAdapterOperationResult:
        return self._simulated("handle_oauth_callback")

    def exchange_token(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._simulated("exchange_token")

    def refresh_token(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._simulated("refresh_token")

    def revoke_token(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._simulated("revoke_token")

    def disconnect(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._simulated("disconnect")

    def fetch_metrics(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._simulated("fetch_metrics")

    def prepare_publish(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._simulated("prepare_publish")

    def upload_video(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._simulated("upload_video")

    def publish_video(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._simulated("publish_video")

    def schedule_publish(self, *_args: object, **_kwargs: object) -> DouyinAdapterOperationResult:
        return self._simulated("schedule_publish")

    def _simulated(self, operation: str) -> DouyinAdapterOperationResult:
        return build_sandbox_douyin_operation_result(
            provider_id=self.provider_id,
            source_type=self.source_type,
            operation=operation,
            is_real_provider=self.is_real_provider,
            simulation_reference=SANDBOX_OPERATION_REFERENCES[operation],
            simulation_details={
                "provider": self.provider_id,
                "source": self.source_type,
                "mode": "sandbox",
                "outcome": "simulated",
                "dry_run": True,
                "external_call": False,
            },
        )


class DouyinRealAdapter(DouyinProviderAdapter):
    def __init__(self) -> None:
        super().__init__(
            provider_id="douyin_real",
            provider_name="Douyin Real Adapter Skeleton",
            source_type="real",
            is_real_provider=True,
        )


def list_douyin_provider_adapters() -> list[DouyinProviderAdapter]:
    return [DouyinSandboxAdapter(), DouyinRealAdapter()]


def get_douyin_provider_adapter(provider_id: str) -> DouyinProviderAdapter | None:
    adapters = {adapter.provider_id: adapter for adapter in list_douyin_provider_adapters()}
    return adapters.get(provider_id)
