import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProviderReadinessSummaryPanel } from "./ProviderReadinessSummaryPanel";
import type { ProviderReadinessSummary } from "../api/client";

const readinessItems = [
  {
    boundary_id: "provider_registry",
    boundary_name: "Provider Registry",
    readiness_status: "local_fake_ready",
    is_blocking_real_integration: false,
    safe_status_message: "Provider registry metadata is available for this known provider.",
    source_metadata: { provider_type: "platform", connection_status: "not_required" },
  },
  {
    boundary_id: "capability_metadata",
    boundary_name: "Capability Metadata",
    readiness_status: "local_fake_ready",
    is_blocking_real_integration: false,
    safe_status_message: "Capability metadata is static, read-only, and does not imply real integration.",
    source_metadata: { supports_oauth: false, supports_metrics_read: true, supports_token_refresh: false },
  },
  {
    boundary_id: "connection_state",
    boundary_name: "Connection State",
    readiness_status: "not_required",
    is_blocking_real_integration: false,
    safe_status_message: "Local fake provider does not require authorization and stores no tokens.",
    source_metadata: { authorization_status: "not_required", sensitive_storage_status: "none" },
  },
  {
    boundary_id: "credential_reference",
    boundary_name: "Credential Reference",
    readiness_status: "not_required",
    is_blocking_real_integration: false,
    safe_status_message: "Local fake provider does not require credentials, OAuth, tokens, or secrets.",
    source_metadata: { reference_kind: "none_required", storage_status: "none" },
  },
  {
    boundary_id: "security_audit",
    boundary_name: "Security Audit",
    readiness_status: "metadata_only",
    is_blocking_real_integration: false,
    safe_status_message: "Security audit metadata can be read safely; real audit trails are not required.",
    source_metadata: { safe_audit_event_count: 1, audit_boundary_status: "metadata_only" },
  },
  {
    boundary_id: "oauth_boundary",
    boundary_name: "OAuth Boundary",
    readiness_status: "not_required",
    is_blocking_real_integration: false,
    safe_status_message:
      "Local fake provider does not require OAuth state, callback handling, token exchange, or token storage.",
    source_metadata: { state_policy_status: "not_required", callback_policy_status: "not_required" },
  },
  {
    boundary_id: "token_lifecycle_boundary",
    boundary_name: "Token Lifecycle Boundary",
    readiness_status: "not_required",
    is_blocking_real_integration: false,
    safe_status_message:
      "Local fake provider does not require token storage, refresh, expiry handling, revoke, disconnect, or rotation.",
    source_metadata: { token_storage_policy_status: "none", refresh_policy_status: "not_required" },
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
    blocking_reasons: [
      "local fake provider is not a real Douyin provider",
      "no real OAuth",
      "no real metrics",
      "no real publish",
    ],
    next_safe_steps: [
      "keep fake/local workflow available as fallback",
      "use v0.8 boundaries for review before v0.9 POC",
    ],
    safe_summary:
      "Local fake provider is ready only for local fake/demo/test workflow; it is not real Douyin readiness and no real OAuth, real metrics, upload, publish, or scheduling is available.",
    boundary_notes: [
      "local fake/demo/test data only",
      "not real Douyin data",
      "no OAuth required",
      "no token stored",
      "no external service call",
    ],
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
    readiness_items: readinessItems.map((item) => ({
      ...item,
      readiness_status: item.boundary_id === "security_audit" ? "metadata_only" : "placeholder_metadata_only",
      is_blocking_real_integration: item.boundary_id !== "security_audit",
    })),
    blocking_reasons: [
      "OAuth is not implemented",
      "OAuth callback route is not implemented",
      "OAuth state storage is not implemented",
      "credential storage is not implemented",
      "token lifecycle is not implemented",
      "no real Douyin API call",
      "cannot be treated as douyin_real",
    ],
    next_safe_steps: [
      "review provider registry, OAuth boundary, credential reference, token lifecycle and audit metadata",
      "define v0.9 sandbox/mock callback smoke test separately",
      "do not add real token storage without a separate ADR",
    ],
    safe_summary:
      "Douyin sandbox readiness is placeholder metadata only; OAuth, credential storage, token lifecycle, real API calls, metrics fetching, upload, publish, and scheduling are not ready.",
    boundary_notes: [
      "placeholder metadata only",
      "not connected",
      "tokens are not stored",
      "secrets are not stored",
      "no token exchange",
      "no real metrics fetching",
      "no upload / publish / scheduling",
    ],
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
    readiness_items: readinessItems.map((item) => ({
      ...item,
      readiness_status: item.boundary_id === "security_audit" ? "metadata_only" : "placeholder_metadata_only",
      is_blocking_real_integration: item.boundary_id !== "security_audit",
    })),
    blocking_reasons: [
      "real OAuth is not implemented",
      "real OAuth callback route is not implemented",
      "real credential storage is not implemented",
      "token storage is not implemented",
      "token refresh / revoke / disconnect is not implemented",
      "no real metrics fetching",
      "no upload / publish / scheduling",
    ],
    next_safe_steps: [
      "complete v0.8 readiness review before v0.9 POC",
      "create separate v0.9 Douyin provider adapter skeleton ADR",
      "create separate sandbox/mock callback smoke test plan",
      "do not store real tokens until encrypted credential storage is designed and reviewed",
    ],
    safe_summary:
      "Douyin real readiness is a future real provider placeholder only; real OAuth, credential storage, token lifecycle, metrics fetching, upload, publish, and scheduling are not ready.",
    boundary_notes: [
      "future real provider placeholder only",
      "not real Douyin integration",
      "OAuth is not implemented",
      "no access token or refresh token storage",
      "no token refresh / revoke / disconnect",
      "no API key storage",
      "no secret storage",
      "no real metrics fetching",
      "no upload / publish / scheduling",
    ],
  },
];

