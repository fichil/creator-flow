import { FormEvent, useEffect, useState } from "react";

import {
  addFileMaterial,
  addLinkMaterial,
  addTextMaterial,
  archiveProject,
  createRenderJob,
  createSubtitleDraft,
  generateScriptDrafts,
  generateStoryboards,
  generateTopicCandidates,
  getProject,
  getRenderJobs,
  getScriptDrafts,
  getStoryboards,
  getSubtitleDrafts,
  getTopicCandidates,
  Material,
  ProjectDetail,
  RenderJob,
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

export function ProjectDetailPage({ projectId, onBack }: ProjectDetailPageProps) {
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasSelectedStoryboard, setHasSelectedStoryboard] = useState<boolean | null>(null);
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
              <TopicCandidatesPanel isArchived={isArchived} projectId={project.id} />
              <ScriptDraftsPanel isArchived={isArchived} projectId={project.id} />
              <StoryboardsPanel
                isArchived={isArchived}
                projectId={project.id}
                onSelectionStateChange={setHasSelectedStoryboard}
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
          <h2 className="text-lg font-semibold text-stone-950">Topic Candidates</h2>
          <p className="mt-1 text-sm text-stone-600">基于已显式导入素材生成的 fake provider 候选选题。</p>
        </div>
        <button
          className="rounded bg-teal-700 px-4 py-2 text-sm font-medium text-white hover:bg-teal-800 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={isArchived || generating}
          type="button"
          onClick={handleGenerate}
        >
          {generating ? "Generating..." : "Generate Topic Candidates"}
        </button>
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-100 p-3 text-sm text-stone-700">
          Archived projects are read-only.
        </p>
      )}
      {error && <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {loading && <p className="mt-4 text-sm text-stone-600">正在加载候选选题...</p>}
      {!loading && candidates.length === 0 && (
        <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-4 text-sm text-stone-600">
          No topic candidates yet.
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
      aria-label={`Topic candidate: ${candidate.title}`}
      className={`rounded border bg-white p-4 ${
        isSelected ? "border-teal-300 bg-teal-50 ring-1 ring-teal-200" : "border-stone-200"
      }`}
      data-status={candidate.status}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{candidate.title}</h3>
          <p className="mt-1 text-xs text-stone-500">Created {new Date(candidate.created_at).toLocaleString()}</p>
        </div>
        {isSelected ? (
          <span className="rounded border border-teal-300 bg-white px-3 py-1 text-xs font-semibold text-teal-800">
            Selected
          </span>
        ) : (
          <button
            className="rounded border border-teal-700 px-3 py-1 text-xs font-semibold text-teal-800 hover:bg-teal-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={disabled}
            type="button"
            onClick={() => onSelect(candidate.id)}
          >
            {selecting ? "Selecting..." : "Select"}
          </button>
        )}
      </div>
      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Angle</dt>
          <dd className="mt-1 text-stone-800">{candidate.angle}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Audience</dt>
          <dd className="mt-1 text-stone-800">{candidate.audience}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Hook</dt>
          <dd className="mt-1 text-stone-800">{candidate.hook}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Status</dt>
          <dd className="mt-1 text-stone-800">{candidate.status}</dd>
        </div>
      </dl>
      <div className="mt-3 text-sm">
        <p className="text-xs font-semibold uppercase text-stone-500">Rationale</p>
        <p className="mt-1 text-stone-800">{candidate.rationale}</p>
      </div>
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-stone-500">
        <span>Source materials: {candidate.source_material_ids.join(", ") || "none"}</span>
        {candidate.selected_at && <span>Selected {new Date(candidate.selected_at).toLocaleString()}</span>}
      </div>
    </article>
  );
}

function formatTopicCandidateError(err: unknown, fallback: string) {
  const message = err instanceof Error ? err.message : fallback;
  if (message === "project has no materials") {
    return "Add at least one material before generating topic candidates.";
  }
  if (message.startsWith("archived project")) {
    return "Archived projects are read-only.";
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
      setError(formatScriptDraftError(err, "Failed to load script drafts."));
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
      setError(formatScriptDraftError(err, "Failed to generate script drafts."));
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
      setError(formatScriptDraftError(err, "Failed to select script draft."));
    } finally {
      setSelectingId(null);
    }
  }

  return (
    <section className="mt-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-stone-950">Script Drafts</h2>
          <p className="mt-1 text-sm text-stone-600">Fake provider drafts based on the selected topic and explicit materials.</p>
        </div>
        <button
          className="rounded bg-indigo-700 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-800 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={isArchived || generating}
          type="button"
          onClick={handleGenerate}
        >
          {generating ? "Generating..." : "Generate Script Drafts"}
        </button>
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-100 p-3 text-sm text-stone-700">
          Archived projects are read-only.
        </p>
      )}
      {error && <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {loading && <p className="mt-4 text-sm text-stone-600">Loading script drafts...</p>}
      {!loading && scriptDrafts.length === 0 && (
        <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-4 text-sm text-stone-600">
          No script drafts yet.
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
      aria-label={`Script draft: ${scriptDraft.title}`}
      className={`rounded border bg-white p-4 ${
        isSelected ? "border-indigo-300 bg-indigo-50 ring-1 ring-indigo-200" : "border-stone-200"
      }`}
      data-status={scriptDraft.status}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{scriptDraft.title}</h3>
          <p className="mt-1 text-xs text-stone-500">Created {new Date(scriptDraft.created_at).toLocaleString()}</p>
        </div>
        {isSelected ? (
          <span className="rounded border border-indigo-300 bg-white px-3 py-1 text-xs font-semibold text-indigo-800">
            Selected
          </span>
        ) : scriptDraft.status === "draft" ? (
          <button
            className="rounded border border-indigo-700 px-3 py-1 text-xs font-semibold text-indigo-800 hover:bg-indigo-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={disabled}
            type="button"
            onClick={() => onSelect(scriptDraft.id)}
          >
            {selecting ? "Selecting..." : "Select"}
          </button>
        ) : null}
      </div>
      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Opening hook</dt>
          <dd className="mt-1 text-stone-800">{scriptDraft.opening_hook}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Call to action</dt>
          <dd className="mt-1 text-stone-800">{scriptDraft.call_to_action}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Estimated duration</dt>
          <dd className="mt-1 text-stone-800">{scriptDraft.estimated_duration_seconds} seconds</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Status</dt>
          <dd className="mt-1 text-stone-800">{scriptDraft.status}</dd>
        </div>
      </dl>
      <div className="mt-3 text-sm">
        <p className="text-xs font-semibold uppercase text-stone-500">Body</p>
        <p className="mt-1 whitespace-pre-wrap text-stone-800">{scriptDraft.body}</p>
      </div>
      <div className="mt-3 text-sm">
        <p className="text-xs font-semibold uppercase text-stone-500">Rationale</p>
        <p className="mt-1 text-stone-800">{scriptDraft.rationale}</p>
      </div>
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-stone-500">
        <span>Source materials: {scriptDraft.source_material_ids.join(", ") || "none"}</span>
        {scriptDraft.selected_at && <span>Selected {new Date(scriptDraft.selected_at).toLocaleString()}</span>}
      </div>
    </article>
  );
}

function formatScriptDraftError(err: unknown, fallback: string) {
  const message = err instanceof Error ? err.message : fallback;
  if (message === "project has no materials") {
    return "Add at least one material before generating script drafts.";
  }
  if (message === "project has no selected topic candidate") {
    return "Select a topic candidate before generating script drafts.";
  }
  if (message.startsWith("archived project")) {
    return "Archived projects are read-only.";
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
      setError(formatStoryboardError(err, "Failed to load storyboards."));
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
      setError(formatStoryboardError(err, "Failed to generate storyboards."));
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
      setError(formatStoryboardError(err, "Failed to select storyboard."));
    } finally {
      setSelectingId(null);
    }
  }

  return (
    <section className="mt-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-stone-950">Storyboards</h2>
          <p className="mt-1 text-sm text-stone-600">
            Fake provider storyboard drafts based on the selected topic, selected script, and explicit materials.
          </p>
        </div>
        <button
          className="rounded bg-sky-700 px-4 py-2 text-sm font-medium text-white hover:bg-sky-800 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={isArchived || generating}
          type="button"
          onClick={handleGenerate}
        >
          {generating ? "Generating..." : "Generate Storyboards"}
        </button>
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-100 p-3 text-sm text-stone-700">
          Archived projects are read-only.
        </p>
      )}
      {error && <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {loading && <p className="mt-4 text-sm text-stone-600">Loading storyboards...</p>}
      {!loading && storyboards.length === 0 && (
        <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-4 text-sm text-stone-600">
          No storyboards yet.
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
      aria-label={`Storyboard: ${storyboard.title}`}
      className={`rounded border bg-white p-4 ${
        isSelected ? "border-sky-300 bg-sky-50 ring-1 ring-sky-200" : "border-stone-200"
      }`}
      data-status={storyboard.status}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-stone-950">{storyboard.title}</h3>
          <p className="mt-1 text-xs text-stone-500">Created {new Date(storyboard.created_at).toLocaleString()}</p>
        </div>
        {isSelected ? (
          <span className="rounded border border-sky-300 bg-white px-3 py-1 text-xs font-semibold text-sky-800">
            Selected
          </span>
        ) : storyboard.status === "draft" ? (
          <button
            className="rounded border border-sky-700 px-3 py-1 text-xs font-semibold text-sky-800 hover:bg-sky-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={disabled}
            type="button"
            onClick={() => onSelect(storyboard.id)}
          >
            {selecting ? "Selecting..." : "Select"}
          </button>
        ) : null}
      </div>
      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Summary</dt>
          <dd className="mt-1 text-stone-800">{storyboard.summary}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Visual style</dt>
          <dd className="mt-1 text-stone-800">{storyboard.visual_style}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Status</dt>
          <dd className="mt-1 text-stone-800">{storyboard.status}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Source materials</dt>
          <dd className="mt-1 text-stone-800">{storyboard.source_material_ids.join(", ") || "none"}</dd>
        </div>
      </dl>
      {storyboard.selected_at && (
        <p className="mt-3 text-xs text-stone-500">Selected {new Date(storyboard.selected_at).toLocaleString()}</p>
      )}

      <div className="mt-4">
        <h4 className="text-xs font-semibold uppercase text-stone-500">Scenes</h4>
        <ol className="mt-3 divide-y divide-stone-200 border-y border-stone-200">
          {scenes.map((scene) => (
            <li
              aria-label={`Scene ${scene.scene_order}: ${scene.scene_title}`}
              className="py-3"
              data-scene-order={scene.scene_order}
              data-testid="storyboard-scene"
              key={scene.id}
            >
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <h5 className="text-sm font-semibold text-stone-950">
                  Scene {scene.scene_order}: {scene.scene_title}
                </h5>
                <span className="text-xs text-stone-500">{scene.estimated_duration_seconds} seconds</span>
              </div>
              <dl className="mt-2 grid gap-2 text-sm md:grid-cols-2">
                <div>
                  <dt className="text-xs font-semibold uppercase text-stone-500">Narration</dt>
                  <dd className="mt-1 text-stone-800">{scene.narration}</dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold uppercase text-stone-500">Visual description</dt>
                  <dd className="mt-1 text-stone-800">{scene.visual_description}</dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold uppercase text-stone-500">On-screen text</dt>
                  <dd className="mt-1 text-stone-800">{scene.on_screen_text}</dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold uppercase text-stone-500">Source material</dt>
                  <dd className="mt-1 text-stone-800">{scene.source_material_id ?? "none"}</dd>
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
    return "Add at least one material before generating storyboards.";
  }
  if (message === "project has no selected topic candidate") {
    return "Select a topic candidate before generating storyboards.";
  }
  if (message === "project has no selected script draft") {
    return "Select a script draft before generating storyboards.";
  }
  if (message.startsWith("archived project")) {
    return "Archived projects are read-only.";
  }
  if (message.includes("(404)") || message.includes("not found")) {
    return message;
  }
  return fallback;
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
      setError(formatSubtitleDraftError(err, "Failed to load subtitle drafts."));
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
      setError(formatSubtitleDraftError(err, "Failed to create fake subtitle draft."));
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
      setError(formatSubtitleDraftError(err, "Failed to select subtitle draft."));
    } finally {
      setSelectingId(null);
    }
  }

  const createDisabled = isArchived || hasSelectedStoryboard !== true || creating;

  return (
    <section className="mt-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-stone-950">Subtitle Drafts</h2>
          <p className="mt-1 text-sm text-stone-600">
            FakeSubtitle drafts and deterministic subtitle cue metadata for the selected storyboard.
          </p>
        </div>
        <button
          className="rounded bg-violet-700 px-4 py-2 text-sm font-medium text-white hover:bg-violet-800 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={createDisabled}
          type="button"
          onClick={handleCreate}
        >
          {creating ? "Creating..." : "Create fake subtitle draft"}
        </button>
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-100 p-3 text-sm text-stone-700">
          Archived projects are read-only.
        </p>
      )}
      {hasSelectedStoryboard === false && !isArchived && (
        <p className="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          Select a storyboard before creating fake subtitle drafts.
        </p>
      )}
      {hasSelectedStoryboard === null && !isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-50 p-3 text-sm text-stone-600">
          Checking storyboard selection before enabling fake subtitles.
        </p>
      )}
      {error && <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {loading && <p className="mt-4 text-sm text-stone-600">Loading subtitle drafts...</p>}
      {!loading && subtitleDrafts.length === 0 && (
        <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-4 text-sm text-stone-600">
          No subtitle drafts yet.
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
      aria-label={`Subtitle draft ${subtitleDraft.id}`}
      className={`rounded border bg-white p-4 ${
        isSelected ? "border-violet-300 bg-violet-50 ring-1 ring-violet-200" : "border-stone-200"
      }`}
      data-status={subtitleDraft.status}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-stone-950">Subtitle draft #{subtitleDraft.id}</h3>
          <p className="mt-1 text-xs text-stone-500">Created {new Date(subtitleDraft.created_at).toLocaleString()}</p>
        </div>
        {isSelected ? (
          <span className="rounded border border-violet-300 bg-white px-3 py-1 text-xs font-semibold text-violet-800">
            Selected
          </span>
        ) : subtitleDraft.status === "draft" ? (
          <button
            className="rounded border border-violet-700 px-3 py-1 text-xs font-semibold text-violet-800 hover:bg-violet-50 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={disabled}
            type="button"
            onClick={() => onSelect(subtitleDraft.id)}
          >
            {selecting ? "Selecting..." : "Select"}
          </button>
        ) : null}
      </div>

      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Generator</dt>
          <dd className="mt-1 text-stone-800">
            {subtitleDraft.generator_name} {subtitleDraft.generator_version}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Status</dt>
          <dd className="mt-1 text-stone-800">{subtitleDraft.status}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Storyboard</dt>
          <dd className="mt-1 text-stone-800">#{subtitleDraft.storyboard_draft_id}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Updated</dt>
          <dd className="mt-1 text-stone-800">{new Date(subtitleDraft.updated_at).toLocaleString()}</dd>
        </div>
      </dl>
      {subtitleDraft.selected_at && (
        <p className="mt-3 text-xs text-stone-500">Selected {new Date(subtitleDraft.selected_at).toLocaleString()}</p>
      )}

      <div className="mt-4 rounded border border-stone-200 bg-stone-50 p-3">
        <h4 className="text-xs font-semibold uppercase text-stone-500">Subtitle cues</h4>
        {cues.length === 0 ? (
          <p className="mt-3 rounded border border-dashed border-stone-300 bg-white p-3 text-sm text-stone-600">
            No subtitle cues yet.
          </p>
        ) : (
          <ol className="mt-3 divide-y divide-stone-200 border-y border-stone-200">
            {cues.map((cue) => (
              <li
                aria-label={`Subtitle cue ${cue.cue_order}`}
                className="py-3"
                data-cue-order={cue.cue_order}
                data-testid="subtitle-cue"
                key={cue.id}
              >
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <h5 className="text-sm font-semibold text-stone-950">Cue {cue.cue_order}</h5>
                  <span className="text-xs text-stone-500">
                    {cue.start_time_seconds}s - {cue.end_time_seconds}s
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
    return "Select a storyboard before creating fake subtitle drafts.";
  }
  if (message === "selected storyboard has no scenes") {
    return "The selected storyboard has no scenes for fake subtitles.";
  }
  if (message.startsWith("archived project")) {
    return "Archived projects are read-only.";
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
      setError(formatRenderJobError(err, "Failed to load render jobs."));
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
      setError(formatRenderJobError(err, "Failed to create fake render job."));
    } finally {
      setCreating(false);
    }
  }

  const createDisabled = isArchived || hasSelectedStoryboard !== true || creating;

  return (
    <section className="mt-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-stone-950">Render Jobs</h2>
          <p className="mt-1 text-sm text-stone-600">
            FakeRenderer jobs and deterministic fake video artifact metadata for the selected storyboard.
          </p>
        </div>
        <button
          className="rounded bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={createDisabled}
          type="button"
          onClick={handleCreate}
        >
          {creating ? "Creating..." : "Create fake render job"}
        </button>
      </div>

      {isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-100 p-3 text-sm text-stone-700">
          Archived projects are read-only.
        </p>
      )}
      {hasSelectedStoryboard === false && !isArchived && (
        <p className="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          Select a storyboard before creating fake render jobs.
        </p>
      )}
      {hasSelectedStoryboard === null && !isArchived && (
        <p className="mt-3 rounded border border-stone-200 bg-stone-50 p-3 text-sm text-stone-600">
          Checking storyboard selection before enabling fake rendering.
        </p>
      )}
      {error && <p className="mt-3 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {loading && <p className="mt-4 text-sm text-stone-600">Loading render jobs...</p>}
      {!loading && renderJobs.length === 0 && (
        <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-4 text-sm text-stone-600">
          No render jobs yet.
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
    <article aria-label={`Render job ${renderJob.id}`} className="rounded border border-stone-200 bg-white p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-stone-950">Render job #{renderJob.id}</h3>
          <p className="mt-1 text-xs text-stone-500">Created {new Date(renderJob.created_at).toLocaleString()}</p>
        </div>
        <span className="rounded border border-emerald-300 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-800">
          {renderJob.status}
        </span>
      </div>

      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Renderer</dt>
          <dd className="mt-1 text-stone-800">
            {renderJob.renderer_name} {renderJob.renderer_version}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Storyboard</dt>
          <dd className="mt-1 text-stone-800">#{renderJob.storyboard_draft_id}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Requested output</dt>
          <dd className="mt-1 text-stone-800">
            {renderJob.requested_format} / {renderJob.requested_aspect_ratio} / {renderJob.requested_resolution}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-stone-500">Updated</dt>
          <dd className="mt-1 text-stone-800">{new Date(renderJob.updated_at).toLocaleString()}</dd>
        </div>
      </dl>

      {renderJob.error_message && <p className="mt-3 text-sm text-red-700">{renderJob.error_message}</p>}
      {renderJob.artifact ? (
        <div className="mt-4 rounded border border-stone-200 bg-stone-50 p-3">
          <h4 className="text-xs font-semibold uppercase text-stone-500">Artifact metadata</h4>
          <dl className="mt-3 grid gap-3 text-sm md:grid-cols-2">
            <div>
              <dt className="text-xs font-semibold uppercase text-stone-500">Type</dt>
              <dd className="mt-1 text-stone-800">{renderJob.artifact.artifact_type}</dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase text-stone-500">MIME type</dt>
              <dd className="mt-1 text-stone-800">{renderJob.artifact.mime_type}</dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase text-stone-500">Duration</dt>
              <dd className="mt-1 text-stone-800">{renderJob.artifact.duration_seconds} seconds</dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase text-stone-500">Dimensions</dt>
              <dd className="mt-1 text-stone-800">
                {renderJob.artifact.width} x {renderJob.artifact.height}
              </dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase text-stone-500">File size</dt>
              <dd className="mt-1 text-stone-800">{renderJob.artifact.file_size_bytes} bytes</dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase text-stone-500">File name</dt>
              <dd className="mt-1 break-all text-stone-800">{renderJob.artifact.file_name}</dd>
            </div>
          </dl>
          <p className="mt-3 break-all text-xs text-stone-600">{renderJob.artifact.storage_path}</p>
        </div>
      ) : (
        <p className="mt-4 rounded border border-dashed border-stone-300 bg-white p-3 text-sm text-stone-600">
          No artifact metadata yet.
        </p>
      )}
    </article>
  );
}

function formatRenderJobError(err: unknown, fallback: string) {
  const message = err instanceof Error ? err.message : fallback;
  if (message === "project has no selected storyboard") {
    return "Select a storyboard before creating fake render jobs.";
  }
  if (message === "selected storyboard has no scenes") {
    return "The selected storyboard has no scenes to render.";
  }
  if (message.startsWith("archived project")) {
    return "Archived projects are read-only.";
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
