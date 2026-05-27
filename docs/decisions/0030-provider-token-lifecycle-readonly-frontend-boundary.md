# ADR 0030: Provider Token Lifecycle Boundary Read-only Frontend Boundary

## Status

Accepted

## Context

v0.7.0 已完成 fake/local metrics review summary workflow。v0.8 Batch 1 已通过 ADR 0018 定义 Provider、Credential、OAuth、Secret、token lifecycle、安全审计、connection status 和 fake/sandbox/real source separation 边界。

v0.8 Batch 2 已通过 ADR 0019 实现 backend-only Provider Registry & Capability Metadata foundation。Batch 3 已通过 ADR 0020 实现 frontend read-only Provider Registry UI boundary。Batch 4 已通过 ADR 0021 实现 backend-only Provider Connection State & Sensitive Storage Status foundation。Batch 5 已通过 ADR 0022 实现 frontend read-only Provider Connection State UI boundary。Batch 6 已通过 ADR 0023 实现 backend-only Provider Credential Reference & Secret Redaction foundation。Batch 7 已通过 ADR 0024 实现 frontend read-only Provider Credential Reference UI boundary。Batch 8 已通过 ADR 0025 实现 backend-only Provider Security Audit Event & Redacted Audit Log foundation。Batch 9 已通过 ADR 0026 实现 frontend read-only Provider Security Audit Event UI boundary。Batch 10 已通过 ADR 0027 实现 backend-only Provider OAuth State & Callback Boundary foundation。Batch 11 已通过 ADR 0028 实现 frontend read-only Provider OAuth Boundary UI foundation。Batch 12 已通过 ADR 0029 实现 backend-only Provider Token Lifecycle Boundary foundation。

本批在 Batch 12 的只读 API 之上增加 frontend read-only Provider Token Lifecycle Boundary UI。真实 Douyin POC 必须等 registry、capability、connection state、authorization status、sensitive storage status、credential reference、secret redaction、security audit event、OAuth state/callback boundary、token lifecycle boundary 和 source-separation 的前后端展示边界稳定后再进入。

## Decision

Frontend 可以读取 `GET /api/provider-token-lifecycle-boundaries`，但只能展示非敏感 provider token lifecycle boundary metadata。

Frontend 必须显式展示 `source_type`、`implementation_status`、`token_lifecycle_policy_status`、`token_storage_policy_status`、`refresh_policy_status`、`expiry_policy_status`、`revoke_policy_status`、`disconnect_policy_status`、`rotation_policy_status`、`error_redaction_policy_status`、`audit_event_policy_status`、`safe_status_message` 和 boundary notes。Frontend 必须区分 `fake_local`、`douyin_sandbox`、`douyin_real`。

`fake_local` 可展示为 local fake/demo/test workflow，token lifecycle not required，token storage / refresh / revoke / disconnect / rotation not required。`douyin_sandbox` 和 `douyin_real` 只能展示为 placeholder / not_implemented / required_planned，不得展示为可用真实 token lifecycle 集成。

`can_refresh_token`、`can_revoke_token`、`can_disconnect`、`can_rotate_token` 和 `can_mark_token_expired` 当前必须显示为不可执行。Frontend 不新增 connect / authorize / OAuth start / callback / token exchange / refresh / revoke / disconnect / rotate / mark expired / upload / publish / schedule UI。

Frontend 不新增 secret input、token viewer、credential viewer、authorization code input、OAuth state input、raw request viewer、raw response viewer、raw payload viewer、token response viewer、refresh response viewer 或 revoke response viewer。Frontend 不接收、不保存、不缓存、不展示 access token、refresh token、token value、secret、API key、authorization code、OAuth client secret、OAuth state value、credential material、private key、raw request、raw response、raw payload、token expiry value、token refresh response、token revoke response 或 provider token response。

`required_planned` 只能展示为 future planned boundary，不代表 token refresh / expiry / revoke / disconnect / rotation 已启用。`token_storage_policy_status` / `refresh_policy_status` / `revoke_policy_status` / `disconnect_policy_status` / `rotation_policy_status` 只能展示 metadata，不代表 token storage、refresh、revoke、disconnect 或 rotation 已实现。

## Consequences

用户和审查者可以在 UI 中看到 provider token lifecycle boundary。

后续 v0.9 Douyin Provider POC 可以复用这套 UI 边界，但必须先更新 registry / connection state / credential reference / security audit / OAuth boundary / token lifecycle / capability metadata 并另行通过 ADR 和测试。

本批 UI 不代表 OAuth、token storage、token refresh、token revoke、disconnect、Credential storage、真实 Douyin、真实指标或真实发布可用。

## Non-Goals

