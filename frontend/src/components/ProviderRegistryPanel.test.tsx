import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProviderRegistryPanel } from "./ProviderRegistryPanel";
import type { PlatformProvider } from "../api/client";

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

function installProviderFetchMock(body: unknown = { providers }, status = 200) {
  const calls: string[] = [];
  const fetchMock = vi.fn((input: RequestInfo | URL) => {
    const url = new URL(input.toString());
    calls.push(`GET ${url.pathname}`);
    return jsonResponse(body, status);
  });
  vi.stubGlobal("fetch", fetchMock);
  return { calls, fetchMock };
}

describe("ProviderRegistryPanel", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("shows a loading state while requesting provider metadata", () => {
    const fetchMock = vi.fn(() => new Promise<Response>(() => undefined));
    vi.stubGlobal("fetch", fetchMock);

    render(<ProviderRegistryPanel />);

    expect(screen.getByText("正在加载 Provider Registry metadata...")).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("calls GET /api/providers and displays source-separated provider metadata", async () => {
    const server = installProviderFetchMock();

    render(<ProviderRegistryPanel />);

    expect(await screen.findByText("Provider Registry")).toBeTruthy();
    await waitFor(() => expect(server.calls).toContain("GET /api/providers"));

    const fakeLocalCard = screen.getByLabelText("Provider fake_local");
    expect(within(fakeLocalCard).getByText("Local Fake Provider")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("fake_local").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getByText("not_required")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("available")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("no")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("not required")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText(/local fake\/demo\/test data/).length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("not real Douyin data").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no OAuth required").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no token stored").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("Local fake capability").length).toBe(2);
    expect(within(fakeLocalCard).getByText("OAuth")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("Real publish")).toBeTruthy();

    const sandboxCard = screen.getByLabelText("Provider douyin_sandbox");
    expect(within(sandboxCard).getByText("Douyin Sandbox Placeholder")).toBeTruthy();
    expect(within(sandboxCard).getByText("sandbox")).toBeTruthy();
    expect(within(sandboxCard).getByText("not_connected")).toBeTruthy();
    expect(within(sandboxCard).getByText("not available")).toBeTruthy();
    expect(within(sandboxCard).getByText("required in future")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("placeholder only").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText(/OAuth is not implemented|OAuth not implemented/).length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("tokens are not stored").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("no real Douyin API call").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("cannot be treated as douyin_real").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getByText("Sandbox boundary only")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("Not available").length).toBeGreaterThanOrEqual(7);

    const realCard = screen.getByLabelText("Provider douyin_real");
    expect(within(realCard).getByText("Douyin Real Placeholder")).toBeTruthy();
    expect(within(realCard).getByText("real")).toBeTruthy();
    expect(within(realCard).getByText("not_connected")).toBeTruthy();
    expect(within(realCard).getByText("yes, future placeholder")).toBeTruthy();
    expect(within(realCard).getAllByText("future real provider placeholder only").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("not real Douyin integration").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no real metrics fetching").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no upload / publish / scheduling").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("Not available").length).toBeGreaterThanOrEqual(8);
  });

  it("does not render platform operation buttons", async () => {
    installProviderFetchMock();

    render(<ProviderRegistryPanel />);

    await screen.findByLabelText("Provider fake_local");
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

  it("shows a safe error message when provider metadata loading fails", async () => {
    installProviderFetchMock(
      {
        detail:
          "sensitive authorization_code token credential api_key client_secret should not be displayed by the UI",
      },
      500,
    );

    render(<ProviderRegistryPanel />);

    expect(await screen.findByText("Provider Registry metadata 加载失败。请稍后重试。")).toBeTruthy();
    expect(screen.queryByText(/authorization_code token credential/)).toBeNull();
  });

  it("shows an empty state when the registry response has no providers", async () => {
    installProviderFetchMock({ providers: [] });

    render(<ProviderRegistryPanel />);

    expect(await screen.findByText("暂无 Provider metadata")).toBeTruthy();
    expect(screen.getByText("后端暂未返回 provider registry metadata。")).toBeTruthy();
  });
});
