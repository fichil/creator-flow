import { useEffect, useState } from "react";

import { listPlatformProviders, PlatformProvider, ProviderCapabilityMetadata } from "../api/client";
import { EmptyState } from "./EmptyState";

const capabilityLabels: Array<{ key: keyof ProviderCapabilityMetadata; label: string }> = [
  { key: "supports_oauth", label: "OAuth" },
  { key: "supports_metrics_read", label: "Metrics read" },
  { key: "supports_publish_prepare", label: "Publish prepare" },
  { key: "supports_real_publish", label: "Real publish" },
  { key: "supports_sandbox", label: "Sandbox" },
  { key: "supports_token_refresh", label: "Token refresh" },
  { key: "supports_disconnect", label: "Disconnect" },
  { key: "supports_revoke", label: "Revoke" },
];

const sourceLabels: Record<string, string[]> = {
  fake_local: ["local fake/demo/test data", "not real Douyin data", "no OAuth required", "no token stored"],
  sandbox: ["placeholder only", "OAuth not implemented", "tokens are not stored", "no real Douyin API call", "cannot be treated as douyin_real"],
  real: [
    "future real provider placeholder only",
    "not real Douyin integration",
    "no real metrics fetching",
    "no upload / publish / scheduling",
  ],
};

export function ProviderRegistryPanel() {
  const [providers, setProviders] = useState<PlatformProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);

    listPlatformProviders()
      .then((items) => {
        if (!cancelled) {
          setProviders(items);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError(true);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="mt-6 rounded border border-stone-200 bg-white p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-stone-950">Provider Registry</h2>
          <p className="mt-1 max-w-3xl text-sm text-stone-600">
            这是只读 Provider Registry metadata，用于区分 fake/local、sandbox placeholder 和 future real provider。
            当前不代表真实 Douyin 已接入，不实现 OAuth，不保存 token，不抓取真实指标，也不上传、不发布、不排期发布。
          </p>
        </div>
        <span className="rounded border border-stone-300 bg-stone-100 px-3 py-1 text-xs font-semibold text-stone-700">
          read-only metadata
        </span>
      </div>

      {loading && <p className="mt-4 text-sm text-stone-600">正在加载 Provider Registry metadata...</p>}
      {error && (
        <p className="mt-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          Provider Registry metadata 加载失败。请稍后重试。
        </p>
      )}
      {!loading && !error && providers.length === 0 && (
        <div className="mt-4">
          <EmptyState title="暂无 Provider metadata" description="后端暂未返回 provider registry metadata。" />
        </div>
      )}
      {!loading && !error && providers.length > 0 && (
        <div className="mt-4 grid gap-3 lg:grid-cols-3">
          {providers.map((provider) => (
            <ProviderCard key={provider.provider_id} provider={provider} />
          ))}
        </div>
      )}
    </section>
  );
}

function ProviderCard({ provider }: { provider: PlatformProvider }) {
  const sourceNotes = sourceLabels[provider.source_type] ?? [];

  return (
    <article aria-label={`Provider ${provider.provider_id}`} className="rounded border border-stone-200 bg-stone-50 p-4">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{provider.provider_name}</h3>
          <p className="mt-1 break-all text-xs text-stone-500">{provider.provider_id}</p>
        </div>
        <ProviderSourceBadge sourceType={provider.source_type} />
      </div>

      <dl className="mt-4 grid gap-3 text-sm">
        <MetadataRow label="provider_type" value={provider.provider_type} />
        <MetadataRow label="source_type" value={provider.source_type} />
        <MetadataRow label="implementation_status" value={provider.implementation_status} />
        <MetadataRow label="connection_status" value={provider.connection_status} />
        <MetadataRow label="availability" value={provider.is_available ? "available" : "not available"} />
        <MetadataRow
          label="real provider"
          value={provider.is_real_provider ? "yes, future placeholder" : "no"}
        />
        <MetadataRow
          label="authorization"
          value={provider.requires_user_authorization ? "required in future" : "not required"}
        />
      </dl>

      <div className="mt-4">
        <h4 className="text-xs font-semibold uppercase text-stone-500">Source boundary labels</h4>
        <div className="mt-2 flex flex-wrap gap-2">
          {sourceNotes.map((note) => (
            <span
              className="rounded border border-stone-300 bg-white px-2 py-1 text-xs font-medium text-stone-700"
              key={note}
            >
              {note}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-4">
        <h4 className="text-xs font-semibold uppercase text-stone-500">Capability metadata</h4>
        <div className="mt-2 grid gap-2">
          {capabilityLabels.map(({ key, label }) => (
            <CapabilityRow
              enabled={provider.capabilities[key]}
              key={key}
              label={label}
              provider={provider}
              capabilityKey={key}
            />
          ))}
        </div>
      </div>

      <div className="mt-4">
        <h4 className="text-xs font-semibold uppercase text-stone-500">Boundary notes</h4>
        <ul className="mt-2 space-y-1 text-sm text-stone-700">
          {provider.boundary_notes.map((note) => (
            <li className="break-words" key={note}>
              {note}
            </li>
          ))}
        </ul>
      </div>
    </article>
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

function ProviderSourceBadge({ sourceType }: { sourceType: string }) {
  const className =
    sourceType === "fake_local"
      ? "border-teal-300 bg-teal-50 text-teal-800"
      : sourceType === "sandbox"
        ? "border-amber-300 bg-amber-50 text-amber-800"
        : "border-stone-300 bg-white text-stone-800";

  return <span className={`rounded border px-2 py-1 text-xs font-semibold ${className}`}>source: {sourceType}</span>;
}

function CapabilityRow({
  capabilityKey,
  enabled,
  label,
  provider,
}: {
  capabilityKey: keyof ProviderCapabilityMetadata;
  enabled: boolean;
  label: string;
  provider: PlatformProvider;
}) {
  return (
    <div className="flex items-center justify-between gap-3 rounded border border-stone-200 bg-white px-3 py-2">
      <span className="text-sm font-medium text-stone-800">{label}</span>
      <span
        className={`shrink-0 rounded border px-2 py-1 text-xs font-semibold ${
          enabled ? "border-teal-300 bg-teal-50 text-teal-800" : "border-stone-300 bg-stone-100 text-stone-700"
        }`}
      >
        {formatCapabilityValue(provider, capabilityKey, enabled)}
      </span>
    </div>
  );
}

function formatCapabilityValue(
  provider: PlatformProvider,
  capabilityKey: keyof ProviderCapabilityMetadata,
  enabled: boolean,
) {
  if (!enabled) {
    return "Not available";
  }
  if (
    provider.source_type === "fake_local" &&
    (capabilityKey === "supports_metrics_read" || capabilityKey === "supports_publish_prepare")
  ) {
    return "Local fake capability";
  }
  if (provider.source_type === "sandbox" && capabilityKey === "supports_sandbox") {
    return "Sandbox boundary only";
  }
  return "Available per metadata";
}
