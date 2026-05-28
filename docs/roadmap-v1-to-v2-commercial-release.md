# Roadmap to v2.0 Commercial Release

This document is a planning artifact. It extends the roadmap from the released v0.9.0 Douyin Provider POC / Sandbox Integration baseline through v1.0 user testing, v1.5 Minimum Production Release, and v2.0 Multi-Tenant SaaS Commercial Release.

v1.0 is now in Batch 1 OAuth boundary / callback contract work. v1.5 and v2.0 remain future roadmap targets, and v1.0 contract planning does not make the current app production, commercial, or SaaS ready.

## Current Capability Boundary

Current v0.9.0 release capability remains POC-oriented:

- v0.9.0 establishes provider safety boundaries, sandbox-only deterministic workflows, registry / factory routing, POC readiness documentation, sandbox-only API contract, and frontend sandbox POC review surface.
- v0.9.0 does not provide production readiness, commercial readiness, real Douyin publish readiness, or SaaS readiness.
- v0.9.0 does not claim real OAuth, real token exchange, real credential storage, real metrics ingestion, real upload, real publishing, or scheduled publishing.
- v1.0 Batch 1 adds only OAuth boundary / callback contract documentation and does not implement any new runtime capability.

## Version Summary

| Version | Target | Commercial Boundary |
| --- | --- | --- |
| v0.9 | Douyin Provider POC / Sandbox Integration | Not commercial, not production, not SaaS |
| v1.0 | Douyin Integration User Test Release | Batch 1 OAuth contract started; small user test only |
| v1.1 | Real Integration Hardening | Not commercial launch |
| v1.2 | Publishing Workflow Beta | Controlled pilot only |
| v1.3 | Metrics & Feedback Beta | Controlled pilot only |
| v1.4 | Production Release Candidate | Pre-production gate |
| v1.5 | Minimum Production Release | Controlled direct-customer commercial use |
| v1.6 | SaaS Tenant Foundation | SaaS architecture foundation only |
| v1.7 | SaaS Access Control / Billing / Admin Foundation | SaaS operations foundation only |
| v1.8 | SaaS Reliability / Compliance / Operations | SaaS operational readiness only |
| v1.9 | Multi-Tenant SaaS Release Candidate | Pre-SaaS launch gate |
| v2.0 | Multi-Tenant SaaS Commercial Release | Customer-of-customer SaaS commercialization |

## v0.9 Douyin Provider POC / Sandbox Integration

Goal:

- Establish safe provider boundaries for Douyin integration work.
- Provide sandbox-only deterministic workflow, registry / factory routing, and readiness checklist coverage.
- Provide a sandbox-only backend API callable surface for frontend sandbox POC or smoke checks.
- Provide a frontend sandbox POC panel that displays deterministic simulated / dry-run provider descriptors, mock connection, metrics preview, and publish dry-run results.
- Provide an RC review package for human review / PR / merge / release decision.
- Prepare the contract surface for v1.0 user testing.

Non-Goals:

- Production readiness.
- Commercial readiness.
- Real Douyin publish readiness.
- SaaS readiness.
- Real OAuth, token exchange, credential storage, real metrics read, upload, publish, or scheduling.

Completion Standards:

- POC planning, adapter skeleton, sandbox operations, provider routing, and sandbox metrics / mock workflow POC are documented and tested.
- Sandbox API contract / smoke endpoints return deterministic sandbox / simulated / dry-run results only.
- Frontend sandbox POC panel displays sandbox / simulated / dry-run results only and does not provide real OAuth, upload, publish, scheduling, token, secret, or credential inputs.
- RC checklist, test matrix, validation script, and ADR 0043 are available for human review.
- `fake_local`, `douyin_sandbox`, and `douyin_real` remain separated.
- `douyin_real` remains blocked / not implemented until separate ADRs approve real integration.

Risks:

- Sandbox behavior may be mistaken for real platform behavior.
- Future real platform work may bypass provider security boundaries if not gated by ADR and tests.

Exit Conditions:

- v1.0 entry ADRs define real OAuth, callback, token lifecycle, credential storage, publish, metrics, and disablement boundaries.
- v0.9 documentation does not claim production, commercial, or SaaS readiness.
- v0.9 RC review leads to a human PR / merge / release decision; it does not automatically create tags or releases.

## v1.0 Douyin Integration User Test Release

Goal:

- Validate whether real Douyin authorization, publishing, status tracking, and minimum metrics read are feasible for a small user test.
- Require explicit user authorization and human-confirmed publishing.

Current Batch 1 Boundary:

