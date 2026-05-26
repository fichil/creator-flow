# AGENTS.md

This repository is currently in the documentation foundation stage.

## Working Rules

- Do not implement application source code until the project moves beyond the documentation foundation stage.
- Before designing or building product features, read `docs/product-spec.md`, `docs/architecture.md`, and `docs/roadmap.md`.
- Keep changes reviewable, testable, and suitable for a focused Git commit.
- Do not commit secrets, API keys, tokens, credentials, local database files, generated media, user uploads, or private user content.
- Do not add dependency managers, virtual environments, Docker files, FastAPI code, React code, Node.js code, or generated assets unless the roadmap explicitly calls for that phase.
- Preserve the human-in-the-loop publishing principle: no automated publishing to Douyin or any other platform without explicit user review and confirmation.
- All external AI, media, trend, rendering, and publishing capabilities should be designed behind provider interfaces rather than binding the project to a single vendor.
