import { useEffect, useState } from "react";

import { listProviderOAuthBoundaries, ProviderOAuthBoundary } from "../api/client";
import { EmptyState } from "./EmptyState";

const sourceLabels: Record<string, string[]> = {
  fake_local: [
    "local fake/demo/test data only",
    "not real Douyin data",
    "OAuth is not required",
    "no state value stored",
    "no authorization code stored",
    "no token exchange",
    "no token stored",
    "no secret stored",
    "no external service call",
  ],
  sandbox: [
    "placeholder OAuth boundary metadata only",
    "OAuth is not implemented",
    "OAuth callback route is not implemented",
    "OAuth state storage is not implemented",
    "CSRF state validation is planned but not active",
    "authorization code is not stored",
    "tokens are not stored",
    "secrets are not stored",
    "no token exchange",
    "no real Douyin API call",
    "cannot be treated as douyin_real",
  ],
  real: [
    "future real provider OAuth boundary placeholder only",
    "not real Douyin integration",
    "OAuth is not implemented",
    "OAuth callback route is not implemented",
    "OAuth state storage is not implemented",
    "CSRF state validation is planned but not active",
    "no authorization code storage",
    "no access token or refresh token storage",
    "no API key storage",
    "no secret storage",
    "no token exchange",
    "no real metrics fetching",
    "no upload / publish / scheduling",
  ],
};

export function ProviderOAuthBoundaryPanel() {
  const [boundaries, setBoundaries] = useState<ProviderOAuthBoundary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);

    listProviderOAuthBoundaries()
      .then((items) => {
        if (!cancelled) {
          setBoundaries(items);
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
          <h2 className="text-lg font-semibold text-stone-950">Provider OAuth Boundaries</h2>
          <p className="mt-1 max-w-3xl text-sm text-stone-600">
            Read-only Provider OAuth Boundary metadata. This panel only displays OAuth state / callback / CSRF /
            redirect / token exchange / token storage / error redaction / audit event policy and status metadata. It
            does not mean real Douyin is connected, OAuth runtime or an OAuth callback route exists, OAuth state storage
            or token exchange exists, or a real provider authorization URL can be generated. It does not store token,
            secret, API key, authorization code, OAuth client secret, OAuth state value, credential material, raw
            request, raw response, or raw payload. Connection, authorization, OAuth start, callback, token exchange,
            refresh, revoke, disconnect, upload, publish, and scheduling actions are not provided here.
          </p>
          <p className="mt-2 max-w-3xl text-xs text-stone-500">
            required_planned means future planned requirement only; it is not active CSRF, state, or callback
            protection. Token exchange and token storage policy statuses are metadata only.
          </p>
        </div>
        <span className="rounded border border-stone-300 bg-stone-100 px-3 py-1 text-xs font-semibold text-stone-700">
          read-only OAuth boundary metadata
        </span>
      </div>

      {loading && <p className="mt-4 text-sm text-stone-600">Loading Provider OAuth Boundary metadata...</p>}
      {error && (
        <p className="mt-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          Provider OAuth Boundary metadata failed to load. Please try again.
        </p>
      )}
      {!loading && !error && boundaries.length === 0 && (
        <div className="mt-4">
          <EmptyState
            title="No Provider OAuth boundaries"
            description="The backend did not return provider OAuth boundary metadata."
          />
        </div>
      )}
      {!loading && !error && boundaries.length > 0 && (
        <div className="mt-4 grid gap-3 lg:grid-cols-3">
          {boundaries.map((boundary) => (
            <ProviderOAuthBoundaryCard boundary={boundary} key={boundary.provider_id} />
          ))}
        </div>
      )}
    </section>
  );
}

function ProviderOAuthBoundaryCard({ boundary }: { boundary: ProviderOAuthBoundary }) {
  const sourceNotes = sourceLabels[boundary.source_type] ?? [];

  return (
    <article
      aria-label={`Provider OAuth boundary ${boundary.provider_id}`}
      className="rounded border border-stone-200 bg-stone-50 p-4"
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{boundary.provider_name}</h3>
          <p className="mt-1 break-all text-xs text-stone-500">{boundary.provider_id}</p>
        </div>
        <ProviderSourceBadge sourceType={boundary.source_type} />
      </div>

      <dl className="mt-4 grid gap-3 text-sm">
        <MetadataRow label="source_type" value={boundary.source_type} />
        <MetadataRow label="implementation_status" value={boundary.implementation_status} />
        <MetadataRow label="oauth_policy_status" value={boundary.oauth_policy_status} />
        <MetadataRow label="state_policy_status" value={boundary.state_policy_status} />
        <MetadataRow label="callback_policy_status" value={boundary.callback_policy_status} />
        <MetadataRow label="csrf_protection_status" value={boundary.csrf_protection_status} />
        <MetadataRow label="redirect_uri_policy_status" value={boundary.redirect_uri_policy_status} />
        <MetadataRow label="token_exchange_policy_status" value={boundary.token_exchange_policy_status} />
        <MetadataRow label="token_storage_policy_status" value={boundary.token_storage_policy_status} />
        <MetadataRow label="error_redaction_policy_status" value={boundary.error_redaction_policy_status} />
        <MetadataRow label="audit_event_policy_status" value={boundary.audit_event_policy_status} />
        <MetadataRow label="availability" value={boundary.is_available ? "available" : "not available"} />
        <MetadataRow label="real provider" value={boundary.is_real_provider ? "yes, future placeholder" : "no"} />
        <MetadataRow
          label="authorization"
          value={boundary.requires_user_authorization ? "required in future" : "not required"}
        />
        <MetadataRow label="can_start_oauth" value={formatBoolean(boundary.can_start_oauth)} />
        <MetadataRow label="can_handle_callback" value={formatBoolean(boundary.can_handle_callback)} />
        <MetadataRow label="can_exchange_token" value={formatBoolean(boundary.can_exchange_token)} />
        <MetadataRow label="can_refresh_token" value={formatBoolean(boundary.can_refresh_token)} />
        <MetadataRow label="can_revoke_token" value={formatBoolean(boundary.can_revoke_token)} />
      </dl>

      <div className="mt-4 rounded border border-stone-200 bg-white p-3">
        <h4 className="text-xs font-semibold uppercase text-stone-500">Safe status message</h4>
        <p className="mt-2 text-sm text-stone-700">{boundary.safe_status_message}</p>
      </div>

      {(boundary.last_status_change_reason || boundary.created_at || boundary.updated_at) && (
        <dl className="mt-4 grid gap-3 text-sm">
          {boundary.last_status_change_reason && (
            <MetadataRow label="last_status_change_reason" value={boundary.last_status_change_reason} />
          )}
          {boundary.created_at && <MetadataRow label="created_at" value={boundary.created_at} />}
          {boundary.updated_at && <MetadataRow label="updated_at" value={boundary.updated_at} />}
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
          {boundary.boundary_notes.map((note) => (
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
