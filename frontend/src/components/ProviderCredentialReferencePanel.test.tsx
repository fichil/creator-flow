import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProviderCredentialReferencePanel } from "./ProviderCredentialReferencePanel";
import type { ProviderCredentialReference } from "../api/client";

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
      "cannot be treated as douyin_real",
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
      "OAuth is not implemented",
      "no access token or refresh token storage",
      "no API key storage",
      "no secret storage",
      "no credential material storage",
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

function installCredentialReferenceFetchMock(
  body: unknown = { credential_references: credentialReferences },
  status = 200,
) {
  const calls: string[] = [];
  const fetchMock = vi.fn((input: RequestInfo | URL) => {
    const url = new URL(input.toString());
    calls.push(`GET ${url.pathname}`);
    return jsonResponse(body, status);
  });
  vi.stubGlobal("fetch", fetchMock);
  return { calls, fetchMock };
}

describe("ProviderCredentialReferencePanel", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("shows a loading state while requesting provider credential reference metadata", () => {
    const fetchMock = vi.fn(() => new Promise<Response>(() => undefined));
    vi.stubGlobal("fetch", fetchMock);

    render(<ProviderCredentialReferencePanel />);

    expect(screen.getByText("Loading Provider Credential Reference metadata...")).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("calls GET /api/provider-credential-references and displays source-separated credential metadata", async () => {
    const server = installCredentialReferenceFetchMock();

    render(<ProviderCredentialReferencePanel />);

    expect(await screen.findByText("Provider Credential References")).toBeTruthy();
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-credential-references"));

    const fakeLocalCard = screen.getByLabelText("Provider credential reference fake_local");
    expect(within(fakeLocalCard).getByText("Local Fake Provider")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText("fake_local").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getByText("none_required")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("not_required")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("none")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("active")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("available")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("no")).toBeTruthy();
    expect(within(fakeLocalCard).getByText("not required")).toBeTruthy();
    expect(within(fakeLocalCard).getAllByText(/local fake\/demo\/test data/).length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("not real Douyin data").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no OAuth required").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no token stored").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no secret stored").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no credential material stored").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getAllByText("no external service call").length).toBeGreaterThan(0);
    expect(within(fakeLocalCard).getByText("Local fake provider credential reference metadata")).toBeTruthy();
    expect(
      within(fakeLocalCard).getByText("Local fake provider does not require credentials, OAuth, tokens, or secrets."),
    ).toBeTruthy();
    expect(within(fakeLocalCard).getByText("initial_metadata")).toBeTruthy();

    const sandboxCard = screen.getByLabelText("Provider credential reference douyin_sandbox");
    expect(within(sandboxCard).getByText("Douyin Sandbox Placeholder")).toBeTruthy();
    expect(within(sandboxCard).getByText("sandbox")).toBeTruthy();
    expect(within(sandboxCard).getByText("oauth_placeholder")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("not_implemented").length).toBeGreaterThanOrEqual(2);
    expect(within(sandboxCard).getByText("active")).toBeTruthy();
    expect(within(sandboxCard).getByText("not available")).toBeTruthy();
    expect(within(sandboxCard).getByText("no")).toBeTruthy();
    expect(within(sandboxCard).getByText("required in future")).toBeTruthy();
    expect(within(sandboxCard).getAllByText("placeholder only").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("OAuth is not implemented").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("tokens are not stored").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("secrets are not stored").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("credential material is not stored").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("no real Douyin API call").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getAllByText("cannot be treated as douyin_real").length).toBeGreaterThan(0);
    expect(within(sandboxCard).getByText("Douyin sandbox credential reference placeholder")).toBeTruthy();
    expect(
      within(sandboxCard).getByText(
        "Douyin sandbox credential reference is placeholder metadata only; OAuth is not implemented and tokens are not stored.",
      ),
    ).toBeTruthy();

    const realCard = screen.getByLabelText("Provider credential reference douyin_real");
    expect(within(realCard).getByText("Douyin Real Placeholder")).toBeTruthy();
    expect(within(realCard).getByText("real")).toBeTruthy();
    expect(within(realCard).getByText("oauth_placeholder")).toBeTruthy();
    expect(within(realCard).getAllByText("not_implemented").length).toBeGreaterThanOrEqual(2);
    expect(within(realCard).getByText("active")).toBeTruthy();
    expect(within(realCard).getByText("not available")).toBeTruthy();
    expect(within(realCard).getByText("yes, future placeholder")).toBeTruthy();
    expect(within(realCard).getByText("required in future")).toBeTruthy();
    expect(within(realCard).getAllByText("future real provider placeholder only").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("not real Douyin integration").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("OAuth is not implemented").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no access token or refresh token storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no API key storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no secret storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no credential material storage").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no real metrics fetching").length).toBeGreaterThan(0);
    expect(within(realCard).getAllByText("no upload / publish / scheduling").length).toBeGreaterThan(0);
    expect(within(realCard).getByText("Douyin real credential reference placeholder")).toBeTruthy();
  });

  it("does not render credential input, token viewer, or platform operation buttons", async () => {
    installCredentialReferenceFetchMock();

    const { container } = render(<ProviderCredentialReferencePanel />);

    await screen.findByLabelText("Provider credential reference fake_local");
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
    ]) {
      expect(screen.queryByRole("button", { name: label })).toBeNull();
    }
    expect(screen.queryAllByRole("textbox")).toHaveLength(0);
    expect(screen.queryByRole("textbox", { name: /secret|token|api key|credential|password/i })).toBeNull();
    expect(container.querySelectorAll("input, textarea, select")).toHaveLength(0);
  });

  it("shows a safe error message when credential reference metadata loading fails", async () => {
    installCredentialReferenceFetchMock(
      {
        detail:
          "sensitive authorization_code token credential api_key client_secret should not be displayed by the UI",
      },
      500,
    );

    render(<ProviderCredentialReferencePanel />);

    expect(
      await screen.findByText("Provider Credential Reference metadata failed to load. Please try again."),
    ).toBeTruthy();
    expect(screen.queryByText(/authorization_code token credential/)).toBeNull();
  });

  it("shows an empty state when the credential reference response has no references", async () => {
    installCredentialReferenceFetchMock({ credential_references: [] });

    render(<ProviderCredentialReferencePanel />);

    expect(await screen.findByText("No Provider credential reference metadata")).toBeTruthy();
    expect(screen.getByText("The backend did not return provider credential reference metadata.")).toBeTruthy();
  });
});
