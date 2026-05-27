import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProviderTokenLifecyclePanel } from "./ProviderTokenLifecyclePanel";
import type { ProviderTokenLifecycleBoundary } from "../api/client";

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
    last_status_change_reason: "initial_metadata",
    created_at: "2026-05-27T08:00:00Z",
    updated_at: "2026-05-27T08:00:00Z",
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
      "cannot be treated as douyin_real",
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

const tokenLifecycleBoundariesWithUnsafeExtraFields = tokenLifecycleBoundaries.map((boundary) => ({
  ...boundary,
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
}));

function jsonResponse(body: unknown, status = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      headers: { "Content-Type": "application/json" },
      status,
    }),
  );
}

function installTokenLifecycleFetchMock(
  body: unknown = { token_lifecycle_boundaries: tokenLifecycleBoundariesWithUnsafeExtraFields },
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

describe("ProviderTokenLifecyclePanel", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("shows a loading state while requesting provider token lifecycle boundary metadata", () => {
    const fetchMock = vi.fn(() => new Promise<Response>(() => undefined));
    vi.stubGlobal("fetch", fetchMock);

    render(<ProviderTokenLifecyclePanel />);

    expect(screen.getByText("Loading Provider Token Lifecycle Boundary metadata...")).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("calls GET /api/provider-token-lifecycle-boundaries and displays read-only metadata", async () => {
    const server = installTokenLifecycleFetchMock();

    render(<ProviderTokenLifecyclePanel />);

    expect(await screen.findByText("Provider Token Lifecycle Boundaries")).toBeTruthy();
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-token-lifecycle-boundaries"));

    const fakeLocalCard = screen.getByLabelText("Provider token lifecycle boundary fake_local");
    expect(within(fakeLocalCard).getByText("Local Fake Provider")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("fake_local").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getByText("available_local_fake")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("not_required").length).toBeGreaterThanOrEqual(6);
    expect(within(fakeLocalCard).getByText("none")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("available")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("not required")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("no").length).toBeGreaterThanOrEqual(6);
    expect(within(fakeLocalCard).getByText(tokenLifecycleBoundaries[0].safe_status_message)).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("local fake/demo/test data only").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("not real Douyin data").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("OAuth is not required").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no token stored").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no refresh token stored").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no token refresh").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no token expiry handling required").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no token revoke").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no disconnect operation").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no external service call").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getByText("initial_metadata")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("2026-05-27T08:00:00Z").length).toBeGreaterThan(0);

    const sandboxCard = screen.getByLabelText("Provider token lifecycle boundary douyin_sandbox");
    expect(within(sandboxCard).getByText("Douyin Sandbox Placeholder")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("sandbox").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("not_implemented").length).toBeGreaterThanOrEqual(2);
    expect(within(sandboxCard).getAllByText("required_planned").length).toBeGreaterThanOrEqual(5);
    expect(within(sandboxCard).getByText("not available")).toBeTruthy();
    expect(within(sandboxCard).getByText("required in future")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("no").length).toBeGreaterThanOrEqual(5);
    expect(within(sandboxCard).getByText(tokenLifecycleBoundaries[1].safe_status_message)).toBeTruthy();
    expect(within(sandboxCard).getAllByText("placeholder token lifecycle boundary metadata only").length).toBeGreaterThan(
      0,
    );
    expect(within(sandboxCard).getAllByText("OAuth is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("tokens are not stored").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("refresh tokens are not stored").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("token refresh is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("token expiry handling is planned but not active").length).toBeGreaterThan(
      0,
    );
    expect(within(sandboxCard).getAllByText("token revoke is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("disconnect is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("no token exchange").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("no real Douyin API call").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("cannot be treated as douyin_real").length).toBeGreaterThan(0);

    const realCard = screen.getByLabelText("Provider token lifecycle boundary douyin_real");
    expect(within(realCard).getByText("Douyin Real Placeholder")).toBeTruthy();
    expect(within(realCard).getAllByText("real").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("not_implemented").length).toBeGreaterThanOrEqual(2);
    expect(within(realCard).getAllByText("required_planned").length).toBeGreaterThanOrEqual(5);
    expect(within(realCard).getByText("not available")).toBeTruthy();
    expect(within(realCard).getByText("yes, future placeholder")).toBeTruthy();
    expect(within(realCard).getByText("required in future")).toBeTruthy();
    expect(within(realCard).getAllByText("no").length).toBeGreaterThanOrEqual(5);
    expect(within(realCard).getByText(tokenLifecycleBoundaries[2].safe_status_message)).toBeTruthy();
    expect(
      within(realCard).getAllByText("future real provider token lifecycle boundary placeholder only").length,
    ).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("not real Douyin integration").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("OAuth is not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no access token or refresh token storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("token refresh is not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("token expiry handling is planned but not active").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("token revoke is not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("disconnect is not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no API key storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no secret storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no token exchange").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no real metrics fetching").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no upload / publish / scheduling").length).toBeGreaterThan(0);

    expect(screen.getByText(/required_planned means future planned requirement only/)).toBeTruthy();

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

  it("does not render token lifecycle action buttons, inputs, token viewers, or raw viewers", async () => {
    installTokenLifecycleFetchMock();

    const { container } = render(<ProviderTokenLifecyclePanel />);

    await screen.findByLabelText("Provider token lifecycle boundary fake_local");
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
      "Enter Authorization Code",
      "Enter OAuth State",
      "Enter API Key",
      "Enter Secret",
      "Raw Request",
      "Raw Response",
      "Raw Payload",
      "Token Response",
      "Refresh Response",
      "Revoke Response",
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

  it("shows a safe error message when provider token lifecycle metadata loading fails", async () => {
    installTokenLifecycleFetchMock(
      {
        detail:
          "sensitive authorization_code token refresh token credential api_key client_secret state_value should not be displayed",
      },
      500,
    );

    render(<ProviderTokenLifecyclePanel />);

    expect(
      await screen.findByText("Provider Token Lifecycle Boundary metadata failed to load. Please try again."),
    ).toBeTruthy();
    expect(screen.queryByText(/authorization_code token refresh token credential/)).toBeNull();
  });

  it("shows an empty state when the token lifecycle response has no metadata", async () => {
    installTokenLifecycleFetchMock({ token_lifecycle_boundaries: [] });

    render(<ProviderTokenLifecyclePanel />);

    expect(await screen.findByText("No Provider token lifecycle boundaries")).toBeTruthy();
    expect(screen.getByText("The backend did not return provider token lifecycle boundary metadata.")).toBeTruthy();
  });
});
