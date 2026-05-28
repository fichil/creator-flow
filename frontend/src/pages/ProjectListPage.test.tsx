import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProjectListPage } from "./ProjectListPage";
import type {
  PlatformProvider,
  Project,
  ProviderConnectionState,
  ProviderCredentialReference,
  ProviderOAuthBoundary,
  ProviderReadinessSummary,
  ProviderSecurityAuditEvent,
  ProviderTokenLifecycleBoundary,
} from "../api/client";

const providers: PlatformProvider[] = [
  {
    provider_id: "fake_local",
    provider_name: "Local Fake Provider",
    provider_type: "platform",
    source_type: "fake_local",
    implementation_status: "available_local_fake",
    connection_status: "not_required",
    is_available: true,
    is_real_provider: false,
    requires_user_authorization: false,
    capabilities: {
      supports_oauth: false,
      supports_metrics_read: true,
      supports_publish_prepare: true,
      supports_real_publish: false,
      supports_sandbox: false,
      supports_token_refresh: false,
      supports_disconnect: false,
      supports_revoke: false,
    },
    boundary_notes: ["local fake/demo/test data only", "not real Douyin data", "no OAuth required", "no token stored"],
  },
  {
    provider_id: "douyin_sandbox",
    provider_name: "Douyin Sandbox Placeholder",
    provider_type: "platform",
    source_type: "sandbox",
    implementation_status: "planned",
    connection_status: "not_connected",
    is_available: false,
    is_real_provider: false,
    requires_user_authorization: true,
    capabilities: {
      supports_oauth: false,
      supports_metrics_read: false,
      supports_publish_prepare: false,
      supports_real_publish: false,
      supports_sandbox: true,
      supports_token_refresh: false,
      supports_disconnect: false,
      supports_revoke: false,
    },
    boundary_notes: ["placeholder only", "OAuth is not implemented", "tokens are not stored", "no real Douyin API call"],
  },
  {
    provider_id: "douyin_real",
    provider_name: "Douyin Real Placeholder",
    provider_type: "platform",
    source_type: "real",
    implementation_status: "planned",
    connection_status: "not_connected",
    is_available: false,
    is_real_provider: true,
    requires_user_authorization: true,
    capabilities: {
      supports_oauth: false,
      supports_metrics_read: false,
      supports_publish_prepare: false,
      supports_real_publish: false,
      supports_sandbox: false,
      supports_token_refresh: false,
      supports_disconnect: false,
      supports_revoke: false,
    },
    boundary_notes: ["future real provider placeholder only", "not real Douyin integration", "no real metrics fetching"],
  },
];

const project: Project = {
  id: 1,
  title: "Existing project",
  description: "Project list smoke test",
  status: "materials_ready",
  created_at: "2026-05-26T08:00:00Z",
  updated_at: "2026-05-26T08:00:00Z",
  material_count: 2,
};

const douyinSandboxDescriptors = [
  {
    provider_id: "douyin_sandbox",
    display_name: "Douyin Sandbox",
    environment: "sandbox",
    mode: "sandbox",
    status: "available_for_sandbox",
    supports_simulation: true,
    supports_real_oauth: false,
    supports_real_publish: false,
    supports_real_metrics: false,
    simulated: true,
    dry_run: true,
    boundary_notes: ["sandbox descriptor", "simulation only", "deterministic dry-run API contract"],
  },
  {
    provider_id: "douyin_real",
    display_name: "Douyin Real",
    environment: "real",
    mode: "real",
    status: "blocked",
    supports_simulation: false,
    supports_real_oauth: false,
    supports_real_publish: false,
    supports_real_metrics: false,
    simulated: false,
    dry_run: false,
    boundary_notes: ["real provider descriptor", "blocked", "not implemented"],
  },
];

