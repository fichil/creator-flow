import importlib.util
import json
import socket
import sqlite3
import urllib.request
from dataclasses import asdict

import pytest

from app.core.config import get_settings
from app.main import app
from app.providers.real_provider_controls import (
    FeatureFlagStatus,
    KillSwitchStatus,
    PlatformPreconditionsStatus,
    RealProviderCapability,
    RealProviderControlDecisionStatus,
    RealProviderControlPolicy,
    RuntimeEnvironmentStatus,
    evaluate_real_provider_control,
)


FAKE_ACCESS_TOKEN_VALUE = "fake-access-token-value"
FAKE_REFRESH_TOKEN_VALUE = "fake-refresh-token-value"
FAKE_SECRET_VALUE = "fake-secret-value"
FAKE_CLIENT_SECRET_VALUE = "fake-client-secret-value"
FAKE_CREDENTIAL_VALUE = "fake-credential-value"
FAKE_AUTHORIZATION_CODE_VALUE = "fake-authorization-code-value"
FAKE_RAW_STATE_VALUE = "fake-raw-oauth-state-value"
FAKE_COOKIE_VALUE = "fake-cookie-value"
FAKE_SESSION_VALUE = "fake-session-value"
FAKE_API_KEY_VALUE = "fake-api-key-value"
FAKE_BEARER_VALUE = "fake-bearer-value"
FAKE_RAW_REQUEST_VALUE = "fake-raw-request-value"
FAKE_RAW_RESPONSE_VALUE = "fake-raw-response-value"

FORBIDDEN_MATERIAL_VALUES = {
    FAKE_ACCESS_TOKEN_VALUE,
    FAKE_REFRESH_TOKEN_VALUE,
    FAKE_SECRET_VALUE,
    FAKE_CLIENT_SECRET_VALUE,
    FAKE_CREDENTIAL_VALUE,
    FAKE_AUTHORIZATION_CODE_VALUE,
    FAKE_RAW_STATE_VALUE,
    FAKE_COOKIE_VALUE,
    FAKE_SESSION_VALUE,
    FAKE_API_KEY_VALUE,
    FAKE_BEARER_VALUE,
    FAKE_RAW_REQUEST_VALUE,
    FAKE_RAW_RESPONSE_VALUE,
}


def test_douyin_real_is_blocked_by_default():
    decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.OAUTH.value,
    )

    assert decision.status == RealProviderControlDecisionStatus.BLOCKED_KILL_SWITCH_ACTIVE.value
    assert decision.provider_id == "douyin_real"
    assert decision.source_type == "real"
    assert decision.kill_switch_status == KillSwitchStatus.ACTIVE.value
    assert decision.real_provider_enabled is False
    assert decision.external_service_allowed is False
    assert decision.sandbox_fallback_performed is False


def test_kill_switch_active_takes_precedence_over_enabled_feature_flag():
    policy = allowing_policy(
        RealProviderCapability.OAUTH,
        kill_switch_status=KillSwitchStatus.ACTIVE.value,
    )

    decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.OAUTH.value,
        control_policy=policy,
    )

    assert decision.status == RealProviderControlDecisionStatus.BLOCKED_KILL_SWITCH_ACTIVE.value
    assert decision.feature_flag_status == FeatureFlagStatus.ENABLED.value
    assert decision.kill_switch_status == KillSwitchStatus.ACTIVE.value
    assert decision.real_provider_enabled is False


def test_feature_flag_disabled_blocks_real_provider():
    policy = allowing_policy(
        RealProviderCapability.OAUTH,
        feature_flag_status=FeatureFlagStatus.DISABLED.value,
    )

    decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.OAUTH.value,
        control_policy=policy,
    )

    assert (
        decision.status
        == RealProviderControlDecisionStatus.BLOCKED_FEATURE_FLAG_DISABLED.value
    )
    assert decision.feature_flag_status == FeatureFlagStatus.DISABLED.value


def test_missing_feature_flag_blocks_real_provider():
    decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.OAUTH.value,
        control_policy={
            "kill_switch_status": KillSwitchStatus.INACTIVE.value,
            "allowed_capabilities": [RealProviderCapability.OAUTH.value],
            "environment_status": RuntimeEnvironmentStatus.ALLOWED.value,
            "platform_preconditions_status": PlatformPreconditionsStatus.ACCEPTED.value,
        },
    )

    assert (
        decision.status
        == RealProviderControlDecisionStatus.BLOCKED_FEATURE_FLAG_DISABLED.value
    )
    assert decision.feature_flag_status == FeatureFlagStatus.MISSING.value


