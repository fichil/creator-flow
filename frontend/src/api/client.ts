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

export type RenderArtifact = {
  id: number;
  project_id: number;
  render_job_id: number;
  subtitle_draft_id: number | null;
  artifact_type: string;
  file_name: string;
  mime_type: string;
  file_size_bytes: number;
  duration_seconds: number;
  width: number;
  height: number;
  storage_path: string;
  checksum_sha256: string | null;
  created_at: string;
};

export type RenderJob = {
  id: number;
  project_id: number;
  storyboard_draft_id: number;
  renderer_name: string;
  renderer_version: string;
  status: "queued" | "running" | "succeeded" | "failed";
  requested_format: string;
  requested_aspect_ratio: string;
  requested_resolution: string;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  updated_at: string;
  artifact: RenderArtifact | null;
};

export type SubtitleCue = {
  id: number;
  subtitle_draft_id: number;
  cue_order: number;
  start_time_seconds: number;
  end_time_seconds: number;
  text: string;
  created_at: string;
};

export type SubtitleDraft = {
  id: number;
  project_id: number;
  script_draft_id: number;
  storyboard_draft_id: number;
  generator_name: string;
  generator_version: string;
  status: "draft" | "selected" | "dismissed";
  selected_at: string | null;
  created_at: string;
  updated_at: string;
  cues: SubtitleCue[];
};

export type ReviewDraft = {
  id: number;
  project_id: number;
  content_plan_id: number;
  generation_schedule_id: number | null;
  generation_run_id: number;
  title: string;
  draft_summary: string;
  input_source_summary: string;
  hotspot_source_summary: string | null;
  review_status: "pending_review" | "approved" | "rejected";
  created_at: string;
  updated_at: string;
};

export type PublishIntent = {
  id: number;
  project_id: number;
  review_draft_id: number;
  target_platform: string;
  title: string;
  caption: string;
  publish_status: "pending_confirmation" | "confirmed" | "cancelled";
  created_at: string;
  updated_at: string;
};

export type PublicationRecord = {
  id: number;
  project_id: number;
  publish_intent_id: number;
  target_platform: string;
  provider_name: string;
  external_publication_id: string | null;
  publication_status: "not_started" | "succeeded" | "failed";
  error_message: string | null;
  created_at: string;
  updated_at: string;
};

export type PublicationMetricSnapshot = {
  id: number;
  project_id: number;
  publication_record_id: number;
  source: string;
  captured_at: string;
  views: number | null;
  likes: number | null;
  comments: number | null;
  shares: number | null;
  favorites: number | null;
  average_watch_time_seconds: number | null;
  completion_rate: number | null;
  provider_payload_summary: string | null;
  created_at: string;
  updated_at: string;
};

export type ContentPlan = {
  id: number;
  project_id: number;
  name: string;
  account_positioning: string;
  content_type: string;
  target_frequency_per_week: number;
  preferences: string | null;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
};

export type GenerationSchedule = {
  id: number;
  project_id: number;
  content_plan_id: number;
  frequency_per_week: number;
  timezone: string;
  preferred_days: string | null;
  preferred_time: string;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
};

