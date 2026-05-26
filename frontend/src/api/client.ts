const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type Project = {
  id: number;
  title: string;
  description: string | null;
  status: string;
  created_at: string;
  updated_at: string;
};

export type Material = {
  id: number;
  project_id: number;
  material_type: string;
  title: string | null;
  text_content: string | null;
  source_url: string | null;
  stored_file_path: string | null;
  original_file_name: string | null;
  created_at: string;
};

export type ProjectDetail = Project & {
  materials: Material[];
};

type TextMaterialType = "text" | "summary" | "project_record";
type FileMaterialType = "image" | "screenshot";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: init?.body instanceof FormData ? undefined : { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    let message = `请求失败 (${response.status})`;
    try {
      const body = await response.json();
      message = typeof body.detail === "string" ? body.detail : message;
    } catch {
      // Keep the status-based message when the response is not JSON.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function listProjects(): Promise<Project[]> {
  return request<Project[]>("/api/projects");
}

export function createProject(payload: { title: string; description?: string }): Promise<Project> {
  return request<Project>("/api/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getProject(projectId: number): Promise<ProjectDetail> {
  return request<ProjectDetail>(`/api/projects/${projectId}`);
}

export function addTextMaterial(
  projectId: number,
  payload: { material_type: TextMaterialType; title?: string; text_content: string },
): Promise<Material> {
  return request<Material>(`/api/projects/${projectId}/materials/text`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function addLinkMaterial(
  projectId: number,
  payload: { title?: string; source_url: string },
): Promise<Material> {
  return request<Material>(`/api/projects/${projectId}/materials/link`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function addFileMaterial(
  projectId: number,
  payload: { material_type: FileMaterialType; title?: string; file: File },
): Promise<Material> {
  const formData = new FormData();
  formData.append("material_type", payload.material_type);
  if (payload.title) {
    formData.append("title", payload.title);
  }
  formData.append("file", payload.file);

  return request<Material>(`/api/projects/${projectId}/materials/file`, {
    method: "POST",
    body: formData,
  });
}
