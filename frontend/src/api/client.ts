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
  source_type: "fake_local" | "sandbox" | "real";
  title: string;
  caption: string;
  publish_status: "pending_confirmation" | "confirmed" | "blocked" | "cancelled";
  confirmation_status: "confirmed" | "missing" | "invalid";
  created_at: string;
  updated_at: string;
  confirmed_at: string | null;
  cancelled_at: string | null;
  safe_status_message: string;
  last_status_change_reason: string;
};

export type PublishAttempt = {
  id: number;
  project_id: number;
  publish_intent_id: number;
  review_draft_id: number;
  provider_id: string;
  source_type: "fake_local" | "sandbox" | "real";
  attempt_status: "created" | "blocked" | "cancelled" | "failed_safe";
  guard_status: "passed_simulated" | "blocked";
  external_call_status: "not_called" | "blocked";
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  safe_status_message: string;
  last_status_change_reason: string;
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

export type PublicationMetricReviewSummary = {
  id: number;
  project_id: number;
  publication_record_id: number;
  source: string;
  is_fake_local: boolean;
  summary_text: string;
  highlights: string;
  low_performance_signals: string;
  next_observations: string;
  snapshot_count: number;
  metric_window_start: string | null;
  metric_window_end: string | null;
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

export type ProviderCapabilityMetadata = {
  supports_oauth: boolean;
  supports_metrics_read: boolean;
  supports_publish_prepare: boolean;
  supports_real_publish: boolean;
  supports_sandbox: boolean;
  supports_token_refresh: boolean;
  supports_disconnect: boolean;
  supports_revoke: boolean;
};

export type PlatformProvider = {
  provider_id: string;
  provider_name: string;
  provider_type: string;
  source_type: string;
  implementation_status: string;
  connection_status: string;
  is_available: boolean;
  is_real_provider: boolean;
  requires_user_authorization: boolean;
  capabilities: ProviderCapabilityMetadata;
  boundary_notes: string[];
};

export type ProviderRegistryListResponse = {
  providers: PlatformProvider[];
};

export type ProviderConnectionState = {
  provider_id: string;
  provider_name: string;
  source_type: string;
  implementation_status: string;
  connection_status: string;
  authorization_status: string;
  sensitive_storage_status: string;
  is_available: boolean;
  is_real_provider: boolean;
  requires_user_authorization: boolean;
  can_connect: boolean;
  can_refresh: boolean;
  can_revoke: boolean;
  can_disconnect: boolean;
  safe_status_message: string;
  boundary_notes: string[];
  last_status_change_reason?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type ProviderConnectionStateListResponse = {
  connections: ProviderConnectionState[];
};

export type ProviderCredentialReference = {
  provider_id: string;
  provider_name: string;
  source_type: string;
  implementation_status: string;
  reference_kind: string;
  reference_status: string;
  storage_status: string;
  redaction_policy_status: string;
  is_available: boolean;
  is_real_provider: boolean;
  requires_user_authorization: boolean;
  safe_display_name: string;
  safe_status_message: string;
  boundary_notes: string[];
  last_status_change_reason?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type ProviderCredentialReferenceListResponse = {
  credential_references: ProviderCredentialReference[];
};

export type ProviderSecurityAuditEvent = {
  audit_event_id: string;
  provider_id: string;
  provider_name: string;
  source_type: string;
  implementation_status: string;
  event_type: string;
  event_status: string;
  event_severity: string;
  actor_type: string;
  redaction_status: string;
  safe_event_message: string;
  safe_metadata: Record<string, unknown>;
  boundary_notes: string[];
  created_at: string;
};

export type ProviderSecurityAuditEventListResponse = {
  audit_events: ProviderSecurityAuditEvent[];
};

export type ListProviderSecurityAuditEventsOptions = {
  providerId?: string;
  limit?: number;
};

export type ProviderOAuthBoundary = {
  provider_id: string;
  provider_name: string;
  source_type: string;
  implementation_status: string;
  oauth_policy_status: string;
  state_policy_status: string;
  callback_policy_status: string;
  csrf_protection_status: string;
  redirect_uri_policy_status: string;
  token_exchange_policy_status: string;
  token_storage_policy_status: string;
  error_redaction_policy_status: string;
  audit_event_policy_status: string;
  is_available: boolean;
  is_real_provider: boolean;
  requires_user_authorization: boolean;
  can_start_oauth: boolean;
  can_handle_callback: boolean;
  can_exchange_token: boolean;
  can_refresh_token: boolean;
  can_revoke_token: boolean;
  safe_status_message: string;
  boundary_notes: string[];
  last_status_change_reason?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type ProviderOAuthBoundaryListResponse = {
  oauth_boundaries: ProviderOAuthBoundary[];
};

export type ProviderTokenLifecycleBoundary = {
  provider_id: string;
  provider_name: string;
  source_type: string;
  implementation_status: string;
  token_lifecycle_policy_status: string;
  token_storage_policy_status: string;
  refresh_policy_status: string;
  expiry_policy_status: string;
  revoke_policy_status: string;
  disconnect_policy_status: string;
  rotation_policy_status: string;
  error_redaction_policy_status: string;
  audit_event_policy_status: string;
  is_available: boolean;
  is_real_provider: boolean;
  requires_user_authorization: boolean;
  can_refresh_token: boolean;
  can_revoke_token: boolean;
  can_disconnect: boolean;
  can_rotate_token: boolean;
  can_mark_token_expired: boolean;
  safe_status_message: string;
  boundary_notes: string[];
  last_status_change_reason?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type ProviderTokenLifecycleBoundaryListResponse = {
  token_lifecycle_boundaries: ProviderTokenLifecycleBoundary[];
};

export type ProviderBoundaryReadinessItem = {
  boundary_id: string;
  boundary_name: string;
  readiness_status: string;
  is_blocking_real_integration: boolean;
  safe_status_message: string;
  source_metadata: Record<string, unknown>;
};

export type ProviderReadinessSummary = {
  provider_id: string;
  provider_name: string;
  source_type: string;
  implementation_status: string;
  is_available: boolean;
  is_real_provider: boolean;
  requires_user_authorization: boolean;
  overall_readiness_status: string;
  v0_9_poc_readiness_status: string;
  can_use_local_fake_workflow: boolean;
  is_safe_to_attempt_real_oauth: boolean;
  is_safe_to_store_tokens: boolean;
  is_safe_to_fetch_real_metrics: boolean;
  is_safe_to_publish: boolean;
  is_ready_for_v0_9_sandbox_poc: boolean;
  is_ready_for_v0_9_real_poc: boolean;
  readiness_items: ProviderBoundaryReadinessItem[];
  blocking_reasons: string[];
  next_safe_steps: string[];
  safe_summary: string;
  boundary_notes: string[];
};

export type ProviderReadinessSummaryListResponse = {
  readiness_summaries: ProviderReadinessSummary[];
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

export async function listPlatformProviders(): Promise<PlatformProvider[]> {
  const response = await request<ProviderRegistryListResponse>("/api/providers");
  return response.providers;
}

export async function listProviderConnectionStates(): Promise<ProviderConnectionState[]> {
  const response = await request<ProviderConnectionStateListResponse>("/api/provider-connections");
  return response.connections;
}

export async function listProviderCredentialReferences(): Promise<ProviderCredentialReference[]> {
  const response = await request<ProviderCredentialReferenceListResponse>("/api/provider-credential-references");
  return response.credential_references;
}

export async function listProviderSecurityAuditEvents(
  options: ListProviderSecurityAuditEventsOptions = {},
): Promise<ProviderSecurityAuditEvent[]> {
  const params = new URLSearchParams();
  if (options.providerId) {
    params.set("provider_id", options.providerId);
  }
  if (typeof options.limit === "number") {
    const safeLimit = Math.min(Math.max(Math.trunc(options.limit), 1), 100);
    params.set("limit", String(safeLimit));
  }
  const query = params.toString();
  const response = await request<ProviderSecurityAuditEventListResponse>(
    `/api/provider-security-audit-events${query ? `?${query}` : ""}`,
  );
  return response.audit_events;
}

export async function listProviderOAuthBoundaries(): Promise<ProviderOAuthBoundary[]> {
  const response = await request<ProviderOAuthBoundaryListResponse>("/api/provider-oauth-boundaries");
  return response.oauth_boundaries;
}

export async function listProviderTokenLifecycleBoundaries(): Promise<ProviderTokenLifecycleBoundary[]> {
  const response = await request<ProviderTokenLifecycleBoundaryListResponse>(
    "/api/provider-token-lifecycle-boundaries",
  );
  return response.token_lifecycle_boundaries;
}

export async function listProviderReadinessSummaries(): Promise<ProviderReadinessSummary[]> {
  const response = await request<ProviderReadinessSummaryListResponse>("/api/provider-readiness-summaries");
  return response.readiness_summaries;
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

export function getPublishAttempts(projectId: number): Promise<PublishAttempt[]> {
  return request<PublishAttempt[]>(`/api/projects/${projectId}/publish-attempts`);
}

export function createPublishAttempt(projectId: number, publishIntentId: number): Promise<PublishAttempt> {
  return request<PublishAttempt>(`/api/projects/${projectId}/publish-intents/${publishIntentId}/attempts`, {
    method: "POST",
  });
}

export function createPublishIntent(
  projectId: number,
  payload: {
    review_draft_id: number;
    target_platform: string;
    title: string;
    caption: string;
    confirm_publish_intent: true;
  },
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

export function listPublicationMetricReviewSummaries(
  projectId: number,
  publicationRecordId: number,
): Promise<PublicationMetricReviewSummary[]> {
  return request<PublicationMetricReviewSummary[]>(
    `/api/projects/${projectId}/publication-records/${publicationRecordId}/metric-review-summaries`,
  );
}

export function createFakePublicationMetricReviewSummary(
  projectId: number,
  publicationRecordId: number,
): Promise<PublicationMetricReviewSummary> {
  return request<PublicationMetricReviewSummary>(
    `/api/projects/${projectId}/publication-records/${publicationRecordId}/metric-review-summaries/fake`,
    {
      method: "POST",
    },
  );
}

export function getPublicationMetricReviewSummary(
  projectId: number,
  publicationRecordId: number,
  summaryId: number,
): Promise<PublicationMetricReviewSummary> {
  return request<PublicationMetricReviewSummary>(
    `/api/projects/${projectId}/publication-records/${publicationRecordId}/metric-review-summaries/${summaryId}`,
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
