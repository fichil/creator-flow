import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { DouyinSandboxPanel } from "./DouyinSandboxPanel";
import type { DouyinProviderDescriptor, DouyinSandboxOperationResponse } from "../api/douyinSandbox";

const descriptors: DouyinProviderDescriptor[] = [
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

const mockConnectionResult: DouyinSandboxOperationResponse = {
  provider_id: "douyin_sandbox",
  source_type: "sandbox",
  mode: "sandbox",
  operation: "sandbox_mock_connection",
  workflow_name: "mock_account_connection",
  status: "simulated_success",
  outcome: "simulated",
  simulated: true,
  dry_run: true,
  safe_message: "Sandbox mock account connection completed with deterministic simulated data.",
  boundary_notes: ["sandbox only", "simulated", "dry-run"],
  operation_references: ["sandbox_oauth_start_001", "sandbox_oauth_callback_001"],
  payload: {
    provider: "douyin_sandbox",
    source: "sandbox",
    outcome: "simulated",
    dry_run: true,
    connection_id: "sandbox_connection_001",
    account_id: "sandbox_account_001",
    account_label: "Sandbox Mock Account",
    connection_status: "simulated_connected",
  },
  external_call_performed: false,
  storage_write_performed: false,
  database_write_performed: false,
};

const metricsPreviewResult: DouyinSandboxOperationResponse = {
  provider_id: "douyin_sandbox",
  source_type: "sandbox",
  mode: "sandbox",
  operation: "sandbox_metrics_preview",
  workflow_name: "sandbox_metrics_poc",
  status: "simulated_success",
  outcome: "simulated",
  simulated: true,
  dry_run: true,
  safe_message: "Sandbox metrics preview completed with deterministic fake metrics.",
  boundary_notes: ["sandbox only", "simulated", "not real metrics"],
  operation_references: ["sandbox_metrics_001"],
  payload: {
    provider: "douyin_sandbox",
    source: "sandbox",
    outcome: "simulated",
    dry_run: true,
    metrics_id: "sandbox_metrics_snapshot_001",
    publication_id: "sandbox_publish_001",
    collected_at: "2026-01-01T00:00:00Z",
    views: 1200,
    likes: 128,
    comments: 16,
    shares: 9,
    favorites: 5,
  },
  external_call_performed: false,
  storage_write_performed: false,
  database_write_performed: false,
};

const publishDryRunResult: DouyinSandboxOperationResponse = {
  provider_id: "douyin_sandbox",
  source_type: "sandbox",
  mode: "sandbox",
  operation: "sandbox_publish_dry_run",
  workflow_name: "dry_run_publish",
  status: "simulated_success",
  outcome: "simulated",
  simulated: true,
  dry_run: true,
  safe_message: "Sandbox publish dry-run completed without upload, publish, or schedule.",
  boundary_notes: ["sandbox only", "simulated", "dry-run"],
  operation_references: ["sandbox_prepare_001", "sandbox_video_001", "sandbox_publish_001"],
  payload: {
    provider: "douyin_sandbox",
    source: "sandbox",
    outcome: "simulated",
    dry_run: true,
    video_id: "sandbox_video_001",
    publish_id: "sandbox_publish_001",
    publish_status: "simulated_success",
    scheduled: false,
    completed_at: "2026-01-01T00:00:00Z",
  },
  external_call_performed: false,
  storage_write_performed: false,
  database_write_performed: false,
};

function jsonResponse(body: unknown, status = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      headers: { "Content-Type": "application/json" },
      status,
    }),
  );
}

