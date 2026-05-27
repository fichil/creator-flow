import { useEffect, useState } from "react";

import { listProviderCredentialReferences, ProviderCredentialReference } from "../api/client";
import { EmptyState } from "./EmptyState";

const sourceLabels: Record<string, string[]> = {
  fake_local: [
    "local fake/demo/test data",
    "not real Douyin data",
    "no OAuth required",
    "no token stored",
    "no secret stored",
    "no credential material stored",
    "no external service call",
  ],
  sandbox: [
    "placeholder only",
    "OAuth is not implemented",
    "tokens are not stored",
    "secrets are not stored",
    "credential material is not stored",
    "no real Douyin API call",
    "cannot be treated as douyin_real",
  ],
  real: [
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
};

export function ProviderCredentialReferencePanel() {
  const [references, setReferences] = useState<ProviderCredentialReference[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);

    listProviderCredentialReferences()
      .then((items) => {
        if (!cancelled) {
          setReferences(items);
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
          <h2 className="text-lg font-semibold text-stone-950">Provider Credential References</h2>
          <p className="mt-1 max-w-3xl text-sm text-stone-600">
            Read-only Provider Credential Reference metadata for reference_status, storage_status, and
            redaction_policy_status. It does not mean real Douyin is connected, OAuth is implemented, token, secret,
            API key, authorization code, OAuth client secret, or credential material is stored. Secret input, token
            viewer, credential management, connection, authorization, refresh, revoke, disconnect, upload, publish, and
            scheduling actions are not provided here.
          </p>
        </div>
        <span className="rounded border border-stone-300 bg-stone-100 px-3 py-1 text-xs font-semibold text-stone-700">
          read-only reference metadata
        </span>
      </div>

      {loading && <p className="mt-4 text-sm text-stone-600">Loading Provider Credential Reference metadata...</p>}
      {error && (
        <p className="mt-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          Provider Credential Reference metadata failed to load. Please try again.
        </p>
      )}
      {!loading && !error && references.length === 0 && (
        <div className="mt-4">
          <EmptyState
            title="No Provider credential reference metadata"
            description="The backend did not return provider credential reference metadata."
          />
        </div>
      )}
      {!loading && !error && references.length > 0 && (
        <div className="mt-4 grid gap-3 lg:grid-cols-3">
          {references.map((reference) => (
            <ProviderCredentialReferenceCard key={reference.provider_id} reference={reference} />
          ))}
        </div>
      )}
    </section>
  );
}

function ProviderCredentialReferenceCard({ reference }: { reference: ProviderCredentialReference }) {
  const sourceNotes = sourceLabels[reference.source_type] ?? [];

  return (
    <article
      aria-label={`Provider credential reference ${reference.provider_id}`}
      className="rounded border border-stone-200 bg-stone-50 p-4"
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{reference.provider_name}</h3>
          <p className="mt-1 break-all text-xs text-stone-500">{reference.provider_id}</p>
        </div>
        <ProviderSourceBadge sourceType={reference.source_type} />
      </div>

      <dl className="mt-4 grid gap-3 text-sm">
        <MetadataRow label="source_type" value={reference.source_type} />
        <MetadataRow label="implementation_status" value={reference.implementation_status} />
        <MetadataRow label="reference_kind" value={reference.reference_kind} />
        <MetadataRow label="reference_status" value={reference.reference_status} />
        <MetadataRow label="storage_status" value={reference.storage_status} />
        <MetadataRow label="redaction_policy_status" value={reference.redaction_policy_status} />
        <MetadataRow label="availability" value={reference.is_available ? "available" : "not available"} />
        <MetadataRow
          label="real provider"
          value={reference.is_real_provider ? "yes, future placeholder" : "no"}
        />
        <MetadataRow
          label="authorization"
          value={reference.requires_user_authorization ? "required in future" : "not required"}
        />
      </dl>

      <div className="mt-4 rounded border border-stone-200 bg-white p-3">
        <h4 className="text-xs font-semibold uppercase text-stone-500">Safe display name</h4>
        <p className="mt-2 text-sm text-stone-700">{reference.safe_display_name}</p>
      </div>

      <div className="mt-4 rounded border border-stone-200 bg-white p-3">
        <h4 className="text-xs font-semibold uppercase text-stone-500">Safe status message</h4>
        <p className="mt-2 text-sm text-stone-700">{reference.safe_status_message}</p>
      </div>

      {(reference.last_status_change_reason || reference.created_at || reference.updated_at) && (
        <dl className="mt-4 grid gap-3 text-sm">
          {reference.last_status_change_reason && (
            <MetadataRow label="last_status_change_reason" value={reference.last_status_change_reason} />
          )}
          {reference.created_at && <MetadataRow label="created_at" value={reference.created_at} />}
          {reference.updated_at && <MetadataRow label="updated_at" value={reference.updated_at} />}
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
          {reference.boundary_notes.map((note) => (
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