- Batch 0 completed docs-only / planning-only release planning.
- Batch 1 is docs-only / contract-only OAuth boundary and callback contract work.
- Batch 1 is documented by [`decisions/0046-v1.0-oauth-boundary-callback-contract.md`](decisions/0046-v1.0-oauth-boundary-callback-contract.md) and [`contracts/v1.0-douyin-oauth-callback-contract.md`](contracts/v1.0-douyin-oauth-callback-contract.md).
- Batch 1 defines future authorization start, success callback, provider error callback, unsupported provider, cancelled authorization, malformed callback, missing state, replayed callback, expired callback, safe response categories, redaction rules, provider isolation, and dependency gates.
- Batch 1 does not implement real OAuth, OAuth URLs, callback routes, OAuth state storage, token exchange, token storage, credential storage, real provider calls, backend APIs, frontend OAuth UI, database changes, uploads, publishing, scheduling, or real metrics reads.
- Future callback routes must wait for Batch 2 state storage / anti-replay, token exchange must wait for Batch 3, credential storage must wait for Batch 4, and real OAuth runtime enablement must wait for Batch 5 feature flag / kill switch controls.
- Real implementation must wait for Douyin Open Platform app readiness, app review / approval, OAuth permission scope confirmation, callback URL confirmation, user authorization consent design, token lifecycle policy, encrypted credential storage design, platform error / rate limit policy, audit log design, and kill switch / feature flag design.

Suggested Capabilities:

- Real Douyin OAuth authorization flow.
- Safe OAuth callback.
- OAuth state replay protection.
- Token exchange and token lifecycle with encrypted storage or an accepted secure storage design.
- Credential reference without leaking real credentials into business tables.
- Minimum user-confirmed publish workflow.
- Publish status tracking.
- Minimum real metrics read under authorization and permission limits.
- Error handling, audit log, kill switch / feature flag, and strict sandbox / real provider separation.
- Documentation of platform limitations, app review status, permission constraints, and failure modes.

Non-Goals:

- Large-scale production commercial use.
- Public SLA commitments.
- Batch commercial publishing.
- Multi-tenant SaaS.
- Customer-of-customer onboarding.

Completion Standards:

- v1.0 readiness checklist is satisfied.
- Real OAuth, callback, token lifecycle, credential storage, publish, metrics, audit, and disablement paths have accepted ADRs and passing tests.
- Platform permission and review limitations are documented for user testers.

Risks:

- Douyin platform review, API permission, rate limit, or policy constraints may block user testing.
- Token lifecycle failures may interrupt account connection or publish status tracking.
- Real metrics may be delayed, partial, or unavailable depending on permissions.

Exit Conditions:

- User test acceptance criteria are met.
- Failure, rollback, and disablement criteria are documented and tested.
- Findings feed into v1.1 hardening.

## v1.1 Real Integration Hardening

Goal:

- Address OAuth, token, publish, metrics, and recovery issues discovered during v1.0 user testing.

Suggested Capabilities:

- OAuth and token lifecycle hardening.
- Token refresh.
- Credential rotation.
- Retry, backoff, and idempotency.
- Structured error model.
- Rate limit handling.
- Provider health checks.
- Audit trail.
- Manual recovery workflow.
- Integration test strategy.
- Security regression tests.

Non-Goals:

- Broad commercial launch.
- SaaS multi-tenancy.
- Automated publishing without human confirmation.

Completion Standards:

- Known v1.0 failure modes have documented mitigations.
- Token refresh, retry, rate limit, and manual recovery paths have tests.
- Security regression tests cover real integration boundaries.

Risks:

- Provider instability may require more defensive workflows.
- Hardening can expand scope without explicit release criteria.

Exit Conditions:

- Real integration paths are stable enough to support publishing beta planning.

## v1.2 Publishing Workflow Beta

Goal:

- Move toward a controlled real publishing workflow beta while retaining human confirmation.

Suggested Capabilities:

- User-confirmed publish queue.
- Publish preflight validation.
- Media asset readiness checks.
- Status reconciliation.
- Duplicate publish prevention.
- Strong link between review queue and publish intent.
- Rollback / compensation documentation; if the platform does not support rollback, document that limitation.
- Publish result observability.

Non-Goals:

- Default automatic publishing.
- Uncontrolled batch publishing.
- Multi-tenant SaaS release.

Completion Standards:

- Preflight, duplicate prevention, publish intent, status reconciliation, and observability have tests.
- Human-in-the-loop publishing remains enforced.

Risks:

- Platform publish semantics may not support reliable rollback.
- Duplicate prevention must handle retries and uncertain provider responses.

Exit Conditions:

- Publishing workflow beta results are accepted for metrics feedback beta planning.

## v1.3 Metrics & Feedback Beta