const connections: ProviderConnectionState[] = [
  {
    provider_id: "fake_local",
    provider_name: "Local Fake Provider",
    source_type: "fake_local",
    implementation_status: "available_local_fake",
    connection_status: "not_required",
    authorization_status: "not_required",
    sensitive_storage_status: "none",
    is_available: true,
    is_real_provider: false,
    requires_user_authorization: false,
    can_connect: false,
    can_refresh: false,
    can_revoke: false,
    can_disconnect: false,
    safe_status_message: "Local fake provider does not require authorization and stores no tokens.",
    boundary_notes: ["local fake/demo/test data only", "not real Douyin data", "no OAuth required", "no tokens stored"],
  },
  {
    provider_id: "douyin_sandbox",
    provider_name: "Douyin Sandbox Placeholder",
    source_type: "sandbox",
    implementation_status: "planned",
    connection_status: "not_connected",
    authorization_status: "not_implemented",
    sensitive_storage_status: "not_implemented",
    is_available: false,
    is_real_provider: false,
    requires_user_authorization: true,
    can_connect: false,
    can_refresh: false,
    can_revoke: false,
    can_disconnect: false,
    safe_status_message:
      "Douyin sandbox is placeholder metadata only; OAuth is not implemented and tokens are not stored.",
    boundary_notes: ["placeholder only", "OAuth is not implemented", "tokens are not stored", "no real Douyin API call"],
  },
  {
    provider_id: "douyin_real",
    provider_name: "Douyin Real Placeholder",
    source_type: "real",
    implementation_status: "planned",
    connection_status: "not_connected",
    authorization_status: "not_implemented",
    sensitive_storage_status: "not_implemented",
    is_available: false,
    is_real_provider: true,
    requires_user_authorization: true,
    can_connect: false,
    can_refresh: false,
    can_revoke: false,
    can_disconnect: false,
    safe_status_message:
      "Douyin real provider is a future placeholder only; no OAuth, token storage, metrics fetching, upload, publish, or scheduling is implemented.",
    boundary_notes: ["future real provider placeholder only", "not real Douyin integration", "no real metrics fetching"],
  },
];

const credentialReferences: ProviderCredentialReference[] = [
  {
    provider_id: "fake_local",
    provider_name: "Local Fake Provider",
    source_type: "fake_local",
    implementation_status: "available_local_fake",
    reference_kind: "none_required",
    reference_status: "not_required",
    storage_status: "none",
    redaction_policy_status: "active",
    is_available: true,
    is_real_provider: false,
    requires_user_authorization: false,
    safe_display_name: "Local fake provider credential reference metadata",
    safe_status_message: "Local fake provider does not require credentials, OAuth, tokens, or secrets.",
    boundary_notes: [
      "local fake/demo/test data only",
      "not real Douyin data",
      "no OAuth required",
      "no token stored",
      "no secret stored",
      "no credential material stored",
    ],
  },
  {
    provider_id: "douyin_sandbox",
    provider_name: "Douyin Sandbox Placeholder",
    source_type: "sandbox",
    implementation_status: "planned",
    reference_kind: "oauth_placeholder",
    reference_status: "not_implemented",
    storage_status: "not_implemented",
    redaction_policy_status: "active",
    is_available: false,
    is_real_provider: false,
    requires_user_authorization: true,
    safe_display_name: "Douyin sandbox credential reference placeholder",
    safe_status_message:
      "Douyin sandbox credential reference is placeholder metadata only; OAuth is not implemented and tokens are not stored.",
    boundary_notes: [
      "placeholder only",
      "OAuth is not implemented",
      "tokens are not stored",
      "secrets are not stored",
      "credential material is not stored",
      "no real Douyin API call",
    ],
  },
  {
    provider_id: "douyin_real",
    provider_name: "Douyin Real Placeholder",
    source_type: "real",
    implementation_status: "planned",
    reference_kind: "oauth_placeholder",
    reference_status: "not_implemented",
    storage_status: "not_implemented",
    redaction_policy_status: "active",
    is_available: false,
    is_real_provider: true,
    requires_user_authorization: true,
    safe_display_name: "Douyin real credential reference placeholder",
    safe_status_message:
      "Douyin real credential reference is a future placeholder only; no OAuth, token storage, metrics fetching, upload, publish, or scheduling is implemented.",
    boundary_notes: [
      "future real provider placeholder only",
      "not real Douyin integration",
      "no access token or refresh token storage",
      "no real metrics fetching",
      "no upload / publish / scheduling",
    ],
  },
];