def test_malformed_feature_flag_blocks_real_provider():
    policy = {
        "feature_flag_status": "enabled-ish",
        "kill_switch_status": KillSwitchStatus.INACTIVE.value,
        "allowed_capabilities": [RealProviderCapability.OAUTH.value],
        "environment_status": RuntimeEnvironmentStatus.ALLOWED.value,
        "platform_preconditions_status": PlatformPreconditionsStatus.ACCEPTED.value,
    }

    decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.OAUTH.value,
        control_policy=policy,
    )

    assert (
        decision.status
        == RealProviderControlDecisionStatus.BLOCKED_FEATURE_FLAG_DISABLED.value
    )
    assert decision.feature_flag_status == FeatureFlagStatus.MALFORMED.value


def test_malformed_kill_switch_blocks_real_provider():
    policy = allowing_policy(
        RealProviderCapability.OAUTH,
        kill_switch_status="inactive-ish",
    )

    decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.OAUTH.value,
        control_policy=policy,
    )

    assert decision.status == RealProviderControlDecisionStatus.BLOCKED_KILL_SWITCH_ACTIVE.value
    assert decision.kill_switch_status == KillSwitchStatus.MALFORMED.value


def test_unsupported_provider_is_blocked():
    decision = evaluate_real_provider_control(
        "unknown_provider",
        RealProviderCapability.OAUTH.value,
    )

    assert (
        decision.status
        == RealProviderControlDecisionStatus.BLOCKED_UNSUPPORTED_PROVIDER.value
    )
    assert decision.provider_id is None
    assert decision.source_type is None


def test_unsupported_capability_is_blocked():
    decision = evaluate_real_provider_control(
        "douyin_real",
        "real_world_domination",
        control_policy=allowing_policy(RealProviderCapability.OAUTH),
    )

    assert (
        decision.status
        == RealProviderControlDecisionStatus.BLOCKED_OPERATION_NOT_ALLOWED.value
    )
    assert decision.capability is None
    assert decision.real_provider_enabled is False


def test_platform_preconditions_missing_blocks_real_provider():
    policy = allowing_policy(
        RealProviderCapability.OAUTH,
        platform_preconditions_status=PlatformPreconditionsStatus.MISSING.value,
    )

    decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.OAUTH.value,
        control_policy=policy,
    )

    assert (
        decision.status
        == RealProviderControlDecisionStatus.BLOCKED_PRECONDITIONS_MISSING.value
    )
    assert decision.platform_preconditions_status == PlatformPreconditionsStatus.MISSING.value


def test_environment_not_allowed_blocks_real_provider():
    policy = allowing_policy(
        RealProviderCapability.OAUTH,
        environment_status=RuntimeEnvironmentStatus.DISABLED.value,
    )

    decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.OAUTH.value,
        control_policy=policy,
    )

    assert (
        decision.status
        == RealProviderControlDecisionStatus.BLOCKED_PRECONDITIONS_MISSING.value
    )
    assert decision.environment_status == RuntimeEnvironmentStatus.DISABLED.value


def test_capability_disabled_blocks_real_provider():
    policy = allowing_policy(RealProviderCapability.OAUTH)

    decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.PUBLISH.value,
        control_policy=policy,
    )

    assert (
        decision.status
        == RealProviderControlDecisionStatus.BLOCKED_CAPABILITY_DISABLED.value
    )
    assert decision.capability == RealProviderCapability.PUBLISH.value


def test_sandbox_fallback_attempt_is_blocked():
    decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.OAUTH.value,
        control_policy=allowing_policy(RealProviderCapability.OAUTH),
        fallback_provider_id="douyin_sandbox",
    )

    assert (
        decision.status
        == RealProviderControlDecisionStatus.BLOCKED_SANDBOX_FALLBACK_FORBIDDEN.value
    )
    assert decision.provider_id == "douyin_real"
    assert decision.source_type == "real"
    assert decision.sandbox_fallback_performed is False


def test_douyin_real_does_not_fallback_to_douyin_sandbox():
    real_decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.METRICS_READ.value,
        control_policy=allowing_policy(RealProviderCapability.METRICS_READ),
        fallback_provider_id="douyin_sandbox",
    )
    sandbox_decision = evaluate_real_provider_control(
        "douyin_sandbox",
        RealProviderCapability.METRICS_READ.value,
        control_policy=allowing_policy(RealProviderCapability.METRICS_READ),
    )

    assert (
        real_decision.status
        == RealProviderControlDecisionStatus.BLOCKED_SANDBOX_FALLBACK_FORBIDDEN.value
    )
    assert sandbox_decision.status == RealProviderControlDecisionStatus.ALLOWED_SANDBOX_ONLY.value
    assert real_decision.sandbox_fallback_performed is False


