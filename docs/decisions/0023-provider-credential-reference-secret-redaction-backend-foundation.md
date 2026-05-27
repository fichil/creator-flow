# ADR 0023: Provider Credential Reference and Secret Redaction Backend Foundation

## Status

Accepted

## Context

v0.7.0 has completed the fake/local metrics review summary workflow. That workflow remains local fake/manual only and does not connect to real Douyin, implement OAuth, store tokens, fetch real metrics, upload, publish, schedule publishing, or call external services.

v0.8 Batch 1 defined Provider, Credential, OAuth, Secret, token lifecycle, audit, connection status, and fake/sandbox/real source separation boundaries in ADR 0018.

v0.8 Batch 2 implemented the backend-only Provider Registry & Capability Metadata foundation in ADR 0019.

v0.8 Batch 3 implemented the frontend read-only Provider Registry UI boundary in ADR 0020.

v0.8 Batch 4 implemented the backend-only Provider Connection State & Sensitive Storage Status foundation in ADR 0021.

v0.8 Batch 5 implemented the frontend read-only Provider Connection State UI boundary in ADR 0022.

This batch adds backend-only credential reference metadata and a secret redaction foundation on top of Provider Registry and Provider Connection State. The real Douyin POC must wait until registry, capability, connection state, authorization status, sensitive storage status, credential reference, secret redaction, and source-separation boundaries are stable.

## Decision

The backend will add a metadata-only `provider_credential_references` table.

The backend will add a read-only provider credential reference metadata API.

The backend will add a secret redaction helper.

Credential reference metadata must bind to known providers from Provider Registry.

Default credential reference metadata must cover `fake_local`, `douyin_sandbox`, and `douyin_real`.

`fake_local` is a local fake/demo/test workflow. It does not require credentials, tokens, secrets, OAuth, or real platform authorization.

`douyin_sandbox` and `douyin_real` may only be placeholder / not_implemented metadata in this batch. They must not be displayed or returned as available real integrations.

`storage_status` may describe only storage readiness. It must not store tokens, secrets, API keys, credential material, authorization codes, OAuth client secrets, private keys, raw provider responses, or real platform returned data.

The redaction helper must redact sensitive keys and obvious sensitive text patterns.

API consumers may see only non-sensitive metadata, `reference_status`, `storage_status`, `redaction_policy_status`, `safe_status_message`, and boundary notes.

This batch must not add write APIs.

This batch must not read real keys from environment variables.

This batch must not call external services.

This batch must not implement OAuth.

## Consequences

Future UI work can use read-only credential reference metadata to show clearer credential readiness boundaries without creating a credential manager.

Future OAuth state/callback POC work can reuse the redaction helper, but it must pass a later ADR and tests.

Future real Credential storage must design encrypted or reference-based storage separately. The `provider_credential_references` metadata table must not become a credential store.

This batch adds a metadata-only database table, a read-only API, and a redaction helper, but it does not mean OAuth, Credential storage, real Douyin integration, real metrics fetching, uploading, publishing, scheduling, or production-grade platform security is available.

## Non-Goals

- Do not connect to the real Douyin API.
- Do not implement OAuth.
- Do not add an OAuth callback route.
- Do not add connect, authorize, refresh, revoke, or disconnect write APIs.
- Do not store access tokens.
- Do not store refresh tokens.
- Do not store token values.
- Do not store API keys.
- Do not store secrets.
- Do not store client secrets.
- Do not store authorization codes.
- Do not store OAuth client secrets.
- Do not store credential material.
- Do not store encrypted credentials.
- Do not store private keys.
- Do not add real Credential storage.
- Do not add a real Provider adapter.
- Do not fetch real metrics.
- Do not upload real videos.
- Do not publish real content.
- Do not schedule publishing.
- Do not auto-publish.
- Do not synchronize metrics on a schedule.
- Do not call external services.
- Do not add frontend UI.
- Do not add Docker.
- Do not add GitHub Actions.
- Do not modify the v0.7.0 release scope.

## Provider Credential Reference Boundary

Provider Credential Reference is a backend-only metadata layer. It depends on Provider Registry as the provider source of truth.

