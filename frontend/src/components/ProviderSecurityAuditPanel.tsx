import { useEffect, useState } from "react";

import { listProviderSecurityAuditEvents, ProviderSecurityAuditEvent } from "../api/client";
import { EmptyState } from "./EmptyState";

const DEFAULT_AUDIT_LIMIT = 20;

const sourceLabels: Record<string, string[]> = {
  fake_local: [
    "local fake/demo/test audit metadata only",
    "not real Douyin data",
    "no OAuth required",
    "no token stored",
    "no secret stored",
    "no external service call",
  ],
  sandbox: [
    "placeholder audit metadata only",
    "OAuth is not implemented",
    "tokens are not stored",
    "secrets are not stored",
    "no real Douyin API call",
    "cannot be treated as douyin_real",
  ],
  real: [
    "future real provider placeholder audit metadata only",
    "not real Douyin integration",
    "OAuth is not implemented",
    "no access token or refresh token storage",
    "no API key storage",
    "no secret storage",
    "no real metrics fetching",
    "no upload / publish / scheduling",
  ],
};

export function ProviderSecurityAuditPanel() {
  const [events, setEvents] = useState<ProviderSecurityAuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);

    listProviderSecurityAuditEvents({ limit: DEFAULT_AUDIT_LIMIT })
      .then((items) => {
        if (!cancelled) {
          setEvents(items);
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
          <h2 className="text-lg font-semibold text-stone-950">Provider Security Audit Events</h2>
          <p className="mt-1 max-w-3xl text-sm text-stone-600">
            Read-only Provider Security Audit Event metadata. This panel only displays redacted / safe audit metadata
            for event_type, event_status, event_severity, actor_type, redaction_status, safe_event_message,
            safe_metadata, and boundary_notes. It does not mean real Douyin is connected, OAuth runtime or an OAuth
            callback exists, token, secret, API key, authorization code, OAuth client secret, or credential material is
            stored, or raw request, raw response, or raw payload is stored or displayed. Production SIEM, compliance
            archive, external log shipping, connection, authorization, refresh, revoke, disconnect, upload, publish, and
            scheduling actions are not provided here.
          </p>
        </div>
        <span className="rounded border border-stone-300 bg-stone-100 px-3 py-1 text-xs font-semibold text-stone-700">
          read-only audit metadata
        </span>
      </div>

      {loading && <p className="mt-4 text-sm text-stone-600">Loading Provider Security Audit metadata...</p>}
      {error && (
        <p className="mt-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          Provider Security Audit metadata failed to load. Please try again.
        </p>
      )}
      {!loading && !error && events.length === 0 && (
        <div className="mt-4">
          <EmptyState
            title="No Provider security audit events"
            description="The backend did not return provider security audit event metadata."
          />
        </div>
      )}
      {!loading && !error && events.length > 0 && (
        <div className="mt-4 grid gap-3 lg:grid-cols-3">
          {events.map((event) => (
            <ProviderSecurityAuditCard auditEvent={event} key={event.audit_event_id} />
          ))}
        </div>
      )}
    </section>
  );
}

function ProviderSecurityAuditCard({ auditEvent }: { auditEvent: ProviderSecurityAuditEvent }) {
  const sourceNotes = sourceLabels[auditEvent.source_type] ?? [];

  return (
    <article
      aria-label={`Provider security audit event ${auditEvent.provider_id}`}
      className="rounded border border-stone-200 bg-stone-50 p-4"
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{auditEvent.provider_name}</h3>
          <p className="mt-1 break-all text-xs text-stone-500">{auditEvent.provider_id}</p>
        </div>
        <ProviderSourceBadge sourceType={auditEvent.source_type} />
      </div>

      <dl className="mt-4 grid gap-3 text-sm">
        <MetadataRow label="audit_event_id" value={auditEvent.audit_event_id} />
        <MetadataRow label="source_type" value={auditEvent.source_type} />
        <MetadataRow label="implementation_status" value={auditEvent.implementation_status} />
        <MetadataRow label="event_type" value={auditEvent.event_type} />
        <MetadataRow label="event_status" value={auditEvent.event_status} />
        <MetadataRow label="event_severity" value={auditEvent.event_severity} />
        <MetadataRow label="actor_type" value={auditEvent.actor_type} />
        <MetadataRow label="redaction_status" value={auditEvent.redaction_status} />
        <MetadataRow label="created_at" value={auditEvent.created_at} />
      </dl>

      <div className="mt-4 rounded border border-stone-200 bg-white p-3">
        <h4 className="text-xs font-semibold uppercase text-stone-500">Safe event message</h4>
        <p className="mt-2 break-words text-sm text-stone-700">{auditEvent.safe_event_message}</p>
      </div>

      <div className="mt-4 rounded border border-stone-200 bg-white p-3">
        <h4 className="text-xs font-semibold uppercase text-stone-500">Safe metadata</h4>
        <SafeMetadata metadata={auditEvent.safe_metadata} />
      </div>

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
          {auditEvent.boundary_notes.map((note) => (
            <li className="break-words" key={note}>
              {note}
            </li>
          ))}
        </ul>
      </div>
    </article>
  );
}

function SafeMetadata({ metadata }: { metadata: Record<string, unknown> }) {
  const entries = Object.entries(metadata);
  if (entries.length === 0) {
    return <p className="mt-2 text-sm text-stone-700">No safe metadata</p>;
  }

  const metadataText = JSON.stringify(metadata, null, 2);

  return (
    <>
      {metadataText.includes("[REDACTED]") && (
        <p className="mt-2 text-xs font-medium text-stone-600">[REDACTED] values are redaction result metadata.</p>
      )}
      <pre className="mt-2 max-h-64 overflow-auto whitespace-pre-wrap break-words rounded border border-stone-200 bg-stone-950 p-3 text-xs text-stone-50">
        {metadataText}
      </pre>
    </>
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
