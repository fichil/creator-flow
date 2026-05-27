from fastapi.testclient import TestClient

from app.providers.fake_llm import FakeLLMProvider
from app.providers.platform_registry import get_platform_provider, list_platform_providers
from app.providers.registry import get_llm_provider


SENSITIVE_RESPONSE_FIELD_NAMES = {
    "access_token",
    "refresh_token",
    "token_value",
    "api_key",
    "secret",
    "client_secret",
    "authorization_code",
    "credential_material",
    "raw_response",
}

SENSITIVE_ERROR_TERMS = {
    "token",
    "secret",
    "credential",
    "authorization_code",
    "api_key",
    "client_secret",
}


def test_list_provider_registry_returns_stable_provider_metadata(client: TestClient):
    response = client.get("/api/providers")

    assert response.status_code == 200
    body = response.json()
    assert list(body.keys()) == ["providers"]
    assert [provider["provider_id"] for provider in body["providers"]] == [
        "fake_local",
        "douyin_sandbox",
        "douyin_real",
    ]
    assert_response_has_no_sensitive_field_names(body)


def test_fake_local_provider_metadata_is_available_local_fake(client: TestClient):
    provider = get_provider_from_list(client, "fake_local")

    assert provider["provider_name"] == "Local Fake Provider"
    assert provider["provider_type"] == "platform"
    assert provider["source_type"] == "fake_local"
    assert provider["implementation_status"] == "available_local_fake"
    assert provider["connection_status"] == "not_required"
    assert provider["is_available"] is True
    assert provider["is_real_provider"] is False
    assert provider["requires_user_authorization"] is False
    assert provider["capabilities"] == {
        "supports_oauth": False,
        "supports_metrics_read": True,
        "supports_publish_prepare": True,
        "supports_real_publish": False,
        "supports_sandbox": False,
        "supports_token_refresh": False,
        "supports_disconnect": False,
        "supports_revoke": False,
    }
    notes = " ".join(provider["boundary_notes"])
    assert "local fake/demo/test data only" in notes
    assert "not real Douyin data" in notes
    assert "no OAuth required" in notes
    assert "no token stored" in notes


def test_douyin_sandbox_provider_metadata_is_placeholder_only(client: TestClient):
    provider = get_provider_from_list(client, "douyin_sandbox")

    assert provider["provider_name"] == "Douyin Sandbox Placeholder"
    assert provider["provider_type"] == "platform"
    assert provider["source_type"] == "sandbox"
    assert provider["implementation_status"] == "planned"
    assert provider["connection_status"] == "not_connected"
    assert provider["is_available"] is False
    assert provider["is_real_provider"] is False
    assert provider["requires_user_authorization"] is True
    assert provider["capabilities"] == {
        "supports_oauth": False,
        "supports_metrics_read": False,
        "supports_publish_prepare": False,
        "supports_real_publish": False,
        "supports_sandbox": True,
        "supports_token_refresh": False,
        "supports_disconnect": False,
        "supports_revoke": False,
    }
    notes = " ".join(provider["boundary_notes"])
    assert "placeholder only" in notes
    assert "OAuth is not implemented" in notes
    assert "tokens are not stored" in notes
    assert "no real Douyin API call" in notes
    assert "cannot be treated as douyin_real" in notes


def test_douyin_real_provider_metadata_is_unavailable_real_placeholder(client: TestClient):
    provider = get_provider_from_list(client, "douyin_real")

    assert provider["provider_name"] == "Douyin Real Placeholder"
    assert provider["provider_type"] == "platform"
    assert provider["source_type"] == "real"
    assert provider["implementation_status"] == "planned"
    assert provider["connection_status"] == "not_connected"
    assert provider["is_available"] is False
    assert provider["is_real_provider"] is True
    assert provider["requires_user_authorization"] is True
    assert provider["capabilities"] == {
        "supports_oauth": False,
        "supports_metrics_read": False,
        "supports_publish_prepare": False,
        "supports_real_publish": False,
        "supports_sandbox": False,
        "supports_token_refresh": False,
        "supports_disconnect": False,
        "supports_revoke": False,
    }
    notes = " ".join(provider["boundary_notes"])
    assert "not real Douyin integration" in notes
    assert "OAuth is not implemented" in notes
    assert "access token or refresh token storage" in notes
    assert "no real metrics fetching" in notes
    assert "no upload / publish / scheduling" in notes


def test_get_each_provider_by_id(client: TestClient):
    for provider_id in ("fake_local", "douyin_sandbox", "douyin_real"):
        response = client.get(f"/api/providers/{provider_id}")

        assert response.status_code == 200
        assert response.json()["provider_id"] == provider_id
        assert_response_has_no_sensitive_field_names(response.json())


def test_unknown_provider_returns_404_without_sensitive_terms(client: TestClient):
    response = client.get("/api/providers/unknown")

    assert response.status_code == 404
    assert response.json()["detail"] == "Provider not found"
    response_text = response.text.lower()
    for term in SENSITIVE_ERROR_TERMS:
        assert term not in response_text


def test_registry_module_returns_static_metadata_without_credentials(monkeypatch):
    monkeypatch.setenv("DOUYIN_API_KEY", "fake-env-value")
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", "fake-env-value")
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", "fake-env-value")

    providers = list_platform_providers()
    fake_local = get_platform_provider("fake_local")
    missing = get_platform_provider("missing")

    assert [provider.provider_id for provider in providers] == ["fake_local", "douyin_sandbox", "douyin_real"]
    assert fake_local is not None
    assert fake_local.provider_id == "fake_local"
    assert missing is None


def test_existing_llm_fake_provider_registry_semantics_are_not_changed():
    provider = get_llm_provider()

    assert isinstance(provider, FakeLLMProvider)
    assert provider.provider_name == "fake_llm"


def get_provider_from_list(client: TestClient, provider_id: str) -> dict:
    response = client.get("/api/providers")
    assert response.status_code == 200
    providers = {provider["provider_id"]: provider for provider in response.json()["providers"]}
    return providers[provider_id]


def assert_response_has_no_sensitive_field_names(payload) -> None:
    for key in collect_keys(payload):
        assert key not in SENSITIVE_RESPONSE_FIELD_NAMES


def collect_keys(payload) -> set[str]:
    if isinstance(payload, dict):
        keys = set(payload)
        for value in payload.values():
            keys.update(collect_keys(value))
        return keys
    if isinstance(payload, list):
        keys = set()
        for value in payload:
            keys.update(collect_keys(value))
        return keys
    return set()
