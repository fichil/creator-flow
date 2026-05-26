import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProjectDetailPage } from "./ProjectDetailPage";
import type { ProjectDetail, TopicCandidate } from "../api/client";

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

type ServerOptions = {
  project?: ProjectDetail;
  candidates?: TopicCandidate[];
  generateError?: string;
  selectError?: string;
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
