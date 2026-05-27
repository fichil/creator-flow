import { FormEvent, useEffect, useState } from "react";

import {
  addFileMaterial,
  addLinkMaterial,
  addTextMaterial,
  archiveProject,
  approveReviewDraft,
  ContentPlan,
  createContentPlan,
  createGenerationRun,
  createGenerationSchedule,
  createRenderJob,
  createSubtitleDraft,
  disableContentPlan,
  disableGenerationSchedule,
  enableContentPlan,
  enableGenerationSchedule,
  generateScriptDrafts,
  generateStoryboards,
  generateTopicCandidates,
  GenerationRun,
  GenerationSchedule,
  getContentPlans,
  getGenerationRuns,
  getGenerationSchedules,
  getProject,
  getRenderJobs,
  getReviewDrafts,
  getScriptDrafts,
  getStoryboards,
  getSubtitleDrafts,
  getTopicCandidates,
  Material,
  ProjectDetail,
  RenderJob,
  rejectReviewDraft,
  ReviewDraft,
  ScriptDraft,
  selectScriptDraft,
  selectStoryboard,
  selectSubtitleDraft,
  selectTopicCandidate,
  Storyboard,
  SubtitleDraft,
  TopicCandidate,
  updateProject,
} from "../api/client";
import { EmptyState } from "../components/EmptyState";
import { StatusBadge } from "../components/StatusBadge";

type ProjectDetailPageProps = {
  projectId: number;
  onBack: () => void;
};

type TextMaterialType = "text" | "summary" | "project_record";
type FileMaterialType = "image" | "screenshot";

const materialLabels: Record<string, string> = {
  text: "文本",
  summary: "摘要",
  project_record: "项目记录",
  link: "链接",
  image: "图片",
  screenshot: "截图",
};

const statusLabels: Record<string, string> = {
  candidate: "候选",
  draft: "草稿",
  selected: "已选择",
  dismissed: "已忽略",
  queued: "排队中",
  running: "运行中",
  succeeded: "成功",
  failed: "失败",
  pending_review: "待审核",
  approved: "已通过",
  rejected: "已拒绝",
};

function formatStatus(status: string) {
  return statusLabels[status] ?? status;
}

function formatSourceMaterialIds(ids: number[]) {
  return ids.length > 0 ? ids.join(", ") : "无";
}

export function ProjectDetailPage({ projectId, onBack }: ProjectDetailPageProps) {
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasSelectedStoryboard, setHasSelectedStoryboard] = useState<boolean | null>(null);
  const [reviewDraftRefreshKey, setReviewDraftRefreshKey] = useState(0);
  const isArchived = project?.status === "archived";

  async function reload() {
    setLoading(true);
    try {
      const detail = await getProject(projectId);
      setProject(detail);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    setHasSelectedStoryboard(null);
    setReviewDraftRefreshKey(0);
    void reload();
  }, [projectId]);

  return (
    <section className="mx-auto max-w-6xl px-4 py-8">
      <button className="text-sm font-medium text-stone-600 hover:text-stone-950" onClick={onBack} type="button">
        返回项目列表
      </button>

      {loading && <p className="mt-8 text-sm text-stone-600">正在加载项目...</p>}
      {error && <p className="mt-8 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}

      {project && !loading && (
        <>
          <div className="mt-4 flex flex-wrap items-start justify-between gap-4 border-b border-stone-200 pb-6">
            <div>
              <h1 className="text-2xl font-semibold text-stone-950">{project.title}</h1>
              {project.description && <p className="mt-2 max-w-3xl text-sm text-stone-600">{project.description}</p>}
              <p className="mt-3 text-xs text-stone-500">创建于 {new Date(project.created_at).toLocaleString()}</p>
            </div>
            <StatusBadge status={project.status} />
          </div>

          <div className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
            <div>
              <h2 className="text-lg font-semibold text-stone-950">素材列表</h2>
              {isArchived && (
                <p className="mt-3 rounded border border-stone-200 bg-stone-100 p-3 text-sm text-stone-700">
                  归档项目不能继续添加素材。
                </p>
              )}
              {project.materials.length === 0 ? (
                <div className="mt-4">
                  <EmptyState title="还没有素材" description="添加文本、链接、图片或截图后，项目状态会变为素材已就绪。" />
                </div>
              ) : (
                <div className="mt-4 space-y-3">
                  {project.materials.map((material) => (
                    <MaterialItem material={material} key={material.id} />
                  ))}
                </div>
              )}
              <ContentPlansPanel
                isArchived={isArchived}
                projectId={project.id}
                onGenerationRunCreated={() => setReviewDraftRefreshKey((value) => value + 1)}
              />
              <TopicCandidatesPanel isArchived={isArchived} projectId={project.id} />
              <ScriptDraftsPanel isArchived={isArchived} projectId={project.id} />
              <StoryboardsPanel
                isArchived={isArchived}
                projectId={project.id}
                onSelectionStateChange={setHasSelectedStoryboard}
              />
              <ReviewDraftsPanel
                isArchived={isArchived}
                projectId={project.id}
                refreshKey={reviewDraftRefreshKey}
              />
              <SubtitleDraftsPanel
                hasSelectedStoryboard={hasSelectedStoryboard}
                isArchived={isArchived}
                projectId={project.id}
              />
              <RenderJobsPanel
                hasSelectedStoryboard={hasSelectedStoryboard}
                isArchived={isArchived}
                projectId={project.id}
              />
            </div>

            <div className="space-y-4">
              <ProjectEditForm project={project} onUpdated={reload} />
              <ArchiveProjectPanel project={project} onArchived={reload} />
              <TextMaterialForm disabled={isArchived} projectId={project.id} onAdded={reload} />
              <LinkMaterialForm disabled={isArchived} projectId={project.id} onAdded={reload} />
              <FileMaterialForm disabled={isArchived} projectId={project.id} onAdded={reload} />
            </div>
          </div>
        </>
      )}
    </section>
  );
}

