import { FormEvent, useEffect, useState } from "react";

import {
  addFileMaterial,
  addLinkMaterial,
  addTextMaterial,
  archiveProject,
  generateTopicCandidates,
  getProject,
  getTopicCandidates,
  Material,
  ProjectDetail,
  selectTopicCandidate,
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
