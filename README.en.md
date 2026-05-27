# creator-flow

[简体中文](README.md) | [English](README.en.md)

creator-flow is an open-source AI short-video content pipeline for turning user-provided ideas, chat summaries, text, images, screenshots, and links into review-ready short-video drafts.

## Status

`v0.3 Rendering Workflow - Batch 7 Release Candidate`

This repository has completed the v0.1 local runnable skeleton, the v0.2 AI Planning Workflow, and v0.3 Batch 1 through Batch 7 of the fake rendering/subtitle/preview workflow. v0.3 Batch 7 completed fake workflow stabilization and Release Candidate closure. The current planning path uses a local deterministic `FakeLLMProvider` to generate and select Topic Candidates, Script Drafts, and Storyboards from explicitly imported materials, including storyboard scenes on the project detail page; the app can also create fake render jobs, show fake preview manifest metadata, create fake subtitle drafts, and show subtitle cues from a selected Storyboard.

Local development instructions are available in [`docs/development.md`](docs/development.md).

Real OpenAI, Claude, Gemini, or other LLM integrations are still not implemented. The app does not store API keys, secrets, or tokens and does not call real AI services. v0.3 has completed Release Candidate closure for the fake rendering/subtitle/preview metadata workflow, but real MP4 rendering, real video playback, FFmpeg, TTS, real subtitle files, real audio, scheduled generation, platform publishing, production deployment, and user accounts are still not implemented.
This version is not production ready.

## Local Quick Start

From the repository root in Windows PowerShell:

```powershell
.\scripts\dev-backend.ps1
```

Open another PowerShell:

```powershell
.\scripts\dev-frontend.ps1
```

Common verification commands:

```powershell
.\scripts\test-backend.ps1
.\scripts\build-frontend.ps1
.\scripts\smoke-api.ps1
```

## Planned Capabilities

- Explicitly import user-selected chat summaries, text, images, screenshots, and links.
- Generate topic ideas, scripts, storyboards, subtitles, and asset plans behind Provider boundaries.
- Produce 9:16 MP4 videos through an `FFmpeg` pipeline.
- Configure content plans, account positioning, content types, and generation frequency.
- Automatically generate review-ready drafts on schedule from explicitly imported materials and optional trend signals.
- Place generated video projects into a `Review Queue` before any publishing step.
- Feed post-publication metrics back into future content review and topic optimization.
- Use Douyin as the first publishing platform while preserving a multi-platform architecture through Provider abstractions.

Topic Candidate, Script Draft, and Storyboard generation and selection are implemented in v0.2 with a local fake provider. v0.3 has completed Release Candidate closure for fake render jobs, fake preview manifest metadata display, fake subtitle drafts, and subtitle cues. Real AI, real subtitle files, real audio, asset plans, real MP4 rendering and playback, publishing, scheduling, and metrics feedback remain future planned capabilities.

## Current Local Capabilities

- Start the backend and frontend locally.
- Create a `ContentProject`.
- Explicitly add text, summary, project record, link, image, and screenshot materials to a project.
- View the project list, project details, and material list.
- Generate and select Topic Candidates from explicitly imported materials.
- Generate and select Script Drafts from a selected Topic Candidate.
- Generate Storyboards from a selected Topic Candidate, selected Script Draft, and explicit materials, then inspect ordered scenes.
- Create fake render jobs from a selected Storyboard and persist deterministic fake preview manifest metadata; the project detail page shows that metadata, but it does not read runtime manifest files or play real video, and no real MP4 file is generated yet.
- Create fake subtitle drafts from a selected Storyboard and persist deterministic subtitle cue metadata; no real `.srt` / `.vtt`, audio, or video file is generated yet.
- View existing materials and planning drafts on archived projects while preventing further generation or selection.
- Store project and material metadata in local `SQLite`.
- Store uploaded files under local `uploads/`, excluded from Git.

## Automation Boundary

creator-flow may eventually generate drafts automatically according to the user's configured frequency. Automation may only create review-ready drafts. Any action that publishes, schedules, or uploads content for public release on Douyin or another platform must require explicit user review and confirmation.

## Product Principles

- User materials must be explicitly imported. The MVP must not automatically read private ChatGPT history.
- The system must not scan local files, browser sessions, or private accounts by default.
- Trend signals may support topic selection, but the account narrative should remain grounded in the user's real experience and original materials.
- The first content direction focuses on real programmer problems, AI-assisted solutions, and open-source project development logs.
- External AI, trend, TTS, video rendering, and platform publishing capabilities must be abstracted behind Provider interfaces.
- The first video generation path uses scripts + images or screenshots + TTS + subtitles + `FFmpeg`.
- Expensive pure AI text-to-video capabilities may be optional future Providers, not the MVP default path.

## Privacy

creator-flow should only process materials explicitly provided by the user or data sources explicitly enabled by the user. Secrets, tokens, uploaded materials, local databases, generated videos, generated audio, generated images, subtitles, and private content must not be committed to the repository.

## License

Apache-2.0. See `LICENSE`.