const auditEvents: ProviderSecurityAuditEvent[] = [
  {
    audit_event_id: "audit-fake-local",
    provider_id: "fake_local",
    provider_name: "Local Fake Provider",
    source_type: "fake_local",
    implementation_status: "available_local_fake",
    event_type: "boundary_initialized",
    event_status: "recorded",
    event_severity: "info",
    actor_type: "system",
    redaction_status: "active",
    safe_event_message: "fake_local provider boundary initialized",
    safe_metadata: { status: "recorded" },
    boundary_notes: [
      "local fake/demo/test audit metadata only",
      "not real Douyin data",
      "no OAuth required",
      "no token stored",
      "no secret stored",
      "no external service call",
    ],
    created_at: "2026-05-27T08:00:00Z",
  },
  {
    audit_event_id: "audit-douyin-sandbox",
    provider_id: "douyin_sandbox",
    provider_name: "Douyin Sandbox Placeholder",
    source_type: "sandbox",
    implementation_status: "planned",
    event_type: "credential_reference_checked",
    event_status: "planned",
    event_severity: "warning",
    actor_type: "internal",
    redaction_status: "active",
    safe_event_message: "sandbox placeholder audit metadata checked",
    safe_metadata: { status: "planned" },
    boundary_notes: [
      "placeholder audit metadata only",
      "OAuth is not implemented",
      "tokens are not stored",
      "secrets are not stored",
      "no real Douyin API call",
    ],
    created_at: "2026-05-27T08:01:00Z",
  },
  {
    audit_event_id: "audit-douyin-real",
    provider_id: "douyin_real",
    provider_name: "Douyin Real Placeholder",
    source_type: "real",
    implementation_status: "planned",
    event_type: "authorization_status_checked",
    event_status: "not_implemented",
    event_severity: "security",
    actor_type: "user_placeholder",
    redaction_status: "redacted",
    safe_event_message: "redacted_value=[REDACTED] Bearer [REDACTED]",
    safe_metadata: { redacted_field: "[REDACTED]", safe: "visible" },
    boundary_notes: [
      "future real provider placeholder audit metadata only",
      "not real Douyin integration",
      "OAuth is not implemented",
      "no access token or refresh token storage",
      "no real metrics fetching",
      "no upload / publish / scheduling",
    ],
    created_at: "2026-05-27T08:02:00Z",
  },
];

const oauthBoundaries: ProviderOAuthBoundary[] = [
  {
    provider_id: "fake_local",
    provider_name: "Local Fake Provider",
    source_type: "fake_local",
    implementation_status: "available_local_fake",
    oauth_policy_status: "not_required",
    state_policy_status: "not_required",
    callback_policy_status: "not_required",
    csrf_protection_status: "not_required",
    redirect_uri_policy_status: "not_required",
    token_exchange_policy_status: "not_required",
    token_storage_policy_status: "none",
    error_redaction_policy_status: "active",
    audit_event_policy_status: "metadata_only",
    is_available: true,
    is_real_provider: false,
    requires_user_authorization: false,
    can_start_oauth: false,
    can_handle_callback: false,
    can_exchange_token: false,
    can_refresh_token: false,
    can_revoke_token: false,
    safe_status_message:
      "Local fake provider does not require OAuth state, callback handling, token exchange, or token storage.",
    boundary_notes: [
      "local fake/demo/test data only",
      "not real Douyin data",
      "OAuth is not required",
      "no state value stored",
      "no authorization code stored",
      "no token exchange",
      "no token stored",
      "no secret stored",
      "no external service call",
    ],
  },
  {
    provider_id: "douyin_sandbox",
    provider_name: "Douyin Sandbox Placeholder",
    source_type: "sandbox",
    implementation_status: "planned",
    oauth_policy_status: "not_implemented",
    state_policy_status: "required_planned",
    callback_policy_status: "required_planned",
    csrf_protection_status: "required_planned",
    redirect_uri_policy_status: "required_planned",
    token_exchange_policy_status: "not_implemented",
    token_storage_policy_status: "not_implemented",
    error_redaction_policy_status: "active",
    audit_event_policy_status: "metadata_only",
    is_available: false,
    is_real_provider: false,
    requires_user_authorization: true,
    can_start_oauth: false,
    can_handle_callback: false,
    can_exchange_token: false,
    can_refresh_token: false,
    can_revoke_token: false,
    safe_status_message:
      "Douyin sandbox OAuth boundary is placeholder metadata only; OAuth is not implemented and no state value, authorization code, or token is stored.",
    boundary_notes: [
      "placeholder OAuth boundary metadata only",
      "OAuth is not implemented",
      "OAuth callback route is not implemented",
      "OAuth state storage is not implemented",
      "tokens are not stored",
      "secrets are not stored",
      "no token exchange",
      "no real Douyin API call",
    ],
  },
  {
    provider_id: "douyin_real",
    provider_name: "Douyin Real Placeholder",
    source_type: "real",
    implementation_status: "planned",
    oauth_policy_status: "not_implemented",
    state_policy_status: "required_planned",
    callback_policy_status: "required_planned",
    csrf_protection_status: "required_planned",
    redirect_uri_policy_status: "required_planned",
    token_exchange_policy_status: "not_implemented",
    token_storage_policy_status: "not_implemented",
    error_redaction_policy_status: "active",
    audit_event_policy_status: "metadata_only",
    is_available: false,
    is_real_provider: true,
    requires_user_authorization: true,
    can_start_oauth: false,
    can_handle_callback: false,
    can_exchange_token: false,
    can_refresh_token: false,
    can_revoke_token: false,
    safe_status_message:
      "Douyin real OAuth boundary is a future placeholder only; OAuth callback, state validation, token exchange, token storage, metrics fetching, upload, publish, and scheduling are not implemented.",
    boundary_notes: [
      "future real provider OAuth boundary placeholder only",
      "not real Douyin integration",
      "OAuth is not implemented",
      "OAuth callback route is not implemented",
      "OAuth state storage is not implemented",
      "no access token or refresh token storage",
      "no token exchange",
      "no real metrics fetching",
      "no upload / publish / scheduling",
    ],
  },
];

