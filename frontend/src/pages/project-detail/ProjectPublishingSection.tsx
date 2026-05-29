import { useEffect, useState } from "react";

import {
  cancelPublishIntent,
  createFakePublicationMetricReviewSummary,
  confirmPublishIntent,
  createFakePublicationMetric,
  createPublishIntent,
  fakePublishIntent,
  getPublicationRecords,
  getPublishIntents,
  getReviewDrafts,
  listPublicationMetrics,
  listPublicationMetricReviewSummaries,
  PublicationMetricReviewSummary,
  PublicationMetricSnapshot,
  PublicationRecord,
  PublishIntent,
  ReviewDraft,
} from "../../api/client";
import { formatStatus } from "./formatting";
import { PublicationMetricReviewSummariesList } from "./PublicationMetricReviewSummariesList";
import { PublicationMetricsList } from "./PublicationMetricsList";

type ProjectPublishingSectionProps = {
  isArchived: boolean;
  projectId: number;
  refreshKey: number;
};

type PublishingAction =
  | { type: "create"; id: number }
  | { type: "confirm"; id: number }
  | { type: "cancel"; id: number }
  | { type: "fake-publish"; id: number }
  | { type: "fake-metrics"; id: number }
  | { type: "fake-review-summary"; id: number };

export function ProjectPublishingSection({ isArchived, projectId, refreshKey }: ProjectPublishingSectionProps) {
  const [reviewDrafts, setReviewDrafts] = useState<ReviewDraft[]>([]);
  const [publishIntents, setPublishIntents] = useState<PublishIntent[]>([]);
  const [recordsByIntentId, setRecordsByIntentId] = useState<Record<number, PublicationRecord[]>>({});
  const [metricsByRecordId, setMetricsByRecordId] = useState<Record<number, PublicationMetricSnapshot[]>>({});
  const [summariesByRecordId, setSummariesByRecordId] = useState<Record<number, PublicationMetricReviewSummary[]>>({});
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState<PublishingAction | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function reloadPublishingWorkflow() {
    setLoading(true);
    try {
      const [drafts, intents] = await Promise.all([getReviewDrafts(projectId), getPublishIntents(projectId)]);
      const recordEntries = await Promise.all(
        intents.map(async (intent) => [intent.id, await getPublicationRecords(projectId, intent.id)] as const),
      );
      const records = recordEntries.flatMap(([, publicationRecords]) => publicationRecords);
      const metricEntries = await Promise.all(
        records.map(async (record) => [record.id, await listPublicationMetrics(projectId, record.id)] as const),
      );
      const summaryEntries = await Promise.all(
        records.map(
          async (record) => [record.id, await listPublicationMetricReviewSummaries(projectId, record.id)] as const,
        ),
      );
      setReviewDrafts(drafts);
      setPublishIntents(intents);
      setRecordsByIntentId(Object.fromEntries(recordEntries));
      setMetricsByRecordId(Object.fromEntries(metricEntries));
      setSummariesByRecordId(Object.fromEntries(summaryEntries));
      setError(null);
    } catch (err) {
      setError(formatPublishingError(err, "加载本地 fake publishing workflow 失败"));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void reloadPublishingWorkflow();
  }, [projectId, refreshKey]);

  async function handleCreate(reviewDraft: ReviewDraft) {
    if (isArchived) {
      return;
    }
    setAction({ type: "create", id: reviewDraft.id });
    setError(null);
    try {
      await createPublishIntent(projectId, {
        review_draft_id: reviewDraft.id,
        target_platform: "fake_local",
        title: reviewDraft.title,
        caption: reviewDraft.draft_summary,
        confirm_publish_intent: true,
      });
      await reloadPublishingWorkflow();
    } catch (err) {
      setError(formatPublishingError(err, "创建 Publish Intent 失败"));
    } finally {
      setAction(null);
    }
  }

  async function handleConfirm(publishIntentId: number) {
    if (isArchived) {
      return;
    }
    setAction({ type: "confirm", id: publishIntentId });
    setError(null);
    try {
      await confirmPublishIntent(projectId, publishIntentId);
      await reloadPublishingWorkflow();
    } catch (err) {
      setError(formatPublishingError(err, "确认 PublishIntent 失败"));
    } finally {
      setAction(null);
    }
  }

  async function handleCancel(publishIntentId: number) {
    if (isArchived) {
      return;
    }
    setAction({ type: "cancel", id: publishIntentId });
    setError(null);
    try {
      await cancelPublishIntent(projectId, publishIntentId);
      await reloadPublishingWorkflow();
    } catch (err) {
      setError(formatPublishingError(err, "取消 PublishIntent 失败"));
    } finally {
      setAction(null);
    }
  }

  async function handleFakePublish(publishIntentId: number) {
    if (isArchived) {
      return;
    }
    setAction({ type: "fake-publish", id: publishIntentId });
    setError(null);
    try {
      await fakePublishIntent(projectId, publishIntentId);
      await reloadPublishingWorkflow();
    } catch (err) {
      setError(formatPublishingError(err, "执行 Fake Publish 失败"));
    } finally {
      setAction(null);
    }
  }

  async function reloadMetricsForRecord(publicationRecordId: number) {
    const metrics = await listPublicationMetrics(projectId, publicationRecordId);
    setMetricsByRecordId((current) => ({ ...current, [publicationRecordId]: metrics }));
  }

  async function reloadSummariesForRecord(publicationRecordId: number) {
    const summaries = await listPublicationMetricReviewSummaries(projectId, publicationRecordId);
    setSummariesByRecordId((current) => ({ ...current, [publicationRecordId]: summaries }));
  }

  async function handleCreateFakeMetrics(publicationRecordId: number) {
    if (isArchived) {
      return;
    }
    setAction({ type: "fake-metrics", id: publicationRecordId });
    setError(null);
    try {
      await createFakePublicationMetric(projectId, publicationRecordId);
      await reloadMetricsForRecord(publicationRecordId);
    } catch (err) {
      setError(formatPublishingError(err, "创建 fake metrics snapshot 失败"));
    } finally {
      setAction(null);
    }
  }

  async function handleCreateFakeMetricReviewSummary(publicationRecordId: number) {
    if (isArchived) {
      return;
    }
    setAction({ type: "fake-review-summary", id: publicationRecordId });
    setError(null);
    try {
      await createFakePublicationMetricReviewSummary(projectId, publicationRecordId);
      await reloadSummariesForRecord(publicationRecordId);
    } catch (err) {
      setError(formatPublishingError(err, "创建 fake/local metrics review summary 失败"));
    } finally {
      setAction(null);
    }
  }

  const approvedDrafts = reviewDrafts.filter((draft) => draft.review_status === "approved");

  return (
    <section className="mt-8">
      <div>
        <h2 className="text-lg font-semibold text-stone-950">Publish Intent Workflow</h2>
        <p className="mt-1 text-sm text-stone-600">
          本区块只记录本地 Publish Intent；不会上传、发布、排期，也不会调用 Douyin。用户点击确认创建后，
          系统只保存安全元数据，`douyin_real` 仍保持禁用。
        </p>
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-100 p-3 text-sm text-stone-700">
          当前项目已归档，只能查看已有 PublishIntent 和 PublicationRecord，不能继续创建、确认、取消或本地 fake action。
        </p>
      )}
      {error && <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {loading && <p className="mt-4 text-sm text-stone-600">正在加载本地 fake publishing workflow...</p>}

      {!loading && (
        <>
          <div className="mt-4 rounded border border-stone-200 bg-white p-4">
            <h3 className="text-sm font-semibold text-stone-950">Approved Review Drafts</h3>
            {approvedDrafts.length === 0 ? (
              <p className="mt-3 rounded border border-dashed border-stone-300 bg-stone-50 p-3 text-sm text-stone-600">
                需要先通过 Review Draft，并由后端通过本地 media preflight，才能创建 Publish Intent。
              </p>
            ) : (
              <div className="mt-3 space-y-3">
                {approvedDrafts.map((draft) => {
                  const hasActiveIntent = publishIntents.some(
                    (intent) => intent.review_draft_id === draft.id && intent.publish_status !== "cancelled",
                  );
                  const creating = action?.type === "create" && action.id === draft.id;
                  return (
                    <div
                      className="flex flex-wrap items-start justify-between gap-3 rounded border border-stone-200 bg-stone-50 p-3"
                      key={draft.id}
                    >
                      <div>
                        <p className="text-sm font-medium text-stone-950">{draft.title}</p>
                        <p className="mt-1 text-xs text-stone-500">ReviewDraft #{draft.id}</p>
                      </div>
                      <button
                        className="rounded border border-teal-700 px-3 py-1 text-xs font-semibold text-teal-800 hover:bg-teal-50 disabled:cursor-not-allowed disabled:opacity-50"
                        disabled={isArchived || hasActiveIntent || action !== null}
                        type="button"
                        onClick={() => handleCreate(draft)}
                      >
                        {hasActiveIntent
                          ? "已有 Publish Intent"
                          : creating
                            ? "创建中..."
                            : "确认创建 Publish Intent"}
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="mt-4">
            <h3 className="text-sm font-semibold text-stone-950">PublishIntents</h3>
            {publishIntents.length === 0 ? (
              <p className="mt-3 rounded border border-dashed border-stone-300 bg-white p-4 text-sm text-stone-600">
                暂无 PublishIntent。
              </p>
            ) : (
              <div className="mt-3 space-y-3">
                {publishIntents.map((intent) => (
                  <PublishIntentCard
                    action={action}
                    isArchived={isArchived}
                    key={intent.id}
                    publishIntent={intent}
                    metricsByRecordId={metricsByRecordId}
                    summariesByRecordId={summariesByRecordId}
                    records={recordsByIntentId[intent.id] ?? []}
                    onCancel={handleCancel}
                    onConfirm={handleConfirm}
                    onFakePublish={handleFakePublish}
                    onGenerateFakeMetrics={handleCreateFakeMetrics}
                    onGenerateFakeMetricReviewSummary={handleCreateFakeMetricReviewSummary}
                  />
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </section>
  );
}

function PublishIntentCard({
  action,
  isArchived,
  onCancel,
  onConfirm,
  onFakePublish,
  onGenerateFakeMetrics,
  onGenerateFakeMetricReviewSummary,
  metricsByRecordId,
  summariesByRecordId,
  publishIntent,
  records,
}: {
  action: PublishingAction | null;
  isArchived: boolean;
  metricsByRecordId: Record<number, PublicationMetricSnapshot[]>;
  summariesByRecordId: Record<number, PublicationMetricReviewSummary[]>;
  onCancel: (publishIntentId: number) => void;
  onConfirm: (publishIntentId: number) => void;
  onFakePublish: (publishIntentId: number) => void;
  onGenerateFakeMetrics: (publicationRecordId: number) => void;
  onGenerateFakeMetricReviewSummary: (publicationRecordId: number) => void;
  publishIntent: PublishIntent;
  records: PublicationRecord[];
}) {
  const pending = publishIntent.publish_status === "pending_confirmation";
  const confirmed = publishIntent.publish_status === "confirmed";
  const notStartedRecord = records.find((record) => record.publication_status === "not_started");
  const canFakePublish = confirmed && Boolean(notStartedRecord);

  return (
    <article
      aria-label={`PublishIntent ${publishIntent.id}`}
      className="rounded border border-stone-200 bg-white p-4"
      data-status={publishIntent.publish_status}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h4 className="text-base font-semibold text-stone-950">{publishIntent.title}</h4>
          <p className="mt-1 text-xs text-stone-500">PublishIntent #{publishIntent.id}</p>
        </div>
        <span className={getPublishStatusClass(publishIntent.publish_status)}>
          {formatStatus(publishIntent.publish_status)}
        </span>
      </div>

      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">ReviewDraft</dt>
          <dd className="mt-1 text-stone-800">#{publishIntent.review_draft_id}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Target platform</dt>
          <dd className="mt-1 text-stone-800">{publishIntent.target_platform}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Source type</dt>
          <dd className="mt-1 text-stone-800">{publishIntent.source_type}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Publish status</dt>
          <dd className="mt-1 text-stone-800">{formatStatus(publishIntent.publish_status)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Confirmation</dt>
          <dd className="mt-1 text-stone-800">{formatStatus(publishIntent.confirmation_status)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">更新时间</dt>
          <dd className="mt-1 text-stone-800">{new Date(publishIntent.updated_at).toLocaleString()}</dd>
        </div>
      </dl>

      <div className="mt-3 text-sm">
        <p className="text-xs font-semibold uppercase text-stone-500">Caption</p>
        <p className="mt-1 whitespace-pre-wrap text-stone-800">{publishIntent.caption}</p>
      </div>
      <p className="mt-3 rounded border border-stone-200 bg-stone-50 p-3 text-sm text-stone-700">
        {publishIntent.safe_status_message}
      </p>

      {!isArchived && pending && (
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            className="rounded border border-teal-700 px-3 py-1 text-xs font-semibold text-teal-800 hover:bg-teal-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={action !== null}
            type="button"
            onClick={() => onConfirm(publishIntent.id)}
          >
            {action?.type === "confirm" && action.id === publishIntent.id ? "确认中..." : "确认 PublishIntent"}
          </button>
          <button
            className="rounded border border-red-700 px-3 py-1 text-xs font-semibold text-red-800 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={action !== null}
            type="button"
            onClick={() => onCancel(publishIntent.id)}
          >
            {action?.type === "cancel" && action.id === publishIntent.id ? "取消中..." : "取消 PublishIntent"}
          </button>
        </div>
      )}

      {!isArchived && canFakePublish && (
        <button
          className="mt-4 rounded bg-teal-700 px-4 py-2 text-sm font-medium text-white hover:bg-teal-800 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={action !== null}
          type="button"
          onClick={() => onFakePublish(publishIntent.id)}
        >
          {action?.type === "fake-publish" && action.id === publishIntent.id ? "Fake Publishing..." : "Fake Publish"}
        </button>
      )}

      {confirmed && records.length === 0 && (
        <p className="mt-4 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          已确认本地 Publish Intent，但尚未执行任何 provider publish；Batch 6 不自动创建发布执行记录。
        </p>
      )}

      <div className="mt-4">
        <h5 className="text-xs font-semibold uppercase text-stone-500">PublicationRecords</h5>
        {records.length === 0 ? (
          <p className="mt-3 rounded border border-dashed border-stone-300 bg-white p-3 text-sm text-stone-600">
            No publication records yet.
          </p>
        ) : (
          <div className="mt-3 space-y-2">
            {records.map((record) => (
              <PublicationRecordItem
                action={action}
                isArchived={isArchived}
                key={record.id}
                metrics={metricsByRecordId[record.id] ?? []}
                summaries={summariesByRecordId[record.id] ?? []}
                record={record}
                onGenerateFakeMetrics={onGenerateFakeMetrics}
                onGenerateFakeMetricReviewSummary={onGenerateFakeMetricReviewSummary}
              />
            ))}
          </div>
        )}
      </div>
    </article>
  );
}

function PublicationRecordItem({
  action,
  isArchived,
  metrics,
  summaries,
  onGenerateFakeMetrics,
  onGenerateFakeMetricReviewSummary,
  record,
}: {
  action: PublishingAction | null;
  isArchived: boolean;
  metrics: PublicationMetricSnapshot[];
  summaries: PublicationMetricReviewSummary[];
  onGenerateFakeMetrics: (publicationRecordId: number) => void;
  onGenerateFakeMetricReviewSummary: (publicationRecordId: number) => void;
  record: PublicationRecord;
}) {
  const generatingMetrics = action?.type === "fake-metrics" && action.id === record.id;
  const generatingSummary = action?.type === "fake-review-summary" && action.id === record.id;

  return (
    <div
      aria-label={`PublicationRecord ${record.id}`}
      className="rounded border border-stone-200 bg-stone-50 p-3"
      data-status={record.publication_status}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm font-medium text-stone-950">PublicationRecord #{record.id}</p>
        <span className={getPublicationStatusClass(record.publication_status)}>
          {formatStatus(record.publication_status)}
        </span>
      </div>
      <dl className="mt-3 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Provider</dt>
          <dd className="mt-1 text-stone-800">{record.provider_name}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">External publication id</dt>
          <dd className="mt-1 break-all text-stone-800">{record.external_publication_id ?? "无"}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Target platform</dt>
          <dd className="mt-1 text-stone-800">{record.target_platform}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">更新时间</dt>
          <dd className="mt-1 text-stone-800">{new Date(record.updated_at).toLocaleString()}</dd>
        </div>
      </dl>
      {record.error_message && <p className="mt-3 text-sm text-red-700">{record.error_message}</p>}
      {record.publication_status === "succeeded" && (
        <p className="mt-3 rounded border border-teal-200 bg-teal-50 p-3 text-sm text-teal-800">
          Fake execution succeeded. Not a real platform publication.
        </p>
      )}
      <PublicationMetricsList
        isArchived={isArchived}
        isDisabled={action !== null}
        isGenerating={generatingMetrics}
        metrics={metrics}
        onGenerateFakeMetrics={() => onGenerateFakeMetrics(record.id)}
      />
      <PublicationMetricReviewSummariesList
        isArchived={isArchived}
        isDisabled={action !== null}
        isGenerating={generatingSummary}
        summaries={summaries}
        onGenerateFakeSummary={() => onGenerateFakeMetricReviewSummary(record.id)}
      />
    </div>
  );
}

function getPublishStatusClass(status: PublishIntent["publish_status"]) {
  if (status === "confirmed") {
    return "rounded border border-teal-300 bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-800";
  }
  if (status === "cancelled" || status === "blocked") {
    return "rounded border border-red-300 bg-red-50 px-3 py-1 text-xs font-semibold text-red-800";
  }
  return "rounded border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800";
}

function getPublicationStatusClass(status: PublicationRecord["publication_status"]) {
  if (status === "succeeded") {
    return "rounded border border-teal-300 bg-white px-3 py-1 text-xs font-semibold text-teal-800";
  }
  if (status === "failed") {
    return "rounded border border-red-300 bg-white px-3 py-1 text-xs font-semibold text-red-800";
  }
  return "rounded border border-amber-300 bg-white px-3 py-1 text-xs font-semibold text-amber-800";
}

function formatPublishingError(err: unknown, fallback: string) {
  const message = err instanceof Error ? err.message : fallback;
  if (message.startsWith("archived project")) {
    return "当前项目已归档，只能查看，不能继续修改。";
  }
  if (message.includes("(404)") || message.includes("not found")) {
    return message;
  }
  return message || fallback;
}