Credential reference metadata may be returned only for providers known to the registry. Unknown `provider_id` rows in the database must be ignored and must not become real providers through metadata alone.

The metadata layer may return `reference_kind`, `reference_status`, `storage_status`, `redaction_policy_status`, `safe_display_name`, `safe_status_message`, and boundary notes.

The metadata layer must not read environment variables, local credential files, token files, secret files, platform raw responses, or external provider services.

The metadata layer is not Credential storage, encrypted token storage, OAuth storage, a provider adapter, or a platform account connection.

## Secret Redaction Boundary

The redaction helper must support sensitive key detection for token, API key, secret, authorization code, credential material, encrypted credential, private key, OAuth code, password, bearer, cookie, and session style names.

The redaction helper must recursively redact sensitive values in dict, list, and tuple payloads by replacing values with `[REDACTED]`.

The redaction helper must redact obvious text patterns such as `access_token=...`, `refresh_token=...`, `api_key=...`, `client_secret=...`, `authorization_code=...`, and `Bearer ...`.

The redaction helper may be used by later OAuth or provider work, but this batch does not add global logging middleware, OAuth flows, exception handlers, or real credential storage.

The redaction helper is not a secret manager, KMS, encrypted storage layer, or credential vault.

## Source Separation

`fake_local` must remain local fake/demo/test data only. It must say no OAuth required, no token stored, no secret stored, no credential material stored, and no external service call.

`douyin_sandbox` must remain placeholder metadata only. It must say OAuth is not implemented, tokens are not stored, secrets are not stored, credential material is not stored, no real Douyin API call, and it cannot be treated as `douyin_real`.

`douyin_real` must remain a future real provider placeholder only. It must say not real Douyin integration, no OAuth implementation, no access token or refresh token storage, no API key storage, no secret storage, no credential material storage, no real metrics fetching, and no upload / publish / scheduling.

Source separation must not be overridden by database rows. Registry source type, provider name, availability, and real-provider flags remain authoritative.

## API Boundary

The backend may expose `GET /api/provider-credential-references`.

The backend may expose `GET /api/provider-credential-references/{provider_id}`.

The API must return a stable order: `fake_local`, `douyin_sandbox`, `douyin_real`.

Unknown providers must return a safe 404 message that does not echo user input or sensitive-looking terms.

The API must not add POST, PUT, PATCH, DELETE, connect, authorize, callback, refresh, revoke, disconnect, credential write, or token read routes.

The API response must not include fields capable of carrying sensitive values, such as `access_token`, `refresh_token`, `token_value`, `api_key`, `secret_value`, `client_secret`, `authorization_code`, `credential_material`, `encrypted_credential`, `raw_response`, `private_key`, `oauth_code`, `password`, `bearer_token`, or `session_cookie`.

## Security Requirements

- The metadata table must not include columns capable of carrying sensitive values.
- API responses must not expose tokens, secrets, API keys, authorization codes, OAuth client secrets, credential material, encrypted credentials, private keys, raw provider responses, or environment variable values.
- Redaction tests may use fake values only.
- Boundary notes may mention tokens, secrets, OAuth, API keys, and credentials only to state that they are not stored or implemented.
- Tests may include forbidden field names only as negative assertions.
- Git must not include real credentials, real OAuth callback data, real platform responses, SQLite databases, uploads, generated media, `dist/`, `node_modules`, `.venv`, or runtime files.

## Testing Requirements

Backend tests must cover list and read APIs for `fake_local`, `douyin_sandbox`, and `douyin_real`.

Backend tests must verify stable ordering and source separation.

Backend tests must verify that unknown provider rows are ignored and known provider rows can merge only non-sensitive reference metadata without changing registry boundaries.

Backend tests must verify that write methods do not succeed.

Backend tests must verify that API responses and table columns do not contain sensitive field names.

Backend tests must verify that API responses do not leak environment variable values.

Redaction tests must cover sensitive key detection, safe key pass-through, nested mapping redaction, sensitive text pattern redaction, safe error messages, and the absence of environment-variable reads or external service calls.

Existing Provider Registry, Provider Connection State, fake metrics provider, fake publishing workflow, and fake review summary workflow tests must continue to pass.
