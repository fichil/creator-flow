# ADR 0029: Provider Token Lifecycle Boundary Backend Foundation

## Status

Accepted

## Context

v0.7.0 已完成 fake/local metrics review summary workflow。v0.8 Batch 1 已通过 ADR 0018 定义 Provider、Credential、OAuth、Secret、token lifecycle、安全审计、connection status 和 fake/sandbox/real source separation 边界。

v0.8 Batch 2 已通过 ADR 0019 实现 backend-only Provider Registry & Capability Metadata foundation。Batch 3 已通过 ADR 0020 实现 frontend read-only Provider Registry UI boundary。Batch 4 已通过 ADR 0021 实现 backend-only Provider Connection State & Sensitive Storage Status foundation。Batch 5 已通过 ADR 0022 实现 frontend read-only Provider Connection State UI boundary。Batch 6 已通过 ADR 0023 实现 backend-only Provider Credential Reference & Secret Redaction foundation。Batch 7 已通过 ADR 0024 实现 frontend read-only Provider Credential Reference UI boundary。Batch 8 已通过 ADR 0025 实现 backend-only Provider Security Audit Event & Redacted Audit Log foundation。Batch 9 已通过 ADR 0026 实现 frontend read-only Provider Security Audit Event UI boundary。Batch 10 已通过 ADR 0027 实现 backend-only Provider OAuth State & Callback Boundary foundation。Batch 11 已通过 ADR 0028 实现 frontend read-only Provider OAuth Boundary UI foundation。

本批在 Provider Registry、Connection State、Credential Reference、Secret Redaction、Security Audit 和 OAuth Boundary 基础上增加 backend-only Token Lifecycle Boundary metadata foundation。真实 Douyin POC 必须等 registry、capability、connection state、authorization status、sensitive storage status、credential reference、secret redaction、security audit event、OAuth state/callback boundary、token lifecycle boundary 和 source-separation 边界稳定后再进入。

## Decision

Backend 新增 metadata-only `provider_token_lifecycle_boundaries` table、backend-only provider token lifecycle boundary metadata service，以及只读 provider token lifecycle boundary metadata API。

Token lifecycle boundary metadata 必须绑定 Provider Registry 中已知 provider。`source_type` 必须从 Provider Registry 派生，不信任调用方传入。`fake_local` 是 local fake/demo/test workflow，不要求 token storage、refresh、expiry handling、revoke、disconnect 或 rotation。`douyin_sandbox` 和 `douyin_real` 当前只能是 token lifecycle boundary placeholder / not_implemented / required_planned，不得显示为真实可用。

`token_storage_policy_status` 只能描述 token storage 边界，不得保存 access token、refresh token 或 token value。`refresh_policy_status` 只能描述 refresh 边界，不得执行 token refresh。`expiry_policy_status` 只能描述 expiry handling 边界，不得保存真实 expiry value。`revoke_policy_status` 只能描述 revoke 边界，不得执行 revoke。`disconnect_policy_status` 只能描述 disconnect 边界，不得执行 disconnect。`rotation_policy_status` 只能描述 rotation 边界，不得执行 rotation。

API consumer 只能看到非敏感 metadata、policy statuses、`safe_status_message` 和 `boundary_notes`。本批不新增任何对外写 API，不读取环境变量中的真实密钥，不调用外部服务，不实现 token lifecycle operations。

## Consequences

后续 UI 可以基于只读 token lifecycle boundary metadata 展示更明确的 provider token lifecycle readiness 边界。

后续 v0.9 Douyin Provider POC 可以复用 token lifecycle boundary metadata，但必须另行通过 ADR 和测试后才允许新增 mock/sandbox token refresh dry-run 或真实 token lifecycle smoke test。

后续真实 token storage、refresh、expiry handling、revoke、disconnect 和 rotation 必须另行设计，不得把本批 metadata table 当作真实 token store 或 lifecycle executor。

本批新增 metadata-only DB table、internal service 和只读 API，但不代表 OAuth、token storage、token refresh、token revoke、disconnect、Credential storage、真实 Douyin、真实指标或真实发布可用。

## Non-Goals

