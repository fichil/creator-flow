# Roadmap

## v0.1 Documentation Foundation

Goal: establish the product, architecture, roadmap, licensing, and decision records.

Scope:

- README, license, ignore rules, and agent rules.
- Product specification.
- Architecture outline.
- Roadmap.
- Initial ADRs.

Acceptance criteria:

- The repository can be reviewed publicly without exposing secrets, private paths, generated media, or user data.
- The project clearly states that no runnable application exists yet.
- MVP principles and non-goals are documented.

Not doing:

- No backend, frontend, Docker, CI, provider, database, or rendering implementation.
- No dependency installation.
- No generated media.

## v0.2 Local MVP Skeleton

Goal: introduce the minimal local application structure after the documentation foundation is accepted.

Scope:

- FastAPI project skeleton.
- React + Vite + Tailwind project skeleton.
- Local SQLite metadata design.
- Basic project and material import screens.
- Development setup documentation.

Acceptance criteria:

- The app can start locally.
- A user can create a content project and register imported materials.
- No external AI or publishing provider is required for basic navigation.

Not doing:

- No automatic publishing.
- No production deployment.
- No pure AI text-to-video default path.

## v0.3 Script and Storyboard Workflow

Goal: support the core creative planning loop.

Scope:

- Provider interface definitions.
- LLM-backed topic, script, and storyboard generation through configurable providers.
- Manual editing and review states.
- Basic asset plan generation.

Acceptance criteria:

- A user can move from imported materials to topic selection, script draft, and storyboard.
- Provider interfaces keep vendor-specific details out of core domain code.
- User review remains required before later rendering or publishing steps.

Not doing:

- No silent ingestion from private accounts.
- No direct platform publishing.
- No default expensive text-to-video provider.

## v0.4 FFmpeg Rendering MVP

Goal: produce review-ready 9:16 MP4 outputs from approved plans.

Scope:

- TTS provider integration.
- Subtitle generation and editing.
- FFmpeg-based composition of images or screenshots, audio, subtitles, and timing metadata.
- Render job tracking and review state.

Acceptance criteria:

- A user can render a 9:16 MP4 from approved script, visual assets, TTS audio, and subtitles.
- Render outputs are stored outside Git-tracked paths.
- Rendering failures are visible and debuggable.

Not doing:

- No automatic upload or publication.
- No production-scale render farm.
- No mandatory pure AI video provider.

## v1.0 Human-Reviewed Publishing

Goal: prepare and publish reviewed videos through platform provider integrations with explicit user confirmation.

Scope:

- Douyin publishing preparation provider.
- Platform metadata checks.
- Human review and confirmation gate.
- Audit trail for publish intent and publish result.
- Documentation for adding future platform providers.

Acceptance criteria:

- A user can review the final video and metadata before any publish action.
- Publishing requires explicit confirmation.
- Douyin is supported as the first platform, and the provider model supports future platforms.

Not doing:

- No silent background publishing.
- No credential commits.
- No platform lock-in.
