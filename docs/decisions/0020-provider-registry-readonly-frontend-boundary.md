# ADR 0020: Provider Registry Read-only Frontend Boundary

## Status

Accepted

## Context

v0.7.0 has completed the fake/local metrics review summary workflow. That workflow remains local fake/manual only and does not connect to real Douyin, implement OAuth, store tokens, or fetch real platform metrics.

v0.8 Batch 1 defined Provider, Credential, OAuth, Secret, token lifecycle, audit, connection status, and fake/sandbox/real source separation boundaries in ADR 0018.

v0.8 Batch 2 implemented the backend-only Provider Registry & Capability Metadata foundation in ADR 0019. It added read-only provider metadata for `fake_local`, `douyin_sandbox`, and `douyin_real` without adding OAuth, credential storage, token storage, real provider adapters, or external service calls.

This batch adds a frontend read-only UI on top of the Batch 2 read-only API. The real Douyin POC must wait until registry, capability, and source-separation boundaries are stable across backend metadata and frontend display.

## Decision

The frontend may read `GET /api/providers`.

The frontend may display only non-sensitive provider metadata.

The frontend must explicitly display `source_type`, `implementation_status`, `connection_status`, capability metadata, and boundary notes.

The frontend must distinguish `fake_local`, `douyin_sandbox`, and `douyin_real`.

`fake_local` may be displayed as a local fake/demo/test workflow.

`douyin_sandbox` and `douyin_real` may only be displayed as placeholder / not available. They must not be displayed as available real integrations.

Unimplemented capabilities must be displayed as unavailable, disabled, or not implemented. Future plans may be shown only through `implementation_status` and `boundary_notes`, not through capability flags or actions that imply availability.

The frontend must not add connect, authorize, callback, refresh, revoke, disconnect, upload, publish, or schedule UI.

The frontend must not receive, store, cache, or display access tokens, refresh tokens, API keys, secrets, credentials, authorization codes, OAuth client secrets, raw provider responses, or credential material.

## Consequences

Users and reviewers can see provider, source, capability, and connection boundaries in the UI without interpreting placeholder metadata as real platform availability.

Future v0.9 Douyin Provider POC / Sandbox Integration can reuse this UI boundary, but it must first update registry and capability metadata to reflect any newly implemented behavior.

This UI does not mean OAuth, Credential storage, real Douyin integration, real metrics fetching, uploading, publishing, scheduling, or production-grade platform security is available.

## Non-Goals

- Do not connect to the real Douyin API.
- Do not implement OAuth.
- Do not add an OAuth callback route.
- Do not add a connect or authorize button.
- Do not store access tokens.
- Do not store refresh tokens.
- Do not store API keys.
- Do not store secrets.
- Do not store credentials.
- Do not add a Credential model or database table.
- Do not add backend API.
- Do not fetch real metrics.
- Do not upload real videos.
- Do not publish real content.
- Do not schedule publishing.
- Do not auto-publish.
- Do not synchronize metrics on a schedule.
- Do not call external services.
- Do not add Docker.
- Do not add GitHub Actions.
- Do not modify the v0.7.0 release scope.

## Frontend Boundary

The frontend may render a Provider Registry panel or equivalent read-only surface. The UI must make clear that the registry is read-only metadata and does not represent an account connection, OAuth flow, credential manager, provider adapter, or real platform integration.

The frontend must not add write calls, route actions, local storage, session storage, form fields, or buttons that change provider connection state, authorization state, credential state, publish state, upload state, or real platform data state.

Error messages must be safe for users and debugging. They may say that provider registry metadata failed to load, but they must not echo user input, provider raw responses, tokens, secrets, credentials, authorization codes, API keys, or OAuth client secrets.

## Capability Display Boundary

Capability metadata must be displayed as the current registry state, not as marketing copy or future promises.

For `fake_local`, metrics-read and publish-prepare capabilities may be shown only as local fake capabilities, not as real platform capabilities.

For `douyin_sandbox`, `supports_sandbox=true` may be shown only as a sandbox placeholder boundary. It must not imply a real sandbox API call is implemented.

For `douyin_sandbox` and `douyin_real`, OAuth, metrics read, publish prepare, real publish, token refresh, disconnect, and revoke must remain displayed as unavailable until backend metadata and implementation boundaries change in a later batch.

## Source Separation

`fake_local` must be labeled as local fake/demo/test data and not real Douyin data.

`douyin_sandbox` must be labeled as placeholder metadata and must not be treated as `douyin_real`.

`douyin_real` must be labeled as a future real provider placeholder and not real Douyin integration.

All UI text must avoid implying that fake, sandbox, or placeholder data is real platform performance, a real account connection, real OAuth, real metrics fetching, real uploading, real publishing, or scheduling.

## Security Requirements

- Frontend responses must be treated as non-sensitive metadata only.
- The UI must not display token values, refresh token values, API key values, secret values, credential material, authorization code values, OAuth client secret values, private keys, raw platform responses, or real platform returned data.
- The UI must not store provider metadata in a way that can become credential storage.
- Tests may include forbidden field names or boundary text only as negative assertions or documentation of non-implemented behavior.
- Test fixtures must not include real credentials, real OAuth callback data, real platform responses, SQLite databases, uploads, generated media, `dist/`, `node_modules/`, `.venv/`, or runtime files.

## Testing Requirements

Frontend tests must cover loading, success, error, and empty states for the Provider Registry UI.

Frontend tests must verify that `fake_local`, `douyin_sandbox`, and `douyin_real` are visibly distinguishable.

Frontend tests must verify capability metadata display, including local fake capabilities for `fake_local` and unavailable / not implemented capabilities for placeholder providers.

Frontend tests must verify that the UI does not render connect, authorize, callback, refresh, revoke, disconnect, upload, publish, schedule, sync, or real metrics fetch actions.

Existing project list and project detail workflows must continue to pass without changing the v0.7 fake/local metrics review summary workflow semantics.
