# ADR 0003: Technology Stack

## Status

Accepted

## Context

creator-flow needs a practical stack for a local-first MVP that can later grow into a more durable open-source application. The project needs web UI ergonomics, clear backend APIs, simple local persistence, reliable video composition, repeatable deployment, and CI.

## Decision

The planned MVP stack is:

- Backend: Python + FastAPI.
- Frontend: React + Vite + Tailwind.
- MVP database: SQLite.
- Future database option: PostgreSQL.
- Video rendering: FFmpeg.
- Deployment: Docker Compose.
- CI/CD: GitHub Actions.

## Rationale

- FastAPI is a strong fit for typed Python APIs and local service development.
- React + Vite + Tailwind supports fast UI iteration and a broad contributor base.
- SQLite keeps the MVP easy to run locally without requiring external infrastructure.
- PostgreSQL gives a clear future path for more durable or collaborative deployments.
- FFmpeg is mature and well suited to deterministic video rendering from images, audio, subtitles, and timing data.
- Docker Compose is enough for reproducible local and small deployment environments.
- GitHub Actions fits an open-source GitHub workflow.

## Consequences

- The first implementation should stay lightweight and local-friendly.
- Provider interfaces should be designed before integrating external services.
- The documentation foundation must not create the application skeleton yet.
- Future contributors have clear direction without the repository prematurely committing generated project files.
