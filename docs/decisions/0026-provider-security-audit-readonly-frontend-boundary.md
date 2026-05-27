# ADR 0026: Provider Security Audit Event Read-only Frontend Boundary

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

This batch adds a frontend read-only Provider Security Audit Event UI on top of the Batch 8 read-only API. The real Douyin POC must wait until registry, capability, connection state, authorization status, sensitive storage status, credential reference, secret redaction, security audit event, and source-separation display boundaries are stable across backend and frontend.

## Decision

The frontend may read `GET /api/provider-security-audit-events`.

The frontend can only display non-sensitive / redacted provider security audit event metadata. It must explicitly display `source_type`, `implementation_status`, `event_type`, `event_status`, `event_severity`, `actor_type`, `redaction_status`, `safe_event_message`, `safe_metadata`, `boundary_notes`, and `created_at`.

The frontend must distinguish `fake_local`, `douyin_sandbox`, and `douyin_real`. `fake_local` may be shown as local fake/demo/test audit metadata. `douyin_sandbox` and `douyin_real` can only be shown as placeholder / redacted audit metadata and must not be shown as available real integrations.

The frontend does not add connect / authorize / callback / refresh / revoke / disconnect / upload / publish / schedule UI. It does not add an audit event writer UI. It does not add secret input, token viewer, credential viewer, raw request viewer, raw response viewer, or raw payload viewer.

The frontend does not receive, save, cache, or display token, secret, API key, authorization code, OAuth client secret, credential material, private key, raw request, raw response, or raw payload. `redaction_status` can only display redaction metadata and does not mean production-grade SIEM, compliance archive, external log shipping, or security monitoring is implemented.

## Consequences

Users and reviewers can see the Provider Security Audit Event and redacted metadata boundaries in the UI.

The later v0.9 Douyin Provider POC can reuse this UI boundary, but it must first update registry / connection state / credential reference / security audit / capability metadata and pass separate ADR and test review.

This UI does not mean OAuth, Credential storage, real Douyin, real metrics, real publishing, production-grade SIEM, or compliance logging is available.

## Non-Goals

- Do not connect to the real Douyin API.
- Do not implement OAuth.
- Do not add an OAuth callback route.
- Do not add OAuth state storage.
- Do not add token exchange.
- Do not add a connect / authorize button.
- Do not add refresh / revoke / disconnect buttons.
- Do not add audit event writer UI.
- Do not add secret input.
- Do not add token viewer.
- Do not add credential management UI.
- Do not add raw request / raw response / raw payload viewer.
- Do not store access token.
- Do not store refresh token.
- Do not store API key.
- Do not store secret.
- Do not store authorization code.
- Do not store OAuth client secret.
- Do not store credential material.
- Do not store private key.
- Do not store raw request.
- Do not store raw response.
- Do not store raw payload.
- Do not add a Credential model or database table.
- Do not add backend API.
- Do not fetch real metrics.
- Do not upload real video.
- Do not publish for real.
- Do not schedule publishing.
- Do not auto-publish.
- Do not run scheduled sync.
- Do not call external services.
- Do not add Docker.
- Do not add GitHub Actions.
- Do not add production-grade SIEM.
- Do not add an external logging system.
- Do not add a compliance archive.
- Do not change the v0.7.0 release scope.

## Frontend Boundary

The UI is read-only and global to provider security boundaries. It does not create a new route, does not write audit events, and does not alter provider connection, authorization, credential, publishing, or real platform data state.

## Audit Event Display Boundary

The UI may display audit event metadata from known providers only. Event types such as `token_expired`, `disconnect_requested`, or `revoke_requested` are future event metadata only and must not imply token lifecycle, disconnect, or revoke APIs exist in this batch.

## Redacted Metadata Display Boundary

`safe_metadata` is displayed as read-only JSON / key-value metadata. Empty metadata is shown as no safe metadata. A `[REDACTED]` value may be displayed as the result of redaction, but raw payload, raw request, raw response, token, secret, API key, authorization code, OAuth client secret, credential material, or private key values must not be displayed.

## Sensitive Value Display Boundary

The frontend must not render secret inputs, token inputs, API key inputs, credential inputs, password inputs, raw request viewers, raw response viewers, raw payload viewers, token viewers, secret viewers, or credential viewers.

## Source Separation

`fake_local` is local fake/demo/test audit metadata only and is not real Douyin data. `douyin_sandbox` is placeholder audit metadata only, OAuth is not implemented, tokens and secrets are not stored, no real Douyin API call is made, and it cannot be treated as `douyin_real`. `douyin_real` is future real provider placeholder audit metadata only, not real Douyin integration, OAuth is not implemented, token / API key / secret storage is not implemented, real metrics fetching is not implemented, and upload / publish / scheduling is not implemented.

## Security Requirements

The UI must use only `safe_event_message`, `safe_metadata`, `boundary_notes`, and other non-sensitive audit metadata returned by the backend. Error states must use safe generic messages and must not echo server details that could contain sensitive input. The frontend API type must not add fields capable of carrying sensitive values such as token, secret, API key, authorization code, OAuth client secret, credential material, private key, raw request, raw response, or raw payload.

## Testing Requirements

Tests must verify the read-only API call, the bounded `limit` query, loading / success / error / empty states, display of `fake_local`, `douyin_sandbox`, and `douyin_real` audit metadata, safe metadata rendering, `[REDACTED]` rendering without raw fake sensitive values, absence of raw request / response / payload display, and absence of action buttons or secret / token / credential / raw payload inputs.
