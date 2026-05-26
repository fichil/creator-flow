import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProjectDetailPage } from "./ProjectDetailPage";
import type { ProjectDetail, ScriptDraft, TopicCandidate } from "../api/client";

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

type ServerOptions = {
  project?: ProjectDetail;
  candidates?: TopicCandidate[];
  scriptDrafts?: ScriptDraft[];
  generateError?: string;
  generateScriptDraftsError?: string;
  selectError?: string;
  selectScriptDraftError?: string;
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