const readinessSummariesWithUnsafeExtraFields = readinessSummaries.map((summary) => ({
  ...summary,
  access_token: "fake-access-token",
  refresh_token: "fake-refresh-token",
  token: "fake-token",
  token_value: "fake-token-value",
  api_key: "fake-api-key",
  client_secret: "fake-client-secret",
  oauth_client_secret: "fake-oauth-client-secret",
  authorization_code: "fake-auth-code",
  state_value: "fake-state-value",
  oauth_state_value: "fake-oauth-state-value",
  callback_payload: "fake-callback-payload",
  credential_material: "fake-credential-material",
  encrypted_credential: "fake-encrypted-credential",
  raw_request: "fake-raw-request",
  raw_response: "fake-raw-response",
  raw_payload: "fake-raw-payload",
  private_key: "fake-private-key",
  token_expiry_value: "fake-token-expiry-value",
  token_refresh_response: "fake-token-refresh-response",
  token_revoke_response: "fake-token-revoke-response",
  provider_token_response: "fake-provider-token-response",
  readiness_items: summary.readiness_items.map((item) => ({
    ...item,
    source_metadata: {
      ...item.source_metadata,
      access_token: "fake-access-token",
      refresh_token: "fake-refresh-token",
      raw_payload: "fake-raw-payload",
      safe_visible_status: "metadata_only",
    },
  })),
}));

function jsonResponse(body: unknown, status = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      headers: { "Content-Type": "application/json" },
      status,
    }),
  );
}

function installReadinessFetchMock(
  body: unknown = { readiness_summaries: readinessSummariesWithUnsafeExtraFields },
  status = 200,
) {
  const calls: string[] = [];
  const fetchMock = vi.fn((input: RequestInfo | URL) => {
    const url = new URL(input.toString());
    calls.push(`GET ${url.pathname}${url.search}`);
    return jsonResponse(body, status);
  });
  vi.stubGlobal("fetch", fetchMock);
  return { calls, fetchMock };
}