const tokenLifecycleBoundaries: ProviderTokenLifecycleBoundary[] = [
  {
    provider_id: "fake_local",
    provider_name: "Local Fake Provider",
    source_type: "fake_local",
    implementation_status: "available_local_fake",
    token_lifecycle_policy_status: "not_required",
    token_storage_policy_status: "none",
    refresh_policy_status: "not_required",
    expiry_policy_status: "not_required",
    revoke_policy_status: "not_required",
    disconnect_policy_status: "not_required",
    rotation_policy_status: "not_required",
    error_redaction_policy_status: "active",
    audit_event_policy_status: "metadata_only",
    is_available: true,
    is_real_provider: false,
    requires_user_authorization: false,
    can_refresh_token: false,
    can_revoke_token: false,
    can_disconnect: false,
    can_rotate_token: false,
    can_mark_token_expired: false,
    safe_status_message:
      "Local fake provider does not require token storage, refresh, expiry handling, revoke, disconnect, or rotation.",
    boundary_notes: [
      "local fake/demo/test data only",
      "not real Douyin data",
      "OAuth is not required",
      "no token stored",
      "no refresh token stored",
      "no token refresh",
      "no token expiry handling required",
      "no token revoke",
      "no disconnect operation",
      "no external service call",
    ],
  },
  {
    provider_id: "douyin_sandbox",
    provider_name: "Douyin Sandbox Placeholder",
    source_type: "sandbox",
    implementation_status: "planned",
    token_lifecycle_policy_status: "not_implemented",
    token_storage_policy_status: "not_implemented",
    refresh_policy_status: "required_planned",
    expiry_policy_status: "required_planned",
    revoke_policy_status: "required_planned",
    disconnect_policy_status: "required_planned",
    rotation_policy_status: "required_planned",
    error_redaction_policy_status: "active",
    audit_event_policy_status: "metadata_only",
    is_available: false,
    is_real_provider: false,
    requires_user_authorization: true,
    can_refresh_token: false,
    can_revoke_token: false,
    can_disconnect: false,
    can_rotate_token: false,
    can_mark_token_expired: false,
    safe_status_message:
      "Douyin sandbox token lifecycle boundary is placeholder metadata only; token storage, refresh, expiry handling, revoke, and disconnect are not implemented.",
    boundary_notes: [
      "placeholder token lifecycle boundary metadata only",
      "OAuth is not implemented",
      "tokens are not stored",
      "refresh tokens are not stored",
      "token refresh is not implemented",
      "token expiry handling is planned but not active",
      "token revoke is not implemented",
      "disconnect is not implemented",
      "no token exchange",
      "no real Douyin API call",
    ],
  },
  {
    provider_id: "douyin_real",
    provider_name: "Douyin Real Placeholder",
    source_type: "real",
    implementation_status: "planned",
    token_lifecycle_policy_status: "not_implemented",
    token_storage_policy_status: "not_implemented",
    refresh_policy_status: "required_planned",
    expiry_policy_status: "required_planned",
    revoke_policy_status: "required_planned",
    disconnect_policy_status: "required_planned",
    rotation_policy_status: "required_planned",
    error_redaction_policy_status: "active",
    audit_event_policy_status: "metadata_only",
    is_available: false,
    is_real_provider: true,
    requires_user_authorization: true,
    can_refresh_token: false,
    can_revoke_token: false,
    can_disconnect: false,
    can_rotate_token: false,
    can_mark_token_expired: false,
    safe_status_message:
      "Douyin real token lifecycle boundary is a future placeholder only; token storage, refresh, expiry handling, revoke, disconnect, metrics fetching, upload, publish, and scheduling are not implemented.",
    boundary_notes: [
      "future real provider token lifecycle boundary placeholder only",
      "not real Douyin integration",
      "OAuth is not implemented",
      "no access token or refresh token storage",
      "token refresh is not implemented",
      "token expiry handling is planned but not active",
      "token revoke is not implemented",
      "disconnect is not implemented",
      "no API key storage",
      "no secret storage",
      "no token exchange",
      "no real metrics fetching",
      "no upload / publish / scheduling",
    ],
  },
];

