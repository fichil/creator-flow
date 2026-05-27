# ADR 0021: Provider Connection State and Sensitive Storage Status Backend Foundation

## Status

Accepted

## Context

v0.7.0 has completed the fake/local metrics review summary workflow. That workflow remains local fake/manual only and does not connect to real Douyin, implement OAuth, store tokens, fetch real metrics, upload, publish, schedule publishing, or call external services.

v0.8 Batch 1 defined Provider, Credential, OAuth, Secret, token lifecycle, audit, connection status, and fake/sandbox/real source separation boundaries in ADR 0018.

v0.8 Batch 2 implemented the backend-only Provider Registry & Capability Metadata foundation in ADR 0019. It added read-only provider metadata for `fake_local`, `douyin_sandbox`, and `douyin_real`.

v0.8 Batch 3 implemented the frontend read-only Provider Registry UI boundary in ADR 0020.

This batch adds a backend-only connection state / sensitive storage status metadata foundation on top of the Provider Registry. The real Douyin POC must wait until registry, capability, connection state, authorization status, sensitive storage status, and source-separation boundaries are stable.

## Decision

The backend adds a metadata-only `provider_connection_states` table.

The backend adds a read-only provider connection state API.

Connection state must be bound to known providers in the Provider Registry. Unknown database rows must not become real providers and must not appear in the API response.

Default connection state must cover `fake_local`, `douyin_sandbox`, and `douyin_real`.

`fake_local` is a local fake/demo/test workflow. It does not require authorization and does not require sensitive storage.

`douyin_sandbox` and `douyin_real` are placeholder / not connected / not implemented metadata only. They must not be displayed or returned as real available integrations.

`sensitive_storage_status` may describe status only. It must not store access tokens, refresh tokens, API keys, secrets, credential material, authorization codes, OAuth client secrets, raw platform responses, or private keys.

API consumers may see only non-sensitive metadata, `connection_status`, `authorization_status`, `sensitive_storage_status`, `safe_status_message`, and boundary notes.

This batch does not add write APIs, does not read real secrets from environment variables, does not call external services, and does not implement OAuth.

## Consequences

Future UI can use read-only connection state metadata to show clearer platform connection boundaries without adding connection, authorization, credential, upload, publish, or scheduling actions.

Future OAuth state/callback POCs may reuse `connection_status` and `authorization_status`, but they must be designed and tested in a later ADR.

Future Credential storage must separately design encrypted or reference-based storage. The metadata table introduced here must not be treated as a credential store.

This batch adds a metadata-only database table and read-only API, but it does not mean OAuth, Credential storage, real Douyin integration, real metrics fetching, uploading, publishing, scheduling, or production-grade platform security is available.

## Non-Goals

- Do not connect to the real Douyin API.
- Do not implement OAuth.
- Do not add an OAuth callback route.
- Do not add connect / authorize / refresh / revoke / disconnect write APIs.
- Do not store access tokens.
- Do not store refresh tokens.
- Do not store API keys.
- Do not store secrets.
- Do not store credential material.
- Do not store authorization codes.
- Do not store OAuth client secrets.
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

## Provider Connection State Boundary

Provider Connection State is a backend-only metadata layer. It depends on the Provider Registry as the provider source of truth.

The layer may return status metadata only for registry providers. The initial registry-backed set is `fake_local`, `douyin_sandbox`, and `douyin_real`.

The layer may merge non-sensitive database status rows for known providers, but registry identity and source boundaries must remain authoritative. A row must not change `fake_local` into a real provider, nor change `douyin_sandbox` into `douyin_real`.

Unknown `provider_id` rows in the database must be ignored by list responses and must not be treated as real provider availability.

## Sensitive Storage Status Boundary

`sensitive_storage_status` describes whether sensitive storage is required, not configured, not implemented, reference-only, or planned as encrypted storage. It is not storage for sensitive material.

The metadata table may store `provider_id`, `source_type`, `connection_status`, `authorization_status`, `sensitive_storage_status`, `safe_status_message`, status-change reason, and timestamps.

The metadata table must not contain fields capable of carrying access tokens, refresh tokens, token values, API keys, secrets, client secrets, authorization codes, credential material, encrypted credential material, private keys, OAuth codes, passwords, or raw provider responses.

## Source Separation

`fake_local` must remain local fake/demo/test data only. It is not real Douyin data, requires no OAuth, stores no tokens, and makes no external service calls.

`douyin_sandbox` must remain placeholder metadata only. OAuth is not implemented, tokens are not stored, real Douyin API calls are not made, and it cannot be treated as `douyin_real`.

`douyin_real` must remain a future real provider placeholder only. It is not real Douyin integration; OAuth, token storage, real metrics fetching, upload, publish, and scheduling are not implemented.

## API Boundary

The API may expose `GET /api/provider-connections` and `GET /api/provider-connections/{provider_id}`.

The API must not add POST, PUT, PATCH, DELETE, connect, authorize, callback, refresh, revoke, disconnect, credential, upload, publish, schedule, or sync routes.

404 responses must be debuggable but must not echo user input or include token, secret, credential, authorization code, API key, client secret, raw response, or environment values.

The existing Provider Registry API at `GET /api/providers` and `GET /api/providers/{provider_id}` must keep its semantics.

## Security Requirements

- The service must not read real platform secrets from environment variables.
- The service must not read local credential files.
- The service must not call external services.
- The API response must not include sensitive field names such as `access_token`, `refresh_token`, `token_value`, `api_key`, `client_secret`, `authorization_code`, `credential_material`, `encrypted_credential`, `raw_response`, `private_key`, `oauth_code`, or `password`.
- The API response must not contain token values, refresh token values, API key values, secret values, credential material, authorization code values, OAuth client secret values, private keys, real platform returned data, or real Douyin credentials.
- Logs and errors must remain useful for debugging without exposing sensitive material.

## Testing Requirements

Backend tests must cover list and read responses for `fake_local`, `douyin_sandbox`, and `douyin_real`, including stable order and source separation.

Backend tests must verify the default `connection_status`, `authorization_status`, `sensitive_storage_status`, safe status messages, and boundary notes for each provider.

Backend tests must verify that unknown provider rows do not appear in list responses and that known provider rows can merge only non-sensitive status metadata without changing registry source boundaries.

Backend tests must verify that POST, PUT, PATCH, and DELETE provider connection endpoints do not succeed.

Backend tests must verify that the table schema and API response do not contain sensitive field names, and that response bodies do not leak environment values.

Existing Provider Registry, fake metrics, fake publishing, and fake metrics review summary workflows must continue to pass without changing v0.7 fake/local workflow semantics.
