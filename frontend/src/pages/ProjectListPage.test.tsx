import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProjectListPage } from "./ProjectListPage";
import type { PlatformProvider, Project } from "../api/client";

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

  it("keeps the project list workflow visible while mounting Provider Registry metadata", async () => {
    const server = installListPageFetchMock();

    render(<ProjectListPage onCreate={vi.fn()} onOpen={vi.fn()} />);

    expect(screen.getByRole("button", { name: "新建项目" })).toBeTruthy();
    expect(screen.getByLabelText("显示归档项目")).toBeTruthy();
    expect(await screen.findByText("Existing project")).toBeTruthy();
    expect(await screen.findByLabelText("Provider fake_local")).toBeTruthy();
    expect(screen.getByLabelText("Provider douyin_sandbox")).toBeTruthy();
    expect(screen.getByLabelText("Provider douyin_real")).toBeTruthy();
    await waitFor(() => expect(server.calls).toContain("GET /api/providers"));
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
