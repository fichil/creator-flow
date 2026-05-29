# creator-flow

[简体中文](README.md) | [English](README.en.md)

creator-flow is an open-source AI short-video content pipeline for turning user-provided ideas, chat summaries, text, images, screenshots, and links into review-ready short-video drafts.

## Status

`v1.0 Batch 7 - Real Publish Adapter Guarded Implementation`

This repository has completed the v0.1 local runnable skeleton, the v0.2 AI Planning Workflow, the v0.3 fake rendering/subtitle/preview workflow, the v0.4 local fake/manual Scheduled Draft Generation workflow, the v0.5 Human-Confirmed Publishing Workflow, the v0.6.0 local fake/manual metrics feedback workflow, the v0.7.0 Metrics Review Summary local fake/manual workflow, the v0.8.0 Provider & Credential Security Foundation, and the v0.9.0 Douyin Provider POC / Sandbox Integration release. v0.9.0 was released from release commit `0f5263452b65077f2c70c82e506944dd46e60e96` as the POC / Sandbox Integration release.

Local development instructions are available in [`docs/development.md`](docs/development.md), the v0.5 release candidate checklist is available in [`docs/releases/v0.5-rc-checklist.md`](docs/releases/v0.5-rc-checklist.md), the v0.6.0 metrics release checklist is available in [`docs/checklists/v0.6-metrics-feedback-loop-rc.md`](docs/checklists/v0.6-metrics-feedback-loop-rc.md), the v0.7 metrics review summary RC checklist is available in [`docs/checklists/v0.7-metrics-review-summary-rc.md`](docs/checklists/v0.7-metrics-review-summary-rc.md), the v0.8 Provider & Credential Security Foundation RC audit checklist is available in [`docs/checklists/v0.8-provider-security-foundation-rc.md`](docs/checklists/v0.8-provider-security-foundation-rc.md), and the v0.8.0 release notes are available in [`docs/releases/v0.8.0-provider-security-foundation.md`](docs/releases/v0.8.0-provider-security-foundation.md). The v0.9 Batch 0 planning checklist is available in [`docs/checklists/v0.9-douyin-provider-poc-readiness.md`](docs/checklists/v0.9-douyin-provider-poc-readiness.md), the v0.9 entry ADR is available in [`docs/decisions/0035-v0.9-douyin-provider-poc-sandbox-entry.md`](docs/decisions/0035-v0.9-douyin-provider-poc-sandbox-entry.md), the v0.9 Batch 1 adapter skeleton ADR is available in [`docs/decisions/0036-v0.9-douyin-provider-adapter-skeleton.md`](docs/decisions/0036-v0.9-douyin-provider-adapter-skeleton.md), the v0.9 Batch 2 sandbox ops ADR is available in [`docs/decisions/0037-v0.9-douyin-provider-sandbox-ops.md`](docs/decisions/0037-v0.9-douyin-provider-sandbox-ops.md), the v0.9 Batch 3 registry routing ADR is available in [`docs/decisions/0038-v0.9-douyin-provider-registry-routing.md`](docs/decisions/0038-v0.9-douyin-provider-registry-routing.md), the v0.9 Batch 4 sandbox metrics / mock workflow ADR is available in [`docs/decisions/0039-v0.9-douyin-provider-sandbox-metrics-poc.md`](docs/decisions/0039-v0.9-douyin-provider-sandbox-metrics-poc.md), the v0.9 Batch 5 roadmap alignment ADR is available in [`docs/decisions/0040-v0.9-roadmap-to-v2-commercial-release.md`](docs/decisions/0040-v0.9-roadmap-to-v2-commercial-release.md), the v0.9 Batch 6 sandbox API contract ADR is available in [`docs/decisions/0041-v0.9-douyin-sandbox-api-contract.md`](docs/decisions/0041-v0.9-douyin-sandbox-api-contract.md), the v0.9 Batch 7 frontend sandbox POC ADR is available in [`docs/decisions/0042-v0.9-douyin-frontend-sandbox-poc.md`](docs/decisions/0042-v0.9-douyin-frontend-sandbox-poc.md), and the v0.9 Batch 8 readiness finalization ADR is available in [`docs/decisions/0043-v0.9-poc-readiness-finalization.md`](docs/decisions/0043-v0.9-poc-readiness-finalization.md). The v0.9 RC checklist is available in [`docs/releases/v0.9-douyin-provider-poc-rc-checklist.md`](docs/releases/v0.9-douyin-provider-poc-rc-checklist.md), and the v0.9 test matrix is available in [`docs/testing/v0.9-douyin-provider-poc-test-matrix.md`](docs/testing/v0.9-douyin-provider-poc-test-matrix.md). The v1.0 to v2.0 commercial roadmap is available in [`docs/roadmap-v1-to-v2-commercial-release.md`](docs/roadmap-v1-to-v2-commercial-release.md), with readiness checklists for [`v1.0`](docs/checklists/v1.0-douyin-user-test-release-readiness.md), [`v1.5`](docs/checklists/v1.5-minimum-production-release-readiness.md), and [`v2.0`](docs/checklists/v2.0-multi-tenant-saas-commercial-release-readiness.md).