function ContentPlansPanel({
  isArchived,
  onGenerationRunCreated,
  projectId,
}: {
  isArchived: boolean;
  onGenerationRunCreated: () => void;
  projectId: number;
}) {
  const [contentPlans, setContentPlans] = useState<ContentPlan[]>([]);
  const [generationSchedules, setGenerationSchedules] = useState<GenerationSchedule[]>([]);
  const [generationRuns, setGenerationRuns] = useState<GenerationRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [planActionId, setPlanActionId] = useState<number | null>(null);
  const [scheduleActionId, setScheduleActionId] = useState<number | null>(null);
  const [runningKey, setRunningKey] = useState<string | null>(null);

  async function reloadPlanningData() {
    setLoading(true);
    try {
      const [plans, schedules, runs] = await Promise.all([
        getContentPlans(projectId),
        getGenerationSchedules(projectId),
        getGenerationRuns(projectId),
      ]);
      setContentPlans(plans);
      setGenerationSchedules(schedules);
      setGenerationRuns(runs);
      setError(null);
    } catch (err) {
      setError(formatPlanningError(err, "加载内容计划失败"));
    } finally {
      setLoading(false);
    }
  }

  async function reloadAfterMutation() {
    const [plans, schedules, runs] = await Promise.all([
      getContentPlans(projectId),
      getGenerationSchedules(projectId),
      getGenerationRuns(projectId),
    ]);
    setContentPlans(plans);
    setGenerationSchedules(schedules);
    setGenerationRuns(runs);
  }

  useEffect(() => {
    void reloadPlanningData();
  }, [projectId]);

  async function handleCreateContentPlan(payload: {
    name: string;
    account_positioning: string;
    content_type: string;
    target_frequency_per_week: number;
    preferences?: string | null;
  }) {
    if (isArchived) {
      return;
    }
    setError(null);
    try {
      await createContentPlan(projectId, payload);
      await reloadAfterMutation();
    } catch (err) {
      setError(formatPlanningError(err, "创建内容计划失败"));
      throw err;
    }
  }

  async function handleToggleContentPlan(contentPlan: ContentPlan) {
    if (isArchived) {
      return;
    }
    setPlanActionId(contentPlan.id);
    setError(null);
    try {
      if (contentPlan.is_enabled) {
        await disableContentPlan(projectId, contentPlan.id);
      } else {
        await enableContentPlan(projectId, contentPlan.id);
      }
      await reloadAfterMutation();
    } catch (err) {
      setError(formatPlanningError(err, "更新内容计划状态失败"));
    } finally {
      setPlanActionId(null);
    }
  }

  async function handleCreateGenerationSchedule(
    contentPlanId: number,
    payload: {
      frequency_per_week?: number | null;
      timezone: string;
      preferred_days?: string | null;
      preferred_time: string;
    },
  ) {
    if (isArchived) {
      return;
    }
    setError(null);
    try {
      await createGenerationSchedule(projectId, contentPlanId, payload);
      await reloadAfterMutation();
    } catch (err) {
      setError(formatPlanningError(err, "创建生成计划失败"));
      throw err;
    }
  }

  async function handleToggleGenerationSchedule(generationSchedule: GenerationSchedule) {
    if (isArchived) {
      return;
    }
    setScheduleActionId(generationSchedule.id);
    setError(null);
    try {
      if (generationSchedule.is_enabled) {
        await disableGenerationSchedule(projectId, generationSchedule.id);
      } else {
        await enableGenerationSchedule(projectId, generationSchedule.id);
      }
      await reloadAfterMutation();
    } catch (err) {
      setError(formatPlanningError(err, "更新生成计划状态失败"));
    } finally {
      setScheduleActionId(null);
    }
  }

  async function handleCreateManualRun(contentPlanId: number, generationScheduleId?: number) {
    if (isArchived) {
      return;
    }
    const actionKey = `${contentPlanId}:${generationScheduleId ?? "manual"}`;
    setRunningKey(actionKey);
    setError(null);
    try {
      await createGenerationRun(
        projectId,
        contentPlanId,
        generationScheduleId ? { generation_schedule_id: generationScheduleId } : {},
      );
      await reloadAfterMutation();
      onGenerationRunCreated();
    } catch (err) {
      setError(formatPlanningError(err, "创建手动生成运行失败"));
    } finally {
      setRunningKey(null);
    }
  }

  return (
    <section className="mt-8">
      <div>
        <h2 className="text-lg font-semibold text-stone-950">内容计划</h2>
        <p className="mt-1 text-sm text-stone-600">
          本地配置 ContentPlan、GenerationSchedule，并手动触发 fake GenerationRun。
        </p>
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-100 p-3 text-sm text-stone-700">
          当前项目已归档，只能查看内容计划、生成计划和生成运行，不能继续修改或触发。
        </p>
      )}
      {error && <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {!isArchived && <ContentPlanCreateForm onCreate={handleCreateContentPlan} />}
      {loading && <p className="mt-4 text-sm text-stone-600">正在加载内容计划...</p>}
      {!loading && contentPlans.length === 0 && (
        <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-4 text-sm text-stone-600">
          暂无内容计划。
        </p>
      )}
      {!loading && contentPlans.length > 0 && (
        <div className="mt-4 space-y-3">
          {contentPlans.map((contentPlan) => (
            <ContentPlanCard
              contentPlan={contentPlan}
              generationRuns={generationRuns.filter((run) => run.content_plan_id === contentPlan.id)}
              generationSchedules={generationSchedules.filter((schedule) => schedule.content_plan_id === contentPlan.id)}
              isArchived={isArchived}
              key={contentPlan.id}
              planActionId={planActionId}
              runningKey={runningKey}
              scheduleActionId={scheduleActionId}
              onCreateGenerationSchedule={handleCreateGenerationSchedule}
              onCreateManualRun={handleCreateManualRun}
              onToggleContentPlan={handleToggleContentPlan}
              onToggleGenerationSchedule={handleToggleGenerationSchedule}
            />
          ))}
        </div>
      )}
    </section>
  );
}

function ContentPlanCreateForm({
  onCreate,
}: {
  onCreate: (payload: {
    name: string;
    account_positioning: string;
    content_type: string;
    target_frequency_per_week: number;
    preferences?: string | null;
  }) => Promise<void>;
}) {
  const [name, setName] = useState("");
  const [accountPositioning, setAccountPositioning] = useState("");
  const [contentType, setContentType] = useState("");
  const [targetFrequency, setTargetFrequency] = useState("3");
  const [preferences, setPreferences] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await onCreate({
        name,
        account_positioning: accountPositioning,
        content_type: contentType,
        target_frequency_per_week: Number(targetFrequency),
        preferences: preferences || null,
      });
      setName("");
      setAccountPositioning("");
      setContentType("");
      setTargetFrequency("3");
      setPreferences("");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="mt-4 rounded border border-stone-200 bg-white p-4" onSubmit={submit}>
      <h3 className="text-sm font-semibold text-stone-950">创建内容计划</h3>
      <div className="mt-3 grid gap-3 md:grid-cols-2">
        <label className="text-sm text-stone-700">
          计划名称
          <input
            className="mt-1 w-full rounded border border-stone-300 px-3 py-2 text-sm"
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
        </label>
        <label className="text-sm text-stone-700">
          内容类型
          <input
            className="mt-1 w-full rounded border border-stone-300 px-3 py-2 text-sm"
            required
            value={contentType}
            onChange={(event) => setContentType(event.target.value)}
          />
        </label>
        <label className="text-sm text-stone-700">
          每周目标频率
          <input
            className="mt-1 w-full rounded border border-stone-300 px-3 py-2 text-sm"
            max={14}
            min={1}
            required
            type="number"
            value={targetFrequency}
            onChange={(event) => setTargetFrequency(event.target.value)}
          />
        </label>
        <label className="text-sm text-stone-700">
          账号定位
          <input
            className="mt-1 w-full rounded border border-stone-300 px-3 py-2 text-sm"
            required
            value={accountPositioning}
            onChange={(event) => setAccountPositioning(event.target.value)}
          />
        </label>
      </div>
      <label className="mt-3 block text-sm text-stone-700">
        内容偏好
        <textarea
          className="mt-1 min-h-20 w-full rounded border border-stone-300 px-3 py-2 text-sm"
          value={preferences}
          onChange={(event) => setPreferences(event.target.value)}
        />
      </label>
      <button
        className="mt-3 rounded bg-stone-950 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800 disabled:cursor-not-allowed disabled:opacity-50"
        disabled={submitting}
        type="submit"
      >
        {submitting ? "创建中..." : "创建内容计划"}
      </button>
    </form>
  );
}

