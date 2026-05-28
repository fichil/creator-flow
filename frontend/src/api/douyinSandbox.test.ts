import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  listDouyinProviderDescriptors,
  runDouyinSandboxMetricsPreview,
  runDouyinSandboxMockConnection,
  runDouyinSandboxPublishDryRun,
} from "./douyinSandbox";

function jsonResponse(body: unknown, status = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      headers: { "Content-Type": "application/json" },
      status,
    }),
  );
}

describe("douyin sandbox API client", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("calls the sandbox provider descriptor API without external Douyin domains or auth headers", async () => {
    const fetchMock = vi.fn(() => jsonResponse({ providers: [] }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(listDouyinProviderDescriptors()).resolves.toEqual([]);

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit | undefined];
    expect(new URL(url).pathname).toBe("/api/providers/douyin");
    expect(url).not.toContain("douyin.com");
    expect(init?.method ?? "GET").toBe("GET");
    expect(getHeaderValue(init?.headers, "Authorization")).toBeUndefined();
  });

  it("calls the sandbox mock connection endpoint with POST only", async () => {
    const fetchMock = vi.fn(() => jsonResponse({ provider_id: "douyin_sandbox" }));
    vi.stubGlobal("fetch", fetchMock);

    await runDouyinSandboxMockConnection();

    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(new URL(url).pathname).toBe("/api/providers/douyin/sandbox/mock-connection");
    expect(url).not.toContain("douyin.com");
    expect(init.method).toBe("POST");
    expect(init.body).toBeUndefined();
    expect(getHeaderValue(init.headers, "Authorization")).toBeUndefined();
  });

  it("calls the sandbox metrics preview endpoint with POST only", async () => {
    const fetchMock = vi.fn(() => jsonResponse({ provider_id: "douyin_sandbox" }));
    vi.stubGlobal("fetch", fetchMock);

    await runDouyinSandboxMetricsPreview();

    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(new URL(url).pathname).toBe("/api/providers/douyin/sandbox/metrics-preview");
    expect(url).not.toContain("douyin.com");
    expect(init.method).toBe("POST");
    expect(init.body).toBeUndefined();
    expect(getHeaderValue(init.headers, "Authorization")).toBeUndefined();
  });

  it("calls the sandbox publish dry-run endpoint with POST only", async () => {
    const fetchMock = vi.fn(() => jsonResponse({ provider_id: "douyin_sandbox" }));
    vi.stubGlobal("fetch", fetchMock);

    await runDouyinSandboxPublishDryRun();

    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(new URL(url).pathname).toBe("/api/providers/douyin/sandbox/publish-dry-run");
    expect(url).not.toContain("douyin.com");
    expect(init.method).toBe("POST");
    expect(init.body).toBeUndefined();
    expect(getHeaderValue(init.headers, "Authorization")).toBeUndefined();
  });

  it("uses a sandbox-safe error when the backend request fails", async () => {
    vi.stubGlobal("fetch", vi.fn(() => jsonResponse({ detail: "unsafe backend detail" }, 500)));

    await expect(listDouyinProviderDescriptors()).rejects.toThrow("Douyin sandbox API request failed (500)");
  });
});

function getHeaderValue(headers: HeadersInit | undefined, name: string) {
  if (!headers) {
    return undefined;
  }
  if (headers instanceof Headers) {
    return headers.get(name) ?? undefined;
  }
  if (Array.isArray(headers)) {
    return headers.find(([key]) => key.toLowerCase() === name.toLowerCase())?.[1];
  }
  return headers[name as keyof typeof headers];
}
