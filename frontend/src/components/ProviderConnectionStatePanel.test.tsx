import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProviderConnectionStatePanel } from "./ProviderConnectionStatePanel";
import type { ProviderConnectionState } from "../api/client";

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
    boundary_notes: [
      "local fake/demo/test data only",
      "not real Douyin data",
      "no OAuth required",
      "no tokens stored",
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
    boundary_notes: [
      "placeholder only",
      "OAuth is not implemented",
      "tokens are not stored",
      "no real Douyin API call",
      "cannot be treated as douyin_real",
    ],
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
    boundary_notes: [
      "future real provider placeholder only",
      "not real Douyin integration",
      "OAuth is not implemented",
      "no access token or refresh token storage",
      "no real metrics fetching",
      "no upload / publish / scheduling",
    ],
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

function installConnectionFetchMock(body: unknown = { connections }, status = 200) {
  const calls: string[] = [];
  const fetchMock = vi.fn((input: RequestInfo | URL) => {
    const url = new URL(input.toString());
    calls.push(`GET ${url.pathname}`);
    return jsonResponse(body, status);
  });
  vi.stubGlobal("fetch", fetchMock);
  return { calls, fetchMock };
}

describe("ProviderConnectionStatePanel", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("shows a loading state while requesting provider connection state metadata", () => {
    const fetchMock = vi.fn(() => new Promise<Response>(() => undefined));
    vi.stubGlobal("fetch", fetchMock);

    render(<ProviderConnectionStatePanel />);

    expect(screen.getByText("Loading Provider Connection State metadata...")).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("calls GET /api/provider-connections and displays source-separated connection state metadata", async () => {
    const server = installConnectionFetchMock();

    render(<ProviderConnectionStatePanel />);

    expect(await screen.findByText("Provider Connection State")).toBeTruthy();
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-connections"));

    const fakeLocalCard = screen.getByLabelText("Provider connection fake_local");
    expect(within(fakeLocalCard).getByText("Local Fake Provider")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("fake_local").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("not_required").length).toBeGreaterThanOrEqual(2);
    expect(within(fakeLocalCard).getByText("none")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("available")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("not required")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("no").length).toBeGreaterThanOrEqual(5);
    expect(within(fakeLocalCard).getAllByText(/local fake\/demo\/test data/).length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("not real Douyin data").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no OAuth required").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no tokens stored").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no external service call").length).toBeGreaterThan(0);
    expect(
      within(fakeLocalCard).getByText("Local fake provider does not require authorization and stores no tokens."),
    ).toBeTruthy();
    expect(within(fakeLocalCard).getByText("initial_metadata")).toBeTruthy();

    const sandboxCard = screen.getByLabelText("Provider connection douyin_sandbox");
    expect(within(sandboxCard).getByText("Douyin Sandbox Placeholder")).toBeTruthy();
    expect(within(sandboxCard).getByText("sandbox")).toBeTruthy();
    expect(within(sandboxCard).getByText("not_connected")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("not_implemented").length).toBeGreaterThanOrEqual(2);
    expect(within(sandboxCard).getByText("not available")).toBeTruthy();
    expect(within(sandboxCard).getByText("required in future")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("no").length).toBeGreaterThanOrEqual(5);
    expect(within(sandboxCard).getAllByText("placeholder only").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("OAuth is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("tokens are not stored").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("no real Douyin API call").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("cannot be treated as douyin_real").length).toBeGreaterThan(0);
    expect(
      within(sandboxCard).getByText(
        "Douyin sandbox is placeholder metadata only; OAuth is not implemented and tokens are not stored.",
      ),
    ).toBeTruthy();

    const realCard = screen.getByLabelText("Provider connection douyin_real");
    expect(within(realCard).getByText("Douyin Real Placeholder")).toBeTruthy();
    expect(within(realCard).getByText("real")).toBeTruthy();
    expect(within(realCard).getByText("not_connected")).toBeTruthy();
    expect(within(realCard).getAllByText("not_implemented").length).toBeGreaterThanOrEqual(2);
    expect(within(realCard).getByText("not available")).toBeTruthy();
    expect(within(realCard).getByText("yes, future placeholder")).toBeTruthy();
    expect(within(realCard).getByText("required in future")).toBeTruthy();
    expect(within(realCard).getAllByText("no").length).toBeGreaterThanOrEqual(4);
    expect(within(realCard).getAllByText("future real provider placeholder only").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("not real Douyin integration").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("OAuth is not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no access token or refresh token storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no real metrics fetching").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no upload / publish / scheduling").length).toBeGreaterThan(0);
  });

  it("does not render platform connection or publishing operation buttons", async () => {
    installConnectionFetchMock();

    render(<ProviderConnectionStatePanel />);

    await screen.findByLabelText("Provider connection fake_local");
    for (const label of [
      "Connect",
      "Authorize",
      "OAuth Login",
      "Refresh Token",
      "Revoke",
      "Disconnect",
      "Upload",
      "Publish",
      "Schedule",
      "Sync",
    ]) {
      expect(screen.queryByRole("button", { name: label })).toBeNull();
    }
  });

  it("shows a safe error message when provider connection metadata loading fails", async () => {
    installConnectionFetchMock(
      {
        detail:
          "sensitive authorization_code token credential api_key client_secret should not be displayed by the UI",
      },
      500,
    );

    render(<ProviderConnectionStatePanel />);

    expect(await screen.findByText("Provider Connection State metadata failed to load. Please try again.")).toBeTruthy();
    expect(screen.queryByText(/authorization_code token credential/)).toBeNull();
  });

  it("shows an empty state when the connection state response has no connections", async () => {
    installConnectionFetchMock({ connections: [] });

    render(<ProviderConnectionStatePanel />);

    expect(await screen.findByText("No Provider connection state metadata")).toBeTruthy();
    expect(screen.getByText("The backend did not return provider connection state metadata.")).toBeTruthy();
  });
});