function ContentPlanCard({
  contentPlan,
  generationRuns,
  generationSchedules,
  isArchived,
  onCreateGenerationSchedule,
  onCreateManualRun,
  onToggleContentPlan,
  onToggleGenerationSchedule,
  planActionId,
  runningKey,
  scheduleActionId,
}: {
  contentPlan: ContentPlan;
  generationRuns: GenerationRun[];
  generationSchedules: GenerationSchedule[];
  isArchived: boolean;
  onCreateGenerationSchedule: (
    contentPlanId: number,
    payload: {
      frequency_per_week?: number | null;
      timezone: string;
      preferred_days?: string | null;
      preferred_time: string;
    },
  ) => Promise<void>;
  onCreateManualRun: (contentPlanId: number, generationScheduleId?: number) => void;
  onToggleContentPlan: (contentPlan: ContentPlan) => void;
  onToggleGenerationSchedule: (generationSchedule: GenerationSchedule) => void;
  planActionId: number | null;
  runningKey: string | null;
  scheduleActionId: number | null;
}) {
  const manualRunKey = `${contentPlan.id}:manual`;
  const togglingPlan = planActionId === contentPlan.id;

  return (
    <article
      aria-label={`内容计划：${contentPlan.name}`}
      className="rounded border border-stone-200 bg-white p-4"
      data-enabled={contentPlan.is_enabled}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{contentPlan.name}</h3>
          <p className="mt-1 text-xs text-stone-500">创建于 {new Date(contentPlan.created_at).toLocaleString()}</p>
        </div>
        <span className={contentPlan.is_enabled ? "rounded bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-800" : "rounded bg-stone-100 px-3 py-1 text-xs font-semibold text-stone-700"}>
          {contentPlan.is_enabled ? "已启用" : "已停用"}
        </span>
      </div>

      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">账号定位</dt>
          <dd className="mt-1 text-stone-800">{contentPlan.account_positioning}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">内容类型</dt>
          <dd className="mt-1 text-stone-800">{contentPlan.content_type}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">目标频率</dt>
          <dd className="mt-1 text-stone-800">每周 {contentPlan.target_frequency_per_week} 次</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">更新时间</dt>
          <dd className="mt-1 text-stone-800">{new Date(contentPlan.updated_at).toLocaleString()}</dd>
        </div>
      </dl>
      <div className="mt-3 text-sm">
        <p className="text-xs font-semibold uppercase text-stone-500">内容偏好</p>
        <p className="mt-1 whitespace-pre-wrap text-stone-800">{contentPlan.preferences || "暂无内容偏好。"}</p>
      </div>

      {!isArchived && (
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            className="rounded border border-stone-300 px-3 py-1 text-xs font-semibold text-stone-800 hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={togglingPlan}
            type="button"
            onClick={() => onToggleContentPlan(contentPlan)}
          >
            {togglingPlan ? "更新中..." : contentPlan.is_enabled ? "停用计划" : "启用计划"}
          </button>
          <button
            className="rounded border border-teal-700 px-3 py-1 text-xs font-semibold text-teal-800 hover:bg-teal-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={runningKey !== null}
            type="button"
            onClick={() => onCreateManualRun(contentPlan.id)}
          >
            {runningKey === manualRunKey ? "创建中..." : "手动生成"}
          </button>
        </div>
      )}

      <div className="mt-5 border-t border-stone-200 pt-4">
        <h4 className="text-sm font-semibold text-stone-950">生成计划</h4>
        {!isArchived && (
          <GenerationScheduleCreateForm
            contentPlanId={contentPlan.id}
            onCreate={onCreateGenerationSchedule}
          />
        )}
        {generationSchedules.length === 0 ? (
          <p className="mt-3 rounded border border-dashed border-stone-300 bg-white p-3 text-sm text-stone-600">
            暂无生成计划。
          </p>
        ) : (
          <div className="mt-3 divide-y divide-stone-200 border-y border-stone-200">
            {generationSchedules.map((generationSchedule) => (
              <GenerationScheduleItem
                generationSchedule={generationSchedule}
                isArchived={isArchived}
                key={generationSchedule.id}
                runningKey={runningKey}
                scheduleActionId={scheduleActionId}
                onCreateManualRun={onCreateManualRun}
                onToggleGenerationSchedule={onToggleGenerationSchedule}
              />
            ))}
          </div>
        )}
      </div>

      <div className="mt-5 border-t border-stone-200 pt-4">
        <h4 className="text-sm font-semibold text-stone-950">GenerationRuns</h4>
        {generationRuns.length === 0 ? (
          <p className="mt-3 rounded border border-dashed border-stone-300 bg-white p-3 text-sm text-stone-600">
            暂无 GenerationRun。
          </p>
        ) : (
          <div className="mt-3 divide-y divide-stone-200 border-y border-stone-200">
            {generationRuns.map((generationRun) => (
              <GenerationRunItem generationRun={generationRun} key={generationRun.id} />
            ))}
          </div>
        )}
      </div>
    </article>
  );
}

function GenerationScheduleCreateForm({
  contentPlanId,
  onCreate,
}: {
  contentPlanId: number;
  onCreate: (
    contentPlanId: number,
    payload: {
      frequency_per_week?: number | null;
      timezone: string;
      preferred_days?: string | null;
      preferred_time: string;
    },
  ) => Promise<void>;
}) {
  const [frequency, setFrequency] = useState("");
  const [timezone, setTimezone] = useState("Asia/Shanghai");
  const [preferredDays, setPreferredDays] = useState("");
  const [preferredTime, setPreferredTime] = useState("09:00");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await onCreate(contentPlanId, {
        frequency_per_week: frequency ? Number(frequency) : null,
        timezone,
        preferred_days: preferredDays || null,
        preferred_time: preferredTime,
      });
      setFrequency("");
      setTimezone("Asia/Shanghai");
      setPreferredDays("");
      setPreferredTime("09:00");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="mt-3 grid gap-3 md:grid-cols-4" onSubmit={submit}>
      <label className="text-sm text-stone-700">
        计划频率
        <input
          className="mt-1 w-full rounded border border-stone-300 px-3 py-2 text-sm"
          max={14}
          min={1}
          placeholder="继承"
          type="number"
          value={frequency}
          onChange={(event) => setFrequency(event.target.value)}
        />
      </label>
      <label className="text-sm text-stone-700">
        时区
        <input
          className="mt-1 w-full rounded border border-stone-300 px-3 py-2 text-sm"
          required
          value={timezone}
          onChange={(event) => setTimezone(event.target.value)}
        />
      </label>
      <label className="text-sm text-stone-700">
        偏好日期
        <input
          className="mt-1 w-full rounded border border-stone-300 px-3 py-2 text-sm"
          placeholder="Mon,Wed,Fri"
          value={preferredDays}
          onChange={(event) => setPreferredDays(event.target.value)}
        />
      </label>
      <label className="text-sm text-stone-700">
        偏好时间
        <input
          className="mt-1 w-full rounded border border-stone-300 px-3 py-2 text-sm"
          required
          type="time"
          value={preferredTime}
          onChange={(event) => setPreferredTime(event.target.value)}
        />
      </label>
      <div className="md:col-span-4">
        <button
          className="rounded border border-sky-700 px-3 py-2 text-xs font-semibold text-sky-800 hover:bg-sky-50 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={submitting}
          type="submit"
        >
          {submitting ? "创建中..." : "创建生成计划"}
        </button>
      </div>
    </form>
  );
}

function GenerationScheduleItem({
  generationSchedule,
  isArchived,
  onCreateManualRun,
  onToggleGenerationSchedule,
  runningKey,
  scheduleActionId,
}: {
  generationSchedule: GenerationSchedule;
  isArchived: boolean;
  onCreateManualRun: (contentPlanId: number, generationScheduleId?: number) => void;
  onToggleGenerationSchedule: (generationSchedule: GenerationSchedule) => void;
  runningKey: string | null;
  scheduleActionId: number | null;
}) {
  const scheduleRunKey = `${generationSchedule.content_plan_id}:${generationSchedule.id}`;
  const togglingSchedule = scheduleActionId === generationSchedule.id;

  return (
    <div aria-label={`生成计划 ${generationSchedule.id}`} className="py-3" data-enabled={generationSchedule.is_enabled}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-stone-950">GenerationSchedule #{generationSchedule.id}</p>
          <p className="mt-1 text-xs text-stone-500">更新于 {new Date(generationSchedule.updated_at).toLocaleString()}</p>
        </div>
        <span className={generationSchedule.is_enabled ? "rounded bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-800" : "rounded bg-stone-100 px-3 py-1 text-xs font-semibold text-stone-700"}>
          {generationSchedule.is_enabled ? "已启用" : "已停用"}
        </span>
      </div>
      <dl className="mt-3 grid gap-3 text-sm md:grid-cols-4">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">频率</dt>
          <dd className="mt-1 text-stone-800">每周 {generationSchedule.frequency_per_week} 次</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">时区</dt>
          <dd className="mt-1 text-stone-800">{generationSchedule.timezone}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">偏好日期</dt>
          <dd className="mt-1 text-stone-800">{generationSchedule.preferred_days || "未设置"}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">偏好时间</dt>
          <dd className="mt-1 text-stone-800">{generationSchedule.preferred_time}</dd>
        </div>
      </dl>
      {!isArchived && (
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            className="rounded border border-stone-300 px-3 py-1 text-xs font-semibold text-stone-800 hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={togglingSchedule}
            type="button"
            onClick={() => onToggleGenerationSchedule(generationSchedule)}
          >
            {togglingSchedule ? "更新中..." : generationSchedule.is_enabled ? "停用生成计划" : "启用生成计划"}
          </button>
          <button
            className="rounded border border-teal-700 px-3 py-1 text-xs font-semibold text-teal-800 hover:bg-teal-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={runningKey !== null}
            type="button"
            onClick={() => onCreateManualRun(generationSchedule.content_plan_id, generationSchedule.id)}
          >
            {runningKey === scheduleRunKey ? "创建中..." : "按此计划手动生成"}
          </button>
        </div>
      )}
    </div>
  );
}

