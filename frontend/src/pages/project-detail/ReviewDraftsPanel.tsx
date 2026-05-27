import { useEffect, useState } from "react";

import { approveReviewDraft, getReviewDrafts, rejectReviewDraft, ReviewDraft } from "../../api/client";
import { formatStatus } from "./formatting";

export function ReviewDraftsPanel({
  isArchived,
  onReviewDraftsChanged,
  projectId,
  refreshKey,
}: {
  isArchived: boolean;
  onReviewDraftsChanged?: () => void;
  projectId: number;
  refreshKey: number;
}) {
  const [reviewDrafts, setReviewDrafts] = useState<ReviewDraft[]>([]);
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState<{ draftId: number; type: "approve" | "reject" } | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function reloadReviewDrafts() {
    setLoading(true);
    try {
      const items = await getReviewDrafts(projectId);
      setReviewDrafts(items);
      setError(null);
    } catch (err) {
      setError(formatReviewDraftError(err, "加载待审核草稿失败"));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void reloadReviewDrafts();
  }, [projectId, refreshKey]);

  async function handleApprove(reviewDraftId: number) {
    if (isArchived) {
      return;
    }
    setAction({ draftId: reviewDraftId, type: "approve" });
    setError(null);
    try {
      await approveReviewDraft(projectId, reviewDraftId);
      await reloadReviewDrafts();
      onReviewDraftsChanged?.();
    } catch (err) {
      setError(formatReviewDraftError(err, "通过待审核草稿失败"));
    } finally {
      setAction(null);
    }
  }

  async function handleReject(reviewDraftId: number) {
    if (isArchived) {
      return;
    }
    setAction({ draftId: reviewDraftId, type: "reject" });
    setError(null);
    try {
      await rejectReviewDraft(projectId, reviewDraftId);
      await reloadReviewDrafts();
      onReviewDraftsChanged?.();
    } catch (err) {
      setError(formatReviewDraftError(err, "拒绝待审核草稿失败"));
    } finally {
      setAction(null);
    }
  }

  return (
    <section className="mt-8">
      <div>
        <h2 className="text-lg font-semibold text-stone-950">待审核草稿</h2>
        <p className="mt-1 text-sm text-stone-600">
          展示 fake manual GenerationRun 创建的 review draft placeholder。
        </p>
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-100 p-3 text-sm text-stone-700">
          当前项目已归档，只能查看待审核草稿，不能继续审核操作。
        </p>
      )}
      {error && <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {loading && <p className="mt-4 text-sm text-stone-600">正在加载待审核草稿...</p>}
      {!loading && reviewDrafts.length === 0 && (
        <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-4 text-sm text-stone-600">
          暂无待审核草稿。
        </p>
      )}
      {!loading && reviewDrafts.length > 0 && (
        <div className="mt-4 space-y-3">
          {reviewDrafts.map((reviewDraft) => (
            <ReviewDraftCard
              action={action}
              isArchived={isArchived}
              key={reviewDraft.id}
              reviewDraft={reviewDraft}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          ))}
        </div>
      )}
    </section>
  );
}

function ReviewDraftCard({
  action,
  isArchived,
  onApprove,
  onReject,
  reviewDraft,
}: {
  action: { draftId: number; type: "approve" | "reject" } | null;
  isArchived: boolean;
  onApprove: (reviewDraftId: number) => void;
  onReject: (reviewDraftId: number) => void;
  reviewDraft: ReviewDraft;
}) {
  const actionInProgress = action?.draftId === reviewDraft.id;
  const disableActions = action !== null;
  const approveDisabled = disableActions || reviewDraft.review_status === "approved";
  const rejectDisabled = disableActions || reviewDraft.review_status === "rejected";

  return (
    <article
      aria-label={`待审核草稿：${reviewDraft.title}`}
      className="rounded border border-stone-200 bg-white p-4"
      data-status={reviewDraft.review_status}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{reviewDraft.title}</h3>
          <p className="mt-1 text-xs text-stone-500">创建于 {new Date(reviewDraft.created_at).toLocaleString()}</p>
        </div>
        <span className={getReviewDraftStatusClass(reviewDraft.review_status)}>
          {formatStatus(reviewDraft.review_status)}
        </span>
      </div>

      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">审核状态</dt>
          <dd className="mt-1 text-stone-800">{formatStatus(reviewDraft.review_status)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">GenerationRun</dt>
          <dd className="mt-1 text-stone-800">#{reviewDraft.generation_run_id}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">GenerationSchedule</dt>
          <dd className="mt-1 text-stone-800">
            {reviewDraft.generation_schedule_id ? `#${reviewDraft.generation_schedule_id}` : "手动运行 / 无计划"}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">更新时间</dt>
          <dd className="mt-1 text-stone-800">{new Date(reviewDraft.updated_at).toLocaleString()}</dd>
        </div>
      </dl>

      <div className="mt-3 text-sm">
        <p className="text-xs font-semibold uppercase text-stone-500">草稿摘要</p>
        <p className="mt-1 whitespace-pre-wrap text-stone-800">{reviewDraft.draft_summary}</p>
      </div>
      <div className="mt-3 text-sm">
        <p className="text-xs font-semibold uppercase text-stone-500">输入来源</p>
        <p className="mt-1 whitespace-pre-wrap text-stone-800">{reviewDraft.input_source_summary}</p>
      </div>
      <div className="mt-3 text-sm">
        <p className="text-xs font-semibold uppercase text-stone-500">热点来源</p>
        <p className="mt-1 whitespace-pre-wrap text-stone-800">
          {reviewDraft.hotspot_source_summary || "未启用热点来源 / 无热点来源"}
        </p>
      </div>

      {!isArchived && (
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            className="rounded border border-teal-700 px-3 py-1 text-xs font-semibold text-teal-800 hover:bg-teal-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={approveDisabled}
            type="button"
            onClick={() => onApprove(reviewDraft.id)}
          >
            {actionInProgress && action?.type === "approve" ? "通过中..." : "通过"}
          </button>
          <button
            className="rounded border border-red-700 px-3 py-1 text-xs font-semibold text-red-800 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={rejectDisabled}
            type="button"
            onClick={() => onReject(reviewDraft.id)}
          >
            {actionInProgress && action?.type === "reject" ? "拒绝中..." : "拒绝"}
          </button>
        </div>
      )}
    </article>
  );
}

function getReviewDraftStatusClass(status: ReviewDraft["review_status"]) {
  if (status === "approved") {
    return "rounded border border-teal-300 bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-800";
  }
  if (status === "rejected") {
    return "rounded border border-red-300 bg-red-50 px-3 py-1 text-xs font-semibold text-red-800";
  }
  return "rounded border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800";
}

function formatReviewDraftError(err: unknown, fallback: string) {
  const message = err instanceof Error ? err.message : fallback;
  if (message.startsWith("archived project")) {
    return "当前项目已归档，只能查看，不能继续修改。";
  }
  if (message.includes("(404)") || message.includes("not found")) {
    return message;
  }
  return message || fallback;
}