The v0.9 Batch 9 release / PR merge preparation ADR is available in [`docs/decisions/0044-v0.9-release-merge-preparation.md`](docs/decisions/0044-v0.9-release-merge-preparation.md), with the PR description draft in [`docs/releases/v0.9-pr-description-draft.md`](docs/releases/v0.9-pr-description-draft.md), release notes draft in [`docs/releases/v0.9-release-notes-draft.md`](docs/releases/v0.9-release-notes-draft.md), merge readiness checklist in [`docs/releases/v0.9-merge-readiness-checklist.md`](docs/releases/v0.9-merge-readiness-checklist.md), and tag readiness checklist in [`docs/releases/v0.9-tag-readiness-checklist.md`](docs/releases/v0.9-tag-readiness-checklist.md). The v1.0 Batch 0 planning ADR is available in [`docs/decisions/0045-v1.0-douyin-user-test-release-planning.md`](docs/decisions/0045-v1.0-douyin-user-test-release-planning.md), and the v1.0 plan is available in [`docs/plans/v1.0-douyin-user-test-release-plan.md`](docs/plans/v1.0-douyin-user-test-release-plan.md). The v1.0 Batch 1 OAuth boundary / callback contract ADR is available in [`docs/decisions/0046-v1.0-oauth-boundary-callback-contract.md`](docs/decisions/0046-v1.0-oauth-boundary-callback-contract.md), the callback contract is available in [`docs/contracts/v1.0-douyin-oauth-callback-contract.md`](docs/contracts/v1.0-douyin-oauth-callback-contract.md), and the contract test matrix is available in [`docs/testing/v1.0-oauth-callback-contract-test-matrix.md`](docs/testing/v1.0-oauth-callback-contract-test-matrix.md). The v1.0 Batch 2 OAuth state storage / anti-replay ADR is available in [`docs/decisions/0047-v1.0-oauth-state-storage-anti-replay.md`](docs/decisions/0047-v1.0-oauth-state-storage-anti-replay.md), the state storage contract is available in [`docs/contracts/v1.0-douyin-oauth-state-storage-contract.md`](docs/contracts/v1.0-douyin-oauth-state-storage-contract.md), and the state storage test matrix is available in [`docs/testing/v1.0-oauth-state-storage-test-matrix.md`](docs/testing/v1.0-oauth-state-storage-test-matrix.md). The v1.0 Batch 3 token exchange boundary ADR is available in [`docs/decisions/0048-v1.0-token-exchange-boundary-fake-gated.md`](docs/decisions/0048-v1.0-token-exchange-boundary-fake-gated.md), the token exchange boundary contract is available in [`docs/contracts/v1.0-douyin-token-exchange-boundary-contract.md`](docs/contracts/v1.0-douyin-token-exchange-boundary-contract.md), and the test matrix is available in [`docs/testing/v1.0-token-exchange-boundary-test-matrix.md`](docs/testing/v1.0-token-exchange-boundary-test-matrix.md). The v1.0 Batch 4 credential storage boundary ADR is available in [`docs/decisions/0049-v1.0-credential-reference-encrypted-storage-design.md`](docs/decisions/0049-v1.0-credential-reference-encrypted-storage-design.md), the credential storage boundary contract is available in [`docs/contracts/v1.0-douyin-credential-storage-boundary-contract.md`](docs/contracts/v1.0-douyin-credential-storage-boundary-contract.md), and the test matrix is available in [`docs/testing/v1.0-credential-storage-boundary-test-matrix.md`](docs/testing/v1.0-credential-storage-boundary-test-matrix.md).

