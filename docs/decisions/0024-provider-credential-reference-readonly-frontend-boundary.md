# ADR 0024: Provider Credential Reference Read-only Frontend Boundary

## Status

Accepted

## Context

v0.7.0 has completed the fake/local metrics review summary workflow. That workflow remains local fake/manual only and does not connect to real Douyin, implement OAuth, store tokens, fetch real metrics, upload, publish, schedule publishing, or call external services.

v0.8 Batch 1 defined Provider, Credential, OAuth, Secret, token lifecycle, audit, connection status, and fake/sandbox/real source separation boundaries in ADR 0018.

v0.8 Batch 2 implemented the backend-only Provider Registry & Capability Metadata foundation in ADR 0019.

v0.8 Batch 3 implemented the frontend read-only Provider Registry UI boundary in ADR 0020.

v0.8 Batch 4 implemented the backend-only Provider Connection State & Sensitive Storage Status foundation in ADR 0021.

v0.8 Batch 5 implemented the frontend read-only Provider Connection State UI boundary in ADR 0022.

v0.8 Batch 6 implemented the backend-only Provider Credential Reference & Secret Redaction foundation in ADR 0023.

This batch adds a frontend read-only Provider Credential Reference UI on top of the Batch 6 read-only API. The real Douyin POC must wait until registry, capability, connection state, authorization status, sensitive storage status, credential reference, secret redaction, and source-separation boundaries are stable across backend metadata and frontend display.

## Decision

The frontend may read `GET /api/provider-credential-references`.

The frontend may display only non-sensitive provider credential reference metadata.

The frontend must explicitly display `source_type`, `implementation_status`, `reference_kind`, `reference_status`, `storage_status`, `redaction_policy_status`, `safe_display_name`, `safe_status_message`, and boundary notes.

The frontend must distinguish `fake_local`, `douyin_sandbox`, and `douyin_real`.

`fake_local` may be displayed as a local fake/demo/test workflow with `reference_kind=none_required`, `reference_status=not_required`, and `storage_status=none`.

`douyin_sandbox` and `douyin_real` may only be displayed as placeholder / not_implemented metadata. They must not be displayed as available real integrations.

The frontend must not add connect, authorize, callback, refresh, revoke, disconnect, upload, publish, or schedule UI.

The frontend must not add secret input, token viewer, credential viewer, or credential management UI.

The frontend must not receive, store, cache, or display tokens, secrets, API keys, authorization codes, OAuth client secrets, credential material, private keys, raw provider responses, or sensitive storage values.

`redaction_policy_status` may be displayed only as redaction metadata. It must not be presented as production-grade KMS, a secret manager, or encrypted token storage.

## Consequences

Users and reviewers can see provider credential reference, storage readiness, and redaction policy boundaries in the UI without interpreting placeholder metadata as real platform availability.

Future v0.9 Douyin Provider POC / Sandbox Integration can reuse this UI boundary, but it must first update registry, connection state, credential reference, and capability metadata and pass a later ADR and tests.

This UI does not mean OAuth, Credential storage, encrypted token storage, real Douyin integration, real metrics fetching, uploading, publishing, scheduling, or production-grade platform security is available.

## Non-Goals

- Do not connect to the real Douyin API.
- Do not implement OAuth.
- Do not add an OAuth callback route.
- Do not add a connect or authorize button.
- Do not add refresh, revoke, or disconnect buttons.
- Do not add secret input.
- Do not add token viewer.
- Do not add credential management UI.
- Do not store access tokens.
- Do not store refresh tokens.
- Do not store API keys.
- Do not store secrets.
- Do not store authorization codes.
- Do not store OAuth client secrets.
- Do not store credential material.
- Do not store private keys.
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

The frontend may render a Provider Credential Reference panel or equivalent read-only surface. The UI must make clear that the panel is read-only metadata and does not represent an account connection, OAuth flow, credential manager, secret manager, provider adapter, platform account settings page, or real platform integration.

The frontend must not add write calls, route actions, local storage, session storage, form fields, or buttons that change provider connection state, authorization state, credential state, publish state, upload state, or real platform data state.