- 不接真实 Douyin API。
- 不实现 OAuth。
- 不新增 OAuth callback route。
- 不新增 OAuth state storage。
- 不新增 token exchange。
- 不生成真实 provider authorization URL。
- 不新增 token refresh route。
- 不新增 token revoke route。
- 不新增 disconnect route。
- 不新增 connect / authorize / refresh / revoke / disconnect 写 API。
- 不保存 access token。
- 不保存 refresh token。
- 不保存 token value。
- 不保存 API key。
- 不保存 secret。
- 不保存 client secret。
- 不保存 authorization code。
- 不保存 OAuth client secret。
- 不保存 OAuth state value。
- 不保存 credential material。
- 不保存 encrypted credential。
- 不保存 private key。
- 不保存 raw request。
- 不保存 raw response。
- 不保存 raw payload。
- 不保存 token expiry value。
- 不保存 token refresh response。
- 不保存 token revoke response。
- 不保存 provider token response。
- 不新增真实 Credential storage。
- 不新增真实 Provider adapter。
- 不抓取真实指标。
- 不上传真实视频。
- 不真实发布。
- 不排期发布。
- 不做自动发布。
- 不做定时同步。
- 不调用外部服务。
- 不新增前端 UI。
- 不新增 Docker。
- 不新增 GitHub Actions。
- 不新增生产级 token lifecycle security module。
- 不修改 v0.7.0 release scope。

## Provider Token Lifecycle Boundary

Provider Token Lifecycle Boundary 是 backend-only metadata layer。它只描述 provider token lifecycle policy readiness，不改变连接状态、授权状态、credential 状态、token 状态、发布状态或真实平台数据状态。

## Token Storage Boundary

Token storage 当前只允许通过 `token_storage_policy_status` 表达 `none`、`planned`、`not_implemented` 或 `unavailable`。该 table、service 和 API 不保存 access token、refresh token、token value、token expiry value 或 provider token response。

## Token Refresh Boundary

`refresh_policy_status` 只能说明 refresh policy 是否不需要、计划中或未实现。本批不执行 token refresh，不读取 refresh token，不调用 provider refresh endpoint，也不保存 token refresh response。

## Token Expiry Boundary

`expiry_policy_status` 只能说明 expiry handling policy 是否不需要、计划中或未实现。本批不保存真实 token expiry value，不计算真实平台 token expiry，不触发过期处理 workflow。

## Token Revoke Boundary

`revoke_policy_status` 只能说明 revoke policy 是否不需要、计划中或未实现。本批不执行 token revoke，不调用 provider revoke endpoint，也不保存 token revoke response。

## Disconnect Boundary

`disconnect_policy_status` 只能说明 disconnect policy 是否不需要、计划中或未实现。本批不执行 disconnect，不改变 provider connection state，也不调用任何外部服务。

## Token Rotation Boundary

`rotation_policy_status` 只能说明 rotation policy 是否不需要、计划中或未实现。本批不执行 token rotation，不生成新 token，不读取或保存任何 credential material。

## Error Redaction Boundary

Token lifecycle boundary metadata 只能使用 safe status message 和 boundary notes。错误说明不得包含 token、secret、API key、authorization code、OAuth state value、credential material、raw request、raw response 或 raw payload。

## Source Separation

`fake_local` 只表示 local fake/demo/test workflow，不要求 token、refresh、revoke 或 disconnect。`douyin_sandbox` 只是 placeholder token lifecycle boundary metadata，不能当成 `douyin_real`。`douyin_real` 只是 future real provider placeholder，不代表真实 Douyin integration、真实 OAuth、真实 token lifecycle、真实指标读取或真实发布可用。

## API Boundary

API 只读暴露 `/api/provider-token-lifecycle-boundaries` 和 `/api/provider-token-lifecycle-boundaries/{provider_id}`。API 不新增 POST、PUT、PATCH、DELETE，不新增 token refresh route、token revoke route、disconnect route、connect route、authorize route、callback route 或 token read route。

## Security Requirements

Service 不读取环境变量，不读取本地凭据文件，不连接外部服务，不执行 OAuth，不生成 provider authorization URL，不执行 token exchange、token refresh、token revoke、disconnect 或 rotation。数据库字段和 API response 不得包含可承载敏感值的字段名。

## Testing Requirements

测试必须覆盖默认 metadata、source separation、未知 provider 忽略、合法 provider 非敏感 row 合并、只读 API、未知 provider 404、禁止写方法成功返回、环境变量假值不泄漏、表字段黑名单和现有 provider registry / connection / credential reference / security audit / OAuth boundary / redaction / fake workflow 测试继续通过。
