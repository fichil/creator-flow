# Architecture

## Technology Stack

- Backend: Python + FastAPI.
- Frontend: React + Vite + Tailwind.
- MVP database: SQLite.
- Future database option: PostgreSQL.
- Video rendering: FFmpeg.
- Deployment: Docker Compose.
- CI/CD: GitHub Actions.
- License: Apache-2.0.

This document describes planned architecture only. No application code is implemented in the documentation foundation stage.

## Logical Modules

- Material Import: accepts user-selected text, summaries, screenshots, images, and links.
- Content Project: tracks imported materials, generated drafts, render state, review status, and publishing intent.
- Topic Studio: proposes topics and angles from imported materials and optional trend signals.
- Script Studio: drafts and edits short-video scripts.
- Storyboard Studio: maps script segments to visuals, captions, and asset requirements.
- Voice and Subtitle Pipeline: prepares TTS input and subtitles.
- Rendering Pipeline: produces 9:16 MP4 outputs with FFmpeg.
- Publishing Preparation: prepares platform metadata and performs pre-publish checks.
- Human Review Gate: requires explicit user confirmation before publishing.
- Provider Registry: connects external AI, media, rendering, trend, and publishing integrations through stable interfaces.

## Provider Interface Direction

Provider interfaces should isolate the core workflow from external services.

- `LLMProvider`: topic ideation, script generation, rewrite suggestions, metadata drafts, and structured extraction.
- `ImageProvider`: optional image generation, image editing, thumbnail assistance, or visual asset retrieval.
- `TTSProvider`: voiceover generation from approved script text.
- `VideoRenderer`: video composition and rendering, with FFmpeg as the MVP implementation.
- `PublisherProvider`: platform-specific publishing preparation and user-confirmed publish actions.
- `TrendSourceProvider`: optional trend signals for topic discovery and framing.

Provider implementations must not leak vendor-specific assumptions into the domain model.

## Core Domain Models

- UserMaterial: a user-imported text, image, screenshot, link, or summary.
- ContentProject: a unit of work that groups materials, drafts, review state, renders, and publishing preparation.
- TopicCandidate: a proposed topic, angle, audience, hook, and rationale.
- ScriptDraft: a short-video script with editable structure and status.
- Storyboard: ordered scenes with visual, narration, subtitle, and timing guidance.
- AssetPlan: required images, screenshots, generated assets, voiceover, captions, and metadata.
- RenderJob: a rendering request, status, logs, inputs, and output path.
- PublishIntent: platform target, metadata, checks, confirmation state, and publish result.
- ProviderConfig: configuration for a provider without storing secrets in Git.

## Content Project State Machine

Planned states:

- `draft`: project created, materials may still be added.
- `materials_ready`: enough imported material exists to generate ideas.
- `topic_selected`: the user has accepted or edited a topic.
- `script_ready`: a script draft has been generated and approved for storyboard planning.
- `storyboard_ready`: scenes and asset requirements are ready.
- `render_ready`: assets, subtitles, and voiceover inputs are ready for rendering.
- `rendering`: a render job is running.
- `review_ready`: the MP4 is ready for user review.
- `publish_prepared`: platform metadata and checks are prepared.
- `publish_confirmed`: the user explicitly confirmed publishing.
- `published`: the platform publish action completed.
- `archived`: the project is no longer active.

Publishing transitions must pass through `review_ready`, `publish_prepared`, and `publish_confirmed`.

## Data and File Storage Boundaries

- SQLite stores local MVP metadata, project state, and references to files.
- PostgreSQL may be supported later for more durable or collaborative deployments.
- User uploads, generated assets, local render outputs, voiceover files, subtitles, and local databases are runtime data and must not be committed.
- Secrets and provider credentials must be supplied through local configuration or environment variables, never committed files.
- Generated videos, audio, images, subtitles, and uploaded source material belong under ignored runtime directories such as `data/generated/` or `uploads/`.

## Security Principles

- Process only user-explicitly imported materials.
- Do not silently read private chats, local files, browser state, or platform accounts.
- Require explicit user confirmation before publishing.
- Keep credentials out of Git and out of generated documentation examples.
- Treat external providers as replaceable and untrusted boundaries.
- Log enough for debugging without storing private content unnecessarily.

## Not Implemented Yet

- FastAPI service code.
- React frontend code.
- Database migrations.
- Docker Compose deployment.
- GitHub Actions workflows.
- Provider implementations.
- FFmpeg command orchestration.
- Douyin publishing integration.
- Pure AI text-to-video generation.
