# ADR 0031: Provider Integration Readiness Summary Backend Foundation

## Status

Accepted

## Context

v0.7.0 已完成 fake/local metrics review summary workflow。v0.8 Batch 1 已通过 ADR 0018 定义 Provider、Credential、OAuth、Secret、token lifecycle、安全审计、connection status 和 fake/sandbox/real source separation 边界。

v0.8 Batch 2 到 Batch 13 已完成 Provider Registry、Connection State、Credential Reference、Security Audit、OAuth Boundary、Token Lifecycle Boundary 的前后端只读 foundation。这些批次只建立真实平台接入前的 metadata、source separation、redaction 和 read-only display 边界，不代表真实 Douyin、真实 OAuth、真实 token lifecycle、真实指标读取或真实发布已经可用。

本批在这些边界之上增加 backend-only Provider Integration Readiness Summary foundation。真实 Douyin POC 必须等 readiness summary 也能明确表达 blocking reasons、safe next steps 和 source separation 后再进入。

## Decision

Backend 新增 backend-only provider readiness summary service，并新增只读 provider readiness summary API。本批不新增数据库表；readiness summary 必须由已有非敏感 metadata 计算得出。

Readiness summary 必须绑定 Provider Registry 中已知 provider。`source_type` 必须从 Provider Registry 派生，不信任调用方传入。`fake_local` 可显示 local fake workflow readiness，但不得显示为真实 Douyin readiness。`douyin_sandbox` 和 `douyin_real` 当前只能显示 placeholder / metadata-only / not ready 状态，不得显示为真实可用。

Readiness summary 必须包含 `overall_readiness_status`、`v0_9_poc_readiness_status`、`readiness_items`、`blocking_reasons`、`next_safe_steps`、`safe_summary` 和 `boundary_notes`，帮助后续 v0.9 POC 审查。API consumer 只能看到非敏感 readiness metadata、safe summary、readiness items、blocking reasons、next safe steps 和 boundary notes。

本批不新增任何对外写 API，不读取环境变量中的真实密钥，不调用外部服务，不实现 OAuth、token lifecycle 或 real provider workflow。

## Consequences

后续 UI 可以基于只读 readiness summary metadata 展示更明确的 v0.9 readiness 边界。

后续 v0.9 Douyin Provider POC 可以复用 readiness summary，但必须另行通过 ADR 和测试后才允许新增 provider adapter skeleton、mock/sandbox callback smoke test 或 real metrics POC。

本批新增 internal service 和只读 API，但不代表 OAuth、token storage、token refresh、token revoke、disconnect、Credential storage、真实 Douyin、真实指标或真实发布可用。Readiness summary 是 review aid，不是 production readiness certification。

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
- 不新增数据库表。
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
- 不声明 production readiness。
- 不修改 v0.7.0 release scope。

## Provider Readiness Summary Boundary

Provider readiness summary 是 backend-only computed metadata layer。它只聚合已存在的 provider metadata，并为每个 known provider 生成稳定、可审查、非敏感的 readiness summary。

`fake_local` 的 `overall_readiness_status` 可以表示 local fake/demo/test workflow 可用，但该状态只适用于本地 fake workflow，不得扩展为真实 Douyin readiness。`douyin_sandbox` 和 `douyin_real` 当前必须保持 placeholder / metadata-only / not ready 表达。

## Metadata Aggregation Boundary

Readiness summary 可以聚合 Provider Registry、Connection State、Credential Reference、Security Audit、OAuth Boundary 和 Token Lifecycle Boundary 的非敏感 metadata。它不得读取 token、refresh token、secret、API key、authorization code、OAuth client secret、OAuth state value、credential material、private key、raw request、raw response、raw payload、token expiry value、token refresh response、token revoke response 或 provider token response。

该服务不得新增数据库表，不保存 readiness state，不写入 provider registry，不修改 connection、credential、OAuth、token 或 publishing state。

## v0.9 POC Readiness Boundary

`v0_9_poc_readiness_status` 只能作为 review aid。它可以表达 `not_applicable_local_fake`、`blocked_missing_real_oauth`、`blocked_missing_token_lifecycle`、`blocked_missing_credential_storage`、`blocked_placeholder_only` 或 `metadata_ready_for_review` 等非敏感状态，但不得声明 v0.9 POC 已完成。

如果未来进入 v0.9 Douyin Provider POC，必须另行通过 ADR 和测试，明确 provider adapter skeleton、mock/sandbox callback smoke test、token storage、token lifecycle 和 metrics POC 边界。

## Blocking Reasons Boundary

`blocking_reasons` 必须解释为什么 provider 不能被视为真实集成 ready。对于 sandbox/real placeholder，blocking reasons 应明确 OAuth、callback route、OAuth state storage、credential storage、token lifecycle、real metrics fetching、upload、publish 和 scheduling 仍未实现。

`next_safe_steps` 只能描述安全审查和后续设计步骤，例如 review existing boundary metadata、separate v0.9 ADR、sandbox/mock callback smoke test plan 或 encrypted credential storage design。它不得暗示当前已经可以尝试真实 OAuth、保存真实 token、抓取真实指标或发布。

## Source Separation

Readiness summary 必须继续显式区分 `fake_local`、`douyin_sandbox` 和 `douyin_real`。Unknown provider rows or external inputs must not create readiness summaries.

`fake_local` 只能代表 local fake/demo/test data。`douyin_sandbox` 不能被当作 `douyin_real`。`douyin_real` 当前只能作为 future real provider placeholder，不得显示为 connected、authorized、token stored、token refreshed、real synced 或 published。

## API Boundary

Backend exposes only read-only provider readiness summary endpoints:

- `GET /api/provider-readiness-summaries`
- `GET /api/provider-readiness-summaries/{provider_id}`

Unknown provider IDs return a safe 404 message. The API must not add POST, PUT, PATCH or DELETE endpoints, and must not add connect, authorize, callback, refresh, revoke, disconnect, token exchange or credential write routes.

## Security Requirements

The service must not read environment variables for real platform secrets, local credential files, token files, raw provider responses or any external service. It must not call external services, execute OAuth, generate provider authorization URLs, exchange tokens, refresh tokens, revoke tokens, disconnect providers or rotate tokens.

API responses must not include sensitive field names or values such as access token, refresh token, token value, API key, secret value, client secret, OAuth client secret, authorization code, OAuth state value, callback payload, credential material, encrypted credential, private key, raw request, raw response, raw payload, token expiry value, token refresh response, token revoke response or provider token response.

## Testing Requirements

Tests must cover list and detail read-only routes, stable provider order, required readiness items, fake/sandbox/real source separation, required blocking reasons, safe next steps, safe 404 responses, absence of sensitive field names, absence of leaked environment values, absence of readiness persistence tables, and rejection of write methods.

Tests must also confirm the service does not read environment variables, does not call external services, does not execute OAuth, token exchange, token refresh, token revoke or disconnect, and does not add forbidden OAuth / token lifecycle / connect / callback routes.
