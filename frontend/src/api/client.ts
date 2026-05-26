const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type Project = {
  id: number;
  title: string;
  description: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  material_count: number;
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

export type TopicCandidate = {
  id: number;
  project_id: number;
  generation_run_id: number;
  title: string;
  angle: string;
  audience: string;
  hook: string;
  rationale: string;
  status: "candidate" | "selected" | "dismissed";
  selected_at: string | null;
  created_at: string;
  updated_at: string;
  source_material_ids: number[];
};

export type TopicGenerationRun = {
  id: number;
  project_id: number;
  provider_name: string;
  provider_version: string;
  status: "running" | "succeeded" | "failed";
  requested_candidate_count: number;
  input_material_count: number;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
};

export type GenerateTopicCandidatesResponse = {
  run: TopicGenerationRun;
  candidates: TopicCandidate[];
};

export type ScriptDraft = {
  id: number;
  project_id: number;
  generation_run_id: number;
  topic_candidate_id: number;
  title: string;
  opening_hook: string;
  body: string;
  call_to_action: string;
  estimated_duration_seconds: number;
  rationale: string;
  status: "draft" | "selected" | "dismissed";
  selected_at: string | null;
  created_at: string;
  updated_at: string;
  source_material_ids: number[];
};

export type ScriptGenerationRun = {
  id: number;
  project_id: number;
  selected_topic_candidate_id: number;
  provider_name: string;
  provider_version: string;
  status: "running" | "succeeded" | "failed";
  requested_script_count: number;
  input_material_count: number;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
};

export type GenerateScriptDraftsResponse = {
  run: ScriptGenerationRun;
  script_drafts: ScriptDraft[];
};

export type StoryboardScene = {
  id: number;
  storyboard_draft_id: number;
  scene_order: number;
  scene_title: string;
  narration: string;
  visual_description: string;
  on_screen_text: string;
  estimated_duration_seconds: number;
  source_material_id: number | null;
  created_at: string;
};

export type Storyboard = {
  id: number;
  project_id: number;
  generation_run_id: number;
  topic_candidate_id: number;
  script_draft_id: number;
  title: string;
  summary: string;
  visual_style: string;
  status: "draft" | "selected" | "dismissed";
  selected_at: string | null;
  created_at: string;
  updated_at: string;
  source_material_ids: number[];
  scenes: StoryboardScene[];
};

export type StoryboardGenerationRun = {
  id: number;
  project_id: number;
  selected_topic_candidate_id: number;
  selected_script_draft_id: number;
  provider_name: string;
  provider_version: string;
  status: "running" | "succeeded" | "failed";
  requested_storyboard_count: number;
  input_material_count: number;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
};

export type GenerateStoryboardsResponse = {
  run: StoryboardGenerationRun;
  storyboards: Storyboard[];
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

export function listProjects(options: { includeArchived?: boolean } = {}): Promise<Project[]> {
  const params = new URLSearchParams();
  if (options.includeArchived) {
    params.set("include_archived", "true");
  }
  const query = params.toString();
  return request<Project[]>(`/api/projects${query ? `?${query}` : ""}`);
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

export function getTopicCandidates(projectId: number): Promise<TopicCandidate[]> {
  return request<TopicCandidate[]>(`/api/projects/${projectId}/topic-candidates`);
}

export function generateTopicCandidates(projectId: number): Promise<GenerateTopicCandidatesResponse> {
  return request<GenerateTopicCandidatesResponse>(`/api/projects/${projectId}/topic-candidates/generate`, {
    method: "POST",
    body: JSON.stringify({ candidate_count: 3 }),
  });
}

export function selectTopicCandidate(projectId: number, candidateId: number): Promise<TopicCandidate> {
  return request<TopicCandidate>(`/api/projects/${projectId}/topic-candidates/${candidateId}/select`, {
    method: "POST",
  });
}

export function getScriptDrafts(projectId: number): Promise<ScriptDraft[]> {
  return request<ScriptDraft[]>(`/api/projects/${projectId}/script-drafts`);
}

export function generateScriptDrafts(projectId: number): Promise<GenerateScriptDraftsResponse> {
  return request<GenerateScriptDraftsResponse>(`/api/projects/${projectId}/script-drafts/generate`, {
    method: "POST",
    body: JSON.stringify({ script_count: 2 }),
  });
}

export function selectScriptDraft(projectId: number, scriptDraftId: number): Promise<ScriptDraft> {
  return request<ScriptDraft>(`/api/projects/${projectId}/script-drafts/${scriptDraftId}/select`, {
    method: "POST",
  });
}

export function getStoryboards(projectId: number): Promise<Storyboard[]> {
  return request<Storyboard[]>(`/api/projects/${projectId}/storyboards`);
}

export function generateStoryboards(projectId: number): Promise<GenerateStoryboardsResponse> {
  return request<GenerateStoryboardsResponse>(`/api/projects/${projectId}/storyboards/generate`, {
    method: "POST",
    body: JSON.stringify({ storyboard_count: 1 }),
  });
}

export function selectStoryboard(projectId: number, storyboardId: number): Promise<Storyboard> {
  return request<Storyboard>(`/api/projects/${projectId}/storyboards/${storyboardId}/select`, {
    method: "POST",
  });
}

export function updateProject(
  projectId: number,
  payload: { title?: string; description?: string | null },
): Promise<Project> {
  return request<Project>(`/api/projects/${projectId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function archiveProject(projectId: number): Promise<Project> {
  return request<Project>(`/api/projects/${projectId}/archive`, {
    method: "POST",
  });
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
