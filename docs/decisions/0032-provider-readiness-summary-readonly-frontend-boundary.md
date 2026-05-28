# ADR 0032: Provider Integration Readiness Summary Read-only Frontend Boundary

## Status

Accepted

## Context

v0.7.0 已完成 fake/local metrics review summary workflow。v0.8 Batch 1 已通过 ADR 0018 定义 Provider、Credential、OAuth、Secret、token lifecycle、安全审计、connection status 和 fake/sandbox/real source separation 边界。

v0.8 Batch 2 到 Batch 13 已完成 Provider Registry、Connection State、Credential Reference、Security Audit、OAuth Boundary、Token Lifecycle Boundary 的前后端只读 foundation。v0.8 Batch 14 已通过 ADR 0031 实现 backend-only Provider Integration Readiness Summary foundation。

本批在 Batch 14 的只读 API 之上增加 frontend read-only Provider Integration Readiness Summary UI。真实 Douyin POC 必须等 readiness summary 的前后端展示边界也能明确表达 blocking reasons、safe next steps 和 source separation 后再进入。

## Decision

Frontend 可以读取 `GET /api/provider-readiness-summaries`，但只能展示非敏感 provider readiness summary metadata。Frontend 必须显式展示 `source_type`、`implementation_status`、`overall_readiness_status`、`v0_9_poc_readiness_status`、`readiness_items`、`blocking_reasons`、`next_safe_steps`、`safe_summary` 和 boundary notes。

Frontend 必须区分 `fake_local`、`douyin_sandbox`、`douyin_real`。`fake_local` 的 `local_fake_ready` 只能展示为 local fake/demo/test workflow readiness，不得展示为真实 Douyin readiness。`douyin_sandbox` 和 `douyin_real` 只能展示为 placeholder / metadata-only / not ready，不得展示为真实 OAuth、真实 token lifecycle、真实 metrics 或真实 publish readiness。

Frontend 不新增 connect / authorize / OAuth start / callback / token exchange / refresh / revoke / disconnect / rotate / mark expired / upload / publish / schedule UI。Frontend 不新增 readiness approval、readiness override、production readiness certification 或 v0.9 POC start UI。

Frontend 不新增 secret input、token viewer、credential viewer、authorization code input、OAuth state input、raw request viewer、raw response viewer、raw payload viewer、token response viewer、refresh response viewer 或 revoke response viewer。

Frontend 不接收、不保存、不缓存、不展示 access token、refresh token、token value、secret、API key、authorization code、OAuth client secret、OAuth state value、credential material、private key、raw request、raw response、raw payload、token expiry value、token refresh response、token revoke response 或 provider token response。Readiness summary 只能展示为 review aid，不代表 production readiness certification 或 v0.9 POC 已完成。

## Consequences

用户和审查者可以在 UI 中看到 provider integration readiness summary、blocking reasons 和 next safe steps。

后续 v0.9 Douyin Provider POC 可以复用这套 UI 边界，但必须先更新 registry / connection state / credential reference / security audit / OAuth boundary / token lifecycle / readiness summary / capability metadata，并另行通过 ADR 和测试。

本批 UI 不代表 OAuth、token storage、token refresh、token revoke、disconnect、Credential storage、真实 Douyin、真实指标、真实发布、v0.9 POC 或 production readiness 可用。

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
- 不新增 readiness approval button。
- 不新增 readiness override button。
- 不新增 production certification UI。
- 不新增 v0.9 POC start UI。
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
- 不声明 production readiness。
- 不声明 v0.9 POC 已完成。
- 不修改 v0.7.0 release scope。

## Frontend Boundary

Provider Integration Readiness Summary UI 是全局只读审查面板，不依赖单个 project，也不新增写路由。它只能调用 Batch 14 的只读 readiness summary API，并把 backend 返回的非敏感 metadata 展示给用户和审查者。