function GenerationRunItem({ generationRun }: { generationRun: GenerationRun }) {
  return (
    <div aria-label={`GenerationRun ${generationRun.id}`} className="py-3" data-status={generationRun.status}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-stone-950">GenerationRun #{generationRun.id}</p>
          <p className="mt-1 text-xs text-stone-500">创建于 {new Date(generationRun.created_at).toLocaleString()}</p>
        </div>
        <span className="rounded bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-800">
          {formatStatus(generationRun.status)}
        </span>
      </div>
      <dl className="mt-3 grid gap-3 text-sm md:grid-cols-3">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">触发方式</dt>
          <dd className="mt-1 text-stone-800">{generationRun.trigger_type === "manual" ? "手动" : generationRun.trigger_type}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">GenerationSchedule</dt>
          <dd className="mt-1 text-stone-800">
            {generationRun.generation_schedule_id ? `#${generationRun.generation_schedule_id}` : "手动运行 / 无计划"}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">更新时间</dt>
          <dd className="mt-1 text-stone-800">{new Date(generationRun.updated_at).toLocaleString()}</dd>
        </div>
      </dl>
      <p className="mt-3 whitespace-pre-wrap text-sm text-stone-700">{generationRun.input_summary}</p>
      {generationRun.result_summary && (
        <p className="mt-2 whitespace-pre-wrap text-sm text-stone-700">{generationRun.result_summary}</p>
      )}
      {generationRun.error_message && <p className="mt-2 text-sm text-red-700">{generationRun.error_message}</p>}
    </div>
  );
}

function formatPlanningError(err: unknown, fallback: string) {
  const message = err instanceof Error ? err.message : fallback;
  if (message.startsWith("archived project")) {
    return "当前项目已归档，只能查看，不能继续修改。";
  }
  return message || fallback;
}

function TopicCandidatesPanel({ isArchived, projectId }: { isArchived: boolean; projectId: number }) {
  const [candidates, setCandidates] = useState<TopicCandidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectingId, setSelectingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function reloadCandidates() {
    setLoading(true);
    try {
      const items = await getTopicCandidates(projectId);
      setCandidates(items);
      setError(null);
    } catch (err) {
      setError(formatTopicCandidateError(err, "加载候选选题失败"));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void reloadCandidates();
  }, [projectId]);

  async function handleGenerate() {
    if (isArchived) {
      return;
    }
    setGenerating(true);
    setError(null);
    try {
      await generateTopicCandidates(projectId);
      await reloadCandidates();
    } catch (err) {
      setError(formatTopicCandidateError(err, "生成候选选题失败"));
    } finally {
      setGenerating(false);
    }
  }

  async function handleSelect(candidateId: number) {
    if (isArchived) {
      return;
    }
    setSelectingId(candidateId);
    setError(null);
    try {
      await selectTopicCandidate(projectId, candidateId);
      await reloadCandidates();
    } catch (err) {
      setError(formatTopicCandidateError(err, "选择候选选题失败"));
    } finally {
      setSelectingId(null);
    }
  }

  return (
    <section className="mt-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-stone-950">选题候选</h2>
          <p className="mt-1 text-sm text-stone-600">基于已显式导入素材生成的模拟选题候选。</p>
        </div>
        <button
          className="rounded bg-teal-700 px-4 py-2 text-sm font-medium text-white hover:bg-teal-800 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={isArchived || generating}
          type="button"
          onClick={handleGenerate}
        >
          {generating ? "生成中..." : "生成选题候选"}
        </button>
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-100 p-3 text-sm text-stone-700">
          当前项目已归档，只能查看，不能继续修改。
        </p>
      )}
      {error && <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {loading && <p className="mt-4 text-sm text-stone-600">正在加载候选选题...</p>}
      {!loading && candidates.length === 0 && (
        <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-4 text-sm text-stone-600">
          暂无选题候选。
        </p>
      )}
      {!loading && candidates.length > 0 && (
        <div className="mt-4 space-y-3">
          {candidates.map((candidate) => (
            <TopicCandidateCard
              candidate={candidate}
              disabled={isArchived || selectingId !== null}
              key={candidate.id}
              selecting={selectingId === candidate.id}
              onSelect={handleSelect}
            />
          ))}
        </div>
      )}
    </section>
  );
}

function TopicCandidateCard({
  candidate,
  disabled,
  onSelect,
  selecting,
}: {
  candidate: TopicCandidate;
  disabled: boolean;
  onSelect: (candidateId: number) => void;
  selecting: boolean;
}) {
  const isSelected = candidate.status === "selected";
  return (
    <article
      aria-label={`选题候选：${candidate.title}`}
      className={`rounded border bg-white p-4 ${
        isSelected ? "border-teal-300 bg-teal-50 ring-1 ring-teal-200" : "border-stone-200"
      }`}
      data-status={candidate.status}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{candidate.title}</h3>
          <p className="mt-1 text-xs text-stone-500">创建于 {new Date(candidate.created_at).toLocaleString()}</p>
        </div>
        {isSelected ? (
          <span className="rounded border border-teal-300 bg-white px-3 py-1 text-xs font-semibold text-teal-800">
            已选择
          </span>
        ) : (
          <button
            className="rounded border border-teal-700 px-3 py-1 text-xs font-semibold text-teal-800 hover:bg-teal-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={disabled}
            type="button"
            onClick={() => onSelect(candidate.id)}
          >
            {selecting ? "选择中..." : "选择"}
          </button>
        )}
      </div>
      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">角度</dt>
          <dd className="mt-1 text-stone-800">{candidate.angle}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">目标受众</dt>
          <dd className="mt-1 text-stone-800">{candidate.audience}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">开场钩子</dt>
          <dd className="mt-1 text-stone-800">{candidate.hook}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">状态</dt>
          <dd className="mt-1 text-stone-800">{formatStatus(candidate.status)}</dd>
        </div>
      </dl>
      <div className="mt-3 text-sm">
        <p className="text-xs font-semibold uppercase text-stone-500">生成理由</p>
        <p className="mt-1 text-stone-800">{candidate.rationale}</p>
      </div>
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-stone-500">
        <span>来源素材：{formatSourceMaterialIds(candidate.source_material_ids)}</span>
        {candidate.selected_at && <span>选择于 {new Date(candidate.selected_at).toLocaleString()}</span>}
      </div>
    </article>
  );
}

function formatTopicCandidateError(err: unknown, fallback: string) {
  const message = err instanceof Error ? err.message : fallback;
  if (message === "project has no materials") {
    return "请先添加至少一个素材，再生成选题候选。";
  }
  if (message.startsWith("archived project")) {
    return "当前项目已归档，只能查看，不能继续修改。";
  }
  if (message.includes("(404)") || message.includes("not found")) {
    return message;
  }
  return fallback;
}

function ScriptDraftsPanel({ isArchived, projectId }: { isArchived: boolean; projectId: number }) {
  const [scriptDrafts, setScriptDrafts] = useState<ScriptDraft[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectingId, setSelectingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function reloadScriptDrafts() {
    setLoading(true);
    try {
      const items = await getScriptDrafts(projectId);
      setScriptDrafts(items);
      setError(null);
    } catch (err) {
      setError(formatScriptDraftError(err, "加载脚本草稿失败"));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void reloadScriptDrafts();
  }, [projectId]);

  async function handleGenerate() {
    if (isArchived) {
      return;
    }
    setGenerating(true);
    setError(null);
    try {
      await generateScriptDrafts(projectId);
      await reloadScriptDrafts();
    } catch (err) {
      setError(formatScriptDraftError(err, "生成脚本草稿失败"));
    } finally {
      setGenerating(false);
    }
  }

  async function handleSelect(scriptDraftId: number) {
    if (isArchived) {
      return;
    }
    setSelectingId(scriptDraftId);
    setError(null);
    try {
      await selectScriptDraft(projectId, scriptDraftId);
      await reloadScriptDrafts();
    } catch (err) {
      setError(formatScriptDraftError(err, "选择脚本草稿失败"));
    } finally {
      setSelectingId(null);
    }
  }

  return (
    <section className="mt-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-stone-950">脚本草稿</h2>
          <p className="mt-1 text-sm text-stone-600">基于已选选题和显式导入素材生成的模拟脚本草稿。</p>
        </div>
        <button
          className="rounded bg-indigo-700 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-800 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={isArchived || generating}
          type="button"
          onClick={handleGenerate}
        >
          {generating ? "生成中..." : "生成脚本草稿"}
        </button>
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-100 p-3 text-sm text-stone-700">
          当前项目已归档，只能查看，不能继续修改。
        </p>
      )}
      {error && <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {loading && <p className="mt-4 text-sm text-stone-600">正在加载脚本草稿...</p>}
      {!loading && scriptDrafts.length === 0 && (
        <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-4 text-sm text-stone-600">
          暂无脚本草稿。
        </p>
      )}
      {!loading && scriptDrafts.length > 0 && (
        <div className="mt-4 space-y-3">
          {scriptDrafts.map((scriptDraft) => (
            <ScriptDraftCard
              disabled={isArchived || selectingId !== null}
              key={scriptDraft.id}
              scriptDraft={scriptDraft}
              selecting={selectingId === scriptDraft.id}
              onSelect={handleSelect}
            />
          ))}
        </div>
      )}
    </section>
  );
}