def test_fake_local_and_sandbox_are_not_mixed_with_real_enablement():
    policy = allowing_policy(
        RealProviderCapability.PUBLISH,
        RealProviderCapability.METRICS_READ,
        RealProviderCapability.OAUTH,
    )

    fake_decision = evaluate_real_provider_control(
        "fake_local",
        RealProviderCapability.PUBLISH.value,
        control_policy=policy,
    )
    sandbox_decision = evaluate_real_provider_control(
        "douyin_sandbox",
        RealProviderCapability.METRICS_READ.value,
        control_policy=policy,
    )

    assert fake_decision.status == RealProviderControlDecisionStatus.ALLOWED_FAKE_ONLY.value
    assert fake_decision.source_type == "fake_local"
    assert fake_decision.real_provider_enabled is False
    assert sandbox_decision.status == RealProviderControlDecisionStatus.ALLOWED_SANDBOX_ONLY.value
    assert sandbox_decision.source_type == "sandbox"
    assert sandbox_decision.real_provider_enabled is False


@pytest.mark.parametrize(
    "capability",
    [
        RealProviderCapability.OAUTH,
        RealProviderCapability.TOKEN_EXCHANGE,
        RealProviderCapability.CREDENTIAL_STORAGE,
        RealProviderCapability.PUBLISH,
        RealProviderCapability.PUBLISH_STATUS,
        RealProviderCapability.METRICS_READ,
        RealProviderCapability.DISCONNECT,
        RealProviderCapability.REVOKE,
    ],
)
def test_real_capabilities_remain_default_blocked(capability):
    decision = evaluate_real_provider_control("douyin_real", capability.value)

    assert decision.status == RealProviderControlDecisionStatus.BLOCKED_KILL_SWITCH_ACTIVE.value
    assert decision.real_provider_enabled is False
    assert decision.external_service_allowed is False


@pytest.mark.parametrize(
    "capability",
    [
        RealProviderCapability.OAUTH,
        RealProviderCapability.TOKEN_EXCHANGE,
        RealProviderCapability.CREDENTIAL_STORAGE,
        RealProviderCapability.PUBLISH,
        RealProviderCapability.METRICS_READ,
    ],
)
def test_real_capabilities_remain_blocked_even_when_controls_are_accepting(capability):
    decision = evaluate_real_provider_control(
        "douyin_real",
        capability.value,
        control_policy=allowing_policy(capability),
    )

    assert decision.status == RealProviderControlDecisionStatus.BLOCKED_REAL_PROVIDER.value
    assert decision.real_provider_enabled is False
    assert decision.external_service_allowed is False


def test_decision_output_contains_only_safe_metadata():
    decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.OAUTH.value,
        control_policy=allowing_policy(RealProviderCapability.OAUTH),
    )

    assert set(asdict(decision)) == {
        "status",
        "provider_id",
        "source_type",
        "capability",
        "feature_flag_status",
        "kill_switch_status",
        "environment_status",
        "platform_preconditions_status",
        "real_provider_enabled",
        "external_service_allowed",
        "sandbox_fallback_performed",
        "safe_status_message",
    }
    assert_no_material_values(decision)


def test_service_result_repr_and_safe_message_do_not_contain_material():
    decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.OAUTH.value,
        control_policy=allowing_policy(RealProviderCapability.OAUTH),
    )

    assert_no_material_text(json.dumps(asdict(decision), sort_keys=True))
    assert_no_material_text(repr(decision))
    assert_no_material_text(decision.safe_status_message)


def test_service_does_not_read_or_leak_environment_secrets(monkeypatch):
    fake_env_values = [
        FAKE_ACCESS_TOKEN_VALUE,
        FAKE_REFRESH_TOKEN_VALUE,
        FAKE_SECRET_VALUE,
        FAKE_CLIENT_SECRET_VALUE,
        FAKE_CREDENTIAL_VALUE,
        FAKE_AUTHORIZATION_CODE_VALUE,
        FAKE_RAW_STATE_VALUE,
        FAKE_COOKIE_VALUE,
        FAKE_SESSION_VALUE,
        FAKE_API_KEY_VALUE,
        FAKE_BEARER_VALUE,
    ]
    monkeypatch.setenv("DOUYIN_ACCESS_TOKEN", fake_env_values[0])
    monkeypatch.setenv("DOUYIN_REFRESH_TOKEN", fake_env_values[1])
    monkeypatch.setenv("DOUYIN_SECRET", fake_env_values[2])
    monkeypatch.setenv("DOUYIN_CLIENT_SECRET", fake_env_values[3])
    monkeypatch.setenv("DOUYIN_CREDENTIAL", fake_env_values[4])
    monkeypatch.setenv("DOUYIN_AUTHORIZATION_CODE", fake_env_values[5])
    monkeypatch.setenv("DOUYIN_RAW_OAUTH_STATE", fake_env_values[6])
    monkeypatch.setenv("DOUYIN_COOKIE", fake_env_values[7])
    monkeypatch.setenv("DOUYIN_SESSION", fake_env_values[8])
    monkeypatch.setenv("DOUYIN_API_KEY", fake_env_values[9])
    monkeypatch.setenv("DOUYIN_BEARER", fake_env_values[10])

    decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.OAUTH.value,
        control_policy=allowing_policy(RealProviderCapability.OAUTH),
    )

    decision_text = json.dumps(asdict(decision), sort_keys=True)
    for value in fake_env_values:
        assert value not in decision_text