- 不接真实 Douyin API。
- 不实现 OAuth。
- 不新增 OAuth callback route。
- 不新增 OAuth state storage。
- 不新增 token exchange。
- 不生成真实 provider authorization URL。
- 不新增 connect / authorize button。
- 不新增 OAuth start button。
- 不新增 callback button。
- 不新增 token exchange button。
- 不新增 token refresh button。
- 不新增 token revoke button。
- 不新增 disconnect button。
- 不新增 rotate token button。
- 不新增 mark token expired button。
- 不新增 secret input。
- 不新增 token viewer。
- 不新增 credential management UI。
- 不新增 authorization code input。
- 不新增 OAuth state input。
- 不新增 raw request / raw response / raw payload viewer。
- 不新增 token response / refresh response / revoke response viewer。
- 不保存 access token。
- 不保存 refresh token。
- 不保存 token value。
- 不保存 API key。
- 不保存 secret。
- 不保存 authorization code。
- 不保存 OAuth client secret。
- 不保存 OAuth state value。
- 不保存 credential material。
- 不保存 private key。
- 不保存 raw request。
- 不保存 raw response。
- 不保存 raw payload。
- 不保存 token expiry value。
- 不保存 token refresh response。
- 不保存 token revoke response。
- 不保存 provider token response。
- 不新增 Credential model 或数据库表。
- 不新增 backend API。
- 不抓取真实指标。
- 不上传真实视频。
- 不真实发布。
- 不排期发布。
- 不做自动发布。
- 不做定时同步。
- 不调用外部服务。
- 不新增 Docker。
- 不新增 GitHub Actions。
- 不新增生产级 token lifecycle security module。
- 不修改 v0.7.0 release scope。

## Frontend Boundary

Provider Token Lifecycle Boundary UI 是只读全局 panel，不新增专门 route，不写入 token lifecycle metadata，也不改变 provider connection、authorization、credential、OAuth、token、publishing 或 real platform data state。

## Token Lifecycle Display Boundary

UI 可以展示 known provider token lifecycle boundary metadata、policy/status values 和 safe boundary notes，但不得展示真实 token lifecycle event、真实 token storage、真实 token refresh、真实 token revoke、真实 disconnect、真实 rotation 或真实 provider response。

## Token Storage Display Boundary

`token_storage_policy_status` 只能描述 token storage readiness。UI 不得显示 stored tokens、configured credentials、encrypted credential material、secret manager status、production KMS status 或 token viewer controls。

## Token Refresh Display Boundary

`refresh_policy_status` 和 `can_refresh_token` 只能说明 refresh 当前不可执行或未来计划。UI 不得渲染 Refresh Token button、refresh response viewer、refresh endpoint output、access token、refresh token 或 provider response data。

## Token Expiry Display Boundary

`expiry_policy_status` 和 `can_mark_token_expired` 只能说明 expiry handling 当前不可执行或未来计划。UI 不得显示 token expiry value，不得提供 Mark Token Expired button，也不得触发任何 expiry workflow。

## Token Revoke Display Boundary

`revoke_policy_status` 和 `can_revoke_token` 只能说明 revoke 当前不可执行或未来计划。UI 不得渲染 Revoke Token button、revoke response viewer 或 provider revoke response data。

## Disconnect Display Boundary

`disconnect_policy_status` 和 `can_disconnect` 只能说明 disconnect 当前不可执行或未来计划。UI 不得渲染 Disconnect button，不得改变 provider connection state，也不得调用任何 disconnect API。

## Token Rotation Display Boundary

`rotation_policy_status` 和 `can_rotate_token` 只能说明 rotation 当前不可执行或未来计划。UI 不得渲染 Rotate Token button，不得生成、读取、保存或展示任何 token material。

## Sensitive Value Display Boundary

Frontend API type 和 UI 不得新增可承载敏感值的字段或显示，例如 access token、refresh token、token value、API key、secret、authorization code、OAuth client secret、OAuth state value、credential material、private key、raw request、raw response、raw payload、token expiry value、token refresh response、token revoke response、provider token response、password、bearer token 或 session cookie。

## Source Separation

`fake_local` 是 local fake/demo/test data only，不是真实 Douyin data，不需要 OAuth，不保存 token 或 refresh token，不执行 token refresh、token revoke、disconnect 或 external service call。

`douyin_sandbox` 是 placeholder token lifecycle boundary metadata only。OAuth is not implemented，tokens and refresh tokens are not stored，token refresh / expiry handling / token revoke / disconnect are not active，no token exchange or real Douyin API call is made，and it cannot be treated as `douyin_real`。

`douyin_real` 是 future real provider token lifecycle boundary placeholder metadata only，不是真实 Douyin integration。OAuth、access token / refresh token storage、token refresh、token revoke、disconnect、real metrics fetching、upload、publish 和 scheduling 都未实现。

## Security Requirements

UI 必须只使用 backend 返回的 `safe_status_message`、policy/status metadata、boundary notes 和其他非敏感 token lifecycle boundary metadata。Error states 必须使用安全通用信息，不得回显可能包含敏感输入的 server detail。Frontend API type 不得新增敏感 carrier fields。

## Testing Requirements

Frontend tests 必须验证只读 API 调用、loading / success / error / empty states、`fake_local` / `douyin_sandbox` / `douyin_real` token lifecycle boundary metadata 展示、policy statuses 和 action booleans 均不可执行、safe status message 和 boundary notes 展示、敏感值和敏感 carrier fields 不显示，以及 absence of token lifecycle action buttons、credential inputs、authorization code inputs、OAuth state inputs、raw request viewers、raw response viewers、raw payload viewers、token response viewers、refresh response viewers 和 revoke response viewers。