function ScriptDraftCard({
  disabled,
  onSelect,
  scriptDraft,
  selecting,
}: {
  disabled: boolean;
  onSelect: (scriptDraftId: number) => void;
  scriptDraft: ScriptDraft;
  selecting: boolean;
}) {
  const isSelected = scriptDraft.status === "selected";
  return (
    <article
      aria-label={`脚本草稿：${scriptDraft.title}`}
      className={`rounded border bg-white p-4 ${
        isSelected ? "border-indigo-300 bg-indigo-50 ring-1 ring-indigo-200" : "border-stone-200"
      }`}
      data-status={scriptDraft.status}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{scriptDraft.title}</h3>
          <p className="mt-1 text-xs text-stone-500">创建于 {new Date(scriptDraft.created_at).toLocaleString()}</p>
        </div>
        {isSelected ? (
          <span className="rounded border border-indigo-300 bg-white px-3 py-1 text-xs font-semibold text-indigo-800">
            已选择
          </span>
        ) : scriptDraft.status === "draft" ? (
          <button
            className="rounded border border-indigo-700 px-3 py-1 text-xs font-semibold text-indigo-800 hover:bg-indigo-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={disabled}
            type="button"
            onClick={() => onSelect(scriptDraft.id)}
          >
            {selecting ? "选择中..." : "选择"}
          </button>
        ) : null}
      </div>
      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">开场钩子</dt>
          <dd className="mt-1 text-stone-800">{scriptDraft.opening_hook}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">行动引导</dt>
          <dd className="mt-1 text-stone-800">{scriptDraft.call_to_action}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">预计时长</dt>
          <dd className="mt-1 text-stone-800">{scriptDraft.estimated_duration_seconds} 秒</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">状态</dt>
          <dd className="mt-1 text-stone-800">{formatStatus(scriptDraft.status)}</dd>
        </div>
      </dl>
      <div className="mt-3 text-sm">
        <p className="text-xs font-semibold uppercase text-stone-500">正文</p>
        <p className="mt-1 whitespace-pre-wrap text-stone-800">{scriptDraft.body}</p>
      </div>
      <div className="mt-3 text-sm">
        <p className="text-xs font-semibold uppercase text-stone-500">生成理由</p>
        <p className="mt-1 text-stone-800">{scriptDraft.rationale}</p>
      </div>
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-stone-500">
        <span>来源素材：{formatSourceMaterialIds(scriptDraft.source_material_ids)}</span>
        {scriptDraft.selected_at && <span>选择于 {new Date(scriptDraft.selected_at).toLocaleString()}</span>}
      </div>
    </article>
  );
}

function formatScriptDraftError(err: unknown, fallback: string) {
  const message = err instanceof Error ? err.message : fallback;
  if (message === "project has no materials") {
    return "请先添加至少一个素材，再生成脚本草稿。";
  }
  if (message === "project has no selected topic candidate") {
    return "请先选择一个选题候选，再生成脚本草稿。";
  }
  if (message.startsWith("archived project")) {
    return "当前项目已归档，只能查看，不能继续修改。";
  }
  if (message.includes("(404)") || message.includes("not found")) {
    return message;
  }
  return fallback;
}

function StoryboardsPanel({
  isArchived,
  onSelectionStateChange,
  projectId,
}: {
  isArchived: boolean;
  onSelectionStateChange: (hasSelectedStoryboard: boolean) => void;
  projectId: number;
}) {
  const [storyboards, setStoryboards] = useState<Storyboard[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectingId, setSelectingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function reloadStoryboards() {
    setLoading(true);
    try {
      const items = await getStoryboards(projectId);
      setStoryboards(items);
      onSelectionStateChange(items.some((storyboard) => storyboard.status === "selected"));
      setError(null);
    } catch (err) {
      setError(formatStoryboardError(err, "加载分镜脚本失败"));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void reloadStoryboards();
  }, [projectId]);

  async function handleGenerate() {
    if (isArchived) {
      return;
    }
    setGenerating(true);
    setError(null);
    try {
      await generateStoryboards(projectId);
      await reloadStoryboards();
    } catch (err) {
      setError(formatStoryboardError(err, "生成分镜脚本失败"));
    } finally {
      setGenerating(false);
    }
  }

  async function handleSelect(storyboardId: number) {
    if (isArchived) {
      return;
    }
    setSelectingId(storyboardId);
    setError(null);
    try {
      await selectStoryboard(projectId, storyboardId);
      await reloadStoryboards();
    } catch (err) {
      setError(formatStoryboardError(err, "选择分镜脚本失败"));
    } finally {
      setSelectingId(null);
    }
  }

  return (
    <section className="mt-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-stone-950">分镜脚本</h2>
          <p className="mt-1 text-sm text-stone-600">
            基于已选选题、已选脚本和显式导入素材生成的模拟分镜脚本。
          </p>
        </div>
        <button
          className="rounded bg-sky-700 px-4 py-2 text-sm font-medium text-white hover:bg-sky-800 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={isArchived || generating}
          type="button"
          onClick={handleGenerate}
        >
          {generating ? "生成中..." : "生成分镜脚本"}
        </button>
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-100 p-3 text-sm text-stone-700">
          当前项目已归档，只能查看，不能继续修改。
        </p>
      )}
      {error && <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {loading && <p className="mt-4 text-sm text-stone-600">正在加载分镜脚本...</p>}
      {!loading && storyboards.length === 0 && (
        <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-4 text-sm text-stone-600">
          暂无分镜脚本。
        </p>
      )}
      {!loading && storyboards.length > 0 && (
        <div className="mt-4 space-y-3">
          {storyboards.map((storyboard) => (
            <StoryboardCard
              disabled={isArchived || selectingId !== null}
              key={storyboard.id}
              storyboard={storyboard}
              selecting={selectingId === storyboard.id}
              onSelect={handleSelect}
            />
          ))}
        </div>
      )}
    </section>
  );
}

