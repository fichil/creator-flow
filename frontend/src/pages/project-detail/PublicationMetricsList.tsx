import { PublicationMetricSnapshot } from "../../api/client";

type PublicationMetricsListProps = {
  isArchived: boolean;
  isDisabled: boolean;
  isGenerating: boolean;
  metrics: PublicationMetricSnapshot[];
  onGenerateFakeMetrics: () => void;
};

export function PublicationMetricsList({
  isArchived,
  isDisabled,
  isGenerating,
  metrics,
  onGenerateFakeMetrics,
}: PublicationMetricsListProps) {
  return (
    <div className="mt-4 rounded border border-stone-200 bg-white p-3">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h6 className="text-xs font-semibold uppercase text-stone-500">Metrics snapshots</h6>
          <p className="mt-1 text-xs text-stone-600">
            Fake/local metrics only. Not real platform performance.
          </p>
        </div>
        {!isArchived && (
          <button
            className="rounded border border-teal-700 px-3 py-1 text-xs font-semibold text-teal-800 hover:bg-teal-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={isDisabled}
            type="button"
            onClick={onGenerateFakeMetrics}
          >
            {isGenerating ? "Generating fake metrics..." : "Generate fake metrics"}
          </button>
        )}
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-50 p-3 text-xs text-stone-600">
          Archived projects are read-only. Existing fake/local metrics can be viewed, but new snapshots cannot be created.
        </p>
      )}

      {metrics.length === 0 ? (
        <p className="mt-3 rounded border border-dashed border-stone-300 bg-stone-50 p-3 text-sm text-stone-600">
          No metrics snapshots yet.
        </p>
      ) : (
        <div className="mt-3 space-y-3">
          {metrics.map((metric) => (
            <MetricSnapshotCard key={metric.id} metric={metric} />
          ))}
        </div>
      )}
    </div>
  );
}

function MetricSnapshotCard({ metric }: { metric: PublicationMetricSnapshot }) {
  return (
    <article aria-label={`MetricSnapshot ${metric.id}`} className="rounded border border-stone-200 bg-stone-50 p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm font-medium text-stone-950">MetricSnapshot #{metric.id}</p>
        <span className="rounded border border-teal-300 bg-white px-3 py-1 text-xs font-semibold text-teal-800">
          {metric.source === "fake_local" ? "Fake/local metrics" : metric.source}
        </span>
      </div>
      {metric.source === "fake_local" && (
        <p className="mt-2 rounded border border-amber-200 bg-amber-50 p-2 text-xs text-amber-800">
          Not real platform performance.
        </p>
      )}
      <dl className="mt-3 grid gap-3 text-sm md:grid-cols-3">
        <MetricValue label="Captured at" value={new Date(metric.captured_at).toLocaleString()} />
        <MetricValue label="Views" value={formatNumber(metric.views)} />
        <MetricValue label="Likes" value={formatNumber(metric.likes)} />
        <MetricValue label="Comments" value={formatNumber(metric.comments)} />
        <MetricValue label="Shares" value={formatNumber(metric.shares)} />
        <MetricValue label="Favorites" value={formatNumber(metric.favorites)} />
        <MetricValue label="Average watch time" value={formatSeconds(metric.average_watch_time_seconds)} />
        <MetricValue label="Completion rate" value={formatPercent(metric.completion_rate)} />
        <MetricValue label="Source" value={metric.source} />
      </dl>
      {metric.provider_payload_summary && (
        <div className="mt-3 text-sm">
          <p className="text-xs font-semibold uppercase text-stone-500">Provider payload summary</p>
          <p className="mt-1 text-stone-800">{metric.provider_payload_summary}</p>
        </div>
      )}
    </article>
  );
}

function MetricValue({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-stone-500">{label}</dt>
      <dd className="mt-1 text-stone-800">{value}</dd>
    </div>
  );
}

function formatNumber(value: number | null) {
  return value === null ? "Not provided" : value.toLocaleString();
}

function formatSeconds(value: number | null) {
  return value === null ? "Not provided" : `${value.toLocaleString()}s`;
}

function formatPercent(value: number | null) {
  return value === null ? "Not provided" : `${Math.round(value * 100)}%`;
}
