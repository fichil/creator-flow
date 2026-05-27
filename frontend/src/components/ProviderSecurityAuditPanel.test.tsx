import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProviderSecurityAuditPanel } from "./ProviderSecurityAuditPanel";
import type { ProviderSecurityAuditEvent } from "../api/client";

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
    safe_metadata: { status: "recorded", redacted_field: "[REDACTED]" },
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
      "cannot be treated as douyin_real",
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
    safe_metadata: {
      redacted_field: "[REDACTED]",
      nested: { redacted_field: "[REDACTED]", safe: "visible" },
    },
    boundary_notes: [
      "future real provider placeholder audit metadata only",
      "not real Douyin integration",
      "OAuth is not implemented",
      "no access token or refresh token storage",
      "no API key storage",
      "no secret storage",
      "no real metrics fetching",
      "no upload / publish / scheduling",
    ],
    created_at: "2026-05-27T08:02:00Z",
  },
];

const auditEventsWithUnsafeExtraFields = auditEvents.map((event) => ({
  ...event,
  unsafe_debug_value:
    "fake-access-token fake-refresh-token fake-api-key fake-client-secret fake-auth-code fake-bearer-token",
}));

function jsonResponse(body: unknown, status = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      headers: { "Content-Type": "application/json" },
      status,
    }),
  );
}

function installAuditFetchMock(body: unknown = { audit_events: auditEventsWithUnsafeExtraFields }, status = 200) {
  const calls: string[] = [];
  const fetchMock = vi.fn((input: RequestInfo | URL) => {
    const url = new URL(input.toString());
    calls.push(`GET ${url.pathname}${url.search}`);
    return jsonResponse(body, status);
  });
  vi.stubGlobal("fetch", fetchMock);
  return { calls, fetchMock };
}

describe("ProviderSecurityAuditPanel", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("shows a loading state while requesting provider security audit metadata", () => {
    const fetchMock = vi.fn(() => new Promise<Response>(() => undefined));
    vi.stubGlobal("fetch", fetchMock);

    render(<ProviderSecurityAuditPanel />);

    expect(screen.getByText("Loading Provider Security Audit metadata...")).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("calls GET /api/provider-security-audit-events with a bounded limit and displays redacted audit metadata", async () => {
    const server = installAuditFetchMock();

    render(<ProviderSecurityAuditPanel />);

    expect(await screen.findByText("Provider Security Audit Events")).toBeTruthy();
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-security-audit-events?limit=20"));

    const fakeLocalCard = screen.getByLabelText("Provider security audit event fake_local");
    expect(within(fakeLocalCard).getByText("Local Fake Provider")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("audit-fake-local")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("fake_local").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getByText("available_local_fake")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("boundary_initialized")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("recorded")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("info")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("system")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("active")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("fake_local provider boundary initialized")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("2026-05-27T08:00:00Z")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("local fake/demo/test audit metadata only").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("not real Douyin data").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no OAuth required").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no token stored").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no secret stored").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no external service call").length).toBeGreaterThan(0);
    expect(fakeLocalCard.textContent).toContain('"status": "recorded"');
    expect(fakeLocalCard.textContent).toContain('"redacted_field": "[REDACTED]"');

    const sandboxCard = screen.getByLabelText("Provider security audit event douyin_sandbox");
    expect(within(sandboxCard).getByText("Douyin Sandbox Placeholder")).toBeTruthy();
    expect(within(sandboxCard).getByText("sandbox")).toBeTruthy();
    expect(within(sandboxCard).getByText("credential_reference_checked")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("planned").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getByText("warning")).toBeTruthy();
    expect(within(sandboxCard).getByText("internal")).toBeTruthy();
    expect(within(sandboxCard).getByText("sandbox placeholder audit metadata checked")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("placeholder audit metadata only").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("OAuth is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("tokens are not stored").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("secrets are not stored").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("no real Douyin API call").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("cannot be treated as douyin_real").length).toBeGreaterThan(0);

    const realCard = screen.getByLabelText("Provider security audit event douyin_real");
    expect(within(realCard).getByText("Douyin Real Placeholder")).toBeTruthy();
    expect(within(realCard).getByText("real")).toBeTruthy();
    expect(within(realCard).getByText("authorization_status_checked")).toBeTruthy();
    expect(within(realCard).getByText("not_implemented")).toBeTruthy();
    expect(within(realCard).getByText("security")).toBeTruthy();
    expect(within(realCard).getByText("user_placeholder")).toBeTruthy();
    expect(within(realCard).getByText("redacted")).toBeTruthy();
    expect(within(realCard).getByText("redacted_value=[REDACTED] Bearer [REDACTED]")).toBeTruthy();
    expect(within(realCard).getAllByText("future real provider placeholder audit metadata only").length).toBeGreaterThan(
      0,
    );
    expect(within(realCard).getAllByText("not real Douyin integration").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("OAuth is not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no access token or refresh token storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no API key storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no secret storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no real metrics fetching").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no upload / publish / scheduling").length).toBeGreaterThan(0);
    expect(realCard.textContent).toContain('"safe": "visible"');
    expect(realCard.textContent).toContain('"redacted_field": "[REDACTED]"');

    for (const leakedValue of [
      "fake-access-token",
      "fake-refresh-token",
      "fake-api-key",
      "fake-client-secret",
      "fake-auth-code",
      "fake-bearer-token",
    ]) {
      expect(screen.queryByText(leakedValue)).toBeNull();
    }
  });

  it("does not render audit writer, raw viewers, inputs, or platform operation buttons", async () => {
    installAuditFetchMock();

    const { container } = render(<ProviderSecurityAuditPanel />);

    await screen.findByLabelText("Provider security audit event fake_local");
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
      "Save Credential",
      "Add Credential",
      "Edit Credential",
      "Delete Credential",
      "View Token",
      "View Secret",
      "Write Audit Event",
      "Create Audit Event",
      "Export Audit Log",
      "Send to SIEM",
      "Raw Request",
      "Raw Response",
      "Raw Payload",
    ]) {
      expect(screen.queryByRole("button", { name: label })).toBeNull();
    }
    expect(screen.queryAllByRole("textbox")).toHaveLength(0);
    expect(screen.queryByRole("textbox", { name: /secret|token|api key|credential|password|raw request/i })).toBeNull();
    expect(container.querySelectorAll("input, textarea, select")).toHaveLength(0);
  });

  it("shows a safe error message when provider security audit metadata loading fails", async () => {
    installAuditFetchMock(
      {
        detail:
          "sensitive authorization_code token credential api_key client_secret raw_request should not be displayed",
      },
      500,
    );

    render(<ProviderSecurityAuditPanel />);

    expect(await screen.findByText("Provider Security Audit metadata failed to load. Please try again.")).toBeTruthy();
    expect(screen.queryByText(/authorization_code token credential/)).toBeNull();
  });

  it("shows an empty state when the security audit response has no events", async () => {
    installAuditFetchMock({ audit_events: [] });

    render(<ProviderSecurityAuditPanel />);

    expect(await screen.findByText("No Provider security audit events")).toBeTruthy();
    expect(screen.getByText("The backend did not return provider security audit event metadata.")).toBeTruthy();
  });
});
