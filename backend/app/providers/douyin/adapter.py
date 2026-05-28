from dataclasses import dataclass

from app.providers.douyin.boundary import (
    DouyinAdapterOperationResult,
    build_blocked_douyin_operation_result,
)


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
