# creator-flow

[简体中文](README.md) | [English](README.en.md)

creator-flow is an open-source AI short-video content pipeline for turning user-provided ideas, chat summaries, text, images, screenshots, and links into review-ready short-video drafts.

## Status

`v0.8.0 - Provider & Credential Security Foundation`

This repository has completed the v0.1 local runnable skeleton, the v0.2 AI Planning Workflow, the v0.3 fake rendering/subtitle/preview workflow, the v0.4 local fake/manual Scheduled Draft Generation workflow, the v0.5 Human-Confirmed Publishing Workflow, the v0.6.0 local fake/manual metrics feedback workflow, the v0.7.0 Metrics Review Summary local fake/manual workflow, and the v0.8.0 Provider & Credential Security Foundation. v0.8.0 completes Provider Registry & Capability Metadata, Provider Connection State, Provider Credential Reference & Secret Redaction, Provider Security Audit Event & Redacted Audit Log, Provider OAuth State & Callback Boundary, Provider Token Lifecycle Boundary, Provider Integration Readiness Summary, matching frontend read-only UI panels, and the v0.8 RC checklist / closure audit.

Local development instructions are available in [`docs/development.md`](docs/development.md), the v0.5 release candidate checklist is available in [`docs/releases/v0.5-rc-checklist.md`](docs/releases/v0.5-rc-checklist.md), the v0.6.0 metrics release checklist is available in [`docs/checklists/v0.6-metrics-feedback-loop-rc.md`](docs/checklists/v0.6-metrics-feedback-loop-rc.md), the v0.7 metrics review summary RC checklist is available in [`docs/checklists/v0.7-metrics-review-summary-rc.md`](docs/checklists/v0.7-metrics-review-summary-rc.md), the v0.8 Provider & Credential Security Foundation RC audit checklist is available in [`docs/checklists/v0.8-provider-security-foundation-rc.md`](docs/checklists/v0.8-provider-security-foundation-rc.md), and the v0.8.0 release notes are available in [`docs/releases/v0.8.0-provider-security-foundation.md`](docs/releases/v0.8.0-provider-security-foundation.md).

v0.8.0 still has no real Douyin integration, no OAuth implementation, no OAuth callback route, no OAuth state storage, no token exchange, no real provider authorization URL generation, no token / secret / API key / credential / authorization code / OAuth state storage, no real metrics fetching, no upload / publish / scheduling, and no external service calls. v0.8.0 is a security-boundary foundation release, not a production-ready real Douyin integration and not a production deployment.

## Roadmap To Douyin User Testing

The current stable release is `v0.8.0 - Provider & Credential Security Foundation`. v0.8.0 has completed the Provider & Credential Security Foundation release; the next stage is v0.9 Douyin Provider POC / Sandbox Integration, and the roadmap continues a gradual path toward Douyin user testing:

- v0.8.0 Provider & Credential Security Foundation (released): Batch 1-16 completed Provider, credential, OAuth, secret, token lifecycle, security audit, source separation, Provider Registry, Connection State, Credential Reference, Security Audit, OAuth Boundary, Token Lifecycle Boundary, Integration Readiness Summary, matching frontend read-only UI panels, the RC checklist, and closure audit. This release provides only metadata-only / read-only security foundations: no real Douyin integration, no OAuth implementation, no OAuth callback route, no OAuth state storage, no token exchange, no real provider authorization URL generation, no token / secret / API key / credential / authorization code / OAuth state storage, no real metrics fetching, no upload / publish / scheduling, no external service calls, and no production-ready real Douyin integration claim.
- v0.9 Douyin Provider POC / Sandbox Integration: the stage for a Douyin Provider POC / Sandbox Integration, sandbox/mock callbacks, account connection status, and minimal metrics-reading validation.
- v1.0 Douyin Integration User Test Release: the stage for a Douyin integration user test release, not a production-grade automated publishing release.

Real Douyin integration still depends on platform availability, app review, OAuth, API permissions, and explicit user authorization. This roadmap does not mean the current app already connects to real Douyin, implements OAuth, stores tokens, fetches real metrics, publishes real content, auto-publishes, batch-publishes, schedules publishing, or provides a production platform dashboard.

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

Topic Candidate, Script Draft, and Storyboard generation and selection are implemented in v0.2 with a local fake provider. v0.3 has completed Release Candidate closure for fake render jobs, fake preview manifest metadata display, fake subtitle drafts, and subtitle cues. v0.4 has completed Release Candidate closure for ContentPlan, GenerationSchedule, fake manual GenerationRun, and Review Draft placeholders. v0.5 has completed the PublishIntent / PublicationRecord backend foundation, confirm workflow foundation, fake publisher execution foundation, project detail local fake publishing workflow, RC checklist, final validation, and v0.5.0 release. v0.6.0 has completed Metrics Feedback Loop boundary documentation, the backend-only fake metrics domain foundation, the project detail fake metrics UI foundation, the metrics workflow RC checklist, and release finalization. v0.7.0 has completed the backend-only fake/local metrics review summary foundation, the project detail fake/local metrics review summary UI foundation, workflow stabilization, the RC checklist, and release finalization. Real AI, real subtitle files, real audio, asset plans, real MP4 rendering and playback, real OAuth, real upload, real publishing, token storage, auto-publishing, scheduled publishing, real Douyin API, a real PublisherProvider, real metrics fetching, scheduled metrics synchronization, analytics recommendation algorithms, real platform dashboards, scheduled GenerationRun, Scheduler / Trigger Engine, and a complete Review Queue remain future planned capabilities.

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
- On the project detail page, explicitly create a `PublishIntent` from an approved `Review Draft` in the same project, view publish intent lists/statuses, and cancel pending publish intents.
- On the project detail page, confirm a pending `PublishIntent`, mark it as `confirmed`, and create one local `not_started` `PublicationRecord` placeholder; this does not execute real platform actions.
- On the project detail page, view `PublicationRecord` entries and run local Fake Publish for a confirmed PublishIntent, moving the matching record from `not_started` to `succeeded` with a stable fake external publication id; this does not mean a real platform publish succeeded.
- Query `PublicationRecord` lists for a specific `PublishIntent`.
- On the project detail page, create deterministic fake metrics snapshots for a specific `PublicationRecord`, then list or read metrics snapshots for that record; `source` is explicitly `fake_local`, boundary labels are visible, and these metrics do not represent real platform performance.
- On the project detail page, create deterministic fake/local metrics review summaries for a specific `PublicationRecord`, then list or read summaries for that record; summaries are only manual review references, not real platform analysis, and they do not automatically modify topics, scripts, or content plans.
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
