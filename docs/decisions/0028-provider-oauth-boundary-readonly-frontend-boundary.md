# ADR 0028: Provider OAuth Boundary Read-only Frontend Boundary

## Status

Accepted

## Context

v0.7.0 has completed the fake/local metrics review summary workflow. That workflow remains local fake/manual only and does not connect to real Douyin, implement OAuth, store tokens, fetch real metrics, upload, publish, schedule publishing, or call external services.

v0.8 Batch 1, through ADR 0018, defined the Provider, Credential, OAuth, Secret, token lifecycle, security audit, connection status, and fake/sandbox/real source-separation boundaries.

v0.8 Batch 2, through ADR 0019, implemented the backend-only Provider Registry & Capability Metadata foundation.

v0.8 Batch 3, through ADR 0020, implemented the frontend read-only Provider Registry UI boundary.

v0.8 Batch 4, through ADR 0021, implemented the backend-only Provider Connection State & Sensitive Storage Status foundation.

v0.8 Batch 5, through ADR 0022, implemented the frontend read-only Provider Connection State UI boundary.

v0.8 Batch 6, through ADR 0023, implemented the backend-only Provider Credential Reference & Secret Redaction foundation.

v0.8 Batch 7, through ADR 0024, implemented the frontend read-only Provider Credential Reference UI boundary.

v0.8 Batch 8, through ADR 0025, implemented the backend-only Provider Security Audit Event & Redacted Audit Log foundation.

v0.8 Batch 9, through ADR 0026, implemented the frontend read-only Provider Security Audit Event UI boundary.

v0.8 Batch 10, through ADR 0027, implemented the backend-only Provider OAuth State & Callback Boundary foundation.

This batch adds a frontend read-only Provider OAuth Boundary UI on top of the Batch 10 read-only API. The real Douyin POC must wait until registry, capability, connection state, authorization status, sensitive storage status, credential reference, secret redaction, security audit event, OAuth state/callback boundary, and source-separation display boundaries are stable across backend and frontend.

## Decision

The frontend may read `GET /api/provider-oauth-boundaries`.

The frontend may only display non-sensitive provider OAuth boundary metadata.

The frontend must explicitly display `source_type`, `implementation_status`, `oauth_policy_status`, `state_policy_status`, `callback_policy_status`, `csrf_protection_status`, `redirect_uri_policy_status`, `token_exchange_policy_status`, `token_storage_policy_status`, `error_redaction_policy_status`, `audit_event_policy_status`, `safe_status_message`, and boundary notes.

The frontend must distinguish `fake_local`, `douyin_sandbox`, and `douyin_real`.

`fake_local` may be shown as a local fake/demo/test workflow where OAuth, state, callback, token exchange, and token storage are not required.

`douyin_sandbox` and `douyin_real` may only be shown as placeholder / not_implemented / required_planned metadata. They must not be shown as available real OAuth integrations.

`can_start_oauth`, `can_handle_callback`, `can_exchange_token`, `can_refresh_token`, and `can_revoke_token` must currently be displayed as unavailable / not executable.

The frontend does not add connect / authorize / OAuth start / callback / token exchange / refresh / revoke / disconnect / upload / publish / schedule UI.

The frontend does not add secret input, token viewer, credential viewer, authorization code input, OAuth state input, raw request viewer, raw response viewer, or raw payload viewer.

The frontend does not receive, save, cache, or display token, secret, API key, authorization code, OAuth client secret, OAuth state value, credential material, private key, raw request, raw response, or raw payload.

`required_planned` can only be displayed as a future planned boundary and does not mean CSRF, state, or callback protection is active.

`token_exchange_policy_status` and `token_storage_policy_status` can only display metadata and do not mean token exchange or token storage is implemented.

## Consequences

Users and reviewers can see the provider OAuth state/callback/token boundary in the UI without adding any OAuth, credential, provider, or publishing workflow.

The later v0.9 Douyin Provider POC can reuse this UI boundary, but it must first update registry / connection state / credential reference / security audit / OAuth boundary / capability metadata and pass separate ADR and test review.

This UI does not mean OAuth, callback route, state storage, token exchange, Credential storage, real Douyin, real metrics, or real publishing is available.

## Non-Goals

