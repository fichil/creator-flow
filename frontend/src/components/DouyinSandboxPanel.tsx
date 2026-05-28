import { useEffect, useState } from "react";

import {
  DouyinProviderDescriptor,
  DouyinSandboxOperationResponse,
  listDouyinProviderDescriptors,
  runDouyinSandboxMetricsPreview,
  runDouyinSandboxMockConnection,
  runDouyinSandboxPublishDryRun,
} from "../api/douyinSandbox";
import { EmptyState } from "./EmptyState";

type ActionKey = "mockConnection" | "metricsPreview" | "publishDryRun";

const actionLabels: Record<ActionKey, string> = {
  mockConnection: "Run sandbox mock connection",
  metricsPreview: "Load sandbox metrics preview",
  publishDryRun: "Run publish dry-run",
};

const sensitiveKeyPattern =
  /^(access_token|refresh_token|client_secret|authorization_code|oauth_state|api_key|credential|cookie|session|bearer|password|secret)$/i;
const sensitiveValuePattern =
  /(access[_-]?token|refresh[_-]?token|client[_-]?secret|authorization[_-]?code|oauth[_-]?state|api[_-]?key|credential|cookie|session|bearer|password|secret)/i;

export function DouyinSandboxPanel() {
  const [providers, setProviders] = useState<DouyinProviderDescriptor[]>([]);
  const [loadingProviders, setLoadingProviders] = useState(true);
  const [providerError, setProviderError] = useState<string | null>(null);
  const [results, setResults] = useState<Partial<Record<ActionKey, DouyinSandboxOperationResponse>>>({});
  const [actionErrors, setActionErrors] = useState<Partial<Record<ActionKey, string>>>({});
  const [runningAction, setRunningAction] = useState<ActionKey | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoadingProviders(true);
    setProviderError(null);

    listDouyinProviderDescriptors()
      .then((items) => {
        if (!cancelled) {
          setProviders(items);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setProviderError("Douyin sandbox provider metadata failed to load. This POC panel remains sandbox-only.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoadingProviders(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  async function runAction(action: ActionKey) {
    setRunningAction(action);
    setActionErrors((current) => ({ ...current, [action]: undefined }));
    try {
      const result = await actionRunner(action)();
      setResults((current) => ({ ...current, [action]: result }));
    } catch {
      setActionErrors((current) => ({
        ...current,
        [action]: "Sandbox request failed. No real Douyin connection, OAuth, upload, publish, or schedule was attempted.",
      }));
    } finally {
      setRunningAction(null);
    }
  }

  return (
    <section className="mt-6 rounded border border-amber-200 bg-white p-4" aria-label="Douyin Sandbox POC Panel">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-stone-950">Douyin Sandbox POC Panel</h2>
          <p className="mt-1 max-w-3xl text-sm text-stone-600">
            This panel is for the v0.9 sandbox POC only. All results are deterministic simulated / dry-run
            responses. It does not connect to real Douyin, perform OAuth, store tokens, upload videos, publish
            content, or schedule content.
          </p>
          <p className="mt-2 max-w-3xl text-xs text-stone-500">
            The panel only calls the v0.9 sandbox backend API. `douyin_real` stays blocked / not implemented, and
            unknown provider ids do not fall back to `douyin_sandbox`.
          </p>
        </div>
        <span className="rounded border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800">
          sandbox POC only
        </span>
      </div>

      <div className="mt-4 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
        Sandbox boundary: deterministic simulated results only, dry-run only, no OAuth URL, no platform-side effects,
        no file upload control, no platform publish control, and no scheduling control.
      </div>

      <div className="mt-5">
        <h3 className="text-base font-semibold text-stone-950">Provider Status</h3>
        {loadingProviders && <p className="mt-3 text-sm text-stone-600">Loading Douyin sandbox provider metadata...</p>}
        {providerError && (
          <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{providerError}</p>
        )}
        {!loadingProviders && !providerError && providers.length === 0 && (
          <div className="mt-3">
            <EmptyState
              title="No Douyin sandbox providers"
              description="The sandbox backend did not return provider descriptors."
            />
          </div>
        )}
        {!loadingProviders && !providerError && providers.length > 0 && (
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            {providers.map((provider) => (
              <ProviderDescriptorCard key={provider.provider_id} provider={provider} />
            ))}
          </div>
        )}
      </div>

      <div className="mt-5 grid gap-3 lg:grid-cols-3">
        <ActionCard
          action="mockConnection"
          description="Creates a deterministic sandbox-only mock account connection result. It is not a real account connection."
          error={actionErrors.mockConnection}
          result={results.mockConnection}
          running={runningAction === "mockConnection"}
          onRun={runAction}
        />
        <ActionCard
          action="metricsPreview"
          description="Loads deterministic fake metrics for preview only. These are not real metrics from Douyin."
          error={actionErrors.metricsPreview}
          result={results.metricsPreview}
          running={runningAction === "metricsPreview"}
          onRun={runAction}
        />
        <ActionCard
          action="publishDryRun"
          description="Runs a sandbox publish dry-run. It performs no upload, no publish, and no schedule."
          error={actionErrors.publishDryRun}
          result={results.publishDryRun}
          running={runningAction === "publishDryRun"}
          onRun={runAction}
        />
      </div>
    </section>
  );
}

function actionRunner(action: ActionKey) {
  if (action === "mockConnection") {
    return runDouyinSandboxMockConnection;
  }
  if (action === "metricsPreview") {
    return runDouyinSandboxMetricsPreview;
  }
  return runDouyinSandboxPublishDryRun;
}

function ProviderDescriptorCard({ provider }: { provider: DouyinProviderDescriptor }) {
  const isSandbox = provider.provider_id === "douyin_sandbox";
  const isReal = provider.provider_id === "douyin_real";

  return (
    <article
      aria-label={`Douyin sandbox provider ${provider.provider_id}`}
      className="rounded border border-stone-200 bg-stone-50 p-4"
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h4 className="text-base font-semibold text-stone-950">{provider.display_name}</h4>
          <p className="mt-1 break-all text-xs text-stone-500">{provider.provider_id}</p>
        </div>
        <span className={`rounded border px-2 py-1 text-xs font-semibold ${badgeClass(provider.mode)}`}>
          {provider.mode}
        </span>
      </div>
      <dl className="mt-4 grid gap-2 text-sm">
        <MetadataRow label="status" value={provider.status} />
        <MetadataRow label="environment" value={provider.environment} />
        <MetadataRow label="simulation" value={provider.supports_simulation ? "supported sandbox simulation" : "not supported"} />
        <MetadataRow label="OAuth capability" value={provider.supports_real_oauth ? "available" : "not implemented"} />
        <MetadataRow label="metrics capability" value={provider.supports_real_metrics ? "available" : "not implemented"} />
        <MetadataRow label="publish capability" value={provider.supports_real_publish ? "available" : "not implemented"} />
      </dl>
      {isSandbox && (
        <p className="mt-3 rounded border border-amber-200 bg-white p-2 text-xs text-amber-900">
          douyin_sandbox can only return sandbox / simulated / dry-run results through this panel.
        </p>
      )}
      {isReal && (
        <p className="mt-3 rounded border border-stone-200 bg-white p-2 text-xs text-stone-700">
          douyin_real is visible for source separation and remains blocked / not implemented.
        </p>
      )}
      <ReadOnlyList heading="Boundary notes" items={provider.boundary_notes.map(safeText)} />
    </article>
  );
}

function ActionCard({
  action,
  description,
  error,
  result,
  running,
  onRun,
}: {
  action: ActionKey;
  description: string;
  error?: string;
  result?: DouyinSandboxOperationResponse;
  running: boolean;
  onRun: (action: ActionKey) => void;
}) {
  return (
    <article className="rounded border border-stone-200 bg-stone-50 p-4">
      <div className="flex min-h-28 flex-col justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{actionLabels[action]}</h3>
          <p className="mt-1 text-sm text-stone-600">{description}</p>
        </div>
        <button
          className="w-fit rounded bg-stone-950 px-3 py-2 text-sm font-medium text-white hover:bg-stone-800 disabled:cursor-not-allowed disabled:bg-stone-400"
          disabled={running}
          type="button"
          onClick={() => onRun(action)}
        >
          {running ? "Running sandbox dry-run..." : actionLabels[action]}
        </button>
      </div>
      {error && <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {result && <OperationResultCard result={result} />}
    </article>
  );
}

function OperationResultCard({ result }: { result: DouyinSandboxOperationResponse }) {
  return (
    <div className="mt-4 rounded border border-stone-200 bg-white p-3" aria-label={`Sandbox result ${result.operation}`}>
      <div className="flex flex-wrap gap-2">
        <span className="rounded border border-amber-300 bg-amber-50 px-2 py-1 text-xs font-semibold text-amber-800">
          sandbox
        </span>
        <span className="rounded border border-teal-300 bg-teal-50 px-2 py-1 text-xs font-semibold text-teal-800">
          simulated
        </span>
        <span className="rounded border border-stone-300 bg-stone-100 px-2 py-1 text-xs font-semibold text-stone-700">
          dry-run
        </span>
      </div>
      <dl className="mt-3 grid gap-2 text-sm">
        <MetadataRow label="provider_id" value={safeText(result.provider_id)} />
        <MetadataRow label="operation" value={safeText(result.operation)} />
        <MetadataRow label="workflow_name" value={safeText(result.workflow_name)} />
        <MetadataRow label="status" value={safeText(result.status)} />
        <MetadataRow label="outcome" value={safeText(result.outcome)} />
        <MetadataRow label="external_call_performed" value={formatBoolean(result.external_call_performed)} />
        <MetadataRow label="storage_write_performed" value={formatBoolean(result.storage_write_performed)} />
        <MetadataRow label="database_write_performed" value={formatBoolean(result.database_write_performed)} />
      </dl>
      <p className="mt-3 text-sm text-stone-700">{safeText(result.safe_message)}</p>
      <ReadOnlyList heading="Boundary notes" items={result.boundary_notes.map(safeText)} />
      <ReadOnlyList heading="Operation references" items={result.operation_references.map(safeText)} />
      <div className="mt-3">
        <h4 className="text-xs font-semibold uppercase text-stone-500">Deterministic sandbox payload</h4>
        <pre className="mt-2 max-h-72 overflow-auto rounded border border-stone-200 bg-stone-50 p-3 text-xs text-stone-800">
          {JSON.stringify(getSafePayload(result.payload), null, 2)}
        </pre>
      </div>
    </div>
  );
}

function MetadataRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-stone-500">{label}</dt>
      <dd className="mt-1 break-words text-stone-800">{value}</dd>
    </div>
  );
}

function ReadOnlyList({ heading, items }: { heading: string; items: string[] }) {
  return (
    <div className="mt-3">
      <h4 className="text-xs font-semibold uppercase text-stone-500">{heading}</h4>
      <ul className="mt-2 space-y-1 text-sm text-stone-700">
        {items.map((item) => (
          <li className="break-words" key={item}>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

function badgeClass(mode: string) {
  if (mode === "sandbox") {
    return "border-amber-300 bg-amber-50 text-amber-800";
  }
  if (mode === "real") {
    return "border-stone-300 bg-white text-stone-800";
  }
  return "border-teal-300 bg-teal-50 text-teal-800";
}

function getSafePayload(payload: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(payload)
      .filter(([key, value]) => !isSensitiveKey(key) && !isSensitiveValue(value))
      .map(([key, value]) => [key, sanitizeValue(value)]),
  );
}

function sanitizeValue(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.filter((item) => !isSensitiveValue(item)).map(sanitizeValue);
  }
  if (value && typeof value === "object") {
    return getSafePayload(value as Record<string, unknown>);
  }
  if (typeof value === "string") {
    return safeText(value);
  }
  return value;
}

function isSensitiveKey(key: string) {
  return sensitiveKeyPattern.test(key);
}

function isSensitiveValue(value: unknown): boolean {
  if (typeof value === "string") {
    return sensitiveValuePattern.test(value);
  }
  if (Array.isArray(value)) {
    return value.some(isSensitiveValue);
  }
  if (value && typeof value === "object") {
    return Object.entries(value).some(([key, nestedValue]) => isSensitiveKey(key) || isSensitiveValue(nestedValue));
  }
  return false;
}

function safeText(value: string) {
  return sensitiveValuePattern.test(value) ? "[redacted sandbox value]" : value;
}

function formatBoolean(value: boolean) {
  return value ? "yes" : "no";
}