The v1.0 Batch 5 real provider feature flag / kill switch ADR is available in [`docs/decisions/0050-v1.0-real-provider-feature-flag-kill-switch.md`](docs/decisions/0050-v1.0-real-provider-feature-flag-kill-switch.md), the contract is available in [`docs/contracts/v1.0-real-provider-feature-flag-kill-switch-contract.md`](docs/contracts/v1.0-real-provider-feature-flag-kill-switch-contract.md), and the test matrix is available in [`docs/testing/v1.0-real-provider-feature-flag-kill-switch-test-matrix.md`](docs/testing/v1.0-real-provider-feature-flag-kill-switch-test-matrix.md). The v1.0 Batch 6 user-confirmed publish intent workflow ADR is available in [`docs/decisions/0051-v1.0-user-confirmed-publish-intent-workflow.md`](docs/decisions/0051-v1.0-user-confirmed-publish-intent-workflow.md), the contract is available in [`docs/contracts/v1.0-user-confirmed-publish-intent-contract.md`](docs/contracts/v1.0-user-confirmed-publish-intent-contract.md), and the test matrix is available in [`docs/testing/v1.0-user-confirmed-publish-intent-test-matrix.md`](docs/testing/v1.0-user-confirmed-publish-intent-test-matrix.md). The v1.0 Batch 7 guarded real publish adapter ADR is available in [`docs/decisions/0052-v1.0-real-publish-adapter-guarded-implementation.md`](docs/decisions/0052-v1.0-real-publish-adapter-guarded-implementation.md), the contract is available in [`docs/contracts/v1.0-real-publish-adapter-guarded-contract.md`](docs/contracts/v1.0-real-publish-adapter-guarded-contract.md), and the test matrix is available in [`docs/testing/v1.0-real-publish-adapter-guarded-test-matrix.md`](docs/testing/v1.0-real-publish-adapter-guarded-test-matrix.md).

v0.9.0 still has no real Douyin integration, no OAuth implementation, no OAuth callback route, no OAuth state storage, no token exchange, no real provider authorization URL generation, no token / secret / API key / credential / authorization code / OAuth state storage, no real metrics fetching, no upload / publish / scheduling, and no external service calls. v0.9.0 is a POC / Sandbox Integration release, not a production-ready real Douyin integration and not a production deployment.

The current v1.0 work line is based on the v0.9.0 release commit `0f5263452b65077f2c70c82e506944dd46e60e96`. v1.0 has moved to Batch 7 guarded real publish adapter foundation after the Batch 6 user-confirmed publish intent workflow. Real provider runtime is still not enabled, and real OAuth, real token exchange, real token storage, real credential storage, real external Douyin calls, real upload, real publish, scheduled publish, and metrics read implementation have not started. The repository still has no real Douyin integration, no OAuth implementation, no token storage, no real metrics fetching, no real upload / publish / scheduling, and no business external service calls.

v1.0 Batch 7 adds a guarded real publish adapter foundation, metadata-only publish attempt schema, local-only guarded attempt API, frontend guarded attempt UI, and tests. It proves that a future real publish adapter must require a confirmed publish intent, Batch 5 controls, review / media / metadata / credential reference preflight, duplicate attempt prevention, and sandbox fallback rejection before any later real provider execution. Batch 7 does not enable the real provider, create OAuth URLs, add OAuth start routes, add OAuth callback routes, perform real token exchange, store real tokens / secrets / credentials / authorization codes / raw OAuth state / OAuth state values, add frontend OAuth UI, call Douyin APIs or business external services, upload, real publish, schedule publishing, fetch real metrics, or persist provider / upload / publish response payloads. v1.0 is not a production commercial release, not v1.5 Minimum Production Release, and not v2.0 Multi-Tenant SaaS Commercial Release.

## Roadmap To Commercial Release

The current released version is `v0.9.0 - Douyin Provider POC / Sandbox Integration`. v1.0 has entered Batch 7 guarded real publish adapter foundation work for the Douyin Integration User Test Release, but the real provider is not enabled and real OAuth runtime, real token exchange, real credential storage, real external Douyin calls, real upload, real publishing, scheduled publishing, and real metrics read have not started. The roadmap moves from v1.0 small-scope user testing to a v1.5 target Minimum Production Release for controlled direct-customer commercial use, and finally to a v2.0 target Multi-Tenant SaaS Commercial Release for customer-of-customer SaaS commercialization:

- v0.8.0 Provider & Credential Security Foundation (released): Batch 1-16 completed Provider, credential, OAuth, secret, token lifecycle, security audit, source separation, Provider Registry, Connection State, Credential Reference, Security Audit, OAuth Boundary, Token Lifecycle Boundary, Integration Readiness Summary, matching frontend read-only UI panels, the RC checklist, and closure audit. This release provides only metadata-only / read-only security foundations: no real Douyin integration, no OAuth implementation, no OAuth callback route, no OAuth state storage, no token exchange, no real provider authorization URL generation, no token / secret / API key / credential / authorization code / OAuth state storage, no real metrics fetching, no upload / publish / scheduling, no external service calls, and no production-ready real Douyin integration claim.
- v0.9 Douyin Provider POC / Sandbox Integration (released as v0.9.0): Batch 0-9 completed POC planning, adapter skeleton, sandbox-only deterministic operations, provider registry / factory routing, sandbox metrics / mock workflow, roadmap alignment, sandbox-only backend API contract, frontend sandbox POC panel, RC readiness package, and release preparation package. v0.9.0 is not commercial, not production, not real provider integration, not real OAuth, not real OAuth URL generation, not real metrics read, and not real publish readiness; it has no real Douyin API calls, no OAuth implementation, no OAuth callback route, no token exchange, no token storage, no real metrics fetching, no upload / publish / scheduling, and no external service calls.
- v1.0 Douyin Integration User Test Release: currently in Batch 7 guarded real publish adapter foundation work, adding metadata-only publish attempts, confirmed publish intent dependency, preflight validation, duplicate attempt prevention, real provider disabled handling, kill switch / platform precondition blocking, and sandbox fallback forbidden foundations after the Batch 6 publish intent workflow. The target remains validating whether real Douyin authorization, publishing, status tracking, and minimum metrics read are feasible; this batch does not enable the real provider or implement real OAuth runtime, real token exchange, real token storage, real credential storage, real external Douyin calls, real upload, real publishing, scheduled publishing, or real metrics read. v1.0 is not a production commercial release and does not provide SLA, broad commercial use, or multi-tenant SaaS.
- v1.1-v1.4: future Real Integration Hardening, Publishing Workflow Beta, Metrics & Feedback Beta, and Production Release Candidate stages.
- v1.5 Minimum Production Release: a future target for controlled direct-customer commercial use after readiness criteria are satisfied. It can support managed, single-tenant, controlled deployment, or pilot commercial contracts, but it is not multi-tenant SaaS, does not default to serving customers' customers, and does not provide white-label, reseller, marketplace, unlimited-scale, or SLA commitments unless future documentation and contracts establish them.
- v1.6-v1.9: future SaaS Tenant Foundation, SaaS Access Control / Billing / Admin Foundation, SaaS Reliability / Compliance / Operations, and Multi-Tenant SaaS Release Candidate stages.
- v2.0 Multi-Tenant SaaS Commercial Release: a future target for customer-of-customer SaaS commercialization, requiring multi-tenancy, organizations, customers, customers' customers, permissions, audit, billing, SLA, admin operations, compliance, and production support.

Real Douyin integration still depends on platform availability, app review, OAuth, API permissions, and explicit user authorization. This roadmap describes future targets, not current capabilities. The current app does not connect to real Douyin, implement OAuth, store tokens, fetch real metrics, publish real content, auto-publish, batch-publish, schedule publishing, provide a production platform dashboard, provide v1.5 controlled direct-customer commercial readiness, or provide v2.0 multi-tenant SaaS commercial readiness.

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
.\scripts\validate-v0.9-poc.ps1
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
- On the project detail page, explicitly confirm creation of a metadata-only `PublishIntent` from an approved `Review Draft` in the same project after local media preflight, view publish intent lists/statuses, and cancel local active intents; intent creation does not upload, publish, or call Douyin.
- The legacy pending `PublishIntent` compatibility path can still be confirmed into one local `not_started` `PublicationRecord` placeholder; this does not execute real platform actions.
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