const readinessItems = [
  {
    boundary_id: "provider_registry",
    boundary_name: "Provider Registry",
    readiness_status: "metadata_only",
    is_blocking_real_integration: false,
    safe_status_message: "Provider registry metadata is available for this known provider.",
    source_metadata: { provider_type: "platform" },
  },
  {
    boundary_id: "capability_metadata",
    boundary_name: "Capability Metadata",
    readiness_status: "metadata_only",
    is_blocking_real_integration: false,
    safe_status_message: "Capability metadata is static, read-only, and does not imply real integration.",
    source_metadata: { supports_oauth: false },
  },
  {
    boundary_id: "connection_state",
    boundary_name: "Connection State",
    readiness_status: "not_required",
    is_blocking_real_integration: false,
    safe_status_message: "Connection state metadata is read-only.",
    source_metadata: { authorization_status: "not_required" },
  },
  {
    boundary_id: "credential_reference",
    boundary_name: "Credential Reference",
    readiness_status: "not_required",
    is_blocking_real_integration: false,
    safe_status_message: "Credential reference metadata is read-only.",
    source_metadata: { storage_status: "none" },
  },
  {
    boundary_id: "security_audit",
    boundary_name: "Security Audit",
    readiness_status: "metadata_only",
    is_blocking_real_integration: false,
    safe_status_message: "Security audit metadata can be read safely.",
    source_metadata: { audit_boundary_status: "metadata_only" },
  },
  {
    boundary_id: "oauth_boundary",
    boundary_name: "OAuth Boundary",
    readiness_status: "not_required",
    is_blocking_real_integration: false,
    safe_status_message: "OAuth boundary metadata is read-only.",
    source_metadata: { state_policy_status: "not_required" },
  },
  {
    boundary_id: "token_lifecycle_boundary",
    boundary_name: "Token Lifecycle Boundary",
    readiness_status: "not_required",
    is_blocking_real_integration: false,
    safe_status_message: "Token lifecycle boundary metadata is read-only.",
    source_metadata: { token_storage_policy_status: "none" },
  },
];

