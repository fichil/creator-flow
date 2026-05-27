# ADR 0018: Provider and Credential Security Boundary

## Status

Accepted

## Context

v0.7.0 has completed the fake/local metrics review summary workflow. The current stable workflow can create deterministic fake/local metrics review summaries for manual review, but it still does not connect to real Douyin, does not implement OAuth, does not store tokens, and does not fetch real platform metrics.

v0.8 is the security foundation before real platform integration. Before any real Douyin POC, creator-flow must stabilize Provider registry, capability metadata, Credential boundary, secret boundary, OAuth state/callback security, token lifecycle, audit log direction, connection status direction, and fake/sandbox/real source separation.

The real Douyin POC must wait until Provider, Credential, OAuth, and token lifecycle boundaries are stable enough to avoid leaking credentials, confusing fake/local data with real data, or bypassing explicit user authorization.

## Decision

Platform capabilities must be exposed through a Provider registry or equivalent registry with capability metadata. Core domain models must not depend on Douyin-specific fields, API shapes, OAuth scopes, or raw platform responses.

Credential material and tokens must be isolated inside the backend security boundary. The frontend must never receive access tokens, refresh tokens, authorization codes, API keys, OAuth client secrets, or platform secrets.

OAuth state/callback handling must protect against CSRF. The callback must validate `state`; callback errors must be visible enough for troubleshooting without leaking secrets.

`fake_local`, sandbox/mock, and real sources must remain distinguishable. The fake/local provider does not require authorization and must never pretend to be a real platform source.

Logs, errors, fixtures, snapshots, and documentation examples must not contain real secrets. Fake/local placeholders may be used only when clearly labeled as placeholders and not real platform credentials.

## Consequences

v0.8 can first define documentation and ADR boundaries without implementing real OAuth.

v0.8 can first define token lifecycle strategy without storing real access tokens, refresh tokens, API keys, secrets, or credentials.

v0.8 can first define Provider and credential boundaries without connecting to real Douyin.

Future v0.9 Douyin Provider POC / Sandbox Integration must follow this ADR before adding sandbox/mock callbacks, token refresh dry-runs, or minimal metrics-reading experiments.

## Non-Goals

- Do not connect to the real Douyin API.
- Do not implement OAuth.
- Do not store access tokens, refresh tokens, API keys, secrets, or credentials.
- Do not fetch real metrics.
- Do not upload real videos.
- Do not publish real content.
- Do not schedule publishing.
- Do not auto-publish.
- Do not do production deployment.
- Do not add GitHub Actions.
- Do not add Docker.
- Do not bypass platform authorization, app review, API permissions, user authorization, or human review.

## Security Requirements

- Secrets must not enter Git.
- Secrets must not enter logs.
- Secrets must not be returned to the frontend.
- Secrets must not enter test snapshots.
- Secrets must not enter error responses.
- Logs must not include tokens, refresh tokens, authorization codes, API keys, OAuth client secrets, or platform credentials.
- Error messages must identify the state, such as not connected, authorization failed, token expired, permission denied, or provider API failed, without exposing credential material.
- Backend storage for future credential material must use encryption or references to a secure store; v0.8 Batch 1 only defines the boundary and does not implement token storage.
- Local development may use fake/local placeholders, but they must be explicitly labeled as not real tokens.

## Provider Capability Boundary

The Provider registry or equivalent registry should expose stable metadata such as:

- `provider_id`
- `provider_name`
- `provider_type`
- `source_type`, such as `fake_local`, `sandbox`, or `real`
- `supports_oauth`
- `supports_metrics_read`
- `supports_publish_prepare`
- `supports_real_publish`
- `supports_sandbox`

Provider adapters must translate platform-specific API responses, error codes, OAuth scopes, and provider details into platform-neutral domain concepts. Provider adapters must not leak platform raw responses, authorization details, or provider-specific fields into core models.

## Credential and Secret Boundary

Credential material includes access tokens, refresh tokens, API keys, OAuth client secrets, platform account credentials, authorization codes, and any future provider secret.

Credential material must remain backend-only. The frontend may display connection status, provider display name, source type, granted capability metadata, and non-sensitive account metadata, but it must not display or cache credential material.

Tests may use clearly labeled fake/local placeholders. Tests must not use real platform credentials, real OAuth callback credentials, or real provider responses.

## OAuth Boundary

OAuth `state` is required for CSRF protection. The callback must reject missing, expired, reused, or mismatched `state` values.

Redirect URI configuration must have an explicit boundary and must not be controlled by untrusted request input.

Token exchange must happen only on the backend. Access tokens and refresh tokens must never be exposed to the frontend.

Future token lifecycle handling must cover refresh, expiry, revoke, disconnect, authorization failure, permission denial, and provider API failure states.

## Fake / Sandbox / Real Source Separation

`fake_local` is local development, demo, or test data. It must not be described as real Douyin performance, real platform analysis, or a real user account connection.

`douyin_sandbox` or other sandbox/mock sources must not be described as `douyin_real`.

`douyin_real` requires explicit user authorization, provider capability checks, credential boundary compliance, and source labeling.

All UI, API responses, and documentation must distinguish fake/local, sandbox/mock, and real data. Without authorization, the v0.7 fake/local workflow must remain usable and must continue to be labeled as fake/local.