Error messages must be safe for users and debugging. They may say that provider credential reference metadata failed to load, but they must not echo user input, provider raw responses, tokens, secrets, credentials, authorization codes, API keys, OAuth client secrets, or private keys.

## Credential Reference Display Boundary

Credential reference metadata must be displayed as the current backend metadata state, not as marketing copy or future promises.

For `fake_local`, `none_required`, `not_required`, and `storage_status=none` mean the local fake/demo/test workflow does not require credentials, tokens, secrets, OAuth, or real platform authorization.

For `douyin_sandbox` and `douyin_real`, `not_implemented` and `not available` must be displayed as unavailable placeholder states. They must not be converted into ready, live, enabled, connected, authorized, configured, stored, or credential-configured language.

## Sensitive Value Display Boundary

The UI may display `safe_display_name`, `safe_status_message`, and boundary notes only as non-sensitive metadata.

The UI must not display token values, refresh token values, API key values, secret values, authorization code values, OAuth client secret values, credential material, encrypted credential material, private keys, raw platform responses, or real platform returned data.

The UI must not provide secret input, token input, API key input, credential input, password input, token viewer, secret viewer, credential viewer, or credential management UI.

## Redaction Policy Display Boundary

`redaction_policy_status` may be displayed only as a status metadata field.

`redaction_policy_status=active` means the backend metadata and tests have a redaction policy boundary. It does not mean production-grade KMS, secret manager, credential vault, encrypted token storage, or real Credential storage exists.

Future real provider planning may be shown only through `implementation_status`, `reference_status`, `storage_status`, `redaction_policy_status`, and `boundary_notes`, not through buttons, configured states, stored states, connected states, or credential management UI.

## Source Separation

`fake_local` must be labeled as local fake/demo/test data, not real Douyin data, no OAuth required, no token stored, no secret stored, no credential material stored, and no external service call.

`douyin_sandbox` must be labeled as placeholder metadata, OAuth not implemented, tokens not stored, secrets not stored, credential material not stored, no real Douyin API call, and not `douyin_real`.

`douyin_real` must be labeled as a future real provider placeholder, not real Douyin integration, no OAuth implementation, no access token or refresh token storage, no API key storage, no secret storage, no credential material storage, no real metrics fetching, and no upload / publish / scheduling.

All UI text must avoid implying that fake, sandbox, or placeholder data is real platform performance, a real account connection, real OAuth, real credential storage, real metrics fetching, real uploading, real publishing, or scheduling.

## Security Requirements

- Frontend responses must be treated as non-sensitive metadata only.
- Frontend API types must not add fields capable of carrying sensitive values, such as `access_token`, `refresh_token`, `token_value`, `api_key`, `client_secret`, `authorization_code`, `credential_material`, `encrypted_credential`, `raw_response`, `private_key`, `oauth_code`, `password`, `bearer_token`, or `session_cookie`.
- The UI must not display token values, refresh token values, API key values, secret values, credential material, authorization code values, OAuth client secret values, private keys, raw provider responses, or real platform returned data.
- The UI must not render environment variable values.
- Tests may include forbidden field names or boundary text only as negative assertions or documentation of non-implemented behavior.
- Test fixtures must not include real credentials, real OAuth callback data, real platform responses, SQLite databases, uploads, generated media, `dist/`, `node_modules`, `.venv`, or runtime files.

## Testing Requirements

Frontend tests must cover loading, success, error, and empty states for the Provider Credential Reference UI.

Frontend tests must verify that `fake_local`, `douyin_sandbox`, and `douyin_real` are visibly distinguishable.

Frontend tests must verify display of `reference_kind`, `reference_status`, `storage_status`, `redaction_policy_status`, `safe_display_name`, `safe_status_message`, and boundary notes.

Frontend tests must verify that the UI does not render connect, authorize, callback, refresh, revoke, disconnect, upload, publish, schedule, sync, real metrics fetch, save credential, add credential, edit credential, delete credential, view token, view secret, secret input, token input, API key input, credential input, or password input actions.

Project list tests must verify that the Provider Registry panel, Provider Connection State panel, Provider Credential Reference panel, new project action, archived-project checkbox, and existing project list or empty-state behavior still work together.

Existing project detail workflows must continue to pass without changing the v0.7 fake/local metrics review summary workflow semantics.
