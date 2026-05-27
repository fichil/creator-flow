# ADR 0025: Provider Security Audit Event and Redacted Audit Log Backend Foundation

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

v0.8 Batch 7 implemented the frontend read-only Provider Credential Reference UI boundary in ADR 0024.

This batch adds a backend-only Provider Security Audit Event & Redacted Audit Log foundation on top of Provider Registry, Connection State, Credential Reference, and Secret Redaction. The real Douyin POC must wait until registry, capability, connection state, authorization status, sensitive storage status, credential reference, secret redaction, security audit event, and source-separation boundaries are stable.

## Decision

The backend will add a metadata-only `provider_security_audit_events` table.

The backend will add a backend-only provider security audit event service.

The backend will add a read-only provider security audit events API.

Audit event metadata must bind to known providers from Provider Registry. The `source_type` must be derived from Provider Registry and must not trust caller-provided source information.

Audit event messages and metadata must pass through the secret redaction helper before storage and response. `safe_metadata_json` may store only redacted / non-sensitive metadata.

`fake_local` is a local fake/demo/test workflow and may record only local fake audit metadata.

`douyin_sandbox` and `douyin_real` may only be placeholder audit metadata in this batch. They must not be displayed or returned as available real integrations.

API consumers may see only non-sensitive metadata, `event_type`, `event_status`, `event_severity`, `actor_type`, `redaction_status`, `safe_event_message`, `safe_metadata`, and boundary notes.

This batch must not add external write APIs, read real keys from environment variables, call external services, or implement OAuth.

## Consequences

Future UI work can use read-only security audit events metadata to show clearer provider security audit boundaries.

Future OAuth state/callback POC work can reuse the audit event service and redaction helper, but it must pass a later ADR and tests.

Future token lifecycle, revoke, and disconnect events may reuse the audit event schema, but this metadata table must not become token storage or a real OAuth audit trail.

This batch adds a metadata-only database table, an internal service, and a read-only API, but it does not mean OAuth, Credential storage, real Douyin integration, real metrics fetching, uploading, publishing, scheduling, production SIEM, external log shipping, or compliance archiving is available.

## Non-Goals

- Do not connect to the real Douyin API.
- Do not implement OAuth.
- Do not add an OAuth callback route.
- Do not add OAuth state storage.
- Do not add token exchange.
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
- Do not store raw requests.
- Do not store raw responses.
- Do not store raw payloads.
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
- Do not add production-grade SIEM.
- Do not add an external logging system.
- Do not add a compliance archive.
- Do not modify the v0.7.0 release scope.

## Provider Security Audit Event Boundary

Provider Security Audit Event is a backend-only metadata layer. It depends on Provider Registry as the provider source of truth.

Audit event metadata may be returned only for providers known to the registry. Unknown `provider_id` rows in the database must be ignored and must not become real providers or real provider audit events through metadata alone.

The metadata layer may return `event_type`, `event_status`, `event_severity`, `actor_type`, `redaction_status`, `safe_event_message`, `safe_metadata`, and boundary notes.

The metadata layer must not read environment variables, local credential files, token files, secret files, platform raw responses, or external provider services.

The metadata layer is not an OAuth audit trail, a Credential store, encrypted token storage, a provider adapter, a production SIEM, external log shipping, or a compliance archive.

## Redacted Audit Log Boundary

The audit event service must redact event messages and metadata before persistence.

`safe_event_message` must not contain token values, refresh token values, API key values, secret values, authorization code values, OAuth client secret values, credential material, private keys, raw platform responses, or real platform returned data.

`safe_metadata_json` must be a JSON object containing only redacted / non-sensitive metadata. It must not store raw requests, raw responses, raw payloads, platform raw responses, or values that can authorize a real platform account.

Redaction uses the backend secret redaction helper from ADR 0023. This helper reduces leakage risk, but it is not a secret manager, KMS, encrypted storage layer, credential vault, SIEM, or compliance logging system.

## Source Separation

`fake_local` must remain local fake/demo/test audit metadata only. It must say no OAuth required, no token stored, no secret stored, and no external service call.

`douyin_sandbox` must remain placeholder audit metadata only. It must say OAuth is not implemented, tokens are not stored, secrets are not stored, no real Douyin API call is made, and it cannot be treated as `douyin_real`.

`douyin_real` must remain future real provider placeholder audit metadata only. It must say not real Douyin integration, OAuth is not implemented, access token / refresh token storage is not present, API key storage is not present, secret storage is not present, real metrics fetching is not present, and upload / publish / scheduling are not implemented.

Source separation must not be overridden by database rows or caller input. Registry source type, provider name, availability, and implementation status remain authoritative.

## API Boundary

The backend may expose `GET /api/provider-security-audit-events`.

The backend may expose `GET /api/provider-security-audit-events/{audit_event_id}`.

The list API may support `provider_id` and `limit` query parameters. `limit` must be bounded to avoid unbounded reads.

Unknown providers or audit event ids must return safe 404 messages that do not echo user input or sensitive-looking values.

The API must not add POST, PUT, PATCH, DELETE, connect, authorize, callback, refresh, revoke, disconnect, credential write, token read, upload, publish, schedule, or sync routes.

The API response must not include fields capable of carrying sensitive values, such as `access_token`, `refresh_token`, `token_value`, `api_key`, `secret_value`, `client_secret`, `oauth_client_secret`, `authorization_code`, `credential_material`, `encrypted_credential`, `raw_request`, `raw_response`, `raw_payload`, `private_key`, `oauth_code`, `password`, `bearer_token`, or `session_cookie`.

## Security Requirements

- The metadata table must not include columns capable of carrying sensitive values.
- API responses must not expose tokens, secrets, API keys, authorization codes, OAuth client secrets, credential material, encrypted credentials, private keys, raw requests, raw responses, raw payloads, real platform returned data, or environment variable values.
- Audit event messages and metadata must be redacted before they are stored.
- Boundary notes may mention tokens, secrets, OAuth, API keys, and credentials only to state that they are not stored or implemented.
- Tests may include fake sensitive-looking values only as redaction input or negative assertions.
- Git must not include real credentials, real OAuth callback data, real platform responses, SQLite databases, uploads, generated media, `dist/`, `node_modules`, `.venv`, or runtime files.

## Testing Requirements

Backend tests must cover empty list behavior, list and read APIs, `provider_id` filtering, limit bounds, safe 404 responses, and no successful write methods.

Backend tests must verify source separation and boundary notes for `fake_local`, `douyin_sandbox`, and `douyin_real`.

Backend tests must verify that unknown provider rows are ignored and that unknown providers cannot be recorded through the internal helper.

Backend tests must verify that audit event messages and nested metadata are redacted before API response.

Backend tests must verify that API responses and table columns do not contain sensitive field names, and that response bodies do not leak environment variable values.

Existing Provider Registry, Provider Connection State, Provider Credential Reference, secret redaction, fake metrics provider, fake publishing workflow, and fake review summary workflow tests must continue to pass.