const readinessSummaries: ProviderReadinessSummary[] = [
  {
    provider_id: "fake_local",
    provider_name: "Local Fake Provider",
    source_type: "fake_local",
    implementation_status: "available_local_fake",
    is_available: true,
    is_real_provider: false,
    requires_user_authorization: false,
    overall_readiness_status: "local_fake_ready",
    v0_9_poc_readiness_status: "not_applicable_local_fake",
    can_use_local_fake_workflow: true,
    is_safe_to_attempt_real_oauth: false,
    is_safe_to_store_tokens: false,
    is_safe_to_fetch_real_metrics: false,
    is_safe_to_publish: false,
    is_ready_for_v0_9_sandbox_poc: false,
    is_ready_for_v0_9_real_poc: false,
    readiness_items: readinessItems,
    blocking_reasons: ["local fake provider is not a real Douyin provider", "no real OAuth", "no real metrics"],
    next_safe_steps: ["keep fake/local workflow available as fallback"],
    safe_summary: "Local fake provider is ready only for local fake/demo/test workflow.",
    boundary_notes: ["local fake/demo/test data only", "not real Douyin data", "no token stored"],
  },
  {
    provider_id: "douyin_sandbox",
    provider_name: "Douyin Sandbox Placeholder",
    source_type: "sandbox",
    implementation_status: "planned",
    is_available: false,
    is_real_provider: false,
    requires_user_authorization: true,
    overall_readiness_status: "sandbox_placeholder_not_ready",
    v0_9_poc_readiness_status: "blocked_placeholder_only",
    can_use_local_fake_workflow: false,
    is_safe_to_attempt_real_oauth: false,
    is_safe_to_store_tokens: false,
    is_safe_to_fetch_real_metrics: false,
    is_safe_to_publish: false,
    is_ready_for_v0_9_sandbox_poc: false,
    is_ready_for_v0_9_real_poc: false,
    readiness_items: readinessItems,
    blocking_reasons: ["OAuth is not implemented", "token lifecycle is not implemented"],
    next_safe_steps: ["define v0.9 sandbox/mock callback smoke test separately"],
    safe_summary: "Douyin sandbox readiness is placeholder metadata only.",
    boundary_notes: ["placeholder metadata only", "no real Douyin API call"],
  },
  {
    provider_id: "douyin_real",
    provider_name: "Douyin Real Placeholder",
    source_type: "real",
    implementation_status: "planned",
    is_available: false,
    is_real_provider: true,
    requires_user_authorization: true,
    overall_readiness_status: "real_placeholder_not_ready",
    v0_9_poc_readiness_status: "blocked_missing_real_oauth",
    can_use_local_fake_workflow: false,
    is_safe_to_attempt_real_oauth: false,
    is_safe_to_store_tokens: false,
    is_safe_to_fetch_real_metrics: false,
    is_safe_to_publish: false,
    is_ready_for_v0_9_sandbox_poc: false,
    is_ready_for_v0_9_real_poc: false,
    readiness_items: readinessItems,
    blocking_reasons: ["real OAuth is not implemented", "token storage is not implemented"],
    next_safe_steps: ["complete v0.8 readiness review before v0.9 POC"],
    safe_summary: "Douyin real readiness is a future real provider placeholder only.",
    boundary_notes: ["future real provider placeholder only", "not real Douyin integration"],
  },
];

function jsonResponse(body: unknown, status = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      headers: { "Content-Type": "application/json" },
      status,
    }),
  );
}

