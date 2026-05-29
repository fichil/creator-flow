import { useEffect, useState } from "react";

import {
  cancelPublishIntent,
  createFakePublicationMetricReviewSummary,
  confirmPublishIntent,
  createFakePublicationMetric,
  createPublishMetricsSnapshot,
  createPublishAttempt,
  createPublishIntent,
  createPublishStatusReconciliation,
  fakePublishIntent,
  getPublishAttempts,
  getPublishMetricsSnapshots,
  getPublishStatusReconciliations,
  getPublishStatusSnapshots,
  getPublicationRecords,
  getPublishIntents,
  getReviewDrafts,
  listPublicationMetrics,
  listPublicationMetricReviewSummaries,
  PublicationMetricReviewSummary,
  PublicationMetricSnapshot,
  PublicationRecord,
  PublishAttempt,
  PublishIntent,
  PublishMetricsSnapshot,
  PublishStatusReconciliation,
  PublishStatusSnapshot,
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
  | { type: "attempt"; id: number }
  | { type: "limited-metrics"; id: string }
  | { type: "reconcile-status"; id: number }
  | { type: "confirm"; id: number }
  | { type: "cancel"; id: number }
  | { type: "fake-publish"; id: number }
  | { type: "fake-metrics"; id: number }
  | { type: "fake-review-summary"; id: number };

export function ProjectPublishingSection({ isArchived, projectId, refreshKey }: ProjectPublishingSectionProps) {
  const [reviewDrafts, setReviewDrafts] = useState<ReviewDraft[]>([]);
  const [publishIntents, setPublishIntents] = useState<PublishIntent[]>([]);
  const [attemptsByIntentId, setAttemptsByIntentId] = useState<Record<number, PublishAttempt[]>>({});
  const [reconciliationsByAttemptId, setReconciliationsByAttemptId] = useState<
    Record<number, PublishStatusReconciliation[]>
  >({});
  const [snapshotsByAttemptId, setSnapshotsByAttemptId] = useState<Record<number, PublishStatusSnapshot[]>>({});
  const [limitedMetricsByStatusSnapshotId, setLimitedMetricsByStatusSnapshotId] = useState<
    Record<string, PublishMetricsSnapshot[]>
  >({});
  const [recordsByIntentId, setRecordsByIntentId] = useState<Record<number, PublicationRecord[]>>({});
  const [metricsByRecordId, setMetricsByRecordId] = useState<Record<number, PublicationMetricSnapshot[]>>({});
  const [summariesByRecordId, setSummariesByRecordId] = useState<Record<number, PublicationMetricReviewSummary[]>>({});
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState<PublishingAction | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function reloadPublishingWorkflow() {
    setLoading(true);
    try {
      const [drafts, intents, attempts, reconciliations, limitedMetricsSnapshots] = await Promise.all([
        getReviewDrafts(projectId),
        getPublishIntents(projectId),
        getPublishAttempts(projectId),
        getPublishStatusReconciliations(projectId),
        getPublishMetricsSnapshots(projectId),
      ]);
      const snapshotEntries = await Promise.all(
        attempts.map(async (attempt) => [attempt.id, await getPublishStatusSnapshots(projectId, attempt.id)] as const),
      );
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
      setAttemptsByIntentId(groupAttemptsByIntent(attempts));
      setReconciliationsByAttemptId(groupReconciliationsByAttempt(reconciliations));
      setSnapshotsByAttemptId(Object.fromEntries(snapshotEntries));
      setLimitedMetricsByStatusSnapshotId(groupLimitedMetricsByStatusSnapshot(limitedMetricsSnapshots));
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

  async function handleCreateAttempt(publishIntentId: number) {
    if (isArchived) {
      return;
    }
    setAction({ type: "attempt", id: publishIntentId });
    setError(null);
    try {
      await createPublishAttempt(projectId, publishIntentId);
      await reloadPublishingWorkflow();
    } catch (err) {
      setError(formatPublishingError(err, "Create guarded publish attempt failed"));
    } finally {
      setAction(null);
    }
  }

  async function handleCreateStatusReconciliation(publishAttemptId: number) {
    if (isArchived) {
      return;
    }
    setAction({ type: "reconcile-status", id: publishAttemptId });
    setError(null);
    try {
      await createPublishStatusReconciliation(projectId, publishAttemptId);
      await reloadPublishingWorkflow();
    } catch (err) {
      setError(formatPublishingError(err, "Create local status reconciliation failed"));
    } finally {
      setAction(null);
    }
  }

  async function handleCreateLimitedMetricsSnapshot(statusSnapshotId: string) {
    if (isArchived) {
      return;
    }
    setAction({ type: "limited-metrics", id: statusSnapshotId });
    setError(null);
    try {
      await createPublishMetricsSnapshot(projectId, statusSnapshotId);
      await reloadPublishingWorkflow();
    } catch (err) {
      setError(formatPublishingError(err, "Create local limited metrics snapshot failed"));
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
                    attempts={attemptsByIntentId[intent.id] ?? []}
                    reconciliationsByAttemptId={reconciliationsByAttemptId}
                    limitedMetricsByStatusSnapshotId={limitedMetricsByStatusSnapshotId}
                    snapshotsByAttemptId={snapshotsByAttemptId}
                    onCancel={handleCancel}
                    onConfirm={handleConfirm}
                    onCreateAttempt={handleCreateAttempt}
                    onCreateStatusReconciliation={handleCreateStatusReconciliation}
                    onCreateLimitedMetricsSnapshot={handleCreateLimitedMetricsSnapshot}
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
  attempts,
  isArchived,
  onCancel,
  onConfirm,
  onCreateAttempt,
  onCreateStatusReconciliation,
  onCreateLimitedMetricsSnapshot,
  onFakePublish,
  onGenerateFakeMetrics,
  onGenerateFakeMetricReviewSummary,
  metricsByRecordId,
  limitedMetricsByStatusSnapshotId,
  reconciliationsByAttemptId,
  summariesByRecordId,
  publishIntent,
  records,
  snapshotsByAttemptId,
}: {
  action: PublishingAction | null;
  attempts: PublishAttempt[];
  isArchived: boolean;
  metricsByRecordId: Record<number, PublicationMetricSnapshot[]>;
  limitedMetricsByStatusSnapshotId: Record<string, PublishMetricsSnapshot[]>;
  reconciliationsByAttemptId: Record<number, PublishStatusReconciliation[]>;
  summariesByRecordId: Record<number, PublicationMetricReviewSummary[]>;
  snapshotsByAttemptId: Record<number, PublishStatusSnapshot[]>;
  onCancel: (publishIntentId: number) => void;
  onConfirm: (publishIntentId: number) => void;
  onCreateAttempt: (publishIntentId: number) => void;
  onCreateStatusReconciliation: (publishAttemptId: number) => void;
  onCreateLimitedMetricsSnapshot: (statusSnapshotId: string) => void;
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
  const hasActiveAttempt = attempts.some((attempt) => attempt.attempt_status === "created");
  const canCreateAttempt = confirmed && !hasActiveAttempt;

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

      {confirmed && (
        <div className="mt-4 rounded border border-sky-200 bg-sky-50 p-3">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h5 className="text-xs font-semibold uppercase text-sky-900">Guarded Publish Attempt</h5>
              <p className="mt-1 text-sm text-sky-900">
                Local guarded attempt only. External publish is blocked by default and the UI does not open OAuth URLs.
              </p>
            </div>
            {!isArchived && canCreateAttempt && (
              <button
                className="rounded border border-sky-700 px-3 py-1 text-xs font-semibold text-sky-900 hover:bg-sky-100 disabled:cursor-not-allowed disabled:opacity-50"
                disabled={action !== null}
                type="button"
                onClick={() => onCreateAttempt(publishIntent.id)}
              >
                {action?.type === "attempt" && action.id === publishIntent.id
                  ? "Creating guarded attempt..."
                  : "Create guarded local attempt"}
              </button>
            )}
          </div>
          {hasActiveAttempt && (
            <p className="mt-3 rounded border border-sky-200 bg-white p-2 text-sm text-sky-900">
              Duplicate guarded attempts are blocked for this active Publish Intent.
            </p>
          )}
          {attempts.length === 0 ? (
            <p className="mt-3 text-sm text-sky-900">No guarded publish attempts yet.</p>
          ) : (
            <div className="mt-3 space-y-2">
              {attempts.map((attempt) => (
                <PublishAttemptItem
                  action={action}
                  attempt={attempt}
                  isArchived={isArchived}
                  key={attempt.id}
                  reconciliations={reconciliationsByAttemptId[attempt.id] ?? []}
                  snapshots={snapshotsByAttemptId[attempt.id] ?? []}
                  limitedMetricsByStatusSnapshotId={limitedMetricsByStatusSnapshotId}
                  onCreateLimitedMetricsSnapshot={onCreateLimitedMetricsSnapshot}
                  onCreateStatusReconciliation={onCreateStatusReconciliation}
                />
              ))}
            </div>
          )}
        </div>
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

function PublishAttemptItem({
  action,
  attempt,
  isArchived,
  onCreateStatusReconciliation,
  onCreateLimitedMetricsSnapshot,
  reconciliations,
  limitedMetricsByStatusSnapshotId,
  snapshots,
}: {
  action: PublishingAction | null;
  attempt: PublishAttempt;
  isArchived: boolean;
  limitedMetricsByStatusSnapshotId: Record<string, PublishMetricsSnapshot[]>;
  onCreateLimitedMetricsSnapshot: (statusSnapshotId: string) => void;
  onCreateStatusReconciliation: (publishAttemptId: number) => void;
  reconciliations: PublishStatusReconciliation[];
  snapshots: PublishStatusSnapshot[];
}) {
  const hasActiveReconciliation = reconciliations.some(
    (reconciliation) => reconciliation.reconciliation_status === "created",
  );
  const hasExternalQueryBlocked = reconciliations.some(
    (reconciliation) => reconciliation.external_query_status === "blocked",
  );
  const hasStaleIgnored = reconciliations.some(
    (reconciliation) =>
      reconciliation.result_category === "stale_status_ignored" ||
      reconciliation.last_status_change_reason === "stale_status_ignored",
  );
  const canCreateReconciliation = attempt.attempt_status === "created" && !hasActiveReconciliation;

  return (
    <div
      aria-label={`PublishAttempt ${attempt.id}`}
      className="rounded border border-sky-200 bg-white p-3"
      data-status={attempt.attempt_status}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm font-medium text-sky-950">PublishAttempt #{attempt.id}</p>
        <span className={getPublishAttemptStatusClass(attempt.attempt_status)}>
          {formatStatus(attempt.attempt_status)}
        </span>
      </div>
      <dl className="mt-3 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-sky-700">Provider</dt>
          <dd className="mt-1 text-sky-950">{attempt.provider_id}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-sky-700">Source type</dt>
          <dd className="mt-1 text-sky-950">{attempt.source_type}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-sky-700">Guard</dt>
          <dd className="mt-1 text-sky-950">{formatStatus(attempt.guard_status)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-sky-700">External call</dt>
          <dd className="mt-1 text-sky-950">{formatStatus(attempt.external_call_status)}</dd>
        </div>
      </dl>
      <p className="mt-3 rounded border border-sky-100 bg-sky-50 p-2 text-sm text-sky-900">
        {attempt.safe_status_message}
      </p>
      <div className="mt-3 rounded border border-emerald-200 bg-emerald-50 p-3">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h6 className="text-xs font-semibold uppercase text-emerald-950">Local Status Reconciliation</h6>
            <p className="mt-1 text-sm text-emerald-950">
              Local status only. This is not real Douyin status and does not fetch metrics.
            </p>
          </div>
          {!isArchived && canCreateReconciliation && (
            <button
              className="rounded border border-emerald-700 px-3 py-1 text-xs font-semibold text-emerald-950 hover:bg-emerald-100 disabled:cursor-not-allowed disabled:opacity-50"
              disabled={action !== null}
              type="button"
              onClick={() => onCreateStatusReconciliation(attempt.id)}
            >
              {action?.type === "reconcile-status" && action.id === attempt.id
                ? "Creating local status reconciliation..."
                : "Create local status reconciliation"}
            </button>
          )}
        </div>
        {attempt.provider_id === "douyin_real" && (
          <p className="mt-3 rounded border border-amber-200 bg-amber-50 p-2 text-sm text-amber-900">
            Real provider disabled. douyin_real status reconciliation does not fallback to douyin_sandbox.
          </p>
        )}
        {hasActiveReconciliation && (
          <p className="mt-3 rounded border border-emerald-200 bg-white p-2 text-sm text-emerald-950">
            Duplicate reconciliation requests are blocked for this active PublishAttempt.
          </p>
        )}
        {hasExternalQueryBlocked && (
          <p className="mt-3 rounded border border-amber-200 bg-amber-50 p-2 text-sm text-amber-900">
            External status query blocked. No real Douyin status was fetched.
          </p>
        )}
        {hasStaleIgnored && (
          <p className="mt-3 rounded border border-stone-200 bg-white p-2 text-sm text-stone-800">
            Stale status ignored safely; the newer local snapshot remains in place.
          </p>
        )}
        {reconciliations.length === 0 ? (
          <p className="mt-3 text-sm text-emerald-950">No local status reconciliations yet.</p>
        ) : (
          <div className="mt-3 space-y-2">
            {reconciliations.map((reconciliation) => (
              <PublishStatusReconciliationItem
                key={reconciliation.reconciliation_id}
                reconciliation={reconciliation}
              />
            ))}
          </div>
        )}
        <div className="mt-3">
          <h6 className="text-xs font-semibold uppercase text-emerald-950">Publish Status Snapshot</h6>
          {snapshots.length === 0 ? (
            <p className="mt-2 text-sm text-emerald-950">
              No local status snapshots yet. Limited metrics snapshot action requires an existing Publish Status
              Snapshot.
            </p>
          ) : (
            <div className="mt-2 space-y-2">
              {snapshots.map((snapshot) => (
                <PublishStatusSnapshotItem
                  action={action}
                  isArchived={isArchived}
                  key={snapshot.status_snapshot_id}
                  limitedMetrics={limitedMetricsByStatusSnapshotId[snapshot.status_snapshot_id] ?? []}
                  snapshot={snapshot}
                  onCreateLimitedMetricsSnapshot={onCreateLimitedMetricsSnapshot}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function PublishStatusReconciliationItem({
  reconciliation,
}: {
  reconciliation: PublishStatusReconciliation;
}) {
  return (
    <div
      aria-label={`PublishStatusReconciliation ${reconciliation.reconciliation_id}`}
      className="rounded border border-emerald-200 bg-white p-3"
      data-status={reconciliation.reconciliation_status}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="break-all text-sm font-medium text-emerald-950">
          Reconciliation {reconciliation.reconciliation_id}
        </p>
        <span className={getReconciliationStatusClass(reconciliation.reconciliation_status)}>
          {formatStatus(reconciliation.reconciliation_status)}
        </span>
      </div>
      <dl className="mt-3 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-emerald-700">Local status</dt>
          <dd className="mt-1 text-emerald-950">{formatStatus(reconciliation.local_publish_status)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-emerald-700">External query</dt>
          <dd className="mt-1 text-emerald-950">{formatStatus(reconciliation.external_query_status)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-emerald-700">Result</dt>
          <dd className="mt-1 text-emerald-950">
            {reconciliation.result_category ? formatStatus(reconciliation.result_category) : "metadata only"}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-emerald-700">Updated</dt>
          <dd className="mt-1 text-emerald-950">{new Date(reconciliation.updated_at).toLocaleString()}</dd>
        </div>
      </dl>
      <p className="mt-3 rounded border border-emerald-100 bg-emerald-50 p-2 text-sm text-emerald-950">
        {reconciliation.safe_status_message}
      </p>
    </div>
  );
}

function PublishStatusSnapshotItem({
  action,
  isArchived,
  limitedMetrics,
  onCreateLimitedMetricsSnapshot,
  snapshot,
}: {
  action: PublishingAction | null;
  isArchived: boolean;
  limitedMetrics: PublishMetricsSnapshot[];
  onCreateLimitedMetricsSnapshot: (statusSnapshotId: string) => void;
  snapshot: PublishStatusSnapshot;
}) {
  const canCreateLimitedMetrics = snapshot.local_publish_status === "local_status_reconciled";
  const hasExternalMetricsBlocked = limitedMetrics.some((metric) => metric.external_query_status === "blocked");
  const hasPermissionMissing = limitedMetrics.some(
    (metric) =>
      metric.result_category === "metrics_permission_missing" ||
      metric.last_status_change_reason === "metrics_permission_missing",
  );
  const hasMalformedFixture = limitedMetrics.some(
    (metric) =>
      metric.result_category === "metrics_fixture_invalid" ||
      metric.last_status_change_reason === "metrics_fixture_invalid",
  );

  return (
    <div
      aria-label={`PublishStatusSnapshot ${snapshot.status_snapshot_id}`}
      className="rounded border border-emerald-200 bg-white p-3"
      data-status={snapshot.local_publish_status}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="break-all text-sm font-medium text-emerald-950">
          Snapshot {snapshot.status_snapshot_id}
        </p>
        <span className={getSnapshotStatusClass(snapshot.local_publish_status)}>
          {formatStatus(snapshot.local_publish_status)}
        </span>
      </div>
      <dl className="mt-3 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-emerald-700">Status source</dt>
          <dd className="mt-1 text-emerald-950">{formatStatus(snapshot.status_source)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-emerald-700">Observed</dt>
          <dd className="mt-1 text-emerald-950">{new Date(snapshot.status_observed_at).toLocaleString()}</dd>
        </div>
      </dl>
      <p className="mt-3 rounded border border-emerald-100 bg-emerald-50 p-2 text-sm text-emerald-950">
        {snapshot.safe_status_message}
      </p>
      <div className="mt-3 rounded border border-indigo-200 bg-indigo-50 p-3">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h6 className="text-xs font-semibold uppercase text-indigo-950">Limited Metrics Snapshot</h6>
            <p className="mt-1 text-sm text-indigo-950">
              Local / fake or sandbox-safe metrics only. These are not real Douyin metrics and do not validate real
              performance.
            </p>
            <p className="mt-1 text-xs text-indigo-900">
              Metrics permission / platform limitation: visible as safe metadata; real platform permission is not used
              in this local foundation.
            </p>
          </div>
          {!isArchived && canCreateLimitedMetrics && (
            <button
              className="rounded border border-indigo-700 px-3 py-1 text-xs font-semibold text-indigo-950 hover:bg-indigo-100 disabled:cursor-not-allowed disabled:opacity-50"
              disabled={action !== null}
              type="button"
              onClick={() => onCreateLimitedMetricsSnapshot(snapshot.status_snapshot_id)}
            >
              {action?.type === "limited-metrics" && action.id === snapshot.status_snapshot_id
                ? "Creating local limited metrics..."
                : "Create local limited metrics snapshot"}
            </button>
          )}
        </div>
        {!canCreateLimitedMetrics && (
          <p className="mt-3 rounded border border-amber-200 bg-amber-50 p-2 text-sm text-amber-900">
            Publish status is not eligible for limited metrics foundation yet.
          </p>
        )}
        {snapshot.provider_id === "douyin_real" && (
          <p className="mt-3 rounded border border-amber-200 bg-amber-50 p-2 text-sm text-amber-900">
            Real provider disabled. douyin_real metrics read does not fallback to douyin_sandbox.
          </p>
        )}
        {hasExternalMetricsBlocked && (
          <p className="mt-3 rounded border border-amber-200 bg-amber-50 p-2 text-sm text-amber-900">
            External metrics query blocked. No real Douyin metrics query ran.
          </p>
        )}
        {hasPermissionMissing && (
          <p className="mt-3 rounded border border-amber-200 bg-amber-50 p-2 text-sm text-amber-900">
            Metrics permission missing. The UI keeps this as a safe local limitation.
          </p>
        )}
        {hasMalformedFixture && (
          <p className="mt-3 rounded border border-red-200 bg-red-50 p-2 text-sm text-red-800">
            Metrics fixture invalid. Raw provider or metrics responses are not shown.
          </p>
        )}
        {limitedMetrics.length === 0 ? (
          <p className="mt-3 text-sm text-indigo-950">No limited metrics snapshots yet.</p>
        ) : (
          <div className="mt-3 space-y-2">
            {limitedMetrics.map((metric) => (
              <PublishMetricsSnapshotItem key={metric.metrics_snapshot_id} metric={metric} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function PublishMetricsSnapshotItem({ metric }: { metric: PublishMetricsSnapshot }) {
  return (
    <div
      aria-label={`PublishMetricsSnapshot ${metric.metrics_snapshot_id}`}
      className="rounded border border-indigo-200 bg-white p-3"
      data-status={metric.metrics_freshness_status}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="break-all text-sm font-medium text-indigo-950">Metrics {metric.metrics_snapshot_id}</p>
        <span className={getMetricsFreshnessClass(metric.metrics_freshness_status)}>
          {formatStatus(metric.metrics_freshness_status)}
        </span>
      </div>
      <dl className="mt-3 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-indigo-700">Metrics source</dt>
          <dd className="mt-1 text-indigo-950">{formatStatus(metric.metrics_source)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-indigo-700">Freshness</dt>
          <dd className="mt-1 text-indigo-950">{formatStatus(metric.metrics_freshness_status)}</dd>
        </div>
        <MetricValue label="Views" value={metric.views_count} />
        <MetricValue label="Likes" value={metric.likes_count} />
        <MetricValue label="Comments" value={metric.comments_count} />
        <MetricValue label="Shares" value={metric.shares_count} />
        <MetricValue label="Favorites" value={metric.favorites_count} />
        <MetricValue
          label="Completion"
          value={metric.completion_rate_basis_points === null ? null : `${metric.completion_rate_basis_points} bp`}
        />
        <div>
          <dt className="text-xs font-semibold uppercase text-indigo-700">Observed</dt>
          <dd className="mt-1 text-indigo-950">
            {metric.metrics_observed_at ? new Date(metric.metrics_observed_at).toLocaleString() : "unknown"}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-indigo-700">External query</dt>
          <dd className="mt-1 text-indigo-950">{formatStatus(metric.external_query_status)}</dd>
        </div>
      </dl>
      <p className="mt-3 rounded border border-indigo-100 bg-indigo-50 p-2 text-sm text-indigo-950">
        {metric.safe_status_message}
      </p>
    </div>
  );
}

function MetricValue({ label, value }: { label: string; value: number | string | null }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-indigo-700">{label}</dt>
      <dd className="mt-1 text-indigo-950">{value === null ? "not available" : value}</dd>
    </div>
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

function getPublishAttemptStatusClass(status: PublishAttempt["attempt_status"]) {
  if (status === "created") {
    return "rounded border border-sky-300 bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-900";
  }
  if (status === "blocked" || status === "failed_safe") {
    return "rounded border border-red-300 bg-red-50 px-3 py-1 text-xs font-semibold text-red-800";
  }
  return "rounded border border-stone-300 bg-stone-50 px-3 py-1 text-xs font-semibold text-stone-800";
}

function getReconciliationStatusClass(status: PublishStatusReconciliation["reconciliation_status"]) {
  if (status === "created" || status === "completed_safe") {
    return "rounded border border-emerald-300 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-900";
  }
  if (status === "blocked" || status === "failed_safe") {
    return "rounded border border-red-300 bg-red-50 px-3 py-1 text-xs font-semibold text-red-800";
  }
  return "rounded border border-stone-300 bg-stone-50 px-3 py-1 text-xs font-semibold text-stone-800";
}

function getSnapshotStatusClass(status: PublishStatusSnapshot["local_publish_status"]) {
  if (status === "local_status_reconciled" || status === "local_attempt_created") {
    return "rounded border border-emerald-300 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-900";
  }
  if (status === "local_blocked" || status === "local_failed_safe" || status === "local_cancelled") {
    return "rounded border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-900";
  }
  return "rounded border border-stone-300 bg-stone-50 px-3 py-1 text-xs font-semibold text-stone-800";
}

function getMetricsFreshnessClass(status: PublishMetricsSnapshot["metrics_freshness_status"]) {
  if (status === "fresh") {
    return "rounded border border-indigo-300 bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-900";
  }
  if (status === "stale" || status === "unknown") {
    return "rounded border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-900";
  }
  return "rounded border border-stone-300 bg-stone-50 px-3 py-1 text-xs font-semibold text-stone-800";
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

function groupAttemptsByIntent(attempts: PublishAttempt[]) {
  return attempts.reduce<Record<number, PublishAttempt[]>>((grouped, attempt) => {
    grouped[attempt.publish_intent_id] = [...(grouped[attempt.publish_intent_id] ?? []), attempt];
    return grouped;
  }, {});
}

function groupReconciliationsByAttempt(reconciliations: PublishStatusReconciliation[]) {
  return reconciliations.reduce<Record<number, PublishStatusReconciliation[]>>((grouped, reconciliation) => {
    grouped[reconciliation.publish_attempt_id] = [
      ...(grouped[reconciliation.publish_attempt_id] ?? []),
      reconciliation,
    ];
    return grouped;
  }, {});
}

function groupLimitedMetricsByStatusSnapshot(metrics: PublishMetricsSnapshot[]) {
  return metrics.reduce<Record<string, PublishMetricsSnapshot[]>>((grouped, metric) => {
    grouped[metric.status_snapshot_id] = [...(grouped[metric.status_snapshot_id] ?? []), metric];
    return grouped;
  }, {});
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
