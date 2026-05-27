import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProjectDetailPage } from "./ProjectDetailPage";
import type {
  ContentPlan,
  GenerationRun,
  GenerationSchedule,
  PublicationMetricSnapshot,
  PublicationRecord,
  PublishIntent,
  ProjectDetail,
  RenderJob,
  ReviewDraft,
  ScriptDraft,
  Storyboard,
  SubtitleDraft,
  TopicCandidate,
} from "../api/client";

const baseProject: ProjectDetail = {
  id: 1,
  title: "Topic UI project",
  description: "A project for topic candidate UI tests.",
  status: "materials_ready",
  created_at: "2026-05-26T08:00:00Z",
  updated_at: "2026-05-26T08:00:00Z",
  material_count: 1,
  materials: [
    {
      id: 11,
      project_id: 1,
      material_type: "text",
      title: "Imported note",
      text_content: "User supplied note.",
      source_url: null,
      stored_file_path: null,
      original_file_name: null,
      created_at: "2026-05-26T08:01:00Z",
    },
  ],
};

const candidateOne: TopicCandidate = {
  id: 101,
  project_id: 1,
  generation_run_id: 201,
  title: "Problem-first topic",
  angle: "Turn a concrete problem into a short story",
  audience: "Developers facing similar workflow blocks",
  hook: "Here is the small workflow issue that slowed the project down.",
  rationale: "Based on the imported material.",
  status: "candidate",
  selected_at: null,
  created_at: "2026-05-26T08:02:00Z",
  updated_at: "2026-05-26T08:02:00Z",
  source_material_ids: [11],
};

const candidateTwo: TopicCandidate = {
  ...candidateOne,
  id: 102,
  title: "Build log topic",
  status: "selected",
  selected_at: "2026-05-26T08:03:00Z",
};

const scriptDraftOne: ScriptDraft = {
  id: 501,
  project_id: 1,
  generation_run_id: 601,
  topic_candidate_id: 102,
  title: "Problem-first script",
  opening_hook: "This workflow looked small until it blocked the whole project.",
  body: "First, show the bug. Then explain the fix. Close with the repeatable workflow.",
  call_to_action: "Save this flow for your next debugging session.",
  estimated_duration_seconds: 58,
  rationale: "Built from the selected topic and imported note.",
  status: "draft",
  selected_at: null,
  created_at: "2026-05-26T08:06:00Z",
  updated_at: "2026-05-26T08:06:00Z",
  source_material_ids: [11],
};

const scriptDraftTwo: ScriptDraft = {
  ...scriptDraftOne,
  id: 502,
  title: "Build log script",
  status: "selected",
  selected_at: "2026-05-26T08:07:00Z",
};

const storyboardOne: Storyboard = {
  id: 801,
  project_id: 1,
  generation_run_id: 901,
  topic_candidate_id: 102,
  script_draft_id: 502,
  title: "Storyboard walkthrough",
  summary: "A source-backed storyboard for the selected script.",
  visual_style: "Clean screen-recording style",
  status: "draft",
  selected_at: null,
  created_at: "2026-05-26T08:10:00Z",
  updated_at: "2026-05-26T08:10:00Z",
  source_material_ids: [11],
  scenes: [
    {
      id: 1002,
      storyboard_draft_id: 801,
      scene_order: 2,
      scene_title: "Show the decision",
      narration: "Use the selected angle to explain the decision.",
      visual_description: "Highlight the planning choice in the project view.",
      on_screen_text: "The decision",
      estimated_duration_seconds: 18,
      source_material_id: 11,
      created_at: "2026-05-26T08:10:00Z",
    },
    {
      id: 1001,
      storyboard_draft_id: 801,
      scene_order: 1,
      scene_title: "Set up the problem",
      narration: "Start with the workflow problem.",
      visual_description: "Show the imported material that anchors the story.",
      on_screen_text: "The problem",
      estimated_duration_seconds: 12,
      source_material_id: 11,
      created_at: "2026-05-26T08:10:00Z",
    },
  ],
};

const storyboardTwo: Storyboard = {
  ...storyboardOne,
  id: 802,
  title: "Selected storyboard",
  status: "selected",
  selected_at: "2026-05-26T08:11:00Z",
  scenes: storyboardOne.scenes.map((scene) => ({
    ...scene,
    id: scene.id + 10,
    storyboard_draft_id: 802,
  })),
};

const renderJobOne: RenderJob = {
  id: 1201,
  project_id: 1,
  storyboard_draft_id: 802,
  renderer_name: "fake_renderer",
  renderer_version: "0.1",
  status: "succeeded",
  requested_format: "mp4",
  requested_aspect_ratio: "9:16",
  requested_resolution: "1080x1920",
  error_message: null,
  created_at: "2026-05-26T08:15:00Z",
  started_at: "2026-05-26T08:15:01Z",
  completed_at: "2026-05-26T08:15:02Z",
  updated_at: "2026-05-26T08:15:02Z",
  artifact: {
    id: 1301,
    project_id: 1,
    render_job_id: 1201,
    subtitle_draft_id: 1301,
    artifact_type: "fake_preview_manifest",
    file_name: "project-1-render-1201-preview-manifest.json",
    mime_type: "application/json",
    file_size_bytes: 386,
    duration_seconds: 30,
    width: 1080,
    height: 1920,
    storage_path: "data/local/render_previews/project-1/project-1-render-1201-preview-manifest.json",
    checksum_sha256: "a".repeat(64),
    created_at: "2026-05-26T08:15:02Z",
  },
};

const renderJobWithoutArtifact: RenderJob = {
  ...renderJobOne,
  id: 1202,
  artifact: null,
};

const queuedRenderJob: RenderJob = {
  ...renderJobOne,
  id: 1203,
  status: "queued",
  started_at: null,
  completed_at: null,
  artifact: null,
};

const subtitleDraftOne: SubtitleDraft = {
  id: 1301,
  project_id: 1,
  script_draft_id: 502,
  storyboard_draft_id: 802,
  generator_name: "fake_subtitle_generator",
  generator_version: "0.1",
  status: "draft",
  selected_at: null,
  created_at: "2026-05-26T08:16:00Z",
  updated_at: "2026-05-26T08:16:00Z",
  cues: [
    {
      id: 1402,
      subtitle_draft_id: 1301,
      cue_order: 2,
      start_time_seconds: 12,
      end_time_seconds: 30,
      text: "Use deterministic subtitle cue metadata.",
      created_at: "2026-05-26T08:16:00Z",
    },
    {
      id: 1401,
      subtitle_draft_id: 1301,
      cue_order: 1,
      start_time_seconds: 0,
      end_time_seconds: 12,
      text: "Start with the selected storyboard.",
      created_at: "2026-05-26T08:16:00Z",
    },
  ],
};

const subtitleDraftTwo: SubtitleDraft = {
  ...subtitleDraftOne,
  id: 1302,
  status: "selected",
  selected_at: "2026-05-26T08:17:00Z",
  cues: subtitleDraftOne.cues.map((cue) => ({
    ...cue,
    id: cue.id + 10,
    subtitle_draft_id: 1302,
  })),
};

const subtitleDraftWithoutCues: SubtitleDraft = {
  ...subtitleDraftOne,
  id: 1303,
  cues: [],
};

const reviewDraftPending: ReviewDraft = {
  id: 1501,
  project_id: 1,
  content_plan_id: 401,
  generation_schedule_id: null,
  generation_run_id: 301,
  title: "Manual run review draft",
  draft_summary: "Deterministic fake draft summary from a manual run.",
  input_source_summary: "ContentPlan #401 plus GenerationRun #301.",
  hotspot_source_summary: null,
  review_status: "pending_review",
  created_at: "2026-05-26T08:19:00Z",
  updated_at: "2026-05-26T08:19:00Z",
};

const reviewDraftApproved: ReviewDraft = {
  ...reviewDraftPending,
  id: 1502,
  generation_schedule_id: 701,
  title: "Approved review draft",
  hotspot_source_summary: "No external hotspot source used.",
  review_status: "approved",
  updated_at: "2026-05-26T08:20:00Z",
};

const reviewDraftRejected: ReviewDraft = {
  ...reviewDraftPending,
  id: 1503,
  title: "Rejected review draft",
  review_status: "rejected",
  updated_at: "2026-05-26T08:21:00Z",
};

const publishIntentPending: PublishIntent = {
  id: 1701,
  project_id: 1,
  review_draft_id: 1502,
  target_platform: "douyin",
  title: "Approved review draft",
  caption: "Deterministic fake draft summary from a manual run.",
  publish_status: "pending_confirmation",
  created_at: "2026-05-26T08:28:00Z",
  updated_at: "2026-05-26T08:28:00Z",
};

const publishIntentConfirmed: PublishIntent = {
  ...publishIntentPending,
  id: 1702,
  publish_status: "confirmed",
  updated_at: "2026-05-26T08:29:00Z",
};

const publicationRecordNotStarted: PublicationRecord = {
  id: 1801,
  project_id: 1,
  publish_intent_id: 1702,
  target_platform: "douyin",
  provider_name: "placeholder",
  external_publication_id: null,
  publication_status: "not_started",
  error_message: null,
  created_at: "2026-05-26T08:29:00Z",
  updated_at: "2026-05-26T08:29:00Z",
};

const publicationRecordSucceeded: PublicationRecord = {
  ...publicationRecordNotStarted,
  provider_name: "fake_publisher",
  external_publication_id: "fake-publication-1801",
  publication_status: "succeeded",
  updated_at: "2026-05-26T08:30:00Z",
};

const metricSnapshotOne: PublicationMetricSnapshot = {
  id: 1901,
  project_id: 1,
  publication_record_id: 1801,
  source: "fake_local",
  captured_at: "2026-05-26T08:31:00Z",
  views: 248,
  likes: 24,
  comments: 9,
  shares: 6,
  favorites: 13,
  average_watch_time_seconds: 12.4,
  completion_rate: 0.72,
  provider_payload_summary: "fake/local metrics generated by FakeMetricsProvider; not real platform performance",
  created_at: "2026-05-26T08:31:00Z",
  updated_at: "2026-05-26T08:31:00Z",
};

