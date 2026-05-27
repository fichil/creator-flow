import os
import socket

from app.security.redaction import (
    REDACTED_VALUE,
    build_safe_error_message,
    is_sensitive_key,
    redact_sensitive_mapping,
    redact_sensitive_text,
)


def test_sensitive_key_detection_marks_known_secret_carrier_names():
    sensitive_keys = [
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
        "cookie",
        "session",
    ]

    for key in sensitive_keys:
        assert is_sensitive_key(key) is True


def test_sensitive_key_detection_leaves_safe_metadata_names_visible():
    safe_keys = [
        "provider_id",
        "provider_name",
        "source_type",
        "connection_status",
        "reference_status",
        "storage_status",
        "safe_status_message",
        "boundary_notes",
    ]

    for key in safe_keys:
        assert is_sensitive_key(key) is False


def test_redact_sensitive_mapping_recursively_redacts_dict_list_and_tuple():
    payload = {
        "provider_id": "fake_local",
        "access_token": "fake-access-token-value",
        "nested": {
            "api_key": "fake-api-key-value",
            "safe": "kept",
            "items": [
                {"client_secret": "fake-client-secret-value"},
                ("safe-tuple-value", {"authorization_code": "fake-auth-code-value"}),
            ],
        },
    }

    redacted = redact_sensitive_mapping(payload)

    assert redacted["provider_id"] == "fake_local"
    assert redacted["access_token"] == REDACTED_VALUE
    assert redacted["nested"]["api_key"] == REDACTED_VALUE
    assert redacted["nested"]["safe"] == "kept"
    assert redacted["nested"]["items"][0]["client_secret"] == REDACTED_VALUE
    assert redacted["nested"]["items"][1][0] == "safe-tuple-value"
    assert redacted["nested"]["items"][1][1]["authorization_code"] == REDACTED_VALUE


def test_redacted_mapping_does_not_contain_nested_sensitive_values():
    payload = {
        "refresh_token": "fake-refresh-token-value",
        "children": [
            {"secret": "fake-secret-value"},
            {"credential_material": "fake-credential-material-value"},
        ],
    }

    redacted_text = str(redact_sensitive_mapping(payload))

    assert "fake-refresh-token-value" not in redacted_text
    assert "fake-secret-value" not in redacted_text
    assert "fake-credential-material-value" not in redacted_text
    assert REDACTED_VALUE in redacted_text


def test_redact_sensitive_text_redacts_common_secret_patterns():
    message = (
        "access_token=fake-access refresh_token=fake-refresh "
        "api_key=fake-api client_secret=fake-client "
        "authorization_code=fake-code Bearer fake-bearer"
    )

    redacted = redact_sensitive_text(message)

    assert "fake-access" not in redacted
    assert "fake-refresh" not in redacted
    assert "fake-api" not in redacted
    assert "fake-client" not in redacted
    assert "fake-code" not in redacted
    assert "fake-bearer" not in redacted
    assert "access_token=[REDACTED]" in redacted
    assert "refresh_token=[REDACTED]" in redacted
    assert "api_key=[REDACTED]" in redacted
    assert "client_secret=[REDACTED]" in redacted
    assert "authorization_code=[REDACTED]" in redacted
    assert "Bearer [REDACTED]" in redacted


def test_build_safe_error_message_does_not_echo_sensitive_input_values():
    message = (
        "Failed with access_token=fake-access secret=fake-secret "
        "api_key=fake-api authorization_code=fake-code"
    )

    safe_message = build_safe_error_message(message)

    assert safe_message == (
        "Provider credential operation failed; sensitive details were redacted."
    )
    assert "fake-access" not in safe_message
    assert "fake-secret" not in safe_message
    assert "fake-api" not in safe_message
    assert "fake-code" not in safe_message


def test_redaction_helper_does_not_read_environment_values(monkeypatch):
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", "fake-env-access-value")
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", "fake-env-client-secret-value")

    payload = {"provider_id": "fake_local", "safe": "visible"}
    redacted_payload = redact_sensitive_mapping(payload)
    redacted_text = redact_sensitive_text("provider_id=fake_local")
    safe_message = build_safe_error_message("metadata read failed")

    combined = f"{redacted_payload} {redacted_text} {safe_message}"
    assert "fake-env-access-value" not in combined
    assert "fake-env-client-secret-value" not in combined
    assert os.environ["DOUYIN_ACCESS_TOKEN"] == "fake-env-access-value"


def test_redaction_helper_does_not_call_external_services(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("external service call attempted")

    monkeypatch.setattr(socket, "create_connection", fail_if_called)

    assert redact_sensitive_text("Bearer fake-bearer") == "Bearer [REDACTED]"
    assert redact_sensitive_mapping({"token": "fake-token-value"}) == {
        "token": REDACTED_VALUE
    }