export type GenerationRun = {
  id: number;
  project_id: number;
  content_plan_id: number;
  generation_schedule_id: number | null;
  status: "queued" | "running" | "succeeded" | "failed";
  trigger_type: "manual" | "scheduled";
  input_summary: string;
  result_summary: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
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

export function getRenderJobs(projectId: number): Promise<RenderJob[]> {
  return request<RenderJob[]>(`/api/projects/${projectId}/renders`);
}

export function createRenderJob(projectId: number): Promise<RenderJob> {
  return request<RenderJob>(`/api/projects/${projectId}/renders`, {
    method: "POST",
    body: JSON.stringify({ requested_format: "mp4", requested_aspect_ratio: "9:16", requested_resolution: "1080x1920" }),
  });
}

export function getSubtitleDrafts(projectId: number): Promise<SubtitleDraft[]> {
  return request<SubtitleDraft[]>(`/api/projects/${projectId}/subtitle-drafts`);
}

export function createSubtitleDraft(projectId: number): Promise<SubtitleDraft> {
  return request<SubtitleDraft>(`/api/projects/${projectId}/subtitle-drafts`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export function selectSubtitleDraft(projectId: number, subtitleDraftId: number): Promise<SubtitleDraft> {
  return request<SubtitleDraft>(`/api/projects/${projectId}/subtitle-drafts/${subtitleDraftId}/select`, {
    method: "POST",
  });
}

export function getReviewDrafts(projectId: number): Promise<ReviewDraft[]> {
  return request<ReviewDraft[]>(`/api/projects/${projectId}/review-drafts`);
}

export function approveReviewDraft(projectId: number, reviewDraftId: number): Promise<ReviewDraft> {
  return request<ReviewDraft>(`/api/projects/${projectId}/review-drafts/${reviewDraftId}/approve`, {
    method: "POST",
  });
}

export function rejectReviewDraft(projectId: number, reviewDraftId: number): Promise<ReviewDraft> {
  return request<ReviewDraft>(`/api/projects/${projectId}/review-drafts/${reviewDraftId}/reject`, {
    method: "POST",
  });
}

export function getPublishIntents(projectId: number): Promise<PublishIntent[]> {
  return request<PublishIntent[]>(`/api/projects/${projectId}/publish-intents`);
}

export function createPublishIntent(
  projectId: number,
  payload: { review_draft_id: number; target_platform: string; title: string; caption: string },
): Promise<PublishIntent> {
  return request<PublishIntent>(`/api/projects/${projectId}/publish-intents`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function confirmPublishIntent(projectId: number, publishIntentId: number): Promise<PublishIntent> {
  return request<PublishIntent>(`/api/projects/${projectId}/publish-intents/${publishIntentId}/confirm`, {
    method: "POST",
  });
}

export function cancelPublishIntent(projectId: number, publishIntentId: number): Promise<PublishIntent> {
  return request<PublishIntent>(`/api/projects/${projectId}/publish-intents/${publishIntentId}/cancel`, {
    method: "POST",
  });
}

export function getPublicationRecords(projectId: number, publishIntentId: number): Promise<PublicationRecord[]> {
  return request<PublicationRecord[]>(
    `/api/projects/${projectId}/publish-intents/${publishIntentId}/publication-records`,
  );
}

export function fakePublishIntent(projectId: number, publishIntentId: number): Promise<PublicationRecord> {
  return request<PublicationRecord>(`/api/projects/${projectId}/publish-intents/${publishIntentId}/fake-publish`, {
    method: "POST",
  });
}

export function listPublicationMetrics(
  projectId: number,
  publicationRecordId: number,
): Promise<PublicationMetricSnapshot[]> {
  return request<PublicationMetricSnapshot[]>(
    `/api/projects/${projectId}/publication-records/${publicationRecordId}/metrics`,
  );
}

export function createFakePublicationMetric(
  projectId: number,
  publicationRecordId: number,
): Promise<PublicationMetricSnapshot> {
  return request<PublicationMetricSnapshot>(
    `/api/projects/${projectId}/publication-records/${publicationRecordId}/metrics/fake`,
    {
      method: "POST",
    },
  );
}

export function getPublicationMetric(
  projectId: number,
  publicationRecordId: number,
  metricSnapshotId: number,
): Promise<PublicationMetricSnapshot> {
  return request<PublicationMetricSnapshot>(
    `/api/projects/${projectId}/publication-records/${publicationRecordId}/metrics/${metricSnapshotId}`,
  );
}

export function getContentPlans(projectId: number): Promise<ContentPlan[]> {
  return request<ContentPlan[]>(`/api/projects/${projectId}/content-plans`);
}

export function createContentPlan(
  projectId: number,
  payload: {
    name: string;
    account_positioning: string;
    content_type: string;
    target_frequency_per_week: number;
    preferences?: string | null;
  },
): Promise<ContentPlan> {
  return request<ContentPlan>(`/api/projects/${projectId}/content-plans`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function enableContentPlan(projectId: number, contentPlanId: number): Promise<ContentPlan> {
  return request<ContentPlan>(`/api/projects/${projectId}/content-plans/${contentPlanId}/enable`, {
    method: "POST",
  });
}

export function disableContentPlan(projectId: number, contentPlanId: number): Promise<ContentPlan> {
  return request<ContentPlan>(`/api/projects/${projectId}/content-plans/${contentPlanId}/disable`, {
    method: "POST",
  });
}

export function getGenerationSchedules(projectId: number): Promise<GenerationSchedule[]> {
  return request<GenerationSchedule[]>(`/api/projects/${projectId}/generation-schedules`);
}

export function createGenerationSchedule(
  projectId: number,
  contentPlanId: number,
  payload: {
    frequency_per_week?: number | null;
    timezone: string;
    preferred_days?: string | null;
    preferred_time: string;
  },
): Promise<GenerationSchedule> {
  return request<GenerationSchedule>(`/api/projects/${projectId}/content-plans/${contentPlanId}/generation-schedules`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function enableGenerationSchedule(projectId: number, generationScheduleId: number): Promise<GenerationSchedule> {
  return request<GenerationSchedule>(`/api/projects/${projectId}/generation-schedules/${generationScheduleId}/enable`, {
    method: "POST",
  });
}

export function disableGenerationSchedule(projectId: number, generationScheduleId: number): Promise<GenerationSchedule> {
  return request<GenerationSchedule>(`/api/projects/${projectId}/generation-schedules/${generationScheduleId}/disable`, {
    method: "POST",
  });
}

export function getGenerationRuns(projectId: number): Promise<GenerationRun[]> {
  return request<GenerationRun[]>(`/api/projects/${projectId}/generation-runs`);
}

export function createGenerationRun(
  projectId: number,
  contentPlanId: number,
  payload: { generation_schedule_id?: number } = {},
): Promise<GenerationRun> {
  return request<GenerationRun>(`/api/projects/${projectId}/content-plans/${contentPlanId}/generation-runs`, {
    method: "POST",
    body: JSON.stringify(payload),
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