const contentPlanOne: ContentPlan = {
  id: 401,
  project_id: 1,
  name: "Weekly AI dev log",
  account_positioning: "Chinese developer sharing practical AI workflow notes",
  content_type: "programmer_real_problem",
  target_frequency_per_week: 3,
  preferences: '{"tone":"practical"}',
  is_enabled: true,
  created_at: "2026-05-26T08:22:00Z",
  updated_at: "2026-05-26T08:22:00Z",
};

const disabledContentPlan: ContentPlan = {
  ...contentPlanOne,
  id: 402,
  name: "Disabled launch notes",
  is_enabled: false,
};

const generationScheduleOne: GenerationSchedule = {
  id: 701,
  project_id: 1,
  content_plan_id: 401,
  frequency_per_week: 3,
  timezone: "Asia/Shanghai",
  preferred_days: "Mon,Wed,Fri",
  preferred_time: "09:30",
  is_enabled: true,
  created_at: "2026-05-26T08:23:00Z",
  updated_at: "2026-05-26T08:23:00Z",
};

const disabledGenerationSchedule: GenerationSchedule = {
  ...generationScheduleOne,
  id: 702,
  preferred_time: "18:00",
  is_enabled: false,
};

const generationRunOne: GenerationRun = {
  id: 1601,
  project_id: 1,
  content_plan_id: 401,
  generation_schedule_id: null,
  status: "succeeded",
  trigger_type: "manual",
  input_summary: "manual trigger for project_id=1; content_plan_id=401",
  result_summary: "deterministic fake manual generation run succeeded",
  error_message: null,
  created_at: "2026-05-26T08:24:00Z",
  updated_at: "2026-05-26T08:24:00Z",
};

type ServerOptions = {
  project?: ProjectDetail;
  candidates?: TopicCandidate[];
  scriptDrafts?: ScriptDraft[];
  storyboards?: Storyboard[];
  renderJobs?: RenderJob[];
  subtitleDrafts?: SubtitleDraft[];
  reviewDrafts?: ReviewDraft[];
  publishIntents?: PublishIntent[];
  publicationRecords?: Record<number, PublicationRecord[]>;
  publicationMetrics?: Record<number, PublicationMetricSnapshot[]>;
  contentPlans?: ContentPlan[];
  generationSchedules?: GenerationSchedule[];
  generationRuns?: GenerationRun[];
  generateError?: string;
  generateScriptDraftsError?: string;
  generateStoryboardsError?: string;
  createRenderError?: string;
  createSubtitleDraftError?: string;
  createPublishIntentError?: string;
  createMetricError?: string;
  selectError?: string;
  selectScriptDraftError?: string;
  selectStoryboardError?: string;
  selectSubtitleDraftError?: string;
};

function jsonResponse(body: unknown, status = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      headers: { "Content-Type": "application/json" },
      status,
    }),
  );
}

