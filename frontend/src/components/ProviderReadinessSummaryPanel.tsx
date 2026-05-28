import { useEffect, useState } from "react";

import { listProviderReadinessSummaries } from "../api/client";
import type { ProviderReadinessSummary } from "../api/client";
import { EmptyState } from "./EmptyState";

const sourceLabels: Record<string, string[]> = {
  fake_local: [
    "local fake/demo/test workflow readiness only",
    "not real Douyin readiness",
    "no real OAuth",
    "no real metrics fetching",
    "no real publish",
    "no token stored",
    "no external service call",
  ],
  sandbox: [
    "sandbox placeholder readiness only",
    "OAuth is not implemented",
    "OAuth callback route is not implemented",
    "OAuth state storage is not implemented",
    "credential storage is not implemented",
    "token lifecycle is not implemented",
    "no real Douyin API call",
    "cannot be treated as douyin_real",
  ],
  real: [
    "future real provider placeholder readiness only",
    "not real Douyin integration ready",
    "real OAuth is not implemented",
    "real OAuth callback route is not implemented",
    "real credential storage is not implemented",
    "token storage is not implemented",
    "token refresh / revoke / disconnect is not implemented",
    "no real metrics fetching",
    "no upload / publish / scheduling",
  ],
};

const sensitiveMetadataKeys = new Set([
  "access_token",
  "refresh_token",
  "token",
  "token_value",
  "api_key",
  "secret",
  "secret_value",
  "client_secret",
  "oauth_client_secret",
  "authorization_code",
  "state_value",
  "oauth_state_value",
  "callback_payload",
  "credential_material",
  "encrypted_credential",
  "raw_request",
  "raw_response",
  "raw_payload",
  "private_key",
  "oauth_code",
  "password",
  "bearer_token",
  "session_cookie",
  "token_expiry_value",
  "token_refresh_response",
  "token_revoke_response",
  "provider_token_response",
]);

const sensitiveValuePattern =
  /(access[_ -]?token|refresh[_ -]?token|token[_ -]?value|api[_ -]?key|client[_ -]?secret|oauth[_ -]?client[_ -]?secret|authorization[_ -]?code|state[_ -]?value|oauth[_ -]?state[_ -]?value|callback[_ -]?payload|credential[_ -]?material|encrypted[_ -]?credential|raw[_ -]?request|raw[_ -]?response|raw[_ -]?payload|private[_ -]?key|oauth[_ -]?code|password|bearer|session[_ -]?cookie|token[_ -]?expiry[_ -]?value|token[_ -]?refresh[_ -]?response|token[_ -]?revoke[_ -]?response|provider[_ -]?token[_ -]?response)/i;