- Do not connect to the real Douyin API.
- Do not implement OAuth.
- Do not add an OAuth callback route.
- Do not add OAuth state storage.
- Do not add token exchange.
- Do not generate a real provider authorization URL.
- Do not add a connect / authorize button.
- Do not add an OAuth start button.
- Do not add a callback button.
- Do not add a token exchange button.
- Do not add a refresh / revoke / disconnect button.
- Do not add secret input.
- Do not add token viewer.
- Do not add credential management UI.
- Do not add authorization code input.
- Do not add OAuth state input.
- Do not add raw request / raw response / raw payload viewer.
- Do not store access token.
- Do not store refresh token.
- Do not store API key.
- Do not store secret.
- Do not store authorization code.
- Do not store OAuth client secret.
- Do not store OAuth state value.
- Do not store credential material.
- Do not store private key.
- Do not store raw request.
- Do not store raw response.
- Do not store raw payload.
- Do not add a Credential model or database table.
- Do not add a backend API.
- Do not fetch real metrics.
- Do not upload real videos.
- Do not publish for real.
- Do not schedule publishing.
- Do not auto-publish.
- Do not run scheduled synchronization.
- Do not call external services.
- Do not add Docker.
- Do not add GitHub Actions.
- Do not add a production-grade OAuth security module.
- Do not modify the v0.7.0 release scope.

## Frontend Boundary

The UI is read-only and global to provider OAuth boundaries. It does not create a new route, does not write OAuth metadata, and does not alter provider connection, authorization, credential, OAuth, token, publishing, or real platform data state.

## OAuth Boundary Display Boundary

The UI may display only known provider OAuth boundary metadata from the backend. It may show policy/status values and safe boundary notes, but it must not show real OAuth authorization URLs, real connection state changes, real OAuth completion, or real token lifecycle state.

## OAuth State Display Boundary

`state_policy_status` can show that future state handling is planned or not implemented. It must not display an OAuth state value, stored state record, state nonce, state verifier, redirect payload, or callback payload.

## Callback Display Boundary

`callback_policy_status` can show that a callback boundary is planned or not implemented. It must not expose a callback route, callback test action, callback payload, raw request, raw response, or authorization code.

## CSRF Display Boundary

`csrf_protection_status=required_planned` means CSRF protection is a future requirement. It is not active security protection in this batch and must not be displayed as enabled or ready.

## Token Exchange Display Boundary

`token_exchange_policy_status` can only describe token exchange readiness. It must not render token exchange controls, token exchange output, token response metadata, access tokens, refresh tokens, or provider response data.

## Token Storage Display Boundary

`token_storage_policy_status` can only describe token storage readiness. It must not display stored tokens, configured credentials, encrypted credential material, secret manager status, production KMS status, or token viewer controls.

## Sensitive Value Display Boundary

The frontend API type and UI must not add fields or displays capable of carrying sensitive values such as token, secret, API key, authorization code, OAuth client secret, OAuth state value, credential material, private key, raw request, raw response, raw payload, password, bearer token, or session cookie.

## Source Separation

`fake_local` is local fake/demo/test data only, not real Douyin data, does not require OAuth, does not store state values, does not store authorization codes, does not exchange tokens, stores no tokens or secrets, and makes no external service calls.

`douyin_sandbox` is placeholder OAuth boundary metadata only. OAuth is not implemented, the OAuth callback route is not implemented, OAuth state storage is not implemented, CSRF state validation is planned but not active, authorization code and tokens are not stored, no token exchange or real Douyin API call is made, and it cannot be treated as `douyin_real`.

`douyin_real` is future real provider OAuth boundary placeholder metadata only, not real Douyin integration. OAuth, callback route, OAuth state storage, token exchange, token storage, real metrics fetching, upload, publish, and scheduling are not implemented.

## Security Requirements

The UI must use only `safe_status_message`, policy/status metadata, boundary notes, and other non-sensitive OAuth boundary metadata returned by the backend. Error states must use safe generic messages and must not echo server details that could contain sensitive input. The frontend API type must not add sensitive carrier fields such as `access_token`, `refresh_token`, `token_value`, `api_key`, `secret_value`, `client_secret`, `oauth_client_secret`, `authorization_code`, `state_value`, `oauth_state_value`, `callback_payload`, `credential_material`, `encrypted_credential`, `raw_request`, `raw_response`, `raw_payload`, `private_key`, `oauth_code`, `password`, `bearer_token`, or `session_cookie`.

## Testing Requirements

Frontend tests must verify the read-only API call, loading / success / error / empty states, display of `fake_local`, `douyin_sandbox`, and `douyin_real` OAuth boundary metadata, display of OAuth policy statuses and action booleans as unavailable, display of safe status messages and boundary notes, absence of sensitive values or sensitive carrier fields, and absence of OAuth action buttons, credential inputs, authorization code inputs, OAuth state inputs, raw request viewers, raw response viewers, and raw payload viewers.