function installFetchMock(options: ServerOptions = {}) {
  const project = options.project ?? baseProject;
  let candidates = [...(options.candidates ?? [])];
  let scriptDrafts = [...(options.scriptDrafts ?? [])];
  let storyboards = [...(options.storyboards ?? [])];
  let renderJobs = [...(options.renderJobs ?? [])];
  let subtitleDrafts = [...(options.subtitleDrafts ?? [])];
  let reviewDrafts = [...(options.reviewDrafts ?? [])];
  let publishIntents = [...(options.publishIntents ?? [])];
  let publicationRecordsByIntentId: Record<number, PublicationRecord[]> = Object.fromEntries(
    Object.entries(options.publicationRecords ?? {}).map(([intentId, records]) => [Number(intentId), [...records]]),
  );
  let publicationMetricsByRecordId: Record<number, PublicationMetricSnapshot[]> = Object.fromEntries(
    Object.entries(options.publicationMetrics ?? {}).map(([recordId, metrics]) => [Number(recordId), [...metrics]]),
  );
  let contentPlans = [...(options.contentPlans ?? [])];
  let generationSchedules = [...(options.generationSchedules ?? [])];
  let generationRuns = [...(options.generationRuns ?? [])];
  const calls: string[] = [];
  const bodies: Record<string, string | undefined> = {};

  const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(input.toString());
    const method = init?.method ?? "GET";
    const call = `${method} ${url.pathname}`;
    calls.push(call);
    bodies[call] = typeof init?.body === "string" ? init.body : undefined;

    if (method === "GET" && url.pathname === "/api/projects/1") {
      return jsonResponse(project);
    }
    if (method === "GET" && url.pathname === "/api/projects/1/topic-candidates") {
      return jsonResponse(candidates);
    }
    if (method === "GET" && url.pathname === "/api/projects/1/script-drafts") {
      return jsonResponse(scriptDrafts);
    }
    if (method === "GET" && url.pathname === "/api/projects/1/storyboards") {
      return jsonResponse(storyboards);
    }
    if (method === "GET" && url.pathname === "/api/projects/1/renders") {
      return jsonResponse(renderJobs);
    }
    if (method === "GET" && url.pathname === "/api/projects/1/subtitle-drafts") {
      return jsonResponse(subtitleDrafts);
    }
    if (method === "GET" && url.pathname === "/api/projects/1/review-drafts") {
      return jsonResponse(reviewDrafts);
    }
    if (method === "GET" && url.pathname === "/api/projects/1/publish-intents") {
      return jsonResponse(publishIntents);
    }
    const listPublicationRecordsMatch = url.pathname.match(
      /^\/api\/projects\/1\/publish-intents\/(\d+)\/publication-records$/,
    );
    if (method === "GET" && listPublicationRecordsMatch) {
      const publishIntentId = Number(listPublicationRecordsMatch[1]);
      return jsonResponse(publicationRecordsByIntentId[publishIntentId] ?? []);
    }
    const listPublicationMetricsMatch = url.pathname.match(
      /^\/api\/projects\/1\/publication-records\/(\d+)\/metrics$/,
    );
    if (method === "GET" && listPublicationMetricsMatch) {
      const publicationRecordId = Number(listPublicationMetricsMatch[1]);
      return jsonResponse(publicationMetricsByRecordId[publicationRecordId] ?? []);
    }
    const createFakeMetricMatch = url.pathname.match(
      /^\/api\/projects\/1\/publication-records\/(\d+)\/metrics\/fake$/,
    );
    if (method === "POST" && createFakeMetricMatch) {
      if (options.createMetricError) {
        return jsonResponse({ detail: options.createMetricError }, 409);
      }
      const publicationRecordId = Number(createFakeMetricMatch[1]);
      const createdMetric: PublicationMetricSnapshot = {
        ...metricSnapshotOne,
        id: 1999,
        publication_record_id: publicationRecordId,
        captured_at: "2026-05-26T08:32:00Z",
        created_at: "2026-05-26T08:32:00Z",
        updated_at: "2026-05-26T08:32:00Z",
      };
      publicationMetricsByRecordId = {
        ...publicationMetricsByRecordId,
        [publicationRecordId]: [createdMetric, ...(publicationMetricsByRecordId[publicationRecordId] ?? [])],
      };
      return jsonResponse(createdMetric, 201);
    }
    if (method === "GET" && url.pathname === "/api/projects/1/content-plans") {
      return jsonResponse(contentPlans);
    }
    if (method === "GET" && url.pathname === "/api/projects/1/generation-schedules") {
      return jsonResponse(generationSchedules);
    }
    if (method === "GET" && url.pathname === "/api/projects/1/generation-runs") {
      return jsonResponse(generationRuns);
    }
    if (method === "POST" && url.pathname === "/api/projects/1/topic-candidates/generate") {
      if (options.generateError) {
        return jsonResponse({ detail: options.generateError }, 409);
      }
      candidates = [
        candidateOne,
        { ...candidateOne, id: 103, title: "Checklist topic" },
        { ...candidateTwo, status: "candidate", selected_at: null },
      ];
      return jsonResponse({
        run: {
          id: 301,
          project_id: 1,
          provider_name: "fake_llm",
          provider_version: "0.1",
          status: "succeeded",
          requested_candidate_count: 3,
          input_material_count: 1,
          error_message: null,
          created_at: "2026-05-26T08:04:00Z",
          completed_at: "2026-05-26T08:04:00Z",
        },
        candidates,
      });
    }
    if (method === "POST" && url.pathname === "/api/projects/1/script-drafts/generate") {
      if (options.generateScriptDraftsError) {
        return jsonResponse({ detail: options.generateScriptDraftsError }, 409);
      }
      scriptDrafts = [scriptDraftOne, { ...scriptDraftOne, id: 503, title: "Checklist script" }];
      return jsonResponse({
        run: {
          id: 701,
          project_id: 1,
          selected_topic_candidate_id: 102,
          provider_name: "fake_llm",
          provider_version: "0.1",
          status: "succeeded",
          requested_script_count: 2,
          input_material_count: 1,
          error_message: null,
          created_at: "2026-05-26T08:08:00Z",
          completed_at: "2026-05-26T08:08:00Z",
        },
        script_drafts: scriptDrafts,
      });
    }
    if (method === "POST" && url.pathname === "/api/projects/1/storyboards/generate") {
      if (options.generateStoryboardsError) {
        return jsonResponse({ detail: options.generateStoryboardsError }, 409);
      }
      storyboards = [storyboardOne];
      return jsonResponse({
        run: {
          id: 1001,
          project_id: 1,
          selected_topic_candidate_id: 102,
          selected_script_draft_id: 502,
          provider_name: "fake_llm",
          provider_version: "0.1",
          status: "succeeded",
          requested_storyboard_count: 1,
          input_material_count: 1,
          error_message: null,
          created_at: "2026-05-26T08:12:00Z",
          completed_at: "2026-05-26T08:12:00Z",
        },
        storyboards,
      });
    }
    if (method === "POST" && url.pathname === "/api/projects/1/topic-candidates/101/select") {
      if (options.selectError) {
        return jsonResponse({ detail: options.selectError }, 409);
      }
      candidates = candidates.map((candidate) => ({
        ...candidate,
        status: candidate.id === 101 ? "selected" : "candidate",
        selected_at: candidate.id === 101 ? "2026-05-26T08:05:00Z" : null,
      }));
      return jsonResponse(candidates.find((candidate) => candidate.id === 101));
    }
    if (method === "POST" && url.pathname === "/api/projects/1/script-drafts/501/select") {
      if (options.selectScriptDraftError) {
        return jsonResponse({ detail: options.selectScriptDraftError }, 409);
      }
      scriptDrafts = scriptDrafts.map((scriptDraft) => ({
        ...scriptDraft,
        status: (scriptDraft.id === 501 ? "selected" : "draft") as ScriptDraft["status"],
        selected_at: scriptDraft.id === 501 ? "2026-05-26T08:09:00Z" : null,
      }));
      return jsonResponse(scriptDrafts.find((scriptDraft) => scriptDraft.id === 501));
    }
    if (method === "POST" && url.pathname === "/api/projects/1/storyboards/801/select") {
      if (options.selectStoryboardError) {
        return jsonResponse({ detail: options.selectStoryboardError }, 409);
      }
      storyboards = storyboards.map((storyboard) => ({
        ...storyboard,
        status: (storyboard.id === 801 ? "selected" : "draft") as Storyboard["status"],
        selected_at: storyboard.id === 801 ? "2026-05-26T08:13:00Z" : null,
      }));
      return jsonResponse(storyboards.find((storyboard) => storyboard.id === 801));
    }
    if (method === "POST" && url.pathname === "/api/projects/1/renders") {
      if (options.createRenderError) {
        return jsonResponse({ detail: options.createRenderError }, 409);
      }
      renderJobs = [renderJobOne];
      return jsonResponse(renderJobOne);
    }
    if (method === "POST" && url.pathname === "/api/projects/1/subtitle-drafts") {
      if (options.createSubtitleDraftError) {
        return jsonResponse({ detail: options.createSubtitleDraftError }, 409);
      }
      subtitleDrafts = [subtitleDraftOne];
      return jsonResponse(subtitleDraftOne);
    }
    if (method === "POST" && url.pathname === "/api/projects/1/subtitle-drafts/1301/select") {
      if (options.selectSubtitleDraftError) {
        return jsonResponse({ detail: options.selectSubtitleDraftError }, 409);
      }
      subtitleDrafts = subtitleDrafts.map((subtitleDraft) => ({
        ...subtitleDraft,
        status: (subtitleDraft.id === 1301 ? "selected" : "draft") as SubtitleDraft["status"],
        selected_at: subtitleDraft.id === 1301 ? "2026-05-26T08:18:00Z" : null,
      }));
      return jsonResponse(subtitleDrafts.find((subtitleDraft) => subtitleDraft.id === 1301));
    }
    if (method === "POST" && url.pathname === "/api/projects/1/content-plans") {
      const payload = JSON.parse(String(init?.body)) as {
        name: string;
        account_positioning: string;
        content_type: string;
        target_frequency_per_week: number;
        preferences?: string | null;
      };
      const createdPlan: ContentPlan = {
        id: 499,
        project_id: 1,
        name: payload.name,
        account_positioning: payload.account_positioning,
        content_type: payload.content_type,
        target_frequency_per_week: payload.target_frequency_per_week,
        preferences: payload.preferences ?? null,
        is_enabled: true,
        created_at: "2026-05-26T08:25:00Z",
        updated_at: "2026-05-26T08:25:00Z",
      };
      contentPlans = [createdPlan, ...contentPlans];
      return jsonResponse(createdPlan, 201);
    }
    const enableContentPlanMatch = url.pathname.match(/^\/api\/projects\/1\/content-plans\/(\d+)\/enable$/);
    if (method === "POST" && enableContentPlanMatch) {
      const contentPlanId = Number(enableContentPlanMatch[1]);
      contentPlans = contentPlans.map((contentPlan) => ({
        ...contentPlan,
        is_enabled: contentPlan.id === contentPlanId ? true : contentPlan.is_enabled,
      }));
      return jsonResponse(contentPlans.find((contentPlan) => contentPlan.id === contentPlanId));
    }
    const disableContentPlanMatch = url.pathname.match(/^\/api\/projects\/1\/content-plans\/(\d+)\/disable$/);
    if (method === "POST" && disableContentPlanMatch) {
      const contentPlanId = Number(disableContentPlanMatch[1]);
      contentPlans = contentPlans.map((contentPlan) => ({
        ...contentPlan,
        is_enabled: contentPlan.id === contentPlanId ? false : contentPlan.is_enabled,
      }));
      return jsonResponse(contentPlans.find((contentPlan) => contentPlan.id === contentPlanId));
    }
    const createGenerationScheduleMatch = url.pathname.match(
      /^\/api\/projects\/1\/content-plans\/(\d+)\/generation-schedules$/,
    );
    if (method === "POST" && createGenerationScheduleMatch) {
      const contentPlanId = Number(createGenerationScheduleMatch[1]);
      const contentPlan = contentPlans.find((item) => item.id === contentPlanId) ?? contentPlanOne;
      const payload = JSON.parse(String(init?.body)) as {
        frequency_per_week?: number | null;
        timezone: string;
        preferred_days?: string | null;
        preferred_time: string;
      };
      const createdSchedule: GenerationSchedule = {
        id: 799,
        project_id: 1,
        content_plan_id: contentPlanId,
        frequency_per_week: payload.frequency_per_week ?? contentPlan.target_frequency_per_week,
        timezone: payload.timezone,
        preferred_days: payload.preferred_days ?? null,
        preferred_time: payload.preferred_time,
        is_enabled: true,
        created_at: "2026-05-26T08:26:00Z",
        updated_at: "2026-05-26T08:26:00Z",
      };
      generationSchedules = [createdSchedule, ...generationSchedules];
      return jsonResponse(createdSchedule, 201);
    }
    const enableGenerationScheduleMatch = url.pathname.match(/^\/api\/projects\/1\/generation-schedules\/(\d+)\/enable$/);
    if (method === "POST" && enableGenerationScheduleMatch) {
      const generationScheduleId = Number(enableGenerationScheduleMatch[1]);
      generationSchedules = generationSchedules.map((generationSchedule) => ({
        ...generationSchedule,
        is_enabled: generationSchedule.id === generationScheduleId ? true : generationSchedule.is_enabled,
      }));
      return jsonResponse(generationSchedules.find((generationSchedule) => generationSchedule.id === generationScheduleId));
    }
    const disableGenerationScheduleMatch = url.pathname.match(/^\/api\/projects\/1\/generation-schedules\/(\d+)\/disable$/);
    if (method === "POST" && disableGenerationScheduleMatch) {
      const generationScheduleId = Number(disableGenerationScheduleMatch[1]);
      generationSchedules = generationSchedules.map((generationSchedule) => ({
        ...generationSchedule,
        is_enabled: generationSchedule.id === generationScheduleId ? false : generationSchedule.is_enabled,
      }));
      return jsonResponse(generationSchedules.find((generationSchedule) => generationSchedule.id === generationScheduleId));
    }
    const createGenerationRunMatch = url.pathname.match(/^\/api\/projects\/1\/content-plans\/(\d+)\/generation-runs$/);
    if (method === "POST" && createGenerationRunMatch) {
      const contentPlanId = Number(createGenerationRunMatch[1]);
      const payload = JSON.parse(String(init?.body)) as { generation_schedule_id?: number };
      const createdRun: GenerationRun = {
        id: 1699,
        project_id: 1,
        content_plan_id: contentPlanId,
        generation_schedule_id: payload.generation_schedule_id ?? null,
        status: "succeeded",
        trigger_type: "manual",
        input_summary: `manual trigger for content_plan_id=${contentPlanId}`,
        result_summary: "deterministic fake manual generation run succeeded",
        error_message: null,
        created_at: "2026-05-26T08:27:00Z",
        updated_at: "2026-05-26T08:27:00Z",
      };
      generationRuns = [createdRun, ...generationRuns];
      reviewDrafts = [
        {
          ...reviewDraftPending,
          id: 1599,
          content_plan_id: contentPlanId,
          generation_schedule_id: payload.generation_schedule_id ?? null,
          generation_run_id: createdRun.id,
          title: "Review draft from new manual run",
          created_at: "2026-05-26T08:27:00Z",
          updated_at: "2026-05-26T08:27:00Z",
        },
        ...reviewDrafts,
      ];
      return jsonResponse(createdRun, 201);
    }
    const approveReviewDraftMatch = url.pathname.match(/^\/api\/projects\/1\/review-drafts\/(\d+)\/approve$/);
    if (method === "POST" && approveReviewDraftMatch) {
      const reviewDraftId = Number(approveReviewDraftMatch[1]);
      reviewDrafts = reviewDrafts.map((reviewDraft) => ({
        ...reviewDraft,
        review_status: reviewDraft.id === reviewDraftId ? "approved" : reviewDraft.review_status,
        updated_at: reviewDraft.id === reviewDraftId ? "2026-05-26T08:22:00Z" : reviewDraft.updated_at,
      }));
      return jsonResponse(reviewDrafts.find((reviewDraft) => reviewDraft.id === reviewDraftId));
    }
    const rejectReviewDraftMatch = url.pathname.match(/^\/api\/projects\/1\/review-drafts\/(\d+)\/reject$/);
    if (method === "POST" && rejectReviewDraftMatch) {
      const reviewDraftId = Number(rejectReviewDraftMatch[1]);
      reviewDrafts = reviewDrafts.map((reviewDraft) => ({
        ...reviewDraft,
        review_status: reviewDraft.id === reviewDraftId ? "rejected" : reviewDraft.review_status,
        updated_at: reviewDraft.id === reviewDraftId ? "2026-05-26T08:23:00Z" : reviewDraft.updated_at,
      }));
      return jsonResponse(reviewDrafts.find((reviewDraft) => reviewDraft.id === reviewDraftId));
    }
    if (method === "POST" && url.pathname === "/api/projects/1/publish-intents") {
      if (options.createPublishIntentError) {
        return jsonResponse({ detail: options.createPublishIntentError }, 409);
      }
      const payload = JSON.parse(String(init?.body)) as {
        review_draft_id: number;
        target_platform: string;
        title: string;
        caption: string;
      };
      const createdIntent: PublishIntent = {
        id: 1799,
        project_id: 1,
        review_draft_id: payload.review_draft_id,
        target_platform: payload.target_platform,
        title: payload.title,
        caption: payload.caption,
        publish_status: "pending_confirmation",
        created_at: "2026-05-26T08:28:00Z",
        updated_at: "2026-05-26T08:28:00Z",
      };
      publishIntents = [createdIntent, ...publishIntents];
      publicationRecordsByIntentId = { ...publicationRecordsByIntentId, [createdIntent.id]: [] };
      return jsonResponse(createdIntent, 201);
    }
    const confirmPublishIntentMatch = url.pathname.match(/^\/api\/projects\/1\/publish-intents\/(\d+)\/confirm$/);
    if (method === "POST" && confirmPublishIntentMatch) {
      const publishIntentId = Number(confirmPublishIntentMatch[1]);
      publishIntents = publishIntents.map((intent) => ({
        ...intent,
        publish_status:
          intent.id === publishIntentId ? ("confirmed" as PublishIntent["publish_status"]) : intent.publish_status,
        updated_at: intent.id === publishIntentId ? "2026-05-26T08:29:00Z" : intent.updated_at,
      }));
      const intent = publishIntents.find((item) => item.id === publishIntentId) ?? publishIntentPending;
      publicationRecordsByIntentId = {
        ...publicationRecordsByIntentId,
        [publishIntentId]: [
          {
            ...publicationRecordNotStarted,
            id: 1899,
            publish_intent_id: publishIntentId,
            target_platform: intent.target_platform,
          },
        ],
      };
      return jsonResponse(publishIntents.find((intent) => intent.id === publishIntentId));
    }
    const cancelPublishIntentMatch = url.pathname.match(/^\/api\/projects\/1\/publish-intents\/(\d+)\/cancel$/);
    if (method === "POST" && cancelPublishIntentMatch) {
      const publishIntentId = Number(cancelPublishIntentMatch[1]);
      publishIntents = publishIntents.map((intent) => ({
        ...intent,
        publish_status:
          intent.id === publishIntentId ? ("cancelled" as PublishIntent["publish_status"]) : intent.publish_status,
        updated_at: intent.id === publishIntentId ? "2026-05-26T08:29:00Z" : intent.updated_at,
      }));
      return jsonResponse(publishIntents.find((intent) => intent.id === publishIntentId));
    }
    const fakePublishIntentMatch = url.pathname.match(/^\/api\/projects\/1\/publish-intents\/(\d+)\/fake-publish$/);
    if (method === "POST" && fakePublishIntentMatch) {
      const publishIntentId = Number(fakePublishIntentMatch[1]);
      const existingRecord = (publicationRecordsByIntentId[publishIntentId] ?? [publicationRecordNotStarted])[0];
      const updatedRecord: PublicationRecord = {
        ...existingRecord,
        provider_name: "fake_publisher",
        external_publication_id: `fake-publication-${existingRecord.id}`,
        publication_status: "succeeded",
        error_message: null,
        updated_at: "2026-05-26T08:30:00Z",
      };
      publicationRecordsByIntentId = {
        ...publicationRecordsByIntentId,
        [publishIntentId]: [updatedRecord],
      };
      return jsonResponse(updatedRecord);
    }
    return jsonResponse({ detail: "not found" }, 404);
  });

  vi.stubGlobal("fetch", fetchMock);
  return { bodies, calls, fetchMock };
}

