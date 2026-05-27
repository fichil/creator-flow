import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProviderOAuthBoundaryPanel } from "./ProviderOAuthBoundaryPanel";
import type { ProviderOAuthBoundary } from "../api/client";

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
    last_status_change_reason: "initial_metadata",
    created_at: "2026-05-27T08:00:00Z",
    updated_at: "2026-05-27T08:00:00Z",
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
      "CSRF state validation is planned but not active",
      "authorization code is not stored",
      "tokens are not stored",
      "secrets are not stored",
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
      "CSRF state validation is planned but not active",
      "no authorization code storage",
      "no access token or refresh token storage",
      "no API key storage",
      "no secret storage",
      "no token exchange",
      "no real metrics fetching",
      "no upload / publish / scheduling",
    ],
  },
];

const oauthBoundariesWithUnsafeExtraFields = oauthBoundaries.map((boundary) => ({
  ...boundary,
  access_token: "fake-access-token",
  refresh_token: "fake-refresh-token",
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
}));

function jsonResponse(body: unknown, status = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      headers: { "Content-Type": "application/json" },
      status,
    }),
  );
}

function installOAuthBoundaryFetchMock(
  body: unknown = { oauth_boundaries: oauthBoundariesWithUnsafeExtraFields },
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

describe("ProviderOAuthBoundaryPanel", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("shows a loading state while requesting provider OAuth boundary metadata", () => {
    const fetchMock = vi.fn(() => new Promise<Response>(() => undefined));
    vi.stubGlobal("fetch", fetchMock);

    render(<ProviderOAuthBoundaryPanel />);

    expect(screen.getByText("Loading Provider OAuth Boundary metadata...")).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("calls GET /api/provider-oauth-boundaries and displays read-only OAuth boundary metadata", async () => {
    const server = installOAuthBoundaryFetchMock();

    render(<ProviderOAuthBoundaryPanel />);

    expect(await screen.findByText("Provider OAuth Boundaries")).toBeTruthy();
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-oauth-boundaries"));

    const fakeLocalCard = screen.getByLabelText("Provider OAuth boundary fake_local");
    expect(within(fakeLocalCard).getByText("Local Fake Provider")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("fake_local").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getByText("available_local_fake")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("not_required").length).toBeGreaterThanOrEqual(6);
    expect(within(fakeLocalCard).getByText("none")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("available")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("not required")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("no").length).toBeGreaterThanOrEqual(6);
    expect(within(fakeLocalCard).getByText(oauthBoundaries[0].safe_status_message)).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("local fake/demo/test data only").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("not real Douyin data").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("OAuth is not required").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no state value stored").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no authorization code stored").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no token exchange").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no token stored").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no secret stored").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no external service call").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getByText("initial_metadata")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("2026-05-27T08:00:00Z").length).toBeGreaterThan(0);

    const sandboxCard = screen.getByLabelText("Provider OAuth boundary douyin_sandbox");
    expect(within(sandboxCard).getByText("Douyin Sandbox Placeholder")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("sandbox").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("not_implemented").length).toBeGreaterThanOrEqual(3);
    expect(within(sandboxCard).getAllByText("required_planned").length).toBeGreaterThanOrEqual(4);
    expect(within(sandboxCard).getByText("not available")).toBeTruthy();
    expect(within(sandboxCard).getByText("required in future")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("no").length).toBeGreaterThanOrEqual(5);
    expect(within(sandboxCard).getByText(oauthBoundaries[1].safe_status_message)).toBeTruthy();
    expect(within(sandboxCard).getAllByText("placeholder OAuth boundary metadata only").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("OAuth is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("OAuth callback route is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("OAuth state storage is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("CSRF state validation is planned but not active").length).toBeGreaterThan(
      0,
    );
    expect(within(sandboxCard).getAllByText("authorization code is not stored").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("tokens are not stored").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("secrets are not stored").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("no token exchange").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("no real Douyin API call").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("cannot be treated as douyin_real").length).toBeGreaterThan(0);

    const realCard = screen.getByLabelText("Provider OAuth boundary douyin_real");
    expect(within(realCard).getByText("Douyin Real Placeholder")).toBeTruthy();
    expect(within(realCard).getAllByText("real").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("not_implemented").length).toBeGreaterThanOrEqual(3);
    expect(within(realCard).getAllByText("required_planned").length).toBeGreaterThanOrEqual(4);
    expect(within(realCard).getByText("not available")).toBeTruthy();
    expect(within(realCard).getByText("yes, future placeholder")).toBeTruthy();
    expect(within(realCard).getByText("required in future")).toBeTruthy();
    expect(within(realCard).getAllByText("no").length).toBeGreaterThanOrEqual(5);
    expect(within(realCard).getByText(oauthBoundaries[2].safe_status_message)).toBeTruthy();
    expect(within(realCard).getAllByText("future real provider OAuth boundary placeholder only").length).toBeGreaterThan(
      0,
    );
    expect(within(realCard).getAllByText("not real Douyin integration").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("OAuth is not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("OAuth callback route is not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("OAuth state storage is not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("CSRF state validation is planned but not active").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no authorization code storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no access token or refresh token storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no API key storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no secret storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no token exchange").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no real metrics fetching").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no upload / publish / scheduling").length).toBeGreaterThan(0);

    expect(screen.getByText(/required_planned means future planned requirement only/)).toBeTruthy();

    for (const leakedValue of [
      "fake-access-token",
      "fake-refresh-token",
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
    ]) {
      expect(screen.queryByText(forbiddenField)).toBeNull();
    }
  });

  it("does not render OAuth action buttons, inputs, token viewers, or raw payload viewers", async () => {
    installOAuthBoundaryFetchMock();

    const { container } = render(<ProviderOAuthBoundaryPanel />);

    await screen.findByLabelText("Provider OAuth boundary fake_local");
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
      "Upload",
      "Publish",
      "Schedule",
      "Sync",
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
    ]) {
      expect(screen.queryByRole("button", { name: label })).toBeNull();
    }
    expect(screen.queryAllByRole("textbox")).toHaveLength(0);
    expect(
      screen.queryByRole("textbox", { name: /secret|token|api key|authorization code|oauth state|credential/i }),
    ).toBeNull();
    expect(container.querySelectorAll("input, textarea, select")).toHaveLength(0);
  });

  it("shows a safe error message when provider OAuth boundary metadata loading fails", async () => {
    installOAuthBoundaryFetchMock(
      {
        detail:
          "sensitive authorization_code token credential api_key client_secret state_value should not be displayed",
      },
      500,
    );

    render(<ProviderOAuthBoundaryPanel />);

    expect(await screen.findByText("Provider OAuth Boundary metadata failed to load. Please try again.")).toBeTruthy();
    expect(screen.queryByText(/authorization_code token credential/)).toBeNull();
  });

  it("shows an empty state when the OAuth boundary response has no metadata", async () => {
    installOAuthBoundaryFetchMock({ oauth_boundaries: [] });

    render(<ProviderOAuthBoundaryPanel />);

    expect(await screen.findByText("No Provider OAuth boundaries")).toBeTruthy();
    expect(screen.getByText("The backend did not return provider OAuth boundary metadata.")).toBeTruthy();
  });
});