def test_service_does_not_call_external_network(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("real provider controls must not call external network")

    monkeypatch.setattr(socket, "create_connection", fail_if_called)
    monkeypatch.setattr(urllib.request, "urlopen", fail_if_called)

    if importlib.util.find_spec("requests") is not None:
        import requests

        monkeypatch.setattr(requests.sessions.Session, "request", fail_if_called)

    if importlib.util.find_spec("httpx") is not None:
        import httpx

        monkeypatch.setattr(httpx.Client, "request", fail_if_called)
        monkeypatch.setattr(httpx.AsyncClient, "request", fail_if_called)

    decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.PUBLISH.value,
        control_policy=allowing_policy(RealProviderCapability.PUBLISH),
    )

    assert decision.external_service_allowed is False
    assert decision.real_provider_enabled is False


def test_batch5_does_not_add_oauth_or_real_provider_routes():
    route_paths = {getattr(route, "path", "") for route in app.routes}

    forbidden_paths = {
        "/api/provider-auth/{provider_id}/oauth/start",
        "/api/provider-auth/{provider_id}/oauth/callback",
        "/api/provider-auth/{provider_id}/oauth/url",
        "/api/provider-auth/{provider_id}/token/exchange",
        "/api/provider-real-controls",
        "/api/douyin-real/publish",
        "/api/douyin-real/metrics",
    }
    assert route_paths.isdisjoint(forbidden_paths)
    assert all("/oauth/start" not in path for path in route_paths)
    assert all("/oauth/callback" not in path for path in route_paths)
    assert all("/oauth/url" not in path for path in route_paths)
    assert all("/token/exchange" not in path for path in route_paths)
    assert all("douyin-real" not in path for path in route_paths)


def test_no_real_token_credential_runtime_control_schema_is_added(client):
    with sqlite3.connect(get_settings().database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert "provider_runtime_controls" not in tables
    assert "provider_tokens" not in tables
    assert "provider_token_storage" not in tables
    assert "provider_credential_payloads" not in tables
    assert "provider_encrypted_credentials" not in tables


def test_no_real_publish_or_metrics_behavior_is_enabled():
    publish_decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.PUBLISH.value,
        control_policy=allowing_policy(RealProviderCapability.PUBLISH),
    )
    metrics_decision = evaluate_real_provider_control(
        "douyin_real",
        RealProviderCapability.METRICS_READ.value,
        control_policy=allowing_policy(RealProviderCapability.METRICS_READ),
    )

    assert publish_decision.status == RealProviderControlDecisionStatus.BLOCKED_REAL_PROVIDER.value
    assert metrics_decision.status == RealProviderControlDecisionStatus.BLOCKED_REAL_PROVIDER.value
    assert publish_decision.external_service_allowed is False
    assert metrics_decision.external_service_allowed is False


def allowing_policy(
    *capabilities: RealProviderCapability,
    feature_flag_status: str = FeatureFlagStatus.ENABLED.value,
    kill_switch_status: str = KillSwitchStatus.INACTIVE.value,
    environment_status: str = RuntimeEnvironmentStatus.ALLOWED.value,
    platform_preconditions_status: str = PlatformPreconditionsStatus.ACCEPTED.value,
) -> RealProviderControlPolicy:
    return RealProviderControlPolicy(
        feature_flag_status=feature_flag_status,
        kill_switch_status=kill_switch_status,
        allowed_capabilities=frozenset(capability.value for capability in capabilities),
        environment_status=environment_status,
        platform_preconditions_status=platform_preconditions_status,
    )


def assert_no_material_values(value) -> None:
    assert_no_material_text(json.dumps(asdict(value), default=str, sort_keys=True))


def assert_no_material_text(text: str) -> None:
    for material_value in FORBIDDEN_MATERIAL_VALUES:
        assert material_value not in text