async function renderProject(options?: ServerOptions) {
  const server = installFetchMock(options);
  render(<ProjectDetailPage projectId={1} onBack={vi.fn()} />);
  await screen.findByText("Topic UI project");
  await waitFor(() => expect(server.calls).toContain("GET /api/projects/1/topic-candidates"));
  await waitFor(() => expect(server.calls).toContain("GET /api/projects/1/script-drafts"));
  await waitFor(() => expect(server.calls).toContain("GET /api/projects/1/storyboards"));
  await waitFor(() => expect(server.calls).toContain("GET /api/projects/1/renders"));
  await waitFor(() => expect(server.calls).toContain("GET /api/projects/1/subtitle-drafts"));
  await waitFor(() => expect(server.calls).toContain("GET /api/projects/1/review-drafts"));
  await waitFor(() => expect(server.calls).toContain("GET /api/projects/1/publish-intents"));
  await waitFor(() => expect(server.calls).toContain("GET /api/projects/1/content-plans"));
  await waitFor(() => expect(server.calls).toContain("GET /api/projects/1/generation-schedules"));
  await waitFor(() => expect(server.calls).toContain("GET /api/projects/1/generation-runs"));
  return server;
}

describe("ProjectDetailPage content plans", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("shows content plan, generation schedule, and generation run lists", async () => {
    await renderProject({
      contentPlans: [contentPlanOne],
      generationRuns: [generationRunOne],
      generationSchedules: [generationScheduleOne],
    });

    const contentPlanCard = screen.getByLabelText("内容计划：Weekly AI dev log");
    expect(within(contentPlanCard).getByText("Chinese developer sharing practical AI workflow notes")).toBeTruthy();
    expect(within(contentPlanCard).getByText("programmer_real_problem")).toBeTruthy();
    expect(within(contentPlanCard).getAllByText("每周 3 次")[0]).toBeTruthy();
    expect(within(contentPlanCard).getByText('{"tone":"practical"}')).toBeTruthy();
    expect(within(contentPlanCard).getAllByText("已启用")[0]).toBeTruthy();

    const generationScheduleItem = within(contentPlanCard).getByLabelText("生成计划 701");
    expect(within(generationScheduleItem).getByText("Asia/Shanghai")).toBeTruthy();
    expect(within(generationScheduleItem).getByText("Mon,Wed,Fri")).toBeTruthy();
    expect(within(generationScheduleItem).getByText("09:30")).toBeTruthy();

    const generationRunItem = within(contentPlanCard).getByLabelText("GenerationRun 1601");
    expect(within(generationRunItem).getByText("成功")).toBeTruthy();
    expect(within(generationRunItem).getByText("手动运行 / 无计划")).toBeTruthy();
  });

  it("creates a content plan", async () => {
    const server = await renderProject();

    fireEvent.change(screen.getByLabelText("计划名称"), { target: { value: "Launch notes plan" } });
    fireEvent.change(screen.getByLabelText("内容类型"), { target: { value: "open_source_build_log" } });
    fireEvent.change(screen.getByLabelText("每周目标频率"), { target: { value: "4" } });
    fireEvent.change(screen.getByLabelText("账号定位"), { target: { value: "AI builder shipping notes" } });
    fireEvent.change(screen.getByLabelText("内容偏好"), { target: { value: '{"tone":"concise"}' } });
    fireEvent.click(screen.getByRole("button", { name: "创建内容计划" }));

    await screen.findByText("Launch notes plan");
    expect(server.calls).toContain("POST /api/projects/1/content-plans");
    expect(server.bodies["POST /api/projects/1/content-plans"]).toBe(
      '{"name":"Launch notes plan","account_positioning":"AI builder shipping notes","content_type":"open_source_build_log","target_frequency_per_week":4,"preferences":"{\\"tone\\":\\"concise\\"}"}',
    );
    expect(server.calls.filter((call) => call === "GET /api/projects/1/content-plans")).toHaveLength(2);
  });

  it("enables and disables content plans", async () => {
    const server = await renderProject({ contentPlans: [contentPlanOne, disabledContentPlan] });

    const enabledPlanCard = screen.getByLabelText("内容计划：Weekly AI dev log");
    fireEvent.click(within(enabledPlanCard).getByRole("button", { name: "停用计划" }));
    await waitFor(() => expect(screen.getByLabelText("内容计划：Weekly AI dev log").getAttribute("data-enabled")).toBe("false"));
    expect(server.calls).toContain("POST /api/projects/1/content-plans/401/disable");

    const disabledPlanCard = screen.getByLabelText("内容计划：Disabled launch notes");
    fireEvent.click(within(disabledPlanCard).getByRole("button", { name: "启用计划" }));
    await waitFor(() => expect(screen.getByLabelText("内容计划：Disabled launch notes").getAttribute("data-enabled")).toBe("true"));
    expect(server.calls).toContain("POST /api/projects/1/content-plans/402/enable");
  });

  it("creates a generation schedule under a content plan", async () => {
    const server = await renderProject({ contentPlans: [contentPlanOne] });

    const contentPlanCard = screen.getByLabelText("内容计划：Weekly AI dev log");
    fireEvent.change(within(contentPlanCard).getByLabelText("计划频率"), { target: { value: "5" } });
    fireEvent.change(within(contentPlanCard).getByLabelText("时区"), { target: { value: "Asia/Shanghai" } });
    fireEvent.change(within(contentPlanCard).getByLabelText("偏好日期"), { target: { value: "Tue,Thu" } });
    fireEvent.change(within(contentPlanCard).getByLabelText("偏好时间"), { target: { value: "10:15" } });
    fireEvent.click(within(contentPlanCard).getByRole("button", { name: "创建生成计划" }));

    await within(contentPlanCard).findByText("10:15");
    expect(server.calls).toContain("POST /api/projects/1/content-plans/401/generation-schedules");
    expect(server.bodies["POST /api/projects/1/content-plans/401/generation-schedules"]).toBe(
      '{"frequency_per_week":5,"timezone":"Asia/Shanghai","preferred_days":"Tue,Thu","preferred_time":"10:15"}',
    );
    expect(server.calls.filter((call) => call === "GET /api/projects/1/generation-schedules")).toHaveLength(2);
  });

  it("enables and disables generation schedules", async () => {
    const server = await renderProject({
      contentPlans: [contentPlanOne],
      generationSchedules: [generationScheduleOne, disabledGenerationSchedule],
    });

    const enabledSchedule = screen.getByLabelText("生成计划 701");
    fireEvent.click(within(enabledSchedule).getByRole("button", { name: "停用生成计划" }));
    await waitFor(() => expect(screen.getByLabelText("生成计划 701").getAttribute("data-enabled")).toBe("false"));
    expect(server.calls).toContain("POST /api/projects/1/generation-schedules/701/disable");

    const disabledSchedule = screen.getByLabelText("生成计划 702");
    fireEvent.click(within(disabledSchedule).getByRole("button", { name: "启用生成计划" }));
    await waitFor(() => expect(screen.getByLabelText("生成计划 702").getAttribute("data-enabled")).toBe("true"));
    expect(server.calls).toContain("POST /api/projects/1/generation-schedules/702/enable");
  });

  it("creates a manual generation run without a schedule and refreshes review drafts", async () => {
    const server = await renderProject({ contentPlans: [contentPlanOne] });

    const contentPlanCard = screen.getByLabelText("内容计划：Weekly AI dev log");
    fireEvent.click(within(contentPlanCard).getByRole("button", { name: "手动生成" }));

    await within(contentPlanCard).findByText("GenerationRun #1699");
    expect(await screen.findByText("Review draft from new manual run")).toBeTruthy();
    expect(server.calls).toContain("POST /api/projects/1/content-plans/401/generation-runs");
    expect(server.bodies["POST /api/projects/1/content-plans/401/generation-runs"]).toBe("{}");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/generation-runs")).toHaveLength(2);
    expect(server.calls.filter((call) => call === "GET /api/projects/1/review-drafts")).toHaveLength(3);
  });

  it("creates a manual generation run with a generation schedule", async () => {
    const server = await renderProject({
      contentPlans: [contentPlanOne],
      generationSchedules: [generationScheduleOne],
    });

    const generationScheduleItem = screen.getByLabelText("生成计划 701");
    fireEvent.click(within(generationScheduleItem).getByRole("button", { name: "按此计划手动生成" }));

    await screen.findByText("GenerationRun #1699");
    expect(server.calls).toContain("POST /api/projects/1/content-plans/401/generation-runs");
    expect(server.bodies["POST /api/projects/1/content-plans/401/generation-runs"]).toBe('{"generation_schedule_id":701}');
    expect(screen.getAllByText("#701")[0]).toBeTruthy();
  });

  it("keeps planning controls read-only for archived projects", async () => {
    await renderProject({
      project: { ...baseProject, status: "archived" },
      contentPlans: [contentPlanOne],
      generationRuns: [generationRunOne],
      generationSchedules: [generationScheduleOne],
      reviewDrafts: [reviewDraftPending],
    });

    const contentPlanCard = screen.getByLabelText("内容计划：Weekly AI dev log");
    const generationScheduleItem = within(contentPlanCard).getByLabelText("生成计划 701");
    expect(screen.getByText("当前项目已归档，只能查看内容计划、生成计划和生成运行，不能继续修改或触发。")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "创建内容计划" })).toBeNull();
    expect(within(contentPlanCard).queryByRole("button", { name: "停用计划" })).toBeNull();
    expect(within(contentPlanCard).queryByRole("button", { name: "手动生成" })).toBeNull();
    expect(within(contentPlanCard).queryByRole("button", { name: "创建生成计划" })).toBeNull();
    expect(within(generationScheduleItem).queryByRole("button", { name: "停用生成计划" })).toBeNull();
    expect(within(generationScheduleItem).queryByRole("button", { name: "按此计划手动生成" })).toBeNull();
    expect(within(contentPlanCard).getByLabelText("GenerationRun 1601")).toBeTruthy();
    expect(screen.getByLabelText("待审核草稿：Manual run review draft")).toBeTruthy();
  });
});

