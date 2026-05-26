import { FormEvent, useEffect, useState } from "react";

import {
  addFileMaterial,
  addLinkMaterial,
  addTextMaterial,
  archiveProject,
  getProject,
  Material,
  ProjectDetail,
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
