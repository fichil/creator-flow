# ADR 0027: Provider OAuth State and Callback Boundary Backend Foundation

## Status

Accepted

## Context

v0.7.0 completed the fake/local metrics review summary workflow.

v0.8 Batch 1, through ADR 0018, defined the Provider, Credential, OAuth, Secret, token lifecycle, security audit, connection status, and fake/sandbox/real source-separation boundaries.

v0.8 Batch 2, through ADR 0019, implemented the backend-only Provider Registry & Capability Metadata foundation.

v0.8 Batch 3, through ADR 0020, implemented the frontend read-only Provider Registry UI boundary.

v0.8 Batch 4, through ADR 0021, implemented the backend-only Provider Connection State & Sensitive Storage Status foundation.

v0.8 Batch 5, through ADR 0022, implemented the frontend read-only Provider Connection State UI boundary.

v0.8 Batch 6, through ADR 0023, implemented the backend-only Provider Credential Reference & Secret Redaction foundation.

v0.8 Batch 7, through ADR 0024, implemented the frontend read-only Provider Credential Reference UI boundary.

v0.8 Batch 8, through ADR 0025, implemented the backend-only Provider Security Audit Event & Redacted Audit Log foundation.

v0.8 Batch 9, through ADR 0026, implemented the frontend read-only Provider Security Audit Event UI boundary.

This batch adds a backend-only OAuth State & Callback Boundary metadata foundation on top of Provider Registry, Connection State, Credential Reference, Secret Redaction, and Security Audit. The real Douyin POC must wait until registry, capability, connection state, authorization status, sensitive storage status, credential reference, secret redaction, security audit event, OAuth state/callback boundary, and source-separation boundaries are stable.

## Decision

The backend adds a metadata-only `provider_oauth_boundaries` table.

The backend adds a backend-only provider OAuth boundary metadata service.

The backend adds a read-only provider OAuth boundary metadata API.

OAuth boundary metadata must bind to providers known by Provider Registry. `source_type` must be derived from Provider Registry and not trusted from callers or database rows.

`fake_local` is a local fake/demo/test workflow and does not require OAuth state, callback handling, token exchange, or token storage.

`douyin_sandbox` and `douyin_real` can only be OAuth boundary placeholder / not_implemented / required_planned metadata and must not be shown as available real integrations.

`state_policy_status` can only describe state/CSRF boundaries and must not store an OAuth state value. `callback_policy_status` can only describe callback boundaries and must not implement a real callback route. `token_exchange_policy_status` can only describe token exchange boundaries and must not execute token exchange. `token_storage_policy_status` can only describe token storage boundaries and must not store access token or refresh token.

API consumers can only see non-sensitive metadata, policy statuses, `safe_status_message`, and `boundary_notes`. This batch does not add external write APIs, does not read real secrets from environment variables, does not call external services, and does not implement OAuth.

## Consequences

Later UI work can display clearer provider OAuth readiness boundaries from read-only OAuth boundary metadata.

The later v0.9 Douyin Provider POC can reuse OAuth boundary metadata, but mock/sandbox callback or real OAuth smoke tests must pass separate ADR and test review first.

Real OAuth state storage, callback route, token exchange, and token storage must be designed separately. This metadata table must not be used as a real OAuth state store, callback handler, or token store.

This batch adds a metadata-only database table, internal service, and read-only API, but it does not mean OAuth, callback route, state storage, token exchange, Credential storage, real Douyin, real metrics, or real publishing is available.

## Non-Goals

- Do not connect to the real Douyin API.
- Do not implement OAuth.
- Do not add an OAuth callback route.
- Do not add OAuth state storage.
- Do not add token exchange.
- Do not generate a real provider authorization URL.
- Do not add connect / authorize / refresh / revoke / disconnect write APIs.
- Do not store access token.
- Do not store refresh token.
- Do not store token value.
- Do not store API key.
- Do not store secret.
- Do not store client secret.
- Do not store authorization code.
- Do not store OAuth client secret.
- Do not store OAuth state value.
- Do not store credential material.
- Do not store encrypted credential.
- Do not store private key.
- Do not store raw request.
- Do not store raw response.
- Do not store raw payload.
- Do not add real Credential storage.
- Do not add a real Provider adapter.
- Do not fetch real metrics.
- Do not upload real video.
- Do not publish for real.
- Do not schedule publishing.
- Do not auto-publish.
- Do not run scheduled sync.
- Do not call external services.
- Do not add frontend UI.
- Do not add Docker.
- Do not add GitHub Actions.
- Do not add a production-grade OAuth security module.
- Do not change the v0.7.0 release scope.

## Provider OAuth Boundary

Provider OAuth Boundary is backend-only metadata. It expresses whether OAuth is not required, planned, not implemented, or unavailable for a known provider. It is not a Provider adapter and does not make platform requests.

## OAuth State Boundary

OAuth state metadata can describe that state validation is required or planned, but it must not store a state value, state nonce, raw callback input, or anything that can authorize a user session.

## Callback Boundary

Callback metadata can describe callback readiness and safety policy. It does not add a real callback route and does not accept, parse, store, or replay callback payloads.

## CSRF Protection Boundary

CSRF protection metadata can describe whether state validation is not required for `fake_local` or required/planned for future real providers. It does not activate a real CSRF implementation for OAuth callbacks in this batch.

## Redirect URI Boundary

Redirect URI metadata can describe whether redirect URI policy is not required, required/planned, not configured, or not implemented. It must not generate or return a real provider authorization URL.

## Token Exchange Boundary

Token exchange metadata can describe planned or not implemented exchange policy. It must not exchange authorization codes for tokens, call external services, or store token responses.

## Token Storage Boundary

Token storage metadata can describe none, planned, not implemented, or unavailable storage policy. It must not store access token, refresh token, token value, OAuth client secret, API key, credential material, or encrypted credential.

## Error Redaction Boundary

OAuth boundary error metadata must be safe to return to API consumers. Any future OAuth callback or token exchange errors must be redacted through a separate implementation before real flows are introduced.

## Source Separation

`fake_local` means local fake/demo/test data only and does not require OAuth. `douyin_sandbox` means placeholder OAuth boundary metadata only and cannot be treated as `douyin_real`. `douyin_real` means future real provider OAuth boundary placeholder only and is not real Douyin integration.

## API Boundary

The API is read-only. It returns known provider OAuth boundary metadata only and must ignore database rows for unknown providers. It does not add POST / PUT / PATCH / DELETE, connect, authorize, callback, refresh, revoke, disconnect, credential, token, or real OAuth routes.

## Security Requirements

The OAuth boundary table and API response must not contain fields capable of storing sensitive values such as access token, refresh token, token value, API key, secret, client secret, OAuth client secret, authorization code, OAuth state value, credential material, encrypted credential, private key, raw request, raw response, or raw payload.

The service must not read environment variables for real platform secrets, must not read local credential files, must not call external services, must not generate authorization URLs, must not execute token exchange, and must not save real OAuth state, authorization code, token response, provider response, or redirect payload.

## Testing Requirements

Tests must verify stable ordering, source separation, default metadata for `fake_local`, `douyin_sandbox`, and `douyin_real`, per-provider read endpoints, 404 behavior without sensitive terms, lack of sensitive response fields and table columns, lack of environment value leakage, unknown provider row filtering, safe metadata row merge for known providers without changing registry boundaries, disabled write methods, absence of real OAuth / connect / callback / lifecycle routes, and continued compatibility of Provider Registry, Connection State, Credential Reference, Security Audit, redaction helper, fake metrics, fake publishing, and fake/local review summary tests.