该 UI 不改变 project、publishing、metrics、provider connection、credential、OAuth、token 或 readiness state。该 UI 也不修改 v0.7 fake/local metrics review summary workflow 语义。

## Readiness Summary Display Boundary

UI 可以展示 provider name、provider id、source type、implementation status、overall readiness status、v0.9 POC readiness status、local fake workflow flag、安全操作 flag、safe summary、readiness items、blocking reasons、next safe steps 和 boundary notes。

`metadata_ready_for_review` 只能展示为 review metadata ready，不得展示为 integration ready。`placeholder_not_ready`、`sandbox_placeholder_not_ready` 和 `real_placeholder_not_ready` 不得展示为 real provider ready、connected、authorized、token stored、real synced、published 或 production ready。

## v0.9 POC Readiness Display Boundary

`v0_9_poc_readiness_status` 只能帮助审查 v0.9 POC 的阻塞项和下一步，不表示 POC 已开始或已完成。`is_ready_for_v0_9_sandbox_poc=false` 和 `is_ready_for_v0_9_real_poc=false` 不得渲染为 Start POC、Run POC、Connect real provider 或任何可点击操作。

## Blocking Reasons Display Boundary

`blocking_reasons` 必须清晰展示真实 OAuth、callback route、OAuth state storage、credential storage、token lifecycle、real metrics fetching、upload、publish 和 scheduling 等缺失项，避免用户误以为 provider 已经 ready。

## Next Safe Steps Display Boundary

`next_safe_steps` 只能作为只读审查建议展示，例如复核 metadata、补充 v0.9 ADR、设计 sandbox/mock callback smoke test 或 encrypted credential storage。它不得变成可点击写操作，也不得暗示当前可以保存真实 token、尝试真实 OAuth、抓取真实指标或发布。

## Sensitive Value Display Boundary

UI 不得展示 access token、refresh token、token value、secret、API key、authorization code、OAuth client secret、OAuth state value、credential material、private key、raw request、raw response、raw payload、token expiry value、token refresh response、token revoke response 或 provider token response。

如果 backend 的 `source_metadata` 将来包含未知字段，frontend 必须保持 conservative display：只展示安全摘要或非敏感 key/value，过滤可承载敏感值的字段名和值模式。UI 不提供 raw payload viewer。

## Source Separation

UI 必须继续显式区分 `fake_local`、`douyin_sandbox` 和 `douyin_real`。`fake_local` 只代表 local fake/demo/test workflow readiness，不是真实 Douyin readiness。`douyin_sandbox` 只是 sandbox placeholder readiness，不代表真实 OAuth、真实 token lifecycle、真实 metrics 或真实 publish 可用，也不能被当成 `douyin_real`。`douyin_real` 只是 future real provider placeholder readiness，不代表真实 Douyin integration ready。

## Security Requirements

Frontend 不读取真实平台环境变量，不调用外部服务，不执行 OAuth，不生成 provider authorization URL，不执行 token exchange、token refresh、token revoke、disconnect 或 rotation。Frontend 不提供 readiness approval、override、certification 或 v0.9 POC start 操作。

Frontend API client 不得新增 create / update / delete readiness summary、approve readiness、override readiness、certify readiness、start OAuth、authorize provider、OAuth callback、connect provider、token exchange、refresh token、revoke token、disconnect provider、rotate token、mark token expired、credential save、credential read、token read、secret read、raw request read、raw response read 或 raw payload read function。

## Testing Requirements

Frontend tests must cover the read-only fetch call, loading state, error state, empty state, stable display of `fake_local` / `douyin_sandbox` / `douyin_real`, safe summary display, readiness items, blocking reasons, next safe steps, boundary notes, absence of sensitive field names or values, and absence of forbidden action buttons or inputs.

Project list tests must keep Provider Registry, Connection State, Credential Reference, Security Audit, OAuth Boundary, Token Lifecycle Boundary, and Readiness Summary panels visible without changing existing project list, archived checkbox, table, or empty-state semantics.