function StoryboardCard({
  disabled,
  onSelect,
  selecting,
  storyboard,
}: {
  disabled: boolean;
  onSelect: (storyboardId: number) => void;
  selecting: boolean;
  storyboard: Storyboard;
}) {
  const isSelected = storyboard.status === "selected";
  const scenes = [...storyboard.scenes].sort((left, right) => left.scene_order - right.scene_order || left.id - right.id);

  return (
    <article
      aria-label={`分镜脚本：${storyboard.title}`}
      className={`rounded border bg-white p-4 ${
        isSelected ? "border-sky-300 bg-sky-50 ring-1 ring-sky-200" : "border-stone-200"
      }`}
      data-status={storyboard.status}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{storyboard.title}</h3>
          <p className="mt-1 text-xs text-stone-500">创建于 {new Date(storyboard.created_at).toLocaleString()}</p>
        </div>
        {isSelected ? (
          <span className="rounded border border-sky-300 bg-white px-3 py-1 text-xs font-semibold text-sky-800">
            已选择
          </span>
        ) : storyboard.status === "draft" ? (
          <button
            className="rounded border border-sky-700 px-3 py-1 text-xs font-semibold text-sky-800 hover:bg-sky-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={disabled}
            type="button"
            onClick={() => onSelect(storyboard.id)}
          >
            {selecting ? "选择中..." : "选择"}
          </button>
        ) : null}
      </div>
      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">摘要</dt>
          <dd className="mt-1 text-stone-800">{storyboard.summary}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">视觉风格</dt>
          <dd className="mt-1 text-stone-800">{storyboard.visual_style}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">状态</dt>
          <dd className="mt-1 text-stone-800">{formatStatus(storyboard.status)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">来源素材</dt>
          <dd className="mt-1 text-stone-800">{formatSourceMaterialIds(storyboard.source_material_ids)}</dd>
        </div>
      </dl>
      {storyboard.selected_at && (
        <p className="mt-3 text-xs text-stone-500">选择于 {new Date(storyboard.selected_at).toLocaleString()}</p>
      )}

      <div className="mt-4">
        <h4 className="text-xs font-semibold uppercase text-stone-500">场景</h4>
        <ol className="mt-3 divide-y divide-stone-200 border-y border-stone-200">
          {scenes.map((scene) => (
            <li
              aria-label={`场景 ${scene.scene_order}：${scene.scene_title}`}
              className="py-3"
              data-scene-order={scene.scene_order}
              data-testid="storyboard-scene"
              key={scene.id}
            >
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <h5 className="text-sm font-semibold text-stone-950">
                  场景 {scene.scene_order}：{scene.scene_title}
                </h5>
                <span className="text-xs text-stone-500">{scene.estimated_duration_seconds} 秒</span>
              </div>
              <dl className="mt-2 grid gap-2 text-sm md:grid-cols-2">
                <div>
                  <dt className="text-xs font-semibold uppercase text-stone-500">旁白</dt>
                  <dd className="mt-1 text-stone-800">{scene.narration}</dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold uppercase text-stone-500">画面描述</dt>
                  <dd className="mt-1 text-stone-800">{scene.visual_description}</dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold uppercase text-stone-500">屏幕文字</dt>
                  <dd className="mt-1 text-stone-800">{scene.on_screen_text}</dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold uppercase text-stone-500">来源素材</dt>
                  <dd className="mt-1 text-stone-800">{scene.source_material_id ?? "无"}</dd>
                </div>
              </dl>
            </li>
          ))}
        </ol>
      </div>
    </article>
  );
}

function formatStoryboardError(err: unknown, fallback: string) {
  const message = err instanceof Error ? err.message : fallback;
  if (message === "project has no materials") {
    return "请先添加至少一个素材，再生成分镜脚本。";
  }
  if (message === "project has no selected topic candidate") {
    return "请先选择一个选题候选，再生成分镜脚本。";
  }
  if (message === "project has no selected script draft") {
    return "请先选择一个脚本草稿，再生成分镜脚本。";
  }
  if (message.startsWith("archived project")) {
    return "当前项目已归档，只能查看，不能继续修改。";
  }
  if (message.includes("(404)") || message.includes("not found")) {
    return message;
  }
  return fallback;
}

function ReviewDraftsPanel({
  isArchived,
  projectId,
  refreshKey,
}: {
  isArchived: boolean;
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

function SubtitleDraftsPanel({
  hasSelectedStoryboard,
  isArchived,
  projectId,
}: {
  hasSelectedStoryboard: boolean | null;
  isArchived: boolean;
  projectId: number;
}) {
  const [subtitleDrafts, setSubtitleDrafts] = useState<SubtitleDraft[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [selectingId, setSelectingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function reloadSubtitleDrafts() {
    setLoading(true);
    try {
      const items = await getSubtitleDrafts(projectId);
      setSubtitleDrafts(items);
      setError(null);
    } catch (err) {
      setError(formatSubtitleDraftError(err, "加载字幕草稿失败"));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void reloadSubtitleDrafts();
  }, [projectId]);

  async function handleCreate() {
    if (isArchived || hasSelectedStoryboard !== true) {
      return;
    }
    setCreating(true);
    setError(null);
    try {
      await createSubtitleDraft(projectId);
      await reloadSubtitleDrafts();
    } catch (err) {
      setError(formatSubtitleDraftError(err, "创建模拟字幕草稿失败"));
    } finally {
      setCreating(false);
    }
  }

  async function handleSelect(subtitleDraftId: number) {
    if (isArchived) {
      return;
    }
    setSelectingId(subtitleDraftId);
    setError(null);
    try {
      await selectSubtitleDraft(projectId, subtitleDraftId);
      await reloadSubtitleDrafts();
    } catch (err) {
      setError(formatSubtitleDraftError(err, "选择字幕草稿失败"));
    } finally {
      setSelectingId(null);
    }
  }

  const createDisabled = isArchived || hasSelectedStoryboard !== true || creating;

  return (
    <section className="mt-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-stone-950">字幕草稿</h2>
          <p className="mt-1 text-sm text-stone-600">
            基于已选分镜脚本生成的模拟字幕草稿和字幕 cue 元数据。
          </p>
        </div>
        <button
          className="rounded bg-violet-700 px-4 py-2 text-sm font-medium text-white hover:bg-violet-800 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={createDisabled}
          type="button"
          onClick={handleCreate}
        >
          {creating ? "创建中..." : "创建模拟字幕草稿"}
        </button>
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-100 p-3 text-sm text-stone-700">
          当前项目已归档，只能查看，不能继续修改。
        </p>
      )}
      {hasSelectedStoryboard === false && !isArchived && (
        <p className="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          请先选择一个分镜脚本，再创建模拟字幕草稿。
        </p>
      )}
      {hasSelectedStoryboard === null && !isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-50 p-3 text-sm text-stone-600">
          正在检查分镜脚本选择状态，确认后才能创建模拟字幕。
        </p>
      )}
      {error && <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {loading && <p className="mt-4 text-sm text-stone-600">正在加载字幕草稿...</p>}
      {!loading && subtitleDrafts.length === 0 && (
        <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-4 text-sm text-stone-600">
          暂无字幕草稿。
        </p>
      )}
      {!loading && subtitleDrafts.length > 0 && (
        <div className="mt-4 space-y-3">
          {subtitleDrafts.map((subtitleDraft) => (
            <SubtitleDraftCard
              disabled={isArchived || selectingId !== null}
              key={subtitleDraft.id}
              selecting={selectingId === subtitleDraft.id}
              subtitleDraft={subtitleDraft}
              onSelect={handleSelect}
            />
          ))}
        </div>
      )}
    </section>
  );
}

function SubtitleDraftCard({
  disabled,
  onSelect,
  selecting,
  subtitleDraft,
}: {
  disabled: boolean;
  onSelect: (subtitleDraftId: number) => void;
  selecting: boolean;
  subtitleDraft: SubtitleDraft;
}) {
  const isSelected = subtitleDraft.status === "selected";
  const cues = [...subtitleDraft.cues].sort(
    (left, right) => left.cue_order - right.cue_order || left.id - right.id,
  );

  return (
    <article
      aria-label={`字幕草稿 ${subtitleDraft.id}`}
      className={`rounded border bg-white p-4 ${
        isSelected ? "border-violet-300 bg-violet-50 ring-1 ring-violet-200" : "border-stone-200"
      }`}
      data-status={subtitleDraft.status}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-stone-950">字幕草稿 #{subtitleDraft.id}</h3>
          <p className="mt-1 text-xs text-stone-500">创建于 {new Date(subtitleDraft.created_at).toLocaleString()}</p>
        </div>
        {isSelected ? (
          <span className="rounded border border-violet-300 bg-white px-3 py-1 text-xs font-semibold text-violet-800">
            已选择
          </span>
        ) : subtitleDraft.status === "draft" ? (
          <button
            className="rounded border border-violet-700 px-3 py-1 text-xs font-semibold text-violet-800 hover:bg-violet-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={disabled}
            type="button"
            onClick={() => onSelect(subtitleDraft.id)}
          >
            {selecting ? "选择中..." : "选择"}
          </button>
        ) : null}
      </div>

      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">生成器</dt>
          <dd className="mt-1 text-stone-800">
            {subtitleDraft.generator_name} {subtitleDraft.generator_version}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">状态</dt>
          <dd className="mt-1 text-stone-800">{formatStatus(subtitleDraft.status)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">分镜脚本</dt>
          <dd className="mt-1 text-stone-800">#{subtitleDraft.storyboard_draft_id}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">更新时间</dt>
          <dd className="mt-1 text-stone-800">{new Date(subtitleDraft.updated_at).toLocaleString()}</dd>
        </div>
      </dl>
      {subtitleDraft.selected_at && (
        <p className="mt-3 text-xs text-stone-500">选择于 {new Date(subtitleDraft.selected_at).toLocaleString()}</p>
      )}

      <div className="mt-4 rounded border border-stone-200 bg-stone-50 p-3">
        <h4 className="text-xs font-semibold uppercase text-stone-500">字幕 cue</h4>
        {cues.length === 0 ? (
          <p className="mt-3 rounded border border-dashed border-stone-300 bg-white p-3 text-sm text-stone-600">
            暂无字幕 cue。
          </p>
        ) : (
          <ol className="mt-3 divide-y divide-stone-200 border-y border-stone-200">
            {cues.map((cue) => (
              <li
                aria-label={`字幕 cue ${cue.cue_order}`}
                className="py-3"
                data-cue-order={cue.cue_order}
                data-testid="subtitle-cue"
                key={cue.id}
              >
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <h5 className="text-sm font-semibold text-stone-950">字幕 {cue.cue_order}</h5>
                  <span className="text-xs text-stone-500">
                    {cue.start_time_seconds} 秒 - {cue.end_time_seconds} 秒
                  </span>
                </div>
                <p className="mt-2 whitespace-pre-wrap text-sm text-stone-800">{cue.text}</p>
              </li>
            ))}
          </ol>
        )}
      </div>
    </article>
  );
}

function formatSubtitleDraftError(err: unknown, fallback: string) {
  const message = err instanceof Error ? err.message : fallback;
  if (message === "project has no selected storyboard") {
    return "请先选择一个分镜脚本，再创建模拟字幕草稿。";
  }
  if (message === "selected storyboard has no scenes") {
    return "已选择的分镜脚本没有可用于模拟字幕的场景。";
  }
  if (message.startsWith("archived project")) {
    return "当前项目已归档，只能查看，不能继续修改。";
  }
  if (message.includes("(404)") || message.includes("not found")) {
    return message;
  }
  return message || fallback;
}

function RenderJobsPanel({
  hasSelectedStoryboard,
  isArchived,
  projectId,
}: {
  hasSelectedStoryboard: boolean | null;
  isArchived: boolean;
  projectId: number;
}) {
  const [renderJobs, setRenderJobs] = useState<RenderJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function reloadRenderJobs() {
    setLoading(true);
    try {
      const items = await getRenderJobs(projectId);
      setRenderJobs(items);
      setError(null);
    } catch (err) {
      setError(formatRenderJobError(err, "加载渲染任务失败"));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void reloadRenderJobs();
  }, [projectId]);

  async function handleCreate() {
    if (isArchived || hasSelectedStoryboard !== true) {
      return;
    }
    setCreating(true);
    setError(null);
    try {
      await createRenderJob(projectId);
      await reloadRenderJobs();
    } catch (err) {
      setError(formatRenderJobError(err, "创建模拟渲染任务失败"));
    } finally {
      setCreating(false);
    }
  }

  const createDisabled = isArchived || hasSelectedStoryboard !== true || creating;

  return (
    <section className="mt-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-stone-950">渲染任务</h2>
          <p className="mt-1 text-sm text-stone-600">
            基于已选分镜脚本创建的模拟渲染任务和预览 manifest 元数据。
          </p>
        </div>
        <button
          className="rounded bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={createDisabled}
          type="button"
          onClick={handleCreate}
        >
          {creating ? "创建中..." : "创建模拟渲染任务"}
        </button>
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-100 p-3 text-sm text-stone-700">
          当前项目已归档，只能查看，不能继续修改。
        </p>
      )}
      {hasSelectedStoryboard === false && !isArchived && (
        <p className="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          请先选择一个分镜脚本，再创建模拟渲染任务。
        </p>
      )}
      {hasSelectedStoryboard === null && !isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-50 p-3 text-sm text-stone-600">
          正在检查分镜脚本选择状态，确认后才能创建模拟渲染。
        </p>
      )}
      {error && <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {loading && <p className="mt-4 text-sm text-stone-600">正在加载渲染任务...</p>}
      {!loading && renderJobs.length === 0 && (
        <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-4 text-sm text-stone-600">
          暂无渲染任务。
        </p>
      )}
      {!loading && renderJobs.length > 0 && (
        <div className="mt-4 space-y-3">
          {renderJobs.map((renderJob) => (
            <RenderJobCard key={renderJob.id} renderJob={renderJob} />
          ))}
        </div>
      )}
    </section>
  );
}

function RenderJobCard({ renderJob }: { renderJob: RenderJob }) {
  return (
    <article aria-label={`渲染任务 ${renderJob.id}`} className="rounded border border-stone-200 bg-white p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-stone-950">渲染任务 #{renderJob.id}</h3>
          <p className="mt-1 text-xs text-stone-500">创建于 {new Date(renderJob.created_at).toLocaleString()}</p>
        </div>
        <span className="rounded border border-emerald-300 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-800">
          {formatStatus(renderJob.status)}
        </span>
      </div>

      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">渲染器</dt>
          <dd className="mt-1 text-stone-800">
            {renderJob.renderer_name} {renderJob.renderer_version}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">分镜脚本</dt>
          <dd className="mt-1 text-stone-800">#{renderJob.storyboard_draft_id}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">请求输出</dt>
          <dd className="mt-1 text-stone-800">
            {renderJob.requested_format} / {renderJob.requested_aspect_ratio} / {renderJob.requested_resolution}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">更新时间</dt>
          <dd className="mt-1 text-stone-800">{new Date(renderJob.updated_at).toLocaleString()}</dd>
        </div>
      </dl>

      {renderJob.error_message && <p className="mt-3 text-sm text-red-700">{renderJob.error_message}</p>}
      {renderJob.status === "succeeded" ? (
        <PreviewArtifactMetadata artifact={renderJob.artifact} />
      ) : (
        <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-3 text-sm text-stone-600">
          预览待生成 / 不可用。
        </p>
      )}
    </article>
  );
}

function PreviewArtifactMetadata({ artifact }: { artifact: RenderJob["artifact"] }) {
  if (!artifact) {
    return (
      <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-3 text-sm text-stone-600">
        暂无预览元数据。
      </p>
    );
  }

  return (
    <div className="mt-4 rounded border border-stone-200 bg-stone-50 p-3">
      <h4 className="text-xs font-semibold uppercase text-stone-500">预览 manifest 元数据</h4>
      <dl className="mt-3 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">产物类型</dt>
          <dd className="mt-1 text-stone-800">{artifact.artifact_type}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">MIME 类型</dt>
          <dd className="mt-1 text-stone-800">{artifact.mime_type}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">文件大小</dt>
          <dd className="mt-1 text-stone-800">{artifact.file_size_bytes} bytes</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">校验值</dt>
          <dd className="mt-1 break-all text-stone-800">{artifact.checksum_sha256 ?? "暂无"}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">时长</dt>
          <dd className="mt-1 text-stone-800">{artifact.duration_seconds} 秒</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">尺寸</dt>
          <dd className="mt-1 text-stone-800">
            {artifact.width} x {artifact.height}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">FPS</dt>
          <dd className="mt-1 text-stone-800">暂无</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">字幕草稿</dt>
          <dd className="mt-1 text-stone-800">{artifact.subtitle_draft_id ? `#${artifact.subtitle_draft_id}` : "无"}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Manifest 文件</dt>
          <dd className="mt-1 break-all text-stone-800">{artifact.file_name}</dd>
        </div>
      </dl>
      <p className="mt-3 break-all text-xs text-stone-600">{artifact.storage_path}</p>
    </div>
  );
}

function formatRenderJobError(err: unknown, fallback: string) {
  const message = err instanceof Error ? err.message : fallback;
  if (message === "project has no selected storyboard") {
    return "请先选择一个分镜脚本，再创建模拟渲染任务。";
  }
  if (message === "selected storyboard has no scenes") {
    return "已选择的分镜脚本没有可用于渲染的场景。";
  }
  if (message.startsWith("archived project")) {
    return "当前项目已归档，只能查看，不能继续修改。";
  }
  if (message.includes("(404)") || message.includes("not found")) {
    return message;
  }
  return message || fallback;
}

function MaterialItem({ material }: { material: Material }) {
  return (
    <article className="rounded border border-stone-200 bg-white p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="rounded bg-stone-100 px-2 py-1 text-xs font-medium text-stone-700">
          {materialLabels[material.material_type] ?? material.material_type}
        </span>
        <time className="text-xs text-stone-500">{new Date(material.created_at).toLocaleString()}</time>
      </div>
      {material.title && <h3 className="mt-3 text-sm font-semibold text-stone-950">{material.title}</h3>}
      {material.text_content && <p className="mt-2 whitespace-pre-wrap text-sm text-stone-700">{material.text_content}</p>}
      {material.source_url && (
        <a className="mt-2 block break-all text-sm font-medium text-teal-700" href={material.source_url} rel="noreferrer" target="_blank">
          {material.source_url}
        </a>
      )}
      {material.original_file_name && <p className="mt-2 text-sm text-stone-700">{material.original_file_name}</p>}
      {material.stored_file_path && <p className="mt-1 break-all text-xs text-stone-500">{material.stored_file_path}</p>}
    </article>
  );
}

function ProjectEditForm({ project, onUpdated }: { project: ProjectDetail; onUpdated: () => void }) {
  const [title, setTitle] = useState(project.title);
  const [description, setDescription] = useState(project.description ?? "");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    setTitle(project.title);
    setDescription(project.description ?? "");
  }, [project.id, project.title, project.description]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await updateProject(project.id, { title, description });
      onUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存失败");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="rounded border border-stone-200 bg-white p-4" onSubmit={submit}>
      <h2 className="text-sm font-semibold text-stone-950">编辑项目</h2>
      <input
        className="mt-3 w-full rounded border border-stone-300 px-3 py-2 text-sm"
        required
        value={title}
        onChange={(event) => setTitle(event.target.value)}
      />
      <textarea
        className="mt-3 min-h-24 w-full rounded border border-stone-300 px-3 py-2 text-sm"
        value={description}
        onChange={(event) => setDescription(event.target.value)}
      />
      {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
      <button className="mt-3 w-full rounded bg-stone-950 px-3 py-2 text-sm font-medium text-white disabled:opacity-50" disabled={submitting}>
        {submitting ? "保存中..." : "保存项目"}
      </button>
    </form>
  );
}

function ArchiveProjectPanel({ project, onArchived }: { project: ProjectDetail; onArchived: () => void }) {
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const isArchived = project.status === "archived";

  async function handleArchive() {
    if (isArchived || !window.confirm("确认归档这个项目？")) {
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await archiveProject(project.id);
      onArchived();
    } catch (err) {
      setError(err instanceof Error ? err.message : "归档失败");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="rounded border border-stone-200 bg-white p-4">
      <h2 className="text-sm font-semibold text-stone-950">项目归档</h2>
      <p className="mt-2 text-sm text-stone-600">归档后默认不在项目列表显示，已有素材仍可查看。</p>
      {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
      <button
        className="mt-3 w-full rounded border border-stone-300 px-3 py-2 text-sm font-medium text-stone-800 disabled:opacity-50"
        disabled={isArchived || submitting}
        type="button"
        onClick={handleArchive}
      >
        {isArchived ? "已归档" : submitting ? "归档中..." : "归档项目"}
      </button>
    </div>
  );
}

function TextMaterialForm({ disabled, projectId, onAdded }: { disabled: boolean; projectId: number; onAdded: () => void }) {
  const [materialType, setMaterialType] = useState<TextMaterialType>("text");
  const [title, setTitle] = useState("");
  const [textContent, setTextContent] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (disabled) {
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await addTextMaterial(projectId, { material_type: materialType, title: title || undefined, text_content: textContent });
      setTitle("");
      setTextContent("");
      onAdded();
    } catch (err) {
      setError(err instanceof Error ? err.message : "添加失败");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="rounded border border-stone-200 bg-white p-4" onSubmit={submit}>
      <h2 className="text-sm font-semibold text-stone-950">添加文本类素材</h2>
      <select
        className="mt-3 w-full rounded border border-stone-300 px-3 py-2 text-sm"
        disabled={disabled}
        value={materialType}
        onChange={(event) => setMaterialType(event.target.value as TextMaterialType)}
      >
        <option value="text">文本</option>
        <option value="summary">摘要</option>
        <option value="project_record">项目记录</option>
      </select>
      <input
        className="mt-3 w-full rounded border border-stone-300 px-3 py-2 text-sm"
        disabled={disabled}
        placeholder="标题"
        value={title}
        onChange={(event) => setTitle(event.target.value)}
      />
      <textarea
        className="mt-3 min-h-28 w-full rounded border border-stone-300 px-3 py-2 text-sm"
        disabled={disabled}
        placeholder="输入用户显式提供的素材内容"
        required
        value={textContent}
        onChange={(event) => setTextContent(event.target.value)}
      />
      {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
      <button className="mt-3 w-full rounded bg-stone-950 px-3 py-2 text-sm font-medium text-white disabled:opacity-50" disabled={disabled || submitting}>
        {submitting ? "添加中..." : "添加文本素材"}
      </button>
    </form>
  );
}

function LinkMaterialForm({ disabled, projectId, onAdded }: { disabled: boolean; projectId: number; onAdded: () => void }) {
  const [title, setTitle] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (disabled) {
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await addLinkMaterial(projectId, { title: title || undefined, source_url: sourceUrl });
      setTitle("");
      setSourceUrl("");
      onAdded();
    } catch (err) {
      setError(err instanceof Error ? err.message : "添加失败");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="rounded border border-stone-200 bg-white p-4" onSubmit={submit}>
      <h2 className="text-sm font-semibold text-stone-950">添加链接素材</h2>
      <input
        className="mt-3 w-full rounded border border-stone-300 px-3 py-2 text-sm"
        disabled={disabled}
        placeholder="标题"
        value={title}
        onChange={(event) => setTitle(event.target.value)}
      />
      <input
        className="mt-3 w-full rounded border border-stone-300 px-3 py-2 text-sm"
        disabled={disabled}
        placeholder="https://example.com"
        required
        type="url"
        value={sourceUrl}
        onChange={(event) => setSourceUrl(event.target.value)}
      />
      {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
      <button className="mt-3 w-full rounded bg-stone-950 px-3 py-2 text-sm font-medium text-white disabled:opacity-50" disabled={disabled || submitting}>
        {submitting ? "添加中..." : "添加链接"}
      </button>
    </form>
  );
}

function FileMaterialForm({ disabled, projectId, onAdded }: { disabled: boolean; projectId: number; onAdded: () => void }) {
  const [materialType, setMaterialType] = useState<FileMaterialType>("image");
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (disabled) {
      return;
    }
    if (!file) {
      setError("请选择文件");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await addFileMaterial(projectId, { material_type: materialType, title: title || undefined, file });
      setTitle("");
      setFile(null);
      onAdded();
    } catch (err) {
      setError(err instanceof Error ? err.message : "上传失败");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="rounded border border-stone-200 bg-white p-4" onSubmit={submit}>
      <h2 className="text-sm font-semibold text-stone-950">添加图片或截图</h2>
      <select
        className="mt-3 w-full rounded border border-stone-300 px-3 py-2 text-sm"
        disabled={disabled}
        value={materialType}
        onChange={(event) => setMaterialType(event.target.value as FileMaterialType)}
      >
        <option value="image">图片</option>
        <option value="screenshot">截图</option>
      </select>
      <input
        className="mt-3 w-full rounded border border-stone-300 px-3 py-2 text-sm"
        disabled={disabled}
        placeholder="标题"
        value={title}
        onChange={(event) => setTitle(event.target.value)}
      />
      <input
        accept="image/png,image/jpeg,image/webp,image/gif"
        className="mt-3 w-full rounded border border-stone-300 px-3 py-2 text-sm"
        disabled={disabled}
        required
        type="file"
        onChange={(event) => setFile(event.target.files?.[0] ?? null)}
      />
      {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
      <button className="mt-3 w-full rounded bg-stone-950 px-3 py-2 text-sm font-medium text-white disabled:opacity-50" disabled={disabled || submitting}>
        {submitting ? "上传中..." : "添加文件素材"}
      </button>
    </form>
  );
}