describe("ProjectDetailPage topic candidates", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("requests topic candidates when the project detail page loads", async () => {
    const server = await renderProject();

    expect(server.calls).toContain("GET /api/projects/1/topic-candidates");
    expect(screen.getByText("暂无选题候选。")).toBeTruthy();
  });

  it("shows candidate title, angle, audience, hook, and rationale", async () => {
    await renderProject({ candidates: [candidateOne] });

    expect(screen.getByText("Problem-first topic")).toBeTruthy();
    expect(screen.getByText("Turn a concrete problem into a short story")).toBeTruthy();
    expect(screen.getByText("Developers facing similar workflow blocks")).toBeTruthy();
    expect(screen.getByText("Here is the small workflow issue that slowed the project down.")).toBeTruthy();
    expect(screen.getByText("Based on the imported material.")).toBeTruthy();
    expect(screen.getByText("来源素材：11")).toBeTruthy();
  });

  it("calls generate API and refreshes candidates after generation succeeds", async () => {
    const server = await renderProject();

    fireEvent.click(screen.getByRole("button", { name: "生成选题候选" }));

    await screen.findByText("Checklist topic");
    expect(server.calls).toContain("POST /api/projects/1/topic-candidates/generate");
    expect(server.bodies["POST /api/projects/1/topic-candidates/generate"]).toBe('{"candidate_count":3}');
    expect(server.calls.filter((call) => call === "GET /api/projects/1/topic-candidates")).toHaveLength(2);
  });

  it("calls select API and refreshes candidates after selection succeeds", async () => {
    const server = await renderProject({ candidates: [candidateOne, candidateTwo] });

    const candidateCard = screen.getByLabelText("选题候选：Problem-first topic");
    fireEvent.click(within(candidateCard).getByRole("button", { name: "选择" }));

    await waitFor(() => expect(candidateCard.getAttribute("data-status")).toBe("selected"));
    expect(server.calls).toContain("POST /api/projects/1/topic-candidates/101/select");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/topic-candidates")).toHaveLength(2);
  });

  it("shows a clear selected visual state", async () => {
    await renderProject({ candidates: [candidateTwo] });

    const selectedCard = screen.getByLabelText("选题候选：Build log topic");
    expect(selectedCard.getAttribute("data-status")).toBe("selected");
    expect(within(selectedCard).getAllByText("已选择")[0]).toBeTruthy();
  });

  it("disables generate and select controls for archived projects", async () => {
    await renderProject({
      project: { ...baseProject, status: "archived" },
      candidates: [candidateOne],
    });

    const generateButton = screen.getByRole("button", { name: "生成选题候选" }) as HTMLButtonElement;
    expect(generateButton.disabled).toBe(true);
    expect((screen.getByRole("button", { name: "选择" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getAllByText("当前项目已归档，只能查看，不能继续修改。")[0]).toBeTruthy();
  });

  it("shows a no-materials message when generate returns 409", async () => {
    await renderProject({ generateError: "project has no materials" });

    fireEvent.click(screen.getByRole("button", { name: "生成选题候选" }));

    expect(await screen.findByText("请先添加至少一个素材，再生成选题候选。")).toBeTruthy();
  });

  it("shows a read-only message when select returns archived 409", async () => {
    await renderProject({ candidates: [candidateOne], selectError: "archived project cannot select candidates" });

    fireEvent.click(screen.getByRole("button", { name: "选择" }));

    expect(await screen.findByText("当前项目已归档，只能查看，不能继续修改。")).toBeTruthy();
  });
});

describe("ProjectDetailPage script drafts", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("requests script drafts when the project detail page loads", async () => {
    const server = await renderProject();

    expect(server.calls).toContain("GET /api/projects/1/script-drafts");
    expect(screen.getByText("暂无脚本草稿。")).toBeTruthy();
  });

  it("shows script draft title, opening hook, body, call to action, duration, and rationale", async () => {
    await renderProject({ scriptDrafts: [scriptDraftOne] });

    expect(screen.getByText("Problem-first script")).toBeTruthy();
    expect(screen.getByText("This workflow looked small until it blocked the whole project.")).toBeTruthy();
    expect(screen.getByText("First, show the bug. Then explain the fix. Close with the repeatable workflow.")).toBeTruthy();
    expect(screen.getByText("Save this flow for your next debugging session.")).toBeTruthy();
    expect(screen.getByText("58 秒")).toBeTruthy();
    expect(screen.getByText("Built from the selected topic and imported note.")).toBeTruthy();
    expect(screen.getByText("来源素材：11")).toBeTruthy();
  });

  it("calls generate API and refreshes script drafts after generation succeeds", async () => {
    const server = await renderProject();

    fireEvent.click(screen.getByRole("button", { name: "生成脚本草稿" }));

    await screen.findByText("Checklist script");
    expect(server.calls).toContain("POST /api/projects/1/script-drafts/generate");
    expect(server.bodies["POST /api/projects/1/script-drafts/generate"]).toBe('{"script_count":2}');
    expect(server.calls.filter((call) => call === "GET /api/projects/1/script-drafts")).toHaveLength(2);
  });

  it("calls select API and refreshes script drafts after selection succeeds", async () => {
    const server = await renderProject({ scriptDrafts: [scriptDraftOne, scriptDraftTwo] });

    const scriptDraftCard = screen.getByLabelText("脚本草稿：Problem-first script");
    fireEvent.click(within(scriptDraftCard).getByRole("button", { name: "选择" }));

    await waitFor(() => expect(screen.getByLabelText("脚本草稿：Problem-first script").getAttribute("data-status")).toBe("selected"));
    expect(server.calls).toContain("POST /api/projects/1/script-drafts/501/select");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/script-drafts")).toHaveLength(2);
  });

  it("shows a clear selected visual state for script drafts", async () => {
    await renderProject({ scriptDrafts: [scriptDraftTwo] });

    const selectedCard = screen.getByLabelText("脚本草稿：Build log script");
    expect(selectedCard.getAttribute("data-status")).toBe("selected");
    expect(within(selectedCard).getAllByText("已选择")[0]).toBeTruthy();
  });

  it("disables generate and select controls for archived projects", async () => {
    await renderProject({
      project: { ...baseProject, status: "archived" },
      scriptDrafts: [scriptDraftOne],
    });

    const generateButton = screen.getByRole("button", { name: "生成脚本草稿" }) as HTMLButtonElement;
    const scriptDraftCard = screen.getByLabelText("脚本草稿：Problem-first script");
    expect(generateButton.disabled).toBe(true);
    expect((within(scriptDraftCard).getByRole("button", { name: "选择" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getAllByText("当前项目已归档，只能查看，不能继续修改。")[0]).toBeTruthy();
  });

  it("shows a no-materials message when script generation returns 409", async () => {
    await renderProject({ generateScriptDraftsError: "project has no materials" });

    fireEvent.click(screen.getByRole("button", { name: "生成脚本草稿" }));

    expect(await screen.findByText("请先添加至少一个素材，再生成脚本草稿。")).toBeTruthy();
  });

  it("shows a selected-topic message when script generation returns 409", async () => {
    await renderProject({ generateScriptDraftsError: "project has no selected topic candidate" });

    fireEvent.click(screen.getByRole("button", { name: "生成脚本草稿" }));

    expect(await screen.findByText("请先选择一个选题候选，再生成脚本草稿。")).toBeTruthy();
  });

  it("shows a read-only message when script draft selection returns archived 409", async () => {
    await renderProject({
      scriptDrafts: [scriptDraftOne],
      selectScriptDraftError: "archived project cannot select script drafts",
    });

    const scriptDraftCard = screen.getByLabelText("脚本草稿：Problem-first script");
    fireEvent.click(within(scriptDraftCard).getByRole("button", { name: "选择" }));

    expect(await screen.findByText("当前项目已归档，只能查看，不能继续修改。")).toBeTruthy();
  });
});

describe("ProjectDetailPage storyboards", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("requests storyboards when the project detail page loads", async () => {
    const server = await renderProject();

    expect(server.calls).toContain("GET /api/projects/1/storyboards");
    expect(screen.getByText("暂无分镜脚本。")).toBeTruthy();
  });

  it("shows storyboard title, summary, and visual style", async () => {
    await renderProject({ storyboards: [storyboardOne] });

    expect(screen.getByText("Storyboard walkthrough")).toBeTruthy();
    expect(screen.getByText("A source-backed storyboard for the selected script.")).toBeTruthy();
    expect(screen.getByText("Clean screen-recording style")).toBeTruthy();
    expect(screen.getAllByText("来源素材")[0]).toBeTruthy();
  });

  it("shows storyboard scenes with their structured fields", async () => {
    await renderProject({ storyboards: [storyboardOne] });

    const firstScene = screen.getByLabelText("场景 1：Set up the problem");
    expect(within(firstScene).getByText("场景 1：Set up the problem")).toBeTruthy();
    expect(within(firstScene).getByText("Start with the workflow problem.")).toBeTruthy();
    expect(within(firstScene).getByText("Show the imported material that anchors the story.")).toBeTruthy();
    expect(within(firstScene).getByText("The problem")).toBeTruthy();
    expect(within(firstScene).getByText("12 秒")).toBeTruthy();
    expect(within(firstScene).getByText("11")).toBeTruthy();
  });

  it("shows storyboard scenes sorted by scene order", async () => {
    await renderProject({ storyboards: [storyboardOne] });

    const storyboardCard = screen.getByLabelText("分镜脚本：Storyboard walkthrough");
    const sceneItems = within(storyboardCard).getAllByTestId("storyboard-scene");
    expect(sceneItems.map((scene) => scene.getAttribute("data-scene-order"))).toEqual(["1", "2"]);
  });

  it("calls generate API and refreshes storyboards after generation succeeds", async () => {
    const server = await renderProject();

    fireEvent.click(screen.getByRole("button", { name: "生成分镜脚本" }));

    await screen.findByText("Storyboard walkthrough");
    expect(server.calls).toContain("POST /api/projects/1/storyboards/generate");
    expect(server.bodies["POST /api/projects/1/storyboards/generate"]).toBe('{"storyboard_count":1}');
    expect(server.calls.filter((call) => call === "GET /api/projects/1/storyboards")).toHaveLength(2);
  });

  it("calls select API and refreshes storyboards after selection succeeds", async () => {
    const server = await renderProject({ storyboards: [storyboardOne, storyboardTwo] });

    const storyboardCard = screen.getByLabelText("分镜脚本：Storyboard walkthrough");
    fireEvent.click(within(storyboardCard).getByRole("button", { name: "选择" }));

    await waitFor(() => expect(screen.getByLabelText("分镜脚本：Storyboard walkthrough").getAttribute("data-status")).toBe("selected"));
    expect(server.calls).toContain("POST /api/projects/1/storyboards/801/select");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/storyboards")).toHaveLength(2);
  });

  it("shows a clear selected visual state for storyboards", async () => {
    await renderProject({ storyboards: [storyboardTwo] });

    const selectedCard = screen.getByLabelText("分镜脚本：Selected storyboard");
    expect(selectedCard.getAttribute("data-status")).toBe("selected");
    expect(within(selectedCard).getAllByText("已选择")[0]).toBeTruthy();
  });

  it("disables generate and select controls for archived projects", async () => {
    await renderProject({
      project: { ...baseProject, status: "archived" },
      storyboards: [storyboardOne],
    });

    const generateButton = screen.getByRole("button", { name: "生成分镜脚本" }) as HTMLButtonElement;
    const storyboardCard = screen.getByLabelText("分镜脚本：Storyboard walkthrough");
    expect(generateButton.disabled).toBe(true);
    expect((within(storyboardCard).getByRole("button", { name: "选择" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getAllByText("当前项目已归档，只能查看，不能继续修改。")[0]).toBeTruthy();
  });

  it("shows a no-materials message when storyboard generation returns 409", async () => {
    await renderProject({ generateStoryboardsError: "project has no materials" });

    fireEvent.click(screen.getByRole("button", { name: "生成分镜脚本" }));

    expect(await screen.findByText("请先添加至少一个素材，再生成分镜脚本。")).toBeTruthy();
  });

  it("shows a selected-topic message when storyboard generation returns 409", async () => {
    await renderProject({ generateStoryboardsError: "project has no selected topic candidate" });

    fireEvent.click(screen.getByRole("button", { name: "生成分镜脚本" }));

    expect(await screen.findByText("请先选择一个选题候选，再生成分镜脚本。")).toBeTruthy();
  });

  it("shows a selected-script message when storyboard generation returns 409", async () => {
    await renderProject({ generateStoryboardsError: "project has no selected script draft" });

    fireEvent.click(screen.getByRole("button", { name: "生成分镜脚本" }));

    expect(await screen.findByText("请先选择一个脚本草稿，再生成分镜脚本。")).toBeTruthy();
  });

  it("shows a read-only message when storyboard selection returns archived 409", async () => {
    await renderProject({
      storyboards: [storyboardOne],
      selectStoryboardError: "archived project cannot select storyboards",
    });

    const storyboardCard = screen.getByLabelText("分镜脚本：Storyboard walkthrough");
    fireEvent.click(within(storyboardCard).getByRole("button", { name: "选择" }));

    expect(await screen.findByText("当前项目已归档，只能查看，不能继续修改。")).toBeTruthy();
  });
});

describe("ProjectDetailPage review drafts", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("requests and shows review drafts when the project detail page loads", async () => {
    const server = await renderProject({ reviewDrafts: [reviewDraftPending] });

    expect(server.calls).toContain("GET /api/projects/1/review-drafts");
    const reviewDraftCard = screen.getByLabelText("待审核草稿：Manual run review draft");
    expect(within(reviewDraftCard).getByText("Deterministic fake draft summary from a manual run.")).toBeTruthy();
    expect(within(reviewDraftCard).getByText("ContentPlan #401 plus GenerationRun #301.")).toBeTruthy();
    expect(within(reviewDraftCard).getByText("#301")).toBeTruthy();
    expect(within(reviewDraftCard).getByText("手动运行 / 无计划")).toBeTruthy();
  });

  it("shows pending, approved, and rejected review statuses", async () => {
    await renderProject({ reviewDrafts: [reviewDraftPending, reviewDraftApproved, reviewDraftRejected] });

    expect(within(screen.getByLabelText("待审核草稿：Manual run review draft")).getAllByText("待审核")[0]).toBeTruthy();
    expect(within(screen.getByLabelText("待审核草稿：Approved review draft")).getAllByText("已通过")[0]).toBeTruthy();
    expect(within(screen.getByLabelText("待审核草稿：Rejected review draft")).getAllByText("已拒绝")[0]).toBeTruthy();
  });

  it("shows an explicit hotspot source fallback when the summary is empty", async () => {
    await renderProject({ reviewDrafts: [reviewDraftPending] });

    const reviewDraftCard = screen.getByLabelText("待审核草稿：Manual run review draft");
    expect(within(reviewDraftCard).getByText("未启用热点来源 / 无热点来源")).toBeTruthy();
  });

  it("approves a review draft and refreshes the list", async () => {
    const server = await renderProject({ reviewDrafts: [reviewDraftPending] });

    fireEvent.click(within(screen.getByLabelText("待审核草稿：Manual run review draft")).getByRole("button", { name: "通过" }));

    await waitFor(() =>
      expect(screen.getByLabelText("待审核草稿：Manual run review draft").getAttribute("data-status")).toBe("approved"),
    );
    expect(server.calls).toContain("POST /api/projects/1/review-drafts/1501/approve");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/review-drafts")).toHaveLength(4);
  });

  it("rejects a review draft and refreshes the list", async () => {
    const server = await renderProject({ reviewDrafts: [reviewDraftPending] });

    fireEvent.click(within(screen.getByLabelText("待审核草稿：Manual run review draft")).getByRole("button", { name: "拒绝" }));

    await waitFor(() =>
      expect(screen.getByLabelText("待审核草稿：Manual run review draft").getAttribute("data-status")).toBe("rejected"),
    );
    expect(server.calls).toContain("POST /api/projects/1/review-drafts/1501/reject");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/review-drafts")).toHaveLength(4);
  });

  it("keeps review drafts read-only for archived projects", async () => {
    await renderProject({
      project: { ...baseProject, status: "archived" },
      reviewDrafts: [reviewDraftPending],
    });

    const reviewDraftCard = screen.getByLabelText("待审核草稿：Manual run review draft");
    expect(screen.getByText("当前项目已归档，只能查看待审核草稿，不能继续审核操作。")).toBeTruthy();
    expect(within(reviewDraftCard).queryByRole("button", { name: "通过" })).toBeNull();
    expect(within(reviewDraftCard).queryByRole("button", { name: "拒绝" })).toBeNull();
  });
});

describe("ProjectDetailPage publishing workflow", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("shows the fake publishing section and explains that it is not real platform publishing", async () => {
    await renderProject();

    expect(screen.getByText("Publishing / Fake Publishing")).toBeTruthy();
    expect(screen.getByText(/本区块只是本地 fake publishing workflow/)).toBeTruthy();
    expect(screen.getByText(/不会上传、发布、排期，也不会调用 Douyin/)).toBeTruthy();
    expect(screen.getByText("需要先通过 Review Draft，才能创建 PublishIntent。")).toBeTruthy();
    expect(screen.queryByRole("button", { name: /^Publish$/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /OAuth|授权|上传|排期|真实发布|Real Publish/i })).toBeNull();
  });

  it("shows approved review drafts and creates a PublishIntent", async () => {
    const server = await renderProject({ reviewDrafts: [reviewDraftApproved] });

    fireEvent.click(screen.getByRole("button", { name: "创建 PublishIntent" }));

    await screen.findByLabelText("PublishIntent 1799");
    expect(server.calls).toContain("POST /api/projects/1/publish-intents");
    expect(server.bodies["POST /api/projects/1/publish-intents"]).toBe(
      '{"review_draft_id":1502,"target_platform":"douyin","title":"Approved review draft","caption":"Deterministic fake draft summary from a manual run."}',
    );
    expect(server.calls.filter((call) => call === "GET /api/projects/1/publish-intents")).toHaveLength(2);
  });

  it("shows a visible publishing API error without implying a real platform action", async () => {
    await renderProject({
      createPublishIntentError: "review draft must be approved before creating a publish intent",
      reviewDrafts: [reviewDraftApproved],
    });

    fireEvent.click(screen.getByRole("button", { name: "创建 PublishIntent" }));

    expect(await screen.findByText("review draft must be approved before creating a publish intent")).toBeTruthy();
    expect(screen.queryByRole("button", { name: /^Publish$/i })).toBeNull();
  });

  it("shows pending PublishIntent actions and confirms into a not_started PublicationRecord", async () => {
    const server = await renderProject({
      publishIntents: [publishIntentPending],
      reviewDrafts: [reviewDraftApproved],
    });

    const intentCard = screen.getByLabelText("PublishIntent 1701");
    expect(within(intentCard).getByRole("button", { name: "确认 PublishIntent" })).toBeTruthy();
    expect(within(intentCard).getByRole("button", { name: "取消 PublishIntent" })).toBeTruthy();

    fireEvent.click(within(intentCard).getByRole("button", { name: "确认 PublishIntent" }));

    const updatedIntentCard = await screen.findByLabelText("PublishIntent 1701");
    await waitFor(() => expect(updatedIntentCard.getAttribute("data-status")).toBe("confirmed"));
    expect(server.calls).toContain("POST /api/projects/1/publish-intents/1701/confirm");
    expect(await screen.findByLabelText("PublicationRecord 1899")).toBeTruthy();
    expect(screen.getByText("未开始")).toBeTruthy();
  });

  it("cancels a pending PublishIntent and refreshes the list", async () => {
    const server = await renderProject({
      publishIntents: [publishIntentPending],
      reviewDrafts: [reviewDraftApproved],
    });

    const intentCard = screen.getByLabelText("PublishIntent 1701");
    fireEvent.click(within(intentCard).getByRole("button", { name: "取消 PublishIntent" }));

    await waitFor(() => expect(screen.getByLabelText("PublishIntent 1701").getAttribute("data-status")).toBe("cancelled"));
    expect(server.calls).toContain("POST /api/projects/1/publish-intents/1701/cancel");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/publish-intents")).toHaveLength(2);
  });

  it("runs Fake Publish for a confirmed intent with a not_started record", async () => {
    const server = await renderProject({
      publicationRecords: { 1702: [publicationRecordNotStarted] },
      publishIntents: [publishIntentConfirmed],
      reviewDrafts: [reviewDraftApproved],
    });

    const intentCard = screen.getByLabelText("PublishIntent 1702");
    fireEvent.click(within(intentCard).getByRole("button", { name: "Fake Publish" }));

    await waitFor(() => expect(screen.getByLabelText("PublicationRecord 1801").getAttribute("data-status")).toBe("succeeded"));
    expect(server.calls).toContain("POST /api/projects/1/publish-intents/1702/fake-publish");
    expect(screen.getByText("fake-publication-1801")).toBeTruthy();
    expect(screen.getByText("Fake execution succeeded. Not a real platform publication.")).toBeTruthy();
  });

  it("shows succeeded fake publication records without offering repeated Fake Publish", async () => {
    await renderProject({
      publicationRecords: { 1702: [publicationRecordSucceeded] },
      publishIntents: [publishIntentConfirmed],
      reviewDrafts: [reviewDraftApproved],
    });

    const intentCard = screen.getByLabelText("PublishIntent 1702");
    expect(within(intentCard).getByText("fake-publication-1801")).toBeTruthy();
    expect(within(intentCard).queryByRole("button", { name: "Fake Publish" })).toBeNull();
    expect(within(intentCard).getByText("Fake execution succeeded. Not a real platform publication.")).toBeTruthy();
  });

  it("shows PublicationRecord metrics snapshots with fake/local labels", async () => {
    const server = await renderProject({
      publicationMetrics: { 1801: [metricSnapshotOne] },
      publicationRecords: { 1702: [publicationRecordSucceeded] },
      publishIntents: [publishIntentConfirmed],
      reviewDrafts: [reviewDraftApproved],
    });

    const recordCard = screen.getByLabelText("PublicationRecord 1801");
    await waitFor(() =>
      expect(server.calls).toContain("GET /api/projects/1/publication-records/1801/metrics"),
    );

    expect(within(recordCard).getByLabelText("MetricSnapshot 1901")).toBeTruthy();
    expect(within(recordCard).getAllByText("Fake/local metrics").length).toBeGreaterThan(0);
    expect(within(recordCard).getAllByText(/Not real platform performance/).length).toBeGreaterThan(0);
    expect(within(recordCard).getByText("248")).toBeTruthy();
    expect(within(recordCard).getByText("12.4s")).toBeTruthy();
    expect(within(recordCard).getByText("72%")).toBeTruthy();
    expect(screen.queryByText("Real platform performance")).toBeNull();
  });

  it("shows an empty metrics state for PublicationRecords without snapshots", async () => {
    await renderProject({
      publicationRecords: { 1702: [publicationRecordSucceeded] },
      publishIntents: [publishIntentConfirmed],
      reviewDrafts: [reviewDraftApproved],
    });

    const recordCard = screen.getByLabelText("PublicationRecord 1801");

    expect(within(recordCard).getByText("No metrics snapshots yet.")).toBeTruthy();
    expect(within(recordCard).getByRole("button", { name: "Generate fake metrics" })).toBeTruthy();
  });

  it("creates fake metrics for a PublicationRecord and refreshes the metrics list", async () => {
    const server = await renderProject({
      publicationRecords: { 1702: [publicationRecordSucceeded] },
      publishIntents: [publishIntentConfirmed],
      reviewDrafts: [reviewDraftApproved],
    });

    const recordCard = screen.getByLabelText("PublicationRecord 1801");
    fireEvent.click(within(recordCard).getByRole("button", { name: "Generate fake metrics" }));

    expect(await within(recordCard).findByLabelText("MetricSnapshot 1999")).toBeTruthy();
    expect(server.calls).toContain("POST /api/projects/1/publication-records/1801/metrics/fake");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/publication-records/1801/metrics")).toHaveLength(
      2,
    );
    expect(within(recordCard).getAllByText("Fake/local metrics").length).toBeGreaterThan(0);
  });

  it("shows fake metrics API errors without implying real platform analytics", async () => {
    await renderProject({
      createMetricError: "fake metrics provider unavailable",
      publicationRecords: { 1702: [publicationRecordSucceeded] },
      publishIntents: [publishIntentConfirmed],
      reviewDrafts: [reviewDraftApproved],
    });

    const recordCard = screen.getByLabelText("PublicationRecord 1801");
    fireEvent.click(within(recordCard).getByRole("button", { name: "Generate fake metrics" }));

    expect(await screen.findByText("fake metrics provider unavailable")).toBeTruthy();
    expect(screen.queryByText("Real platform analytics")).toBeNull();
    expect(screen.queryByText("真实平台数据分析")).toBeNull();
  });

  it("keeps publishing workflow actions disabled for archived projects", async () => {
    await renderProject({
      project: { ...baseProject, status: "archived" },
      publicationRecords: { 1702: [publicationRecordNotStarted] },
      publishIntents: [publishIntentConfirmed],
      reviewDrafts: [reviewDraftApproved],
    });

    expect(screen.getByText(/当前项目已归档，只能查看已有 PublishIntent 和 PublicationRecord/)).toBeTruthy();
    expect((screen.getByRole("button", { name: "已有 PublishIntent" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.queryByRole("button", { name: "Fake Publish" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Generate fake metrics" })).toBeNull();
    expect(screen.getByText(/Archived projects are read-only/)).toBeTruthy();
  });
});

describe("ProjectDetailPage subtitle drafts", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("requests and shows the subtitle drafts panel when the project detail page loads", async () => {
    const server = await renderProject();

    expect(server.calls).toContain("GET /api/projects/1/subtitle-drafts");
    expect(screen.getByText("字幕草稿")).toBeTruthy();
    expect(screen.getByText("暂无字幕草稿。")).toBeTruthy();
  });

  it("shows subtitle draft metadata and cues", async () => {
    await renderProject({ storyboards: [storyboardTwo], subtitleDrafts: [subtitleDraftOne] });

    const subtitleDraftCard = screen.getByLabelText("字幕草稿 1301");
    expect(within(subtitleDraftCard).getByText("字幕草稿 #1301")).toBeTruthy();
    expect(within(subtitleDraftCard).getByText("fake_subtitle_generator 0.1")).toBeTruthy();
    expect(within(subtitleDraftCard).getByText("草稿")).toBeTruthy();
    expect(within(subtitleDraftCard).getByText("#802")).toBeTruthy();
    expect(within(subtitleDraftCard).getByText("Start with the selected storyboard.")).toBeTruthy();
    expect(within(subtitleDraftCard).getByText("Use deterministic subtitle cue metadata.")).toBeTruthy();
    expect(within(subtitleDraftCard).getByText("0 秒 - 12 秒")).toBeTruthy();
    expect(within(subtitleDraftCard).getByText("12 秒 - 30 秒")).toBeTruthy();
  });

  it("shows subtitle cues sorted by cue order", async () => {
    await renderProject({ storyboards: [storyboardTwo], subtitleDrafts: [subtitleDraftOne] });

    const subtitleDraftCard = screen.getByLabelText("字幕草稿 1301");
    const cueItems = within(subtitleDraftCard).getAllByTestId("subtitle-cue");
    expect(cueItems.map((cue) => cue.getAttribute("data-cue-order"))).toEqual(["1", "2"]);
  });

  it("shows a fallback when a subtitle draft has no cues", async () => {
    await renderProject({ storyboards: [storyboardTwo], subtitleDrafts: [subtitleDraftWithoutCues] });

    const subtitleDraftCard = screen.getByLabelText("字幕草稿 1303");
    expect(within(subtitleDraftCard).getByText("暂无字幕 cue。")).toBeTruthy();
  });

  it("creates a fake subtitle draft and refreshes subtitle drafts after creation succeeds", async () => {
    const server = await renderProject({ storyboards: [storyboardTwo] });

    await waitFor(() =>
      expect((screen.getByRole("button", { name: "创建模拟字幕草稿" }) as HTMLButtonElement).disabled).toBe(
        false,
      ),
    );
    fireEvent.click(screen.getByRole("button", { name: "创建模拟字幕草稿" }));

    await screen.findByText("字幕草稿 #1301");
    expect(server.calls).toContain("POST /api/projects/1/subtitle-drafts");
    expect(server.bodies["POST /api/projects/1/subtitle-drafts"]).toBe("{}");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/subtitle-drafts")).toHaveLength(2);
  });

  it("selects a subtitle draft and refreshes subtitle drafts after selection succeeds", async () => {
    const server = await renderProject({ storyboards: [storyboardTwo], subtitleDrafts: [subtitleDraftOne, subtitleDraftTwo] });

    const subtitleDraftCard = screen.getByLabelText("字幕草稿 1301");
    fireEvent.click(within(subtitleDraftCard).getByRole("button", { name: "选择" }));

    await waitFor(() => expect(screen.getByLabelText("字幕草稿 1301").getAttribute("data-status")).toBe("selected"));
    expect(server.calls).toContain("POST /api/projects/1/subtitle-drafts/1301/select");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/subtitle-drafts")).toHaveLength(2);
  });

  it("disables fake subtitle creation and selection for archived projects while keeping drafts visible", async () => {
    await renderProject({
      project: { ...baseProject, status: "archived" },
      storyboards: [storyboardTwo],
      subtitleDrafts: [subtitleDraftOne],
    });

    const subtitleDraftCard = screen.getByLabelText("字幕草稿 1301");
    expect(screen.getByText("字幕草稿 #1301")).toBeTruthy();
    expect((screen.getByRole("button", { name: "创建模拟字幕草稿" }) as HTMLButtonElement).disabled).toBe(true);
    expect((within(subtitleDraftCard).getByRole("button", { name: "选择" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getAllByText("当前项目已归档，只能查看，不能继续修改。")[0]).toBeTruthy();
  });

  it("disables fake subtitle creation when there is no selected storyboard", async () => {
    await renderProject({ storyboards: [storyboardOne] });

    await screen.findByText("请先选择一个分镜脚本，再创建模拟字幕草稿。");
    expect((screen.getByRole("button", { name: "创建模拟字幕草稿" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it("shows a visible error when fake subtitle creation fails", async () => {
    await renderProject({ createSubtitleDraftError: "subtitle service unavailable", storyboards: [storyboardTwo] });

    await waitFor(() =>
      expect((screen.getByRole("button", { name: "创建模拟字幕草稿" }) as HTMLButtonElement).disabled).toBe(
        false,
      ),
    );
    fireEvent.click(screen.getByRole("button", { name: "创建模拟字幕草稿" }));

    expect(await screen.findByText("subtitle service unavailable")).toBeTruthy();
  });

  it("shows a visible error when subtitle selection fails", async () => {
    await renderProject({
      selectSubtitleDraftError: "archived project cannot select subtitle drafts",
      storyboards: [storyboardTwo],
      subtitleDrafts: [subtitleDraftOne],
    });

    const subtitleDraftCard = screen.getByLabelText("字幕草稿 1301");
    fireEvent.click(within(subtitleDraftCard).getByRole("button", { name: "选择" }));

    expect(await screen.findByText("当前项目已归档，只能查看，不能继续修改。")).toBeTruthy();
  });
});

describe("ProjectDetailPage render jobs", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("requests and shows the render jobs panel when the project detail page loads", async () => {
    const server = await renderProject();

    expect(server.calls).toContain("GET /api/projects/1/renders");
    expect(screen.getByText("渲染任务")).toBeTruthy();
    expect(screen.getByText("暂无渲染任务。")).toBeTruthy();
  });

  it("shows fake preview manifest metadata", async () => {
    await renderProject({ renderJobs: [renderJobOne], storyboards: [storyboardTwo] });

    const renderJobCard = screen.getByLabelText("渲染任务 1201");
    expect(within(renderJobCard).getByText("渲染任务 #1201")).toBeTruthy();
    expect(within(renderJobCard).getByText("fake_renderer 0.1")).toBeTruthy();
    expect(within(renderJobCard).getByText("成功")).toBeTruthy();
    expect(within(renderJobCard).getByText("mp4 / 9:16 / 1080x1920")).toBeTruthy();
    expect(within(renderJobCard).getByText("预览 manifest 元数据")).toBeTruthy();
    expect(within(renderJobCard).getByText("fake_preview_manifest")).toBeTruthy();
    expect(within(renderJobCard).getByText("application/json")).toBeTruthy();
    expect(within(renderJobCard).getByText("386 bytes")).toBeTruthy();
    expect(within(renderJobCard).getByText("a".repeat(64))).toBeTruthy();
    expect(within(renderJobCard).getByText("30 秒")).toBeTruthy();
    expect(within(renderJobCard).getByText("1080 x 1920")).toBeTruthy();
    expect(within(renderJobCard).getByText("#1301")).toBeTruthy();
    expect(within(renderJobCard).getByText("project-1-render-1201-preview-manifest.json")).toBeTruthy();
    expect(within(renderJobCard).getByText("data/local/render_previews/project-1/project-1-render-1201-preview-manifest.json")).toBeTruthy();
    expect(within(renderJobCard).getByText("暂无")).toBeTruthy();
  });

  it("shows a fallback when a 成功 render job has no preview metadata", async () => {
    await renderProject({ renderJobs: [renderJobWithoutArtifact], storyboards: [storyboardTwo] });

    const renderJobCard = screen.getByLabelText("渲染任务 1202");
    expect(within(renderJobCard).getByText("暂无预览元数据。")).toBeTruthy();
  });

  it("does not render a video player for non-成功 render jobs", async () => {
    await renderProject({ renderJobs: [queuedRenderJob], storyboards: [storyboardTwo] });

    const renderJobCard = screen.getByLabelText("渲染任务 1203");
    expect(within(renderJobCard).getByText("预览待生成 / 不可用。")).toBeTruthy();
    expect(document.querySelector("video")).toBeNull();
  });

  it("creates a fake render job and refreshes render jobs after creation succeeds", async () => {
    const server = await renderProject({ storyboards: [storyboardTwo] });

    await waitFor(() => expect((screen.getByRole("button", { name: "创建模拟渲染任务" }) as HTMLButtonElement).disabled).toBe(false));
    fireEvent.click(screen.getByRole("button", { name: "创建模拟渲染任务" }));

    await screen.findByText("渲染任务 #1201");
    expect(server.calls).toContain("POST /api/projects/1/renders");
    expect(server.bodies["POST /api/projects/1/renders"]).toBe(
      '{"requested_format":"mp4","requested_aspect_ratio":"9:16","requested_resolution":"1080x1920"}',
    );
    expect(server.calls.filter((call) => call === "GET /api/projects/1/renders")).toHaveLength(2);
  });

  it("disables fake render creation for archived projects while keeping existing jobs visible", async () => {
    await renderProject({
      project: { ...baseProject, status: "archived" },
      renderJobs: [renderJobOne],
      storyboards: [storyboardTwo],
    });

    expect(screen.getByText("渲染任务 #1201")).toBeTruthy();
    expect(screen.getByText("data/local/render_previews/project-1/project-1-render-1201-preview-manifest.json")).toBeTruthy();
    expect((screen.getByRole("button", { name: "创建模拟渲染任务" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getAllByText("当前项目已归档，只能查看，不能继续修改。")[0]).toBeTruthy();
  });

  it("disables fake render creation when there is no selected storyboard", async () => {
    await renderProject({ storyboards: [storyboardOne] });

    await screen.findByText("请先选择一个分镜脚本，再创建模拟渲染任务。");
    expect((screen.getByRole("button", { name: "创建模拟渲染任务" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it("shows a visible error when fake render creation fails", async () => {
    await renderProject({ createRenderError: "render service unavailable", storyboards: [storyboardTwo] });

    await waitFor(() => expect((screen.getByRole("button", { name: "创建模拟渲染任务" }) as HTMLButtonElement).disabled).toBe(false));
    fireEvent.click(screen.getByRole("button", { name: "创建模拟渲染任务" }));

    expect(await screen.findByText("render service unavailable")).toBeTruthy();
  });
});