export function ProviderReadinessSummaryPanel() {
  const [summaries, setSummaries] = useState<ProviderReadinessSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);

    listProviderReadinessSummaries()
      .then((items) => {
        if (!cancelled) {
          setSummaries(items);
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
          <h2 className="text-lg font-semibold text-stone-950">Provider Integration Readiness Summary</h2>
          <p className="mt-1 max-w-3xl text-sm text-stone-600">
            Read-only Provider Integration Readiness Summary metadata. This panel only displays non-sensitive readiness
            metadata aggregated from Provider Registry, Connection State, Credential Reference, Security Audit, OAuth
            Boundary, and Token Lifecycle Boundary. It does not mean real Douyin is connected, v0.9 POC is complete,
            OAuth or an OAuth callback route is implemented, OAuth state storage or token exchange exists, or a real
            provider authorization URL can be generated.
          </p>
          <p className="mt-2 max-w-3xl text-xs text-stone-500">
            This panel does not store or display access token, refresh token, token value, secret, API key,
            authorization code, OAuth client secret, OAuth state value, credential material, raw request, raw response,
            raw payload, token expiry value, token refresh response, token revoke response, or provider token response.
            It does not execute token refresh, token revoke, disconnect, or rotation, and it provides no readiness
            override, readiness approval, or production readiness certification.
          </p>
        </div>
        <span className="rounded border border-stone-300 bg-stone-100 px-3 py-1 text-xs font-semibold text-stone-700">
          read-only readiness metadata
        </span>
      </div>

      {loading && <p className="mt-4 text-sm text-stone-600">Loading Provider Readiness Summary metadata...</p>}
      {error && (
        <p className="mt-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          Provider Readiness Summary metadata failed to load. Please try again.
        </p>
      )}
      {!loading && !error && summaries.length === 0 && (
        <div className="mt-4">
          <EmptyState
            title="No Provider readiness summaries"
            description="The backend did not return provider readiness summary metadata."
          />
        </div>
      )}
      {!loading && !error && summaries.length > 0 && (
        <div className="mt-4 grid gap-3 lg:grid-cols-3">
          {summaries.map((summary) => (
            <ProviderReadinessSummaryCard key={summary.provider_id} summary={summary} />
          ))}
        </div>
      )}
    </section>
  );
}

function ProviderReadinessSummaryCard({ summary }: { summary: ProviderReadinessSummary }) {
  const sourceNotes = sourceLabels[summary.source_type] ?? [];

  return (
    <article
      aria-label={`Provider readiness summary ${summary.provider_id}`}
      className="rounded border border-stone-200 bg-stone-50 p-4"
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{summary.provider_name}</h3>
          <p className="mt-1 break-all text-xs text-stone-500">{summary.provider_id}</p>
        </div>
        <ProviderSourceBadge sourceType={summary.source_type} />
      </div>

      <dl className="mt-4 grid gap-3 text-sm">
        <MetadataRow label="source_type" value={summary.source_type} />
        <MetadataRow label="implementation_status" value={summary.implementation_status} />
        <MetadataRow label="overall_readiness_status" value={summary.overall_readiness_status} />
        <MetadataRow label="v0_9_poc_readiness_status" value={summary.v0_9_poc_readiness_status} />
        <MetadataRow label="availability" value={summary.is_available ? "available" : "not available"} />
        <MetadataRow label="real provider" value={summary.is_real_provider ? "yes, future placeholder" : "no"} />
        <MetadataRow
          label="authorization"
          value={summary.requires_user_authorization ? "required in future" : "not required"}
        />
        <MetadataRow label="can_use_local_fake_workflow" value={formatBoolean(summary.can_use_local_fake_workflow)} />
        <MetadataRow label="is_safe_to_attempt_real_oauth" value={formatBoolean(summary.is_safe_to_attempt_real_oauth)} />
        <MetadataRow label="is_safe_to_store_tokens" value={formatBoolean(summary.is_safe_to_store_tokens)} />
        <MetadataRow
          label="is_safe_to_fetch_real_metrics"
          value={formatBoolean(summary.is_safe_to_fetch_real_metrics)}
        />
        <MetadataRow label="is_safe_to_publish" value={formatBoolean(summary.is_safe_to_publish)} />
        <MetadataRow
          label="is_ready_for_v0_9_sandbox_poc"
          value={formatBoolean(summary.is_ready_for_v0_9_sandbox_poc)}
        />
        <MetadataRow label="is_ready_for_v0_9_real_poc" value={formatBoolean(summary.is_ready_for_v0_9_real_poc)} />
      </dl>

      <div className="mt-4 rounded border border-stone-200 bg-white p-3">
        <h4 className="text-xs font-semibold uppercase text-stone-500">Safe summary</h4>
        <p className="mt-2 text-sm text-stone-700">{summary.safe_summary}</p>
      </div>

      <div className="mt-4">
        <h4 className="text-xs font-semibold uppercase text-stone-500">Source readiness labels</h4>
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

      <ReadOnlyList heading="Blocking reasons" items={summary.blocking_reasons} />
      <ReadOnlyList heading="Next safe steps" items={summary.next_safe_steps} />
      <ReadinessItemList summary={summary} />
      <ReadOnlyList heading="Boundary notes" items={summary.boundary_notes} />
    </article>
  );
}

function ReadinessItemList({ summary }: { summary: ProviderReadinessSummary }) {
  return (
    <div className="mt-4">
      <h4 className="text-xs font-semibold uppercase text-stone-500">Readiness items</h4>
      <div className="mt-2 space-y-2">
        {summary.readiness_items.map((item) => {
          const metadataEntries = getSafeMetadataEntries(item.source_metadata);
          return (
            <div className="rounded border border-stone-200 bg-white p-3 text-sm" key={item.boundary_id}>
              <dl className="grid gap-2">
                <MetadataRow label="boundary_id" value={item.boundary_id} />
                <MetadataRow label="boundary_name" value={item.boundary_name} />
                <MetadataRow label="readiness_status" value={item.readiness_status} />
                <MetadataRow
                  label="is_blocking_real_integration"
                  value={formatBoolean(item.is_blocking_real_integration)}
                />
                <MetadataRow label="safe_status_message" value={item.safe_status_message} />
              </dl>
              <div className="mt-3">
                <h5 className="text-xs font-semibold uppercase text-stone-500">Source metadata</h5>
                {metadataEntries.length === 0 ? (
                  <p className="mt-1 text-sm text-stone-600">No source metadata</p>
                ) : (
                  <dl className="mt-2 grid gap-2">
                    {metadataEntries.map(([key, value]) => (
                      <MetadataRow key={key} label={key} value={formatMetadataValue(value)} />
                    ))}
                  </dl>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ReadOnlyList({ heading, items }: { heading: string; items: string[] }) {
  return (
    <div className="mt-4">
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

function getSafeMetadataEntries(metadata: Record<string, unknown>) {
  return Object.entries(metadata).filter(([key, value]) => !isSensitiveMetadataKey(key) && !isSensitiveValue(value));
}

function isSensitiveMetadataKey(key: string) {
  return sensitiveMetadataKeys.has(key.toLowerCase());
}

function isSensitiveValue(value: unknown): boolean {
  if (typeof value === "string") {
    return sensitiveValuePattern.test(value);
  }
  if (Array.isArray(value)) {
    return value.some(isSensitiveValue);
  }
  if (value && typeof value === "object") {
    return Object.entries(value).some(([key, nestedValue]) => isSensitiveMetadataKey(key) || isSensitiveValue(nestedValue));
  }
  return false;
}

function formatMetadataValue(value: unknown) {
  if (typeof value === "boolean") {
    return formatBoolean(value);
  }
  if (value === null || value === undefined) {
    return "not provided";
  }
  if (typeof value === "string" || typeof value === "number") {
    return String(value);
  }
  return "metadata value hidden";
}

function formatBoolean(value: boolean) {
  return value ? "yes" : "no";
}
