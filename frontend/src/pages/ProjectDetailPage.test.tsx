import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProjectDetailPage } from "./ProjectDetailPage";
import type { ProjectDetail, RenderJob, ScriptDraft, Storyboard, SubtitleDraft, TopicCandidate } from "../api/client";

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

type ServerOptions = {
  project?: ProjectDetail;
  candidates?: TopicCandidate[];
  scriptDrafts?: ScriptDraft[];
  storyboards?: Storyboard[];
  renderJobs?: RenderJob[];
  subtitleDrafts?: SubtitleDraft[];
  generateError?: string;
  generateScriptDraftsError?: string;
  generateStoryboardsError?: string;
  createRenderError?: string;
  createSubtitleDraftError?: string;
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
  return server;
}

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
    expect(screen.getByText("No topic candidates yet.")).toBeTruthy();
  });

  it("shows candidate title, angle, audience, hook, and rationale", async () => {
    await renderProject({ candidates: [candidateOne] });

    expect(screen.getByText("Problem-first topic")).toBeTruthy();
    expect(screen.getByText("Turn a concrete problem into a short story")).toBeTruthy();
    expect(screen.getByText("Developers facing similar workflow blocks")).toBeTruthy();
    expect(screen.getByText("Here is the small workflow issue that slowed the project down.")).toBeTruthy();
    expect(screen.getByText("Based on the imported material.")).toBeTruthy();
    expect(screen.getByText("Source materials: 11")).toBeTruthy();
  });

  it("calls generate API and refreshes candidates after generation succeeds", async () => {
    const server = await renderProject();

    fireEvent.click(screen.getByRole("button", { name: "Generate Topic Candidates" }));

    await screen.findByText("Checklist topic");
    expect(server.calls).toContain("POST /api/projects/1/topic-candidates/generate");
    expect(server.bodies["POST /api/projects/1/topic-candidates/generate"]).toBe('{"candidate_count":3}');
    expect(server.calls.filter((call) => call === "GET /api/projects/1/topic-candidates")).toHaveLength(2);
  });

  it("calls select API and refreshes candidates after selection succeeds", async () => {
    const server = await renderProject({ candidates: [candidateOne, candidateTwo] });

    const candidateCard = screen.getByLabelText("Topic candidate: Problem-first topic");
    fireEvent.click(within(candidateCard).getByRole("button", { name: "Select" }));

    await waitFor(() => expect(candidateCard.getAttribute("data-status")).toBe("selected"));
    expect(server.calls).toContain("POST /api/projects/1/topic-candidates/101/select");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/topic-candidates")).toHaveLength(2);
  });

  it("shows a clear selected visual state", async () => {
    await renderProject({ candidates: [candidateTwo] });

    const selectedCard = screen.getByLabelText("Topic candidate: Build log topic");
    expect(selectedCard.getAttribute("data-status")).toBe("selected");
    expect(within(selectedCard).getByText("Selected")).toBeTruthy();
  });

  it("disables generate and select controls for archived projects", async () => {
    await renderProject({
      project: { ...baseProject, status: "archived" },
      candidates: [candidateOne],
    });

    const generateButton = screen.getByRole("button", { name: "Generate Topic Candidates" }) as HTMLButtonElement;
    expect(generateButton.disabled).toBe(true);
    expect((screen.getByRole("button", { name: "Select" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getAllByText("Archived projects are read-only.")[0]).toBeTruthy();
  });

  it("shows a no-materials message when generate returns 409", async () => {
    await renderProject({ generateError: "project has no materials" });

    fireEvent.click(screen.getByRole("button", { name: "Generate Topic Candidates" }));

    expect(await screen.findByText("Add at least one material before generating topic candidates.")).toBeTruthy();
  });

  it("shows a read-only message when select returns archived 409", async () => {
    await renderProject({ candidates: [candidateOne], selectError: "archived project cannot select candidates" });

    fireEvent.click(screen.getByRole("button", { name: "Select" }));

    expect(await screen.findByText("Archived projects are read-only.")).toBeTruthy();
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
    expect(screen.getByText("No script drafts yet.")).toBeTruthy();
  });

  it("shows script draft title, opening hook, body, call to action, duration, and rationale", async () => {
    await renderProject({ scriptDrafts: [scriptDraftOne] });

    expect(screen.getByText("Problem-first script")).toBeTruthy();
    expect(screen.getByText("This workflow looked small until it blocked the whole project.")).toBeTruthy();
    expect(screen.getByText("First, show the bug. Then explain the fix. Close with the repeatable workflow.")).toBeTruthy();
    expect(screen.getByText("Save this flow for your next debugging session.")).toBeTruthy();
    expect(screen.getByText("58 seconds")).toBeTruthy();
    expect(screen.getByText("Built from the selected topic and imported note.")).toBeTruthy();
    expect(screen.getByText("Source materials: 11")).toBeTruthy();
  });

  it("calls generate API and refreshes script drafts after generation succeeds", async () => {
    const server = await renderProject();

    fireEvent.click(screen.getByRole("button", { name: "Generate Script Drafts" }));

    await screen.findByText("Checklist script");
    expect(server.calls).toContain("POST /api/projects/1/script-drafts/generate");
    expect(server.bodies["POST /api/projects/1/script-drafts/generate"]).toBe('{"script_count":2}');
    expect(server.calls.filter((call) => call === "GET /api/projects/1/script-drafts")).toHaveLength(2);
  });

  it("calls select API and refreshes script drafts after selection succeeds", async () => {
    const server = await renderProject({ scriptDrafts: [scriptDraftOne, scriptDraftTwo] });

    const scriptDraftCard = screen.getByLabelText("Script draft: Problem-first script");
    fireEvent.click(within(scriptDraftCard).getByRole("button", { name: "Select" }));

    await waitFor(() => expect(screen.getByLabelText("Script draft: Problem-first script").getAttribute("data-status")).toBe("selected"));
    expect(server.calls).toContain("POST /api/projects/1/script-drafts/501/select");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/script-drafts")).toHaveLength(2);
  });

  it("shows a clear selected visual state for script drafts", async () => {
    await renderProject({ scriptDrafts: [scriptDraftTwo] });

    const selectedCard = screen.getByLabelText("Script draft: Build log script");
    expect(selectedCard.getAttribute("data-status")).toBe("selected");
    expect(within(selectedCard).getByText("Selected")).toBeTruthy();
  });

  it("disables generate and select controls for archived projects", async () => {
    await renderProject({
      project: { ...baseProject, status: "archived" },
      scriptDrafts: [scriptDraftOne],
    });

    const generateButton = screen.getByRole("button", { name: "Generate Script Drafts" }) as HTMLButtonElement;
    const scriptDraftCard = screen.getByLabelText("Script draft: Problem-first script");
    expect(generateButton.disabled).toBe(true);
    expect((within(scriptDraftCard).getByRole("button", { name: "Select" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getAllByText("Archived projects are read-only.")[0]).toBeTruthy();
  });

  it("shows a no-materials message when script generation returns 409", async () => {
    await renderProject({ generateScriptDraftsError: "project has no materials" });

    fireEvent.click(screen.getByRole("button", { name: "Generate Script Drafts" }));

    expect(await screen.findByText("Add at least one material before generating script drafts.")).toBeTruthy();
  });

  it("shows a selected-topic message when script generation returns 409", async () => {
    await renderProject({ generateScriptDraftsError: "project has no selected topic candidate" });

    fireEvent.click(screen.getByRole("button", { name: "Generate Script Drafts" }));

    expect(await screen.findByText("Select a topic candidate before generating script drafts.")).toBeTruthy();
  });

  it("shows a read-only message when script draft selection returns archived 409", async () => {
    await renderProject({
      scriptDrafts: [scriptDraftOne],
      selectScriptDraftError: "archived project cannot select script drafts",
    });

    const scriptDraftCard = screen.getByLabelText("Script draft: Problem-first script");
    fireEvent.click(within(scriptDraftCard).getByRole("button", { name: "Select" }));

    expect(await screen.findByText("Archived projects are read-only.")).toBeTruthy();
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
    expect(screen.getByText("No storyboards yet.")).toBeTruthy();
  });

  it("shows storyboard title, summary, and visual style", async () => {
    await renderProject({ storyboards: [storyboardOne] });

    expect(screen.getByText("Storyboard walkthrough")).toBeTruthy();
    expect(screen.getByText("A source-backed storyboard for the selected script.")).toBeTruthy();
    expect(screen.getByText("Clean screen-recording style")).toBeTruthy();
    expect(screen.getByText("Source materials")).toBeTruthy();
  });

  it("shows storyboard scenes with their structured fields", async () => {
    await renderProject({ storyboards: [storyboardOne] });

    const firstScene = screen.getByLabelText("Scene 1: Set up the problem");
    expect(within(firstScene).getByText("Scene 1: Set up the problem")).toBeTruthy();
    expect(within(firstScene).getByText("Start with the workflow problem.")).toBeTruthy();
    expect(within(firstScene).getByText("Show the imported material that anchors the story.")).toBeTruthy();
    expect(within(firstScene).getByText("The problem")).toBeTruthy();
    expect(within(firstScene).getByText("12 seconds")).toBeTruthy();
    expect(within(firstScene).getByText("11")).toBeTruthy();
  });

  it("shows storyboard scenes sorted by scene order", async () => {
    await renderProject({ storyboards: [storyboardOne] });

    const storyboardCard = screen.getByLabelText("Storyboard: Storyboard walkthrough");
    const sceneItems = within(storyboardCard).getAllByTestId("storyboard-scene");
    expect(sceneItems.map((scene) => scene.getAttribute("data-scene-order"))).toEqual(["1", "2"]);
  });

  it("calls generate API and refreshes storyboards after generation succeeds", async () => {
    const server = await renderProject();

    fireEvent.click(screen.getByRole("button", { name: "Generate Storyboards" }));

    await screen.findByText("Storyboard walkthrough");
    expect(server.calls).toContain("POST /api/projects/1/storyboards/generate");
    expect(server.bodies["POST /api/projects/1/storyboards/generate"]).toBe('{"storyboard_count":1}');
    expect(server.calls.filter((call) => call === "GET /api/projects/1/storyboards")).toHaveLength(2);
  });

  it("calls select API and refreshes storyboards after selection succeeds", async () => {
    const server = await renderProject({ storyboards: [storyboardOne, storyboardTwo] });

    const storyboardCard = screen.getByLabelText("Storyboard: Storyboard walkthrough");
    fireEvent.click(within(storyboardCard).getByRole("button", { name: "Select" }));

    await waitFor(() => expect(screen.getByLabelText("Storyboard: Storyboard walkthrough").getAttribute("data-status")).toBe("selected"));
    expect(server.calls).toContain("POST /api/projects/1/storyboards/801/select");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/storyboards")).toHaveLength(2);
  });

  it("shows a clear selected visual state for storyboards", async () => {
    await renderProject({ storyboards: [storyboardTwo] });

    const selectedCard = screen.getByLabelText("Storyboard: Selected storyboard");
    expect(selectedCard.getAttribute("data-status")).toBe("selected");
    expect(within(selectedCard).getByText("Selected")).toBeTruthy();
  });

  it("disables generate and select controls for archived projects", async () => {
    await renderProject({
      project: { ...baseProject, status: "archived" },
      storyboards: [storyboardOne],
    });

    const generateButton = screen.getByRole("button", { name: "Generate Storyboards" }) as HTMLButtonElement;
    const storyboardCard = screen.getByLabelText("Storyboard: Storyboard walkthrough");
    expect(generateButton.disabled).toBe(true);
    expect((within(storyboardCard).getByRole("button", { name: "Select" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getAllByText("Archived projects are read-only.")[0]).toBeTruthy();
  });

  it("shows a no-materials message when storyboard generation returns 409", async () => {
    await renderProject({ generateStoryboardsError: "project has no materials" });

    fireEvent.click(screen.getByRole("button", { name: "Generate Storyboards" }));

    expect(await screen.findByText("Add at least one material before generating storyboards.")).toBeTruthy();
  });

  it("shows a selected-topic message when storyboard generation returns 409", async () => {
    await renderProject({ generateStoryboardsError: "project has no selected topic candidate" });

    fireEvent.click(screen.getByRole("button", { name: "Generate Storyboards" }));

    expect(await screen.findByText("Select a topic candidate before generating storyboards.")).toBeTruthy();
  });

  it("shows a selected-script message when storyboard generation returns 409", async () => {
    await renderProject({ generateStoryboardsError: "project has no selected script draft" });

    fireEvent.click(screen.getByRole("button", { name: "Generate Storyboards" }));

    expect(await screen.findByText("Select a script draft before generating storyboards.")).toBeTruthy();
  });

  it("shows a read-only message when storyboard selection returns archived 409", async () => {
    await renderProject({
      storyboards: [storyboardOne],
      selectStoryboardError: "archived project cannot select storyboards",
    });

    const storyboardCard = screen.getByLabelText("Storyboard: Storyboard walkthrough");
    fireEvent.click(within(storyboardCard).getByRole("button", { name: "Select" }));

    expect(await screen.findByText("Archived projects are read-only.")).toBeTruthy();
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
    expect(screen.getByText("Subtitle Drafts")).toBeTruthy();
    expect(screen.getByText("No subtitle drafts yet.")).toBeTruthy();
  });

  it("shows subtitle draft metadata and cues", async () => {
    await renderProject({ storyboards: [storyboardTwo], subtitleDrafts: [subtitleDraftOne] });

    const subtitleDraftCard = screen.getByLabelText("Subtitle draft 1301");
    expect(within(subtitleDraftCard).getByText("Subtitle draft #1301")).toBeTruthy();
    expect(within(subtitleDraftCard).getByText("fake_subtitle_generator 0.1")).toBeTruthy();
    expect(within(subtitleDraftCard).getByText("draft")).toBeTruthy();
    expect(within(subtitleDraftCard).getByText("#802")).toBeTruthy();
    expect(within(subtitleDraftCard).getByText("Start with the selected storyboard.")).toBeTruthy();
    expect(within(subtitleDraftCard).getByText("Use deterministic subtitle cue metadata.")).toBeTruthy();
    expect(within(subtitleDraftCard).getByText("0s - 12s")).toBeTruthy();
    expect(within(subtitleDraftCard).getByText("12s - 30s")).toBeTruthy();
  });

  it("shows subtitle cues sorted by cue order", async () => {
    await renderProject({ storyboards: [storyboardTwo], subtitleDrafts: [subtitleDraftOne] });

    const subtitleDraftCard = screen.getByLabelText("Subtitle draft 1301");
    const cueItems = within(subtitleDraftCard).getAllByTestId("subtitle-cue");
    expect(cueItems.map((cue) => cue.getAttribute("data-cue-order"))).toEqual(["1", "2"]);
  });

  it("creates a fake subtitle draft and refreshes subtitle drafts after creation succeeds", async () => {
    const server = await renderProject({ storyboards: [storyboardTwo] });

    await waitFor(() =>
      expect((screen.getByRole("button", { name: "Create fake subtitle draft" }) as HTMLButtonElement).disabled).toBe(
        false,
      ),
    );
    fireEvent.click(screen.getByRole("button", { name: "Create fake subtitle draft" }));

    await screen.findByText("Subtitle draft #1301");
    expect(server.calls).toContain("POST /api/projects/1/subtitle-drafts");
    expect(server.bodies["POST /api/projects/1/subtitle-drafts"]).toBe("{}");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/subtitle-drafts")).toHaveLength(2);
  });

  it("selects a subtitle draft and refreshes subtitle drafts after selection succeeds", async () => {
    const server = await renderProject({ storyboards: [storyboardTwo], subtitleDrafts: [subtitleDraftOne, subtitleDraftTwo] });

    const subtitleDraftCard = screen.getByLabelText("Subtitle draft 1301");
    fireEvent.click(within(subtitleDraftCard).getByRole("button", { name: "Select" }));

    await waitFor(() => expect(screen.getByLabelText("Subtitle draft 1301").getAttribute("data-status")).toBe("selected"));
    expect(server.calls).toContain("POST /api/projects/1/subtitle-drafts/1301/select");
    expect(server.calls.filter((call) => call === "GET /api/projects/1/subtitle-drafts")).toHaveLength(2);
  });

  it("disables fake subtitle creation and selection for archived projects while keeping drafts visible", async () => {
    await renderProject({
      project: { ...baseProject, status: "archived" },
      storyboards: [storyboardTwo],
      subtitleDrafts: [subtitleDraftOne],
    });

    const subtitleDraftCard = screen.getByLabelText("Subtitle draft 1301");
    expect(screen.getByText("Subtitle draft #1301")).toBeTruthy();
    expect((screen.getByRole("button", { name: "Create fake subtitle draft" }) as HTMLButtonElement).disabled).toBe(true);
    expect((within(subtitleDraftCard).getByRole("button", { name: "Select" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getAllByText("Archived projects are read-only.")[0]).toBeTruthy();
  });

  it("disables fake subtitle creation when there is no selected storyboard", async () => {
    await renderProject({ storyboards: [storyboardOne] });

    await screen.findByText("Select a storyboard before creating fake subtitle drafts.");
    expect((screen.getByRole("button", { name: "Create fake subtitle draft" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it("shows a visible error when fake subtitle creation fails", async () => {
    await renderProject({ createSubtitleDraftError: "subtitle service unavailable", storyboards: [storyboardTwo] });

    await waitFor(() =>
      expect((screen.getByRole("button", { name: "Create fake subtitle draft" }) as HTMLButtonElement).disabled).toBe(
        false,
      ),
    );
    fireEvent.click(screen.getByRole("button", { name: "Create fake subtitle draft" }));

    expect(await screen.findByText("subtitle service unavailable")).toBeTruthy();
  });

  it("shows a visible error when subtitle selection fails", async () => {
    await renderProject({
      selectSubtitleDraftError: "archived project cannot select subtitle drafts",
      storyboards: [storyboardTwo],
      subtitleDrafts: [subtitleDraftOne],
    });

    const subtitleDraftCard = screen.getByLabelText("Subtitle draft 1301");
    fireEvent.click(within(subtitleDraftCard).getByRole("button", { name: "Select" }));

    expect(await screen.findByText("Archived projects are read-only.")).toBeTruthy();
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
    expect(screen.getByText("Render Jobs")).toBeTruthy();
    expect(screen.getByText("No render jobs yet.")).toBeTruthy();
  });

  it("shows fake preview manifest metadata", async () => {
    await renderProject({ renderJobs: [renderJobOne], storyboards: [storyboardTwo] });

    const renderJobCard = screen.getByLabelText("Render job 1201");
    expect(within(renderJobCard).getByText("Render job #1201")).toBeTruthy();
    expect(within(renderJobCard).getByText("fake_renderer 0.1")).toBeTruthy();
    expect(within(renderJobCard).getByText("succeeded")).toBeTruthy();
    expect(within(renderJobCard).getByText("mp4 / 9:16 / 1080x1920")).toBeTruthy();
    expect(within(renderJobCard).getByText("Preview manifest metadata")).toBeTruthy();
    expect(within(renderJobCard).getByText("fake_preview_manifest")).toBeTruthy();
    expect(within(renderJobCard).getByText("application/json")).toBeTruthy();
    expect(within(renderJobCard).getByText("386 bytes")).toBeTruthy();
    expect(within(renderJobCard).getByText("a".repeat(64))).toBeTruthy();
    expect(within(renderJobCard).getByText("30 seconds")).toBeTruthy();
    expect(within(renderJobCard).getByText("1080 x 1920")).toBeTruthy();
    expect(within(renderJobCard).getByText("#1301")).toBeTruthy();
    expect(within(renderJobCard).getByText("project-1-render-1201-preview-manifest.json")).toBeTruthy();
    expect(within(renderJobCard).getByText("data/local/render_previews/project-1/project-1-render-1201-preview-manifest.json")).toBeTruthy();
    expect(within(renderJobCard).getByText("Not available")).toBeTruthy();
  });

  it("shows a fallback when a succeeded render job has no preview metadata", async () => {
    await renderProject({ renderJobs: [renderJobWithoutArtifact], storyboards: [storyboardTwo] });

    const renderJobCard = screen.getByLabelText("Render job 1202");
    expect(within(renderJobCard).getByText("No preview artifact metadata available.")).toBeTruthy();
  });

  it("does not render a video player for non-succeeded render jobs", async () => {
    await renderProject({ renderJobs: [queuedRenderJob], storyboards: [storyboardTwo] });

    const renderJobCard = screen.getByLabelText("Render job 1203");
    expect(within(renderJobCard).getByText("Preview pending / unavailable.")).toBeTruthy();
    expect(document.querySelector("video")).toBeNull();
  });

  it("creates a fake render job and refreshes render jobs after creation succeeds", async () => {
    const server = await renderProject({ storyboards: [storyboardTwo] });

    await waitFor(() => expect((screen.getByRole("button", { name: "Create fake render job" }) as HTMLButtonElement).disabled).toBe(false));
    fireEvent.click(screen.getByRole("button", { name: "Create fake render job" }));

    await screen.findByText("Render job #1201");
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

    expect(screen.getByText("Render job #1201")).toBeTruthy();
    expect(screen.getByText("data/local/render_previews/project-1/project-1-render-1201-preview-manifest.json")).toBeTruthy();
    expect((screen.getByRole("button", { name: "Create fake render job" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getAllByText("Archived projects are read-only.")[0]).toBeTruthy();
  });

  it("disables fake render creation when there is no selected storyboard", async () => {
    await renderProject({ storyboards: [storyboardOne] });

    await screen.findByText("Select a storyboard before creating fake render jobs.");
    expect((screen.getByRole("button", { name: "Create fake render job" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it("shows a visible error when fake render creation fails", async () => {
    await renderProject({ createRenderError: "render service unavailable", storyboards: [storyboardTwo] });

    await waitFor(() => expect((screen.getByRole("button", { name: "Create fake render job" }) as HTMLButtonElement).disabled).toBe(false));
    fireEvent.click(screen.getByRole("button", { name: "Create fake render job" }));

    expect(await screen.findByText("render service unavailable")).toBeTruthy();
  });
});