Goal:

- Add controlled real metrics feedback for post-publish review without unsupported performance claims.

Suggested Capabilities:

- Real metrics ingestion.
- Metrics sync schedule.
- Metrics freshness display.
- Metrics permission boundary.
- Platform response redaction.
- Metrics review summary from real metrics.
- Clear separation between fake/local metrics and real metrics.
- No unsupported growth or performance claims.

Non-Goals:

- Guaranteed growth outcomes.
- Metrics-driven automatic publishing.
- SaaS tenant analytics.

Completion Standards:

- Metrics ingestion, freshness, permission, redaction, and review summary behavior have tests.
- Real metrics and fake/local metrics remain visibly separated.

Risks:

- Metrics availability and freshness depend on provider permissions and platform behavior.
- Users may overinterpret metrics summaries as performance guarantees.

Exit Conditions:

- Metrics beta output is reliable enough for production release candidate planning.

## v1.4 Production Release Candidate

Goal:

- Complete the final safety, reliability, deployment, operations, support, and compliance gates before v1.5.

Suggested Capabilities:

- Production deployment checklist.
- Backup / restore.
- Monitoring / alerting.
- Incident response runbook.
- Privacy and data retention documentation.
- Access control.
- Admin operations.
- Support workflow.
- Release rollback plan.
- Performance baseline.
- Security review.
- Dependency and security scanning.
- Final customer acceptance checklist.

Non-Goals:

- Multi-tenant SaaS commercialization.
- Customer-of-customer onboarding.
- Unbounded scale or SLA promises.

Completion Standards:

- Production release candidate checklist is complete.
- Operational and support runbooks have owners and validation evidence.
- Security and privacy review is complete.

Risks:

- Deployment or operational gaps may delay v1.5.
- Support boundaries may be unclear without commercial contract review.

Exit Conditions:

- v1.5 acceptance criteria are ready for controlled direct-customer commercial use.

## v1.5 Minimum Production Release

Goal:

- Provide a Minimum Production Release for controlled direct-customer commercial use.
- Support managed deployment, single-tenant deployment, limited production, or pilot commercial contracts.

Commercial Boundary:

- v1.5 can target direct customer use after readiness criteria are met.
- v1.5 requires contract, acceptance, and support boundaries.
- v1.5 requires production deployment documentation, security and privacy boundaries, backup and restore, monitoring and alerting, customer data isolation explanation, human review and publish confirmation, and clear platform dependency disclosure.
- Douyin platform policy, open capabilities, review status, and API limits remain outside full project control.

Non-Goals:

- Multi-tenant SaaS.
- Customer-of-customer self-service onboarding.
- White-label, reseller, or marketplace capability.
- Unlimited scale or SLA commitments unless later documentation and contracts establish them.

Completion Standards:

- v1.5 readiness checklist is satisfied.
- Production deployment, customer acceptance, support, security, privacy, backup, monitoring, incident response, provider reliability, publish reliability, metrics reliability, and legal / commercial boundaries are documented and tested.

Risks:

- Direct customer deployment may require managed operations that are not reusable for SaaS.
- Provider policy and permission changes may affect production commitments.

Exit Conditions:

- Direct customer production usage is accepted under controlled commercial terms.
- Gaps for multi-tenant SaaS are explicitly handed to v1.6 through v2.0 work.

## v1.6 SaaS Tenant Foundation

Goal:

- Establish the technical foundation for multi-tenant SaaS after v1.5 direct-customer production readiness.

Suggested Capabilities:

- Tenant model.
- Organization model.
- Workspace model.
- Tenant-aware project ownership.
- Tenant-scoped provider connection.
- Tenant-scoped credential reference.
- Tenant data isolation rules.
- Tenant-aware audit logs.
- Migration plan from v1.5 deployments.

Non-Goals:

- SaaS commercial launch.
- Billing or plan enforcement.
- Customer-of-customer self-service commercialization.

Completion Standards:

- Tenant-aware ownership, provider connection, credential reference, and audit boundaries have ADRs, migrations, and tests.
- Migration path from v1.5 deployments is documented.

Risks:

- Retrofitting tenancy can affect every data boundary.
- Credential and audit scopes must not leak across tenants.

Exit Conditions:

- Tenant foundation is accepted for access control, billing, and admin foundation work.

## v1.7 SaaS Access Control / Billing / Admin Foundation

Goal:

- Add the operational controls required for SaaS access, entitlement, billing, and administration.

Suggested Capabilities:

- RBAC.
- Organization roles.
- Customer admin role.
- Internal operator role.
- Tenant admin console.
- Plan / entitlement model.
- Billing integration boundary.
- Invoice / subscription placeholder or real integration plan.
- Usage limits.
- Quota enforcement.
- Support impersonation policy, defaulting to disallowed unless implemented with strong audit.

Non-Goals:

- Full SaaS launch before reliability, compliance, operations, and release candidate gates.
- Ungated support impersonation.

Completion Standards:

- RBAC, entitlement, billing boundary, usage limits, quota enforcement, admin operations, and support policy have tests and documentation.

Risks:

- Access control mistakes can create tenant data leaks.
- Billing integration scope can expand beyond core readiness.

Exit Conditions:

- Access, billing, and admin foundation is ready for SaaS reliability and operations work.

## v1.8 SaaS Reliability / Compliance / Operations

Goal:

- Build the reliability, compliance, and operations layer required before multi-tenant SaaS release candidate work.

Suggested Capabilities:

- Tenant-level monitoring.
- Tenant-level audit export.
- Data retention policy.
- Data deletion policy.
- Privacy policy support docs.
- Incident response by tenant.
- Operational runbooks.
- Scaling plan.
- Background job isolation.
- Rate limiting.
- Abuse prevention.
- Platform policy compliance workflow.

Non-Goals:

- Final SaaS commercial release.
- Broad customer-of-customer onboarding before release candidate acceptance.

Completion Standards:

- Tenant-level monitoring, audit export, data retention, deletion, privacy docs, incident response, scaling, job isolation, rate limiting, abuse prevention, and platform compliance workflows have validation evidence.

Risks:

- Operations gaps may affect all tenants.
- Compliance requirements may vary by customer segment or jurisdiction.

Exit Conditions:

- Reliability and operations gates are ready for v1.9 release candidate.

## v1.9 Multi-Tenant SaaS Release Candidate

Goal:

- Validate tenant isolation, customer organization operations, customer-of-customer access, billing, support, and operations before v2.0.

Suggested Capabilities:

- SaaS acceptance checklist.
- Tenant isolation verification.
- Customer-of-customer access model.
- End-user onboarding model.
- Commercial support workflow.
- SLA readiness.
- Pricing / package documentation.
- Customer data processing documentation.
- Production migration plan.
- Load / performance validation.
- Final legal / compliance review checklist.

Non-Goals:

- v2.0 launch before final legal, support, SLA, security, and operational readiness are accepted.

Completion Standards:

- SaaS acceptance checklist is complete.
- Tenant isolation, onboarding, billing, support, SLA, pricing, data processing, migration, load, security, and compliance evidence is ready for launch review.

Risks:

- Tenant isolation, billing, or support gaps can block launch.
- Platform policy changes may require release candidate updates.

Exit Conditions:

- v2.0 launch criteria are accepted.

## v2.0 Multi-Tenant SaaS Commercial Release

Goal:

- Support multi-tenant SaaS commercialization in which customers can offer the service to their own customers.

Commercial Boundary:

- v2.0 is the target stage for customer-of-customer SaaS commercialization.
- v2.0 requires explicit tenant / customer / customer-of-customer data boundaries.
- v2.0 requires strong tenant isolation, RBAC and organization management, audit logs, billing / plan / usage limits, production SLA and support workflow, security response process, compliance and data processing documentation, operations admin console, scalable deployment and monitoring, real provider security audit, and ongoing platform policy / permission / API limit compliance checks.

Non-Goals:

- Treating v0.9, v1.0, or v1.5 as already sufficient for customer-of-customer SaaS commercialization.
- Bypassing tenant isolation, RBAC, billing, audit, support, SLA, compliance, or operations gates.

Completion Standards:

- v2.0 readiness checklist is satisfied.
- Customer-of-customer onboarding, tenant isolation, provider credentials, audit, RBAC, billing, quotas, support, SLA, compliance, data export / deletion, monitoring, incident response, scalability, and commercial launch criteria have validation evidence.

Risks:

- SaaS commercialization increases blast radius across tenant data, provider credentials, billing, support, and compliance.
- Douyin and other platform policy, permission, and API limitations require ongoing review.

Exit Conditions:

- v2.0 release review accepts the full Multi-Tenant SaaS Commercial Release boundary.

## Cross-Cutting Principles

- Fake/local, sandbox, and real provider sources must remain separated.
- Sandbox data must never be represented as real platform data.
- Real OAuth, token exchange, credential storage, real provider calls, real metrics read, upload, publish, and scheduling require separate ADRs, tests, and security scans.
- Human-in-the-loop publishing remains required unless a future accepted ADR explicitly changes a narrower workflow with appropriate safeguards.
- Roadmap documentation is not a production, commercial, or SaaS readiness declaration.
