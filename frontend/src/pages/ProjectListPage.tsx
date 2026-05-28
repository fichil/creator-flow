import { useEffect, useState } from "react";

import { listProjects, Project } from "../api/client";
import { EmptyState } from "../components/EmptyState";
import { DouyinSandboxPanel } from "../components/DouyinSandboxPanel";
import { ProviderConnectionStatePanel } from "../components/ProviderConnectionStatePanel";
import { ProviderCredentialReferencePanel } from "../components/ProviderCredentialReferencePanel";
import { ProviderOAuthBoundaryPanel } from "../components/ProviderOAuthBoundaryPanel";
import { ProviderRegistryPanel } from "../components/ProviderRegistryPanel";
import { ProviderReadinessSummaryPanel } from "../components/ProviderReadinessSummaryPanel";
import { ProviderSecurityAuditPanel } from "../components/ProviderSecurityAuditPanel";
import { ProviderTokenLifecyclePanel } from "../components/ProviderTokenLifecyclePanel";
import { StatusBadge } from "../components/StatusBadge";

type ProjectListPageProps = {
  onCreate: () => void;
  onOpen: (projectId: number) => void;
};

export function ProjectListPage({ onCreate, onOpen }: ProjectListPageProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [includeArchived, setIncludeArchived] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    listProjects({ includeArchived })
      .then((items) => {
        setProjects(items);
        setError(null);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [includeArchived]);

  return (
    <section className="mx-auto max-w-5xl px-4 py-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-stone-950">内容项目</h1>
          <p className="mt-1 text-sm text-stone-600">本地创建项目并显式导入素材。</p>
        </div>
        <button
          className="rounded bg-stone-950 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
          type="button"
          onClick={onCreate}
        >
          新建项目
        </button>
      </div>
      <ProviderRegistryPanel />
      <ProviderConnectionStatePanel />
      <ProviderCredentialReferencePanel />
      <ProviderSecurityAuditPanel />
      <ProviderOAuthBoundaryPanel />
      <ProviderTokenLifecyclePanel />
      <ProviderReadinessSummaryPanel />
      <DouyinSandboxPanel />
      <label className="mt-5 inline-flex items-center gap-2 text-sm text-stone-700">
        <input
          checked={includeArchived}
          className="h-4 w-4 accent-teal-700"
          type="checkbox"
          onChange={(event) => setIncludeArchived(event.target.checked)}
        />
        显示归档项目
      </label>

      {loading && <p className="mt-8 text-sm text-stone-600">正在加载项目...</p>}
      {error && <p className="mt-8 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {!loading && !error && projects.length === 0 && (
        <div className="mt-8">
          <EmptyState title="还没有项目" description="创建第一个内容项目后，可以为它添加文本、链接、图片或截图素材。" />
        </div>
      )}

      {!loading && !error && projects.length > 0 && (
        <div className="mt-6 overflow-hidden rounded border border-stone-200 bg-white">
          <table className="w-full table-fixed border-collapse text-left text-sm">
            <thead className="bg-stone-100 text-stone-700">
              <tr>
                <th className="w-2/5 px-4 py-3 font-medium">标题</th>
                <th className="w-1/6 px-4 py-3 font-medium">状态</th>
                <th className="w-24 px-4 py-3 font-medium">素材</th>
                <th className="w-1/4 px-4 py-3 font-medium">创建时间</th>
                <th className="px-4 py-3 font-medium">操作</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((project) => (
                <tr className="border-t border-stone-200" key={project.id}>
                  <td className="truncate px-4 py-3 font-medium text-stone-950">{project.title}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={project.status} />
                  </td>
                  <td className="px-4 py-3 text-stone-700">{project.material_count}</td>
                  <td className="px-4 py-3 text-stone-600">{new Date(project.created_at).toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <button className="text-sm font-medium text-teal-700 hover:text-teal-900" onClick={() => onOpen(project.id)}>
                      查看
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
