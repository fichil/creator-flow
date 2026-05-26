import { FormEvent, useState } from "react";

import { createProject } from "../api/client";

type ProjectCreatePageProps = {
  onCancel: () => void;
  onCreated: (projectId: number) => void;
};

export function ProjectCreatePage({ onCancel, onCreated }: ProjectCreatePageProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const project = await createProject({ title, description: description || undefined });
      onCreated(project.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建失败");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-8">
      <button className="text-sm font-medium text-stone-600 hover:text-stone-950" onClick={onCancel} type="button">
        返回项目列表
      </button>
      <h1 className="mt-4 text-2xl font-semibold text-stone-950">新建内容项目</h1>

      <form className="mt-6 space-y-5 rounded border border-stone-200 bg-white p-5" onSubmit={handleSubmit}>
        <label className="block">
          <span className="text-sm font-medium text-stone-800">标题</span>
          <input
            className="mt-2 w-full rounded border border-stone-300 px-3 py-2 text-sm outline-none focus:border-teal-600"
            required
            value={title}
            onChange={(event) => setTitle(event.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-stone-800">描述</span>
          <textarea
            className="mt-2 min-h-28 w-full rounded border border-stone-300 px-3 py-2 text-sm outline-none focus:border-teal-600"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
          />
        </label>
        {error && <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
        <div className="flex justify-end gap-3">
          <button className="rounded border border-stone-300 px-4 py-2 text-sm font-medium" type="button" onClick={onCancel}>
            取消
          </button>
          <button className="rounded bg-stone-950 px-4 py-2 text-sm font-medium text-white disabled:opacity-50" disabled={submitting}>
            {submitting ? "创建中..." : "创建项目"}
          </button>
        </div>
      </form>
    </section>
  );
}
