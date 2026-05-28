const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type DouyinProviderDescriptor = {
  provider_id: string;
  display_name: string;
  environment: string;
  mode: string;
  status: string;
  supports_simulation: boolean;
  supports_real_oauth: boolean;
  supports_real_publish: boolean;
  supports_real_metrics: boolean;
  simulated: boolean;
  dry_run: boolean;
  boundary_notes: string[];
};

export type DouyinProviderDescriptorListResponse = {
  providers: DouyinProviderDescriptor[];
};

export type DouyinSandboxOperationResponse = {
  provider_id: string;
  source_type: string;
  mode: string;
  operation: string;
  workflow_name: string;
  status: string;
  outcome: string;
  simulated: boolean;
  dry_run: boolean;
  safe_message: string;
  boundary_notes: string[];
  operation_references: string[];
  payload: Record<string, unknown>;
  external_call_performed: boolean;
  storage_write_performed: boolean;
  database_write_performed: boolean;
};

async function requestDouyinSandbox<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: init?.body instanceof FormData ? undefined : { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`Douyin sandbox API request failed (${response.status})`);
  }

  return response.json() as Promise<T>;
}

export async function listDouyinProviderDescriptors(): Promise<DouyinProviderDescriptor[]> {
  const response = await requestDouyinSandbox<DouyinProviderDescriptorListResponse>("/api/providers/douyin");
  return response.providers;
}

export function runDouyinSandboxMockConnection(): Promise<DouyinSandboxOperationResponse> {
  return requestDouyinSandbox<DouyinSandboxOperationResponse>("/api/providers/douyin/sandbox/mock-connection", {
    method: "POST",
  });
}

export function runDouyinSandboxMetricsPreview(): Promise<DouyinSandboxOperationResponse> {
  return requestDouyinSandbox<DouyinSandboxOperationResponse>("/api/providers/douyin/sandbox/metrics-preview", {
    method: "POST",
  });
}

export function runDouyinSandboxPublishDryRun(): Promise<DouyinSandboxOperationResponse> {
  return requestDouyinSandbox<DouyinSandboxOperationResponse>("/api/providers/douyin/sandbox/publish-dry-run", {
    method: "POST",
  });
}
