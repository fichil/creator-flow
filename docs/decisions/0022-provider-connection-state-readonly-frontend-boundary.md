# ADR 0022: Provider Connection State Read-only Frontend Boundary

## Status

Accepted

## Context

v0.7.0 has completed the fake/local metrics review summary workflow. That workflow remains local fake/manual only and does not connect to real Douyin, implement OAuth, store tokens, fetch real metrics, upload, publish, schedule publishing, or call external services.

v0.8 Batch 1 defined Provider, Credential, OAuth, Secret, token lifecycle, audit, connection status, and fake/sandbox/real source separation boundaries in ADR 0018.

v0.8 Batch 2 implemented the backend-only Provider Registry & Capability Metadata foundation in ADR 0019.

v0.8 Batch 3 implemented the frontend read-only Provider Registry UI boundary in ADR 0020.

v0.8 Batch 4 implemented the backend-only Provider Connection State & Sensitive Storage Status foundation in ADR 0021.

This batch adds a frontend read-only Provider Connection State UI on top of the Batch 4 read-only API. The real Douyin POC must wait until registry, capability, connection state, authorization status, sensitive storage status, and source-separation boundaries are stable across backend metadata and frontend display.

## Decision

The frontend may read `GET /api/provider-connections`.

The frontend may display only non-sensitive provider connection state metadata.

The frontend must explicitly display `source_type`, `implementation_status`, `connection_status`, `authorization_status`, `sensitive_storage_status`, `safe_status_message`, and boundary notes.

The frontend must distinguish `fake_local`, `douyin_sandbox`, and `douyin_real`.

`fake_local` may be displayed as a local fake/demo/test workflow with `connection_status=not_required`, `authorization_status=not_required`, and `sensitive_storage_status=none`.

`douyin_sandbox` and `douyin_real` may only be displayed as placeholder / not_connected / not_implemented. They must not be displayed as available real integrations.

`can_connect`, `can_refresh`, `can_revoke`, and `can_disconnect` must be shown as non-executable in this batch.

The frontend must not add connect, authorize, callback, refresh, revoke, disconnect, upload, publish, or schedule UI.

The frontend must not receive, store, cache, or display tokens, secrets, API keys, credential material, authorization codes, OAuth client secrets, raw provider responses, or sensitive storage values.

## Consequences

Users and reviewers can see provider connection state and sensitive storage status boundaries in the UI without interpreting placeholder metadata as real platform availability.

Future v0.9 Douyin Provider POC / Sandbox Integration can reuse this UI boundary, but it must first update registry, connection state, and capability metadata and pass a later ADR and tests.

This UI does not mean OAuth, Credential storage, real Douyin integration, real metrics fetching, uploading, publishing, scheduling, or production-grade platform security is available.

## Non-Goals

- Do not connect to the real Douyin API.
- Do not implement OAuth.
- Do not add an OAuth callback route.
- Do not add a connect or authorize button.
- Do not add refresh, revoke, or disconnect buttons.
- Do not store access tokens.
- Do not store refresh tokens.
- Do not store API keys.
- Do not store secrets.
- Do not store credential material.
- Do not store authorization codes.
- Do not store OAuth client secrets.
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

The frontend may render a Provider Connection State panel or equivalent read-only surface. The UI must make clear that the panel is read-only metadata and does not represent an account connection, OAuth flow, credential manager, provider adapter, platform account settings page, or real platform integration.

The frontend must not add write calls, route actions, local storage, session storage, form fields, or buttons that change provider connection state, authorization state, credential state, publish state, upload state, or real platform data state.

Error messages must be safe for users and debugging. They may say that provider connection state metadata failed to load, but they must not echo user input, provider raw responses, tokens, secrets, credentials, authorization codes, API keys, or OAuth client secrets.

## Connection State Display Boundary

Connection state metadata must be displayed as the current backend metadata state, not as marketing copy or future promises.

For `fake_local`, `not_required` means the local fake/demo/test workflow does not require authorization. It must not imply a real account is connected.

For `douyin_sandbox` and `douyin_real`, `not_connected`, `not_implemented`, and `not available` must be displayed as unavailable placeholder states. They must not be converted into ready, live, enabled, connected, authorized, or configured language.

`can_connect=false`, `can_refresh=false`, `can_revoke=false`, and `can_disconnect=false` must not render operation buttons or clickable actions.

## Sensitive Storage Status Display Boundary

`sensitive_storage_status` may be displayed only as status metadata.

The UI must not display token values, refresh token values, API key values, secret values, credential material, encrypted credential material, authorization code values, OAuth client secret values, private keys, raw platform responses, or real platform returned data.

The UI must not store provider connection state metadata in a way that can become credential storage.

## Source Separation

`fake_local` must be labeled as local fake/demo/test data, not real Douyin data, no OAuth required, no tokens stored, and no external service call.

`douyin_sandbox` must be labeled as placeholder metadata, OAuth not implemented, tokens not stored, no real Douyin API call, and not `douyin_real`.

`douyin_real` must be labeled as a future real provider placeholder, not real Douyin integration, no OAuth implementation, no token storage, no real metrics fetching, and no upload / publish / scheduling.

All UI text must avoid implying that fake, sandbox, or placeholder data is real platform performance, a real account connection, real OAuth, real metrics fetching, real uploading, real publishing, or scheduling.

## Security Requirements

- Frontend responses must be treated as non-sensitive metadata only.
- Frontend API types must not add fields capable of carrying sensitive values, such as `access_token`, `refresh_token`, `token_value`, `api_key`, `client_secret`, `authorization_code`, `credential_material`, `encrypted_credential`, `raw_response`, `private_key`, `oauth_code`, or `password`.
- The UI must not display token values, refresh token values, API key values, secret values, credential material, authorization code values, OAuth client secret values, private keys, raw provider responses, or real platform returned data.
- The UI must not render environment variable values.
- Tests may include forbidden field names or boundary text only as negative assertions or documentation of non-implemented behavior.
- Test fixtures must not include real credentials, real OAuth callback data, real platform responses, SQLite databases, uploads, generated media, `dist/`, `node_modules`, `.venv`, or runtime files.

## Testing Requirements

Frontend tests must cover loading, success, error, and empty states for the Provider Connection State UI.

Frontend tests must verify that `fake_local`, `douyin_sandbox`, and `douyin_real` are visibly distinguishable.

Frontend tests must verify display of `connection_status`, `authorization_status`, `sensitive_storage_status`, `safe_status_message`, and boundary notes.

Frontend tests must verify that `can_connect`, `can_refresh`, `can_revoke`, and `can_disconnect` do not render connect, authorize, refresh, revoke, disconnect, upload, publish, schedule, sync, or real metrics fetch actions.

Project list tests must verify that the Provider Registry panel, Provider Connection State panel, new project action, archived-project checkbox, and existing project list or empty-state behavior still work together.

Existing project detail workflows must continue to pass without changing the v0.7 fake/local metrics review summary workflow semantics.
