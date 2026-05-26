# ADR 0002: Human-in-the-Loop Publishing

## Status

Accepted

## Context

Publishing short videos can expose private information, incorrect claims, copyrighted material, or content that does not match the user's intent. AI-generated scripts, captions, metadata, and platform-specific suggestions require human judgment before publication.

Silent automatic publishing would create avoidable safety, privacy, and reputation risks, especially for an open-source project that may be adapted to many provider and platform combinations.

## Decision

The MVP must not silently or automatically publish to Douyin or any other platform.

Any publish, schedule, upload-for-publication, or equivalent platform action must pass through an explicit human review and confirmation step.

## Consequences

- The workflow must include visible review states before publishing.
- Publishing providers must support preparation separately from confirmed publish execution.
- The product can still automate drafts, metadata preparation, checks, rendering, and packaging.
- Users retain final control over platform-facing actions.