function installSandboxFetchMock(options: { failActions?: boolean; failProviders?: boolean } = {}) {
  const calls: string[] = [];
  const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(input.toString());
    calls.push(`${getMethod(input, init)} ${url.pathname}`);
    if (url.pathname === "/api/providers/douyin") {
      return options.failProviders
        ? jsonResponse({ detail: "unsafe server detail with client_secret" }, 500)
        : jsonResponse({ providers: descriptors });
    }
    if (options.failActions) {
      return jsonResponse({ detail: "unsafe server detail with authorization_code" }, 500);
    }
    if (url.pathname === "/api/providers/douyin/sandbox/mock-connection") {
      return jsonResponse(mockConnectionResult);
    }
    if (url.pathname === "/api/providers/douyin/sandbox/metrics-preview") {
      return jsonResponse(metricsPreviewResult);
    }
    if (url.pathname === "/api/providers/douyin/sandbox/publish-dry-run") {
      return jsonResponse(publishDryRunResult);
    }
    return jsonResponse({ detail: "not found" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return { calls, fetchMock };
}

describe("DouyinSandboxPanel", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("renders the sandbox-only boundary banner", async () => {
    installSandboxFetchMock();

    render(<DouyinSandboxPanel />);

    expect(screen.getByText("Douyin Sandbox POC Panel")).toBeTruthy();
    expect(screen.getByText(/v0\.9 sandbox POC only/)).toBeTruthy();
    expect(screen.getByText(/deterministic simulated \/ dry-run/)).toBeTruthy();
    expect(screen.getByText(/does not connect to real Douyin/)).toBeTruthy();
    expect(screen.getByText(/perform OAuth/)).toBeTruthy();
    expect(screen.getByText(/store tokens/)).toBeTruthy();
    expect(screen.getByText(/upload videos/)).toBeTruthy();
    expect(screen.getByText(/publish content/)).toBeTruthy();
    expect(screen.getByText(/schedule content/)).toBeTruthy();
    expect(await screen.findByLabelText("Douyin sandbox provider douyin_sandbox")).toBeTruthy();
  });

  it("loads provider descriptors and preserves sandbox and real provider boundaries", async () => {
    const server = installSandboxFetchMock();

    render(<DouyinSandboxPanel />);

    await waitFor(() => expect(server.calls).toContain("GET /api/providers/douyin"));
    const sandboxCard = await screen.findByLabelText("Douyin sandbox provider douyin_sandbox");
    expect(within(sandboxCard).getByText("Douyin Sandbox")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("sandbox").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getByText("available_for_sandbox")).toBeTruthy();
    expect(within(sandboxCard).getByText("supported sandbox simulation")).toBeTruthy();
    expect(within(sandboxCard).getByText(/sandbox \/ simulated \/ dry-run/)).toBeTruthy();

    const realCard = screen.getByLabelText("Douyin sandbox provider douyin_real");
    expect(within(realCard).getByText("Douyin Real")).toBeTruthy();
    expect(within(realCard).getAllByText("real").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("blocked").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getByText(/douyin_real is visible for source separation/)).toBeTruthy();
  });

  it("runs sandbox mock connection and displays deterministic simulated result", async () => {
    const server = installSandboxFetchMock();

    render(<DouyinSandboxPanel />);

    await screen.findByLabelText("Douyin sandbox provider douyin_sandbox");
    fireEvent.click(screen.getByRole("button", { name: "Run sandbox mock connection" }));

    await waitFor(() => expect(server.calls).toContain("POST /api/providers/douyin/sandbox/mock-connection"));
    const result = await screen.findByLabelText("Sandbox result sandbox_mock_connection");
    expect(within(result).getByText("douyin_sandbox")).toBeTruthy();
    expect(within(result).getByText("sandbox_mock_connection")).toBeTruthy();
    expect(within(result).getByText("simulated_success")).toBeTruthy();
    expect(within(result).getByText(/sandbox_connection_001/)).toBeTruthy();
    expect(within(result).getByText(/sandbox_account_001/)).toBeTruthy();
    expect(within(result).queryByText(/OAuth URL/i)).toBeNull();
    assertNoForbiddenUiText(result.textContent ?? "");
  });

  it("runs sandbox metrics preview and displays deterministic fake metrics", async () => {
    const server = installSandboxFetchMock();

    render(<DouyinSandboxPanel />);

    await screen.findByLabelText("Douyin sandbox provider douyin_sandbox");
    fireEvent.click(screen.getByRole("button", { name: "Load sandbox metrics preview" }));

    await waitFor(() => expect(server.calls).toContain("POST /api/providers/douyin/sandbox/metrics-preview"));
    const result = await screen.findByLabelText("Sandbox result sandbox_metrics_preview");
    expect(within(result).getByText("sandbox_metrics_preview")).toBeTruthy();
    expect(within(result).getByText(/sandbox_metrics_snapshot_001/)).toBeTruthy();
    expect(within(result).getByText(/1200/)).toBeTruthy();
    expect(within(result).getByText(/not real metrics/)).toBeTruthy();
    assertNoForbiddenUiText(result.textContent ?? "");
  });

  it("runs publish dry-run and displays deterministic simulated result without real publish wording", async () => {
    const server = installSandboxFetchMock();

    render(<DouyinSandboxPanel />);

    await screen.findByLabelText("Douyin sandbox provider douyin_sandbox");
    fireEvent.click(screen.getByRole("button", { name: "Run publish dry-run" }));

    await waitFor(() => expect(server.calls).toContain("POST /api/providers/douyin/sandbox/publish-dry-run"));
    const result = await screen.findByLabelText("Sandbox result sandbox_publish_dry_run");
    expect(within(result).getByText("sandbox_publish_dry_run")).toBeTruthy();
    expect(within(result).getAllByText(/sandbox_video_001/).length).toBeGreaterThan(0);
    expect(within(result).getAllByText(/sandbox_publish_001/).length).toBeGreaterThan(0);
    expect(screen.getByText(/no upload, no publish, and no schedule/)).toBeTruthy();
    expect(screen.queryByText(/published to Douyin/i)).toBeNull();
    expect(screen.queryByText(/real publish success/i)).toBeNull();
    assertNoForbiddenUiText(result.textContent ?? "");
  });

  it("shows sandbox-safe errors without leaking backend detail", async () => {
    installSandboxFetchMock({ failActions: true });

    render(<DouyinSandboxPanel />);

    await screen.findByLabelText("Douyin sandbox provider douyin_sandbox");
    fireEvent.click(screen.getByRole("button", { name: "Run sandbox mock connection" }));

    expect(await screen.findByText(/Sandbox request failed/)).toBeTruthy();
    expect(screen.queryByText(/authorization_code/)).toBeNull();
    expect(screen.queryByText(/client_secret/)).toBeNull();
  });

  it("shows provider load errors without token or platform-key guidance", async () => {
    installSandboxFetchMock({ failProviders: true });

    render(<DouyinSandboxPanel />);

    expect(await screen.findByText(/provider metadata failed to load/)).toBeTruthy();
    expect(screen.queryByText(/client_secret/)).toBeNull();
    expect(screen.queryByRole("textbox")).toBeNull();
    expect(screen.queryByLabelText(/token|platform key/i)).toBeNull();
  });

  it("does not render real platform controls or sensitive inputs", async () => {
    installSandboxFetchMock();
    const { container } = render(<DouyinSandboxPanel />);

    await screen.findByText("Douyin Sandbox POC Panel");
    for (const label of [
      "Connect real Douyin",
      "OAuth Login",
      "Start OAuth",
      "Generate OAuth URL",
      "Upload Video",
      "Publish to Douyin",
      "Schedule Publish",
      "Save Token",
    ]) {
      expect(screen.queryByRole("button", { name: label })).toBeNull();
    }
    expect(container.querySelectorAll("input, textarea, select")).toHaveLength(0);
    assertNoForbiddenUiText(container.textContent ?? "");
  });
});

function getMethod(input: RequestInfo | URL, init?: RequestInit) {
  if (init?.method) {
    return init.method;
  }
  return input instanceof Request ? input.method : "GET";
}

function assertNoForbiddenUiText(text: string) {
  for (const term of [
    "access_token",
    "refresh_token",
    "client_secret",
    "authorization_code",
    "oauth_state",
    "api_key",
    "credential",
    "cookie",
    "session",
    "bearer",
    "password",
    "secret",
    "real OAuth",
    "real publish",
    "published to Douyin",
    "production ready",
    "commercial ready",
    "SaaS ready",
  ]) {
    expect(text).not.toContain(term);
  }
}
