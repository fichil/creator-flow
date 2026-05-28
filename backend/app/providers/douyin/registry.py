from dataclasses import dataclass

from app.providers.douyin.adapter import (
    DouyinProviderAdapter,
    DouyinRealAdapter,
    DouyinSandboxAdapter,
)


@dataclass(frozen=True)
class DouyinProviderDescriptor:
    provider_id: str
    display_name: str
    environment: str
    status: str
    supports_simulation: bool
    supports_real_oauth: bool
    supports_real_publish: bool
    supports_real_metrics: bool


_DOUYIN_SANDBOX_DESCRIPTOR = DouyinProviderDescriptor(
    provider_id="douyin_sandbox",
    display_name="Douyin Sandbox Provider",
    environment="sandbox",
    status="available_for_sandbox",
    supports_simulation=True,
    supports_real_oauth=False,
    supports_real_publish=False,
    supports_real_metrics=False,
)

_DOUYIN_REAL_DESCRIPTOR = DouyinProviderDescriptor(
    provider_id="douyin_real",
    display_name="Douyin Real Provider",
    environment="real",
    status="blocked",
    supports_simulation=False,
    supports_real_oauth=False,
    supports_real_publish=False,
    supports_real_metrics=False,
)

_DOUYIN_PROVIDER_DESCRIPTORS: tuple[DouyinProviderDescriptor, ...] = (
    _DOUYIN_SANDBOX_DESCRIPTOR,
    _DOUYIN_REAL_DESCRIPTOR,
)
_DOUYIN_PROVIDER_DESCRIPTOR_BY_ID = {
    descriptor.provider_id: descriptor for descriptor in _DOUYIN_PROVIDER_DESCRIPTORS
}
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


def list_douyin_provider_descriptors() -> list[DouyinProviderDescriptor]:
    return list(_DOUYIN_PROVIDER_DESCRIPTORS)


def get_douyin_provider_descriptor(provider_id: str) -> DouyinProviderDescriptor:
    descriptor = _DOUYIN_PROVIDER_DESCRIPTOR_BY_ID.get(provider_id)
    if descriptor is None:
        raise ValueError(f"Unsupported Douyin provider id: {_format_provider_id(provider_id)}")
    return descriptor


def create_douyin_provider_adapter(provider_id: str) -> DouyinProviderAdapter:
    descriptor = get_douyin_provider_descriptor(provider_id)
    if descriptor.provider_id == "douyin_sandbox":
        return DouyinSandboxAdapter()
    if descriptor.provider_id == "douyin_real":
        return DouyinRealAdapter()
    raise ValueError(f"Unsupported Douyin provider id: {_format_provider_id(provider_id)}")


def _format_provider_id(provider_id: object) -> str:
    if provider_id is None:
        return "<missing>"
    if provider_id == "":
        return "<empty>"
    provider_text = str(provider_id)
    provider_text_lower = provider_text.lower()
    if any(part in provider_text_lower for part in _SENSITIVE_PROVIDER_ID_PARTS):
        return "<redacted>"
    return provider_text
