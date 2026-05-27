# ADR 0019: Provider Registry and Capability Metadata Backend Foundation

## Status

Accepted

## Context

v0.7.0 has completed the fake/local metrics review summary workflow. That workflow remains local fake/manual only and does not connect to real Douyin, implement OAuth, store tokens, or fetch real platform metrics.

v0.8 Batch 1 defined Provider, Credential, OAuth, Secret, token lifecycle, audit, connection status, and fake/sandbox/real source separation boundaries in ADR 0018.

This batch builds on ADR 0018 by adding a backend-only Provider Registry & Capability Metadata foundation. The real Douyin POC must wait until registry, capability metadata, and source separation boundaries are stable enough to avoid presenting future platform plans as available real integration.

## Decision

The backend will provide read-only Provider Registry metadata.

The registry must include at least `fake_local`, `douyin_sandbox`, and `douyin_real`.

Each provider descriptor must explicitly label `source_type`, `implementation_status`, `connection_status`, and capability metadata.

`fake_local` may be available, but it must be labeled as local fake/demo/test data only.

`douyin_sandbox` and `douyin_real` are placeholder metadata only in this batch. They must not implement real platform calls, OAuth, metrics fetching, uploading, publishing, scheduling, or credential storage.

Unimplemented capabilities must stay `false`. Future planning may be described only through `implementation_status` and `boundary_notes`, not through capability flags that imply availability.

Frontend and API consumers must not receive tokens, secrets, credentials, authorization codes, OAuth client secrets, raw provider responses, or credential material.

The registry must not read real secrets from environment variables, connect to the database, or call external services.

## Consequences

Future UI can use the read-only metadata to display provider, source, capability, and connection boundaries without implying real platform availability.

Future v0.9 Douyin Provider POC / Sandbox Integration must follow the source separation and capability metadata exposed by this registry.

This batch adds a backend-only read-only metadata API, but it does not mean OAuth, credential storage, token storage, real Douyin integration, or real metrics fetching is available.

## Non-Goals

- Do not connect to the real Douyin API.
- Do not implement OAuth.
- Do not add an OAuth callback route.
- Do not store access tokens.
- Do not store refresh tokens.
- Do not store API keys.
- Do not store secrets.
- Do not store credentials.
- Do not add a Credential model or database table.
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

## Provider Registry Boundary

Provider Registry is a backend-only source of truth for static provider metadata in this batch. It may describe available local fake behavior and future provider placeholders, but it must not act as a provider adapter.

Provider descriptors include provider id, provider name, provider type, source type, implementation status, connection status, availability, whether the provider is real, whether user authorization is required, capability metadata, and boundary notes.

The registry must not read environment variables, local credential files, database rows, OAuth state, tokens, or platform account data.

## Capability Metadata Boundary

Capability metadata must describe only currently available behavior.

For `fake_local`, metrics-read and publish-prepare metadata may be true only for local fake/demo/test workflows. Real publish, OAuth, token refresh, disconnect, revoke, and sandbox support remain false.

For `douyin_sandbox` and `douyin_real`, OAuth, metrics read, publish prepare, real publish, token refresh, disconnect, and revoke remain false in this batch. Sandbox support may be true only for the sandbox placeholder to indicate source type, not an implemented platform call.

Future plans must be expressed through `implementation_status` and `boundary_notes`, never by setting unimplemented capability flags to true.

## Source Separation

`fake_local`, `douyin_sandbox`, and `douyin_real` must be stable, distinguishable provider ids and source types.

`fake_local` must remain local fake/demo/test data and must not be described as real Douyin data.

`douyin_sandbox` must not be treated as `douyin_real`.

`douyin_real` must remain unavailable until explicit user authorization, credential boundaries, platform permissions, and real provider adapters are implemented in later batches.

## Security Requirements

- API responses must contain only non-sensitive metadata.
- API responses must not include token values, API keys, secrets, credentials, authorization codes, OAuth client secrets, raw provider responses, or credential material.
- Error responses must be useful for troubleshooting but must not echo sensitive input.
- The registry must not read, persist, log, or transform real credential material.
- Placeholder boundary notes may mention that OAuth is not implemented and tokens are not stored, but they must not include real values.

## API Boundary

The allowed API surface for this batch is read-only Provider Registry metadata:

- `GET /api/providers`
- `GET /api/providers/{provider_id}`

Unknown providers return `404` with a non-sensitive message such as `Provider not found`.

This batch must not add connect, callback, refresh, revoke, disconnect, OAuth, credential, publish, upload, scheduling, or metrics-sync routes.
