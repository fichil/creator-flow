import re
from typing import Any


REDACTED_VALUE = "[REDACTED]"

_SENSITIVE_KEYS = {
    "access_token",
    "refresh_token",
    "token",
    "token_value",
    "api_key",
    "secret",
    "secret_value",
    "client_secret",
    "authorization_code",
    "credential",
    "credential_material",
    "encrypted_credential",
    "private_key",
    "oauth_code",
    "password",
    "bearer",
    "bearer_token",
    "cookie",
    "session",
    "session_cookie",
    "oauth_client_secret",
}

_SENSITIVE_ASSIGNMENT_PATTERN = re.compile(
    r"\b("
    r"access_token|refresh_token|token|token_value|api_key|secret|secret_value|"
    r"client_secret|oauth_client_secret|authorization_code|credential|credential_material|"
    r"encrypted_credential|private_key|oauth_code|password|bearer_token|session_cookie"
    r")\s*=\s*[^&\s,;]+",
    re.IGNORECASE,
)
_BEARER_PATTERN = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]+", re.IGNORECASE)


def is_sensitive_key(key: str) -> bool:
    return _normalize_key(key) in _SENSITIVE_KEYS


def redact_sensitive_mapping(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: REDACTED_VALUE if is_sensitive_key(str(key)) else redact_sensitive_mapping(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_sensitive_mapping(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_sensitive_mapping(item) for item in value)
    return value


def redact_sensitive_text(text: str) -> str:
    redacted = _SENSITIVE_ASSIGNMENT_PATTERN.sub(
        lambda match: f"{match.group(1)}={REDACTED_VALUE}",
        text,
    )
    return _BEARER_PATTERN.sub(f"Bearer {REDACTED_VALUE}", redacted)


def build_safe_error_message(message: str) -> str:
    if redact_sensitive_text(message) != message:
        return "Provider credential operation failed; sensitive details were redacted."
    return "Provider credential operation failed."


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace("-", "_")