function installListPageFetchMock(projects: Project[] = [project]) {
  const calls: string[] = [];
  const fetchMock = vi.fn((input: RequestInfo | URL) => {
    const url = new URL(input.toString());
    calls.push(`GET ${url.pathname}${url.search}`);
    if (url.pathname === "/api/providers") {
      return jsonResponse({ providers });
    }
    if (url.pathname === "/api/provider-connections") {
      return jsonResponse({ connections });
    }
    if (url.pathname === "/api/provider-credential-references") {
      return jsonResponse({ credential_references: credentialReferences });
    }
    if (url.pathname === "/api/provider-security-audit-events") {
      return jsonResponse({ audit_events: auditEvents });
    }
    if (url.pathname === "/api/provider-oauth-boundaries") {
      return jsonResponse({ oauth_boundaries: oauthBoundaries });
    }
    if (url.pathname === "/api/provider-token-lifecycle-boundaries") {
      return jsonResponse({ token_lifecycle_boundaries: tokenLifecycleBoundaries });
    }
    if (url.pathname === "/api/provider-readiness-summaries") {
      return jsonResponse({ readiness_summaries: readinessSummaries });
    }
    if (url.pathname === "/api/providers/douyin") {
      return jsonResponse({ providers: douyinSandboxDescriptors });
    }
    if (url.pathname === "/api/projects") {
      return jsonResponse(projects);
    }
    return jsonResponse({ detail: "not found" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return { calls };
}

describe("ProjectListPage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("keeps the project list workflow visible while mounting Provider metadata panels", async () => {
    const server = installListPageFetchMock();

    render(<ProjectListPage onCreate={vi.fn()} onOpen={vi.fn()} />);

    expect(screen.getByRole("button", { name: "新建项目" })).toBeTruthy();
    expect(screen.getByLabelText("显示归档项目")).toBeTruthy();
    expect(await screen.findByText("Existing project")).toBeTruthy();
    expect(await screen.findByLabelText("Provider fake_local")).toBeTruthy();
    expect(screen.getByLabelText("Provider douyin_sandbox")).toBeTruthy();
    expect(screen.getByLabelText("Provider douyin_real")).toBeTruthy();
    expect(await screen.findByLabelText("Provider connection fake_local")).toBeTruthy();
    expect(screen.getByLabelText("Provider connection douyin_sandbox")).toBeTruthy();
    expect(screen.getByLabelText("Provider connection douyin_real")).toBeTruthy();
    expect(await screen.findByLabelText("Provider credential reference fake_local")).toBeTruthy();
    expect(screen.getByLabelText("Provider credential reference douyin_sandbox")).toBeTruthy();
    expect(screen.getByLabelText("Provider credential reference douyin_real")).toBeTruthy();
    expect(await screen.findByLabelText("Provider security audit event fake_local")).toBeTruthy();
    expect(screen.getByLabelText("Provider security audit event douyin_sandbox")).toBeTruthy();
    expect(screen.getByLabelText("Provider security audit event douyin_real")).toBeTruthy();
    expect(await screen.findByLabelText("Provider OAuth boundary fake_local")).toBeTruthy();
    expect(screen.getByLabelText("Provider OAuth boundary douyin_sandbox")).toBeTruthy();
    expect(screen.getByLabelText("Provider OAuth boundary douyin_real")).toBeTruthy();
    expect(await screen.findByLabelText("Provider token lifecycle boundary fake_local")).toBeTruthy();
    expect(screen.getByLabelText("Provider token lifecycle boundary douyin_sandbox")).toBeTruthy();
    expect(screen.getByLabelText("Provider token lifecycle boundary douyin_real")).toBeTruthy();
    expect(await screen.findByLabelText("Provider readiness summary fake_local")).toBeTruthy();
    expect(screen.getByLabelText("Provider readiness summary douyin_sandbox")).toBeTruthy();
    expect(screen.getByLabelText("Provider readiness summary douyin_real")).toBeTruthy();
    expect(await screen.findByLabelText("Douyin sandbox provider douyin_sandbox")).toBeTruthy();
    expect(screen.getByLabelText("Douyin sandbox provider douyin_real")).toBeTruthy();
    await waitFor(() => expect(server.calls).toContain("GET /api/providers"));
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-connections"));
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-credential-references"));
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-security-audit-events?limit=20"));
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-oauth-boundaries"));
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-token-lifecycle-boundaries"));
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-readiness-summaries"));
    await waitFor(() => expect(server.calls).toContain("GET /api/providers/douyin"));
    await waitFor(() => expect(server.calls).toContain("GET /api/projects"));
  });

  it("keeps the original empty project state when there are no projects", async () => {
    installListPageFetchMock([]);

    render(<ProjectListPage onCreate={vi.fn()} onOpen={vi.fn()} />);

    expect(await screen.findByText("还没有项目")).toBeTruthy();
    expect(screen.getByText("创建第一个内容项目后，可以为它添加文本、链接、图片或截图素材。")).toBeTruthy();
    expect(screen.getByRole("button", { name: "新建项目" })).toBeTruthy();
    expect(screen.getByLabelText("显示归档项目")).toBeTruthy();
  });
});
