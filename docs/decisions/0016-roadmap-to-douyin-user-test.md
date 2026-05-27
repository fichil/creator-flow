# 0016 Roadmap from local fake metrics to Douyin user testing

## Status

Accepted

## Context

v0.6.0 has completed the local fake/manual metrics feedback loop. The current release supports `PublicationRecord` metrics snapshots, a backend fake metrics provider, metrics APIs, project detail metrics display, manual fake metrics generation, fake/local metrics boundary labels, and read-only archived projects.

The previous roadmap moved from v0.6 directly to v1.0, which left too little staged risk control before real platform integration. Douyin integration depends on platform availability, app review, OAuth behavior, token security, API permissions, provider capability differences, and user authorization.

The project must avoid presenting fake/local data as real platform performance, and it must preserve the human-in-the-loop publishing principle. Any real platform capability must be introduced through explicit authorization and security boundaries.

## Decision

Add v0.7, v0.8, and v0.9 as required stages before v1.0:

- v0.7 Metrics Review Summary turns existing fake/local metrics snapshots into content review summaries and human reference insights.
- v0.8 Provider & Credential Security Foundation defines Provider registry, credential boundaries, OAuth callback security, token lifecycle, provider capability metadata, audit log direction, and connection status direction.
- v0.9 Douyin Provider POC / Sandbox Integration validates the Douyin provider contract, sandbox/mock callback paths, account connection status, token refresh dry-run, and minimal metrics-reading feasibility.

Define v1.0 as Douyin Integration User Test Release, not as a production-grade automated publishing release. v1.0 may validate real Douyin metrics only when platform permissions and user authorization allow it. If Douyin API permissions are unavailable, v0.9 and v1.0 may use manual import or sandbox/mock provider contract tests as fallback.

Keep the fake/local workflow available as a fallback when no platform authorization exists, when platform permissions are unavailable, or when users only need local demonstration and testing.

All real platform capabilities must pass through explicit user authorization, source labeling, credential security boundaries, and Provider abstractions.

## Consequences

The roadmap becomes more stable and avoids prematurely promising real platform production capability.

Each future release has a clearer acceptance boundary:

- v0.7 validates review summary behavior using fake/local data.
- v0.8 validates security and Provider foundations before real integration.
- v0.9 exposes Douyin API permission, OAuth, token, and sandbox risks early.
- v1.0 keeps user testing scope controlled and avoids production-grade automation claims.

The project can continue to support the current local fake/manual workflow while gradually testing Douyin integration. Documentation and UI must continue to distinguish `fake_local`, `douyin_sandbox`, and `douyin_real` sources, and must not imply that sandbox, mock, or fake metrics are real platform performance.
