import { FormEvent, useEffect, useState } from "react";

import {
  ContentPlan,
  createContentPlan,
  createGenerationRun,
  createGenerationSchedule,
  disableContentPlan,
  disableGenerationSchedule,
  enableContentPlan,
  enableGenerationSchedule,
  GenerationRun,
  GenerationSchedule,
  getContentPlans,
  getGenerationRuns,
  getGenerationSchedules,
} from "../../api/client";
import { formatStatus } from "./formatting";

export function ContentPlansPanel({
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
