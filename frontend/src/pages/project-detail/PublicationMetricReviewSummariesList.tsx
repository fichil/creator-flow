import { PublicationMetricReviewSummary } from "../../api/client";

type PublicationMetricReviewSummariesListProps = {
  isArchived: boolean;
  isDisabled: boolean;
  isGenerating: boolean;
  summaries: PublicationMetricReviewSummary[];
  onGenerateFakeSummary: () => void;
};

export function PublicationMetricReviewSummariesList({
  isArchived,
  isDisabled,
  isGenerating,
  summaries,
  onGenerateFakeSummary,
}: PublicationMetricReviewSummariesListProps) {
  return (
    <div className="mt-4 rounded border border-stone-200 bg-white p-3">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h6 className="text-xs font-semibold uppercase text-stone-500">Metrics review summaries</h6>
          <p className="mt-1 text-xs text-stone-600">
            Fake/local insight from local development, demo, and test data. Not real Douyin performance. Not automatic
            recommendation; does not modify content automatically.
          </p>
        </div>
        {!isArchived && (
          <button
            className="rounded border border-teal-700 px-3 py-1 text-xs font-semibold text-teal-800 hover:bg-teal-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={isDisabled}
            type="button"
            onClick={onGenerateFakeSummary}
          >
            {isGenerating ? "Generating fake/local summary..." : "Generate fake/local summary"}
          </button>
        )}
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-50 p-3 text-xs text-stone-600">
          Archived projects are read-only. Existing fake/local review summaries can be viewed, but new summaries cannot
          be created.
        </p>
      )}

      {summaries.length === 0 ? (
        <p className="mt-3 rounded border border-dashed border-stone-300 bg-stone-50 p-3 text-sm text-stone-600">
          No metrics review summaries yet.
        </p>
      ) : (
        <div className="mt-3 space-y-3">
          {summaries.map((summary) => (
            <MetricReviewSummaryCard key={summary.id} summary={summary} />
          ))}
        </div>
      )}
    </div>
  );
}

function MetricReviewSummaryCard({ summary }: { summary: PublicationMetricReviewSummary }) {
  return (
    <article
      aria-label={`MetricReviewSummary ${summary.id}`}
      className="rounded border border-stone-200 bg-stone-50 p-3"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm font-medium text-stone-950">MetricReviewSummary #{summary.id}</p>
        <span className="rounded border border-teal-300 bg-white px-3 py-1 text-xs font-semibold text-teal-800">
          {summary.source === "fake_local" ? "Fake/local review summary" : summary.source}
        </span>
      </div>
      {summary.is_fake_local && (
        <p className="mt-2 rounded border border-amber-200 bg-amber-50 p-2 text-xs text-amber-800">
          Not real platform analysis. Not real platform performance. Local development / demo / test data only. Not
          automatic recommendation and does not modify content automatically.
        </p>
      )}
      <dl className="mt-3 grid gap-3 text-sm md:grid-cols-3">
        <SummaryValue label="Source" value={summary.source || "Not provided"} />
        <SummaryValue label="Snapshot count" value={summary.snapshot_count.toLocaleString()} />
        <SummaryValue label="Metric window" value={formatMetricWindow(summary)} />
        <SummaryValue label="Created at" value={formatDateTime(summary.created_at)} />
      </dl>
      <SummaryText label="Summary text" value={summary.summary_text} />
      <SummaryText label="Highlights" value={summary.highlights} />
      <SummaryText label="Low performance signals" value={summary.low_performance_signals} />
      <SummaryText label="Next observations" value={summary.next_observations} />
    </article>
  );
}

function SummaryValue({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-stone-500">{label}</dt>
      <dd className="mt-1 text-stone-800">{value}</dd>
    </div>
  );
}

function SummaryText({ label, value }: { label: string; value: string | null }) {
  const displayValue = value && value.trim() ? value : "Not provided for this fake/local summary.";
  return (
    <div className="mt-3 text-sm">
      <p className="text-xs font-semibold uppercase text-stone-500">{label}</p>
      <p className="mt-1 whitespace-pre-wrap text-stone-800">{displayValue}</p>
    </div>
  );
}

function formatMetricWindow(summary: PublicationMetricReviewSummary) {
  if (!summary.metric_window_start && !summary.metric_window_end) {
    return "No metrics window yet";
  }
  return `${summary.metric_window_start ? formatDateTime(summary.metric_window_start) : "Not provided"} -> ${
    summary.metric_window_end ? formatDateTime(summary.metric_window_end) : "Not provided"
  }`;
}

function formatDateTime(value: string | null) {
  return value ? new Date(value).toLocaleString() : "Not provided";
}