describe("ProviderReadinessSummaryPanel", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("shows a loading state while requesting provider readiness summary metadata", () => {
    const fetchMock = vi.fn(() => new Promise<Response>(() => undefined));
    vi.stubGlobal("fetch", fetchMock);

    render(<ProviderReadinessSummaryPanel />);

    expect(screen.getByText("Loading Provider Readiness Summary metadata...")).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("calls GET /api/provider-readiness-summaries and displays read-only readiness metadata", async () => {
    const server = installReadinessFetchMock();

    render(<ProviderReadinessSummaryPanel />);

    expect(await screen.findByText("Provider Integration Readiness Summary")).toBeTruthy();
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-readiness-summaries"));

    const fakeLocalCard = screen.getByLabelText("Provider readiness summary fake_local");
    expect(within(fakeLocalCard).getByText("Local Fake Provider")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("fake_local").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("local_fake_ready").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getByText("not_applicable_local_fake")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("available")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("not required")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("yes").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no").length).toBeGreaterThanOrEqual(6);
    expect(within(fakeLocalCard).getByText(readinessSummaries[0].safe_summary)).toBeTruthy();
    expect(within(fakeLocalCard).getByText("local fake/demo/test workflow readiness only")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("not real Douyin readiness")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("no real OAuth").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getByText("no real metrics fetching")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("no real publish").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no token stored").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no external service call").length).toBeGreaterThan(0);

    const sandboxCard = screen.getByLabelText("Provider readiness summary douyin_sandbox");
    expect(within(sandboxCard).getByText("Douyin Sandbox Placeholder")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("sandbox").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getByText("sandbox_placeholder_not_ready")).toBeTruthy();
    expect(within(sandboxCard).getByText("blocked_placeholder_only")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("not available").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getByText("required in future")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("no").length).toBeGreaterThanOrEqual(7);
    expect(within(sandboxCard).getByText(readinessSummaries[1].safe_summary)).toBeTruthy();
    expect(within(sandboxCard).getByText("sandbox placeholder readiness only")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("OAuth is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("OAuth callback route is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("OAuth state storage is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("credential storage is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("token lifecycle is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("no real Douyin API call").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("cannot be treated as douyin_real").length).toBeGreaterThan(0);

    const realCard = screen.getByLabelText("Provider readiness summary douyin_real");
    expect(within(realCard).getByText("Douyin Real Placeholder")).toBeTruthy();
    expect(within(realCard).getAllByText("real").length).toBeGreaterThan(0);
    expect(within(realCard).getByText("real_placeholder_not_ready")).toBeTruthy();
    expect(within(realCard).getByText("blocked_missing_real_oauth")).toBeTruthy();
    expect(within(realCard).getAllByText("not available").length).toBeGreaterThan(0);
    expect(within(realCard).getByText("yes, future placeholder")).toBeTruthy();
    expect(within(realCard).getByText("required in future")).toBeTruthy();
    expect(within(realCard).getAllByText("no").length).toBeGreaterThanOrEqual(7);
    expect(within(realCard).getByText(readinessSummaries[2].safe_summary)).toBeTruthy();
    expect(within(realCard).getByText("future real provider placeholder readiness only")).toBeTruthy();
    expect(within(realCard).getByText("not real Douyin integration ready")).toBeTruthy();
    expect(within(realCard).getAllByText("real OAuth is not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("real OAuth callback route is not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("real credential storage is not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("token storage is not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("token refresh / revoke / disconnect is not implemented").length).toBeGreaterThan(
      0,
    );
    expect(within(realCard).getAllByText("no real metrics fetching").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no upload / publish / scheduling").length).toBeGreaterThan(0);

    for (const boundaryId of [
      "provider_registry",
      "capability_metadata",
      "connection_state",
      "credential_reference",
      "security_audit",
      "oauth_boundary",
      "token_lifecycle_boundary",
    ]) {
      expect(screen.getAllByText(boundaryId).length).toBeGreaterThan(0);
    }
    expect(screen.getAllByText("safe_visible_status").length).toBeGreaterThan(0);
    expect(screen.getAllByText("metadata_only").length).toBeGreaterThan(0);
    expect(screen.getByText("complete v0.8 readiness review before v0.9 POC")).toBeTruthy();

    for (const leakedValue of [
      "fake-access-token",
      "fake-refresh-token",
      "fake-token",
      "fake-token-value",
      "fake-api-key",
      "fake-client-secret",
      "fake-oauth-client-secret",
      "fake-auth-code",
      "fake-state-value",
      "fake-oauth-state-value",
      "fake-callback-payload",
      "fake-credential-material",
      "fake-encrypted-credential",
      "fake-raw-request",
      "fake-raw-response",
      "fake-raw-payload",
      "fake-private-key",
      "fake-token-expiry-value",
      "fake-token-refresh-response",
      "fake-token-revoke-response",
      "fake-provider-token-response",
    ]) {
      expect(screen.queryByText(leakedValue)).toBeNull();
    }

    for (const forbiddenField of [
      "access_token",
      "refresh_token",
      "token_value",
      "api_key",
      "client_secret",
      "oauth_client_secret",
      "authorization_code",
      "state_value",
      "oauth_state_value",
      "callback_payload",
      "credential_material",
      "encrypted_credential",
      "raw_request",
      "raw_response",
      "raw_payload",
      "private_key",
      "token_expiry_value",
      "token_refresh_response",
      "token_revoke_response",
      "provider_token_response",
    ]) {
      expect(screen.queryByText(forbiddenField)).toBeNull();
    }
  });

  it("does not render readiness actions, provider action buttons, inputs, or viewers", async () => {
    installReadinessFetchMock();

    const { container } = render(<ProviderReadinessSummaryPanel />);

    await screen.findByLabelText("Provider readiness summary fake_local");
    for (const label of [
      "Connect",
      "Authorize",
      "OAuth Login",
      "Start OAuth",
      "OAuth Callback",
      "Test Callback",
      "Exchange Token",
      "Refresh Token",
      "Revoke",
      "Revoke Token",
      "Disconnect",
      "Rotate Token",
      "Mark Token Expired",
      "Upload",
      "Publish",
      "Schedule",
      "Sync",
      "Fetch Real Metrics",
      "Save Credential",
      "Add Credential",
      "Edit Credential",
      "Delete Credential",
      "View Token",
      "View Secret",
      "Approve Readiness",
      "Override Readiness",
      "Certify Production Ready",
      "Start v0.9 POC",
      "Start Real Provider POC",
    ]) {
      expect(screen.queryByRole("button", { name: label })).toBeNull();
    }
    expect(screen.queryAllByRole("textbox")).toHaveLength(0);
    expect(
      screen.queryByRole("textbox", {
        name: /secret|token|refresh token|api key|authorization code|oauth state|credential/i,
      }),
    ).toBeNull();
    expect(container.querySelectorAll("input, textarea, select")).toHaveLength(0);
  });

  it("shows a safe error message when provider readiness metadata loading fails", async () => {
    installReadinessFetchMock(
      {
        detail:
          "sensitive authorization_code token refresh token credential api_key client_secret state_value should not be displayed",
      },
      500,
    );

    render(<ProviderReadinessSummaryPanel />);

    expect(await screen.findByText("Provider Readiness Summary metadata failed to load. Please try again.")).toBeTruthy();
    expect(screen.queryByText(/authorization_code token refresh token credential/)).toBeNull();
  });

  it("shows an empty state when the readiness response has no metadata", async () => {
    installReadinessFetchMock({ readiness_summaries: [] });

    render(<ProviderReadinessSummaryPanel />);

    expect(await screen.findByText("No Provider readiness summaries")).toBeTruthy();
    expect(screen.getByText("The backend did not return provider readiness summary metadata.")).toBeTruthy();
  });
});
