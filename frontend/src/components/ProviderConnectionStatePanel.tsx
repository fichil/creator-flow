import { useEffect, useState } from "react";

import { listProviderConnectionStates, ProviderConnectionState } from "../api/client";
import { EmptyState } from "./EmptyState";

const sourceLabels: Record<string, string[]> = {
  fake_local: [
    "local fake/demo/test data",
    "not real Douyin data",
    "no OAuth required",
    "no tokens stored",
    "no external service call",
  ],
  sandbox: [
    "placeholder only",
    "OAuth is not implemented",
    "tokens are not stored",
    "no real Douyin API call",
    "cannot be treated as douyin_real",
  ],
  real: [
    "future real provider placeholder only",
    "not real Douyin integration",
    "OAuth is not implemented",
    "no access token or refresh token storage",
    "no real metrics fetching",
    "no upload / publish / scheduling",
  ],
};

export function ProviderConnectionStatePanel() {
  const [connections, setConnections] = useState<ProviderConnectionState[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);

    listProviderConnectionStates()
      .then((items) => {
        if (!cancelled) {
          setConnections(items);
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
          <h2 className="text-lg font-semibold text-stone-950">Provider Connection State</h2>
          <p className="mt-1 max-w-3xl text-sm text-stone-600">
            Read-only Provider Connection State metadata for connection_status, authorization_status, and
            sensitive_storage_status. It does not mean real Douyin is connected, OAuth runtime exists, token, secret,
            API key, or credential material is stored, real metrics read exists, or upload / publish / scheduling is
            available. Connection, authorization, refresh, revoke, and disconnect actions are not provided here.
          </p>
        </div>
        <span className="rounded border border-stone-300 bg-stone-100 px-3 py-1 text-xs font-semibold text-stone-700">
          read-only status metadata
        </span>
      </div>

      {loading && <p className="mt-4 text-sm text-stone-600">Loading Provider Connection State metadata...</p>}
      {error && (
        <p className="mt-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          Provider Connection State metadata failed to load. Please try again.
        </p>
      )}
      {!loading && !error && connections.length === 0 && (
        <div className="mt-4">
          <EmptyState
            title="No Provider connection state metadata"
            description="The backend did not return provider connection state metadata."
          />
        </div>
      )}
      {!loading && !error && connections.length > 0 && (
        <div className="mt-4 grid gap-3 lg:grid-cols-3">
          {connections.map((connection) => (
            <ProviderConnectionCard connection={connection} key={connection.provider_id} />
          ))}
        </div>
      )}
    </section>
  );
}

function ProviderConnectionCard({ connection }: { connection: ProviderConnectionState }) {
  const sourceNotes = sourceLabels[connection.source_type] ?? [];

  return (
    <article
      aria-label={`Provider connection ${connection.provider_id}`}
      className="rounded border border-stone-200 bg-stone-50 p-4"
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{connection.provider_name}</h3>
          <p className="mt-1 break-all text-xs text-stone-500">{connection.provider_id}</p>
        </div>
        <ProviderSourceBadge sourceType={connection.source_type} />
      </div>

      <dl className="mt-4 grid gap-3 text-sm">
        <MetadataRow label="source_type" value={connection.source_type} />
        <MetadataRow label="implementation_status" value={connection.implementation_status} />
        <MetadataRow label="connection_status" value={connection.connection_status} />
        <MetadataRow label="authorization_status" value={connection.authorization_status} />
        <MetadataRow label="sensitive_storage_status" value={connection.sensitive_storage_status} />
        <MetadataRow label="availability" value={connection.is_available ? "available" : "not available"} />
        <MetadataRow
          label="real provider"
          value={connection.is_real_provider ? "yes, future placeholder" : "no"}
        />
        <MetadataRow
          label="authorization"
          value={connection.requires_user_authorization ? "required in future" : "not required"}
        />
        <MetadataRow label="can_connect" value={formatBoolean(connection.can_connect)} />
        <MetadataRow label="can_refresh" value={formatBoolean(connection.can_refresh)} />
        <MetadataRow label="can_revoke" value={formatBoolean(connection.can_revoke)} />
        <MetadataRow label="can_disconnect" value={formatBoolean(connection.can_disconnect)} />
      </dl>

      <div className="mt-4 rounded border border-stone-200 bg-white p-3">
        <h4 className="text-xs font-semibold uppercase text-stone-500">Safe status message</h4>
        <p className="mt-2 text-sm text-stone-700">{connection.safe_status_message}</p>
      </div>

      {(connection.last_status_change_reason || connection.created_at || connection.updated_at) && (
        <dl className="mt-4 grid gap-3 text-sm">
          {connection.last_status_change_reason && (
            <MetadataRow label="last_status_change_reason" value={connection.last_status_change_reason} />
          )}
          {connection.created_at && <MetadataRow label="created_at" value={connection.created_at} />}
          {connection.updated_at && <MetadataRow label="updated_at" value={connection.updated_at} />}
        </dl>
      )}

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
        <h4 className="text-xs font-semibold uppercase text-stone-500">Boundary notes</h4>
        <ul className="mt-2 space-y-1 text-sm text-stone-700">
          {connection.boundary_notes.map((note) => (
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

function formatBoolean(value: boolean) {
  return value ? "yes" : "no";
}
