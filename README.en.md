# creator-flow

[简体中文](README.md) | [English](README.en.md)

creator-flow is an open-source AI short-video content pipeline for turning user-provided ideas, chat summaries, text, images, screenshots, and links into review-ready short-video drafts.

## Status

`v0.5 Human-Confirmed Douyin Publishing - Batch 2 backend domain foundation`

This repository has completed the v0.1 local runnable skeleton, the v0.2 AI Planning Workflow, the v0.3 fake rendering/subtitle/preview workflow, the v0.4 local fake/manual Scheduled Draft Generation workflow, and v0.5 Batch 1 through Batch 2 of the publishing boundary and backend domain foundation. The current path supports the local deterministic `FakeLLMProvider` workflow for Topic Candidates, Script Drafts, Storyboards, fake render jobs, fake subtitle drafts, and fake preview manifest metadata; v0.4 also supports project-level `ContentPlan`, `GenerationSchedule` configuration, fake manual `GenerationRun` records, and `Review Draft` placeholders created from manual runs. v0.5 currently adds backend-only `PublishIntent` / `PublicationRecord` foundations: a publish intent can only be explicitly created from an approved Review Draft in the same project, then read or cancelled.

Local development instructions are available in [`docs/development.md`](docs/development.md).

Real OpenAI, Claude, Gemini, or other LLM integrations are still not implemented. The app does not store API keys, secrets, or tokens and does not call real AI services. v0.4 is still a local fake/manual workflow: scheduled `GenerationRun`, Scheduler / Trigger Engine, a complete `Review Queue`, real MP4 rendering, real video playback, FFmpeg, TTS, real subtitle files, real audio, platform publishing, production deployment, and user accounts are still not implemented. Review Drafts remain placeholders; approve / reject only changes review status and does not publish, upload, render, or generate media. The v0.5 publishing domain is also only a backend foundation: it does not connect to the Douyin API, implement OAuth, store credentials, upload, publish, schedule, or auto-publish.
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

Topic Candidate, Script Draft, and Storyboard generation and selection are implemented in v0.2 with a local fake provider. v0.3 has completed Release Candidate closure for fake render jobs, fake preview manifest metadata display, fake subtitle drafts, and subtitle cues. v0.4 has completed Release Candidate closure for ContentPlan, GenerationSchedule, fake manual GenerationRun, and Review Draft placeholders. v0.5 has started the PublishIntent / PublicationRecord backend foundation. Real AI, real subtitle files, real audio, asset plans, real MP4 rendering and playback, real publishing, scheduled GenerationRun, Scheduler / Trigger Engine, a complete Review Queue, and metrics feedback remain future planned capabilities.

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
- Create and view `ContentPlan` records, including account positioning, content type, weekly target frequency, preferences, and enable / disable state.
- Create and view `GenerationSchedule` configuration bound to a `ContentPlan`, including enable / disable state; scheduled triggers are not executed yet.
- Manually create fake `GenerationRun` records and synchronously create review-ready `Review Draft` placeholders; the project detail page refreshes GenerationRuns and Review Drafts after a manual run.
- View `Review Draft` placeholders and approve / reject their review status; these actions do not publish, upload, render, or generate media.
- Explicitly create a `PublishIntent` from an approved `Review Draft` in the same project, list/read publish intents, and cancel pending publish intents; this does not create publication records or execute real platform actions.
- Query `PublicationRecord` lists for a specific `PublishIntent`; the current backend foundation does not create real publication records by default.
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
