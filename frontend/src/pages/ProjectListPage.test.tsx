import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProjectListPage } from "./ProjectListPage";
import type {
  PlatformProvider,
  Project,
  ProviderConnectionState,
  ProviderCredentialReference,
  ProviderSecurityAuditEvent,
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
    await waitFor(() => expect(server.calls).toContain("GET /api/providers"));
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-connections"));
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-credential-references"));
    await waitFor(() => expect(server.calls).toContain("GET /api/provider-security-audit-events?limit=20"));
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
