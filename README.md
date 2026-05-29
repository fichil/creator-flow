# creator-flow

[简体中文](README.md) | [English](README.en.md)

creator-flow 是一个可开源的 AI 短视频内容流水线，帮助用户将显式导入的想法、聊天摘要、文本、图片、截图和链接转化为待审核的短视频草稿。

## 当前状态

`v1.0 Batch 3 - Token Exchange Boundary With Fake-Gated Integration`

当前仓库已完成 v0.1 本地可运行骨架、v0.2 AI Planning Workflow、v0.3 fake rendering/subtitle/preview workflow、v0.4 local fake/manual Scheduled Draft Generation workflow、v0.5 Human-Confirmed Publishing Workflow、v0.6.0 local fake/manual metrics feedback workflow、v0.7.0 Metrics Review Summary local fake/manual workflow、v0.8.0 Provider & Credential Security Foundation，以及 v0.9.0 Douyin Provider POC / Sandbox Integration。v0.9.0 已从 release commit `0f5263452b65077f2c70c82e506944dd46e60e96` 发布为 POC / Sandbox Integration release。

本地开发说明见 [`docs/development.md`](docs/development.md)，v0.5 发布候选验收清单见 [`docs/releases/v0.5-rc-checklist.md`](docs/releases/v0.5-rc-checklist.md)，v0.6.0 metrics release checklist 见 [`docs/checklists/v0.6-metrics-feedback-loop-rc.md`](docs/checklists/v0.6-metrics-feedback-loop-rc.md)，v0.7 metrics review summary RC checklist 见 [`docs/checklists/v0.7-metrics-review-summary-rc.md`](docs/checklists/v0.7-metrics-review-summary-rc.md)，v0.8 Provider & Credential Security Foundation RC audit checklist 见 [`docs/checklists/v0.8-provider-security-foundation-rc.md`](docs/checklists/v0.8-provider-security-foundation-rc.md)，v0.8.0 release notes 见 [`docs/releases/v0.8.0-provider-security-foundation.md`](docs/releases/v0.8.0-provider-security-foundation.md)。v0.9 Batch 0 的 planning checklist 见 [`docs/checklists/v0.9-douyin-provider-poc-readiness.md`](docs/checklists/v0.9-douyin-provider-poc-readiness.md)，entry ADR 见 [`docs/decisions/0035-v0.9-douyin-provider-poc-sandbox-entry.md`](docs/decisions/0035-v0.9-douyin-provider-poc-sandbox-entry.md)。v0.9 Batch 1 adapter skeleton ADR 见 [`docs/decisions/0036-v0.9-douyin-provider-adapter-skeleton.md`](docs/decisions/0036-v0.9-douyin-provider-adapter-skeleton.md)，Batch 2 sandbox ops ADR 见 [`docs/decisions/0037-v0.9-douyin-provider-sandbox-ops.md`](docs/decisions/0037-v0.9-douyin-provider-sandbox-ops.md)，Batch 3 registry routing ADR 见 [`docs/decisions/0038-v0.9-douyin-provider-registry-routing.md`](docs/decisions/0038-v0.9-douyin-provider-registry-routing.md)，Batch 4 sandbox metrics / mock workflow ADR 见 [`docs/decisions/0039-v0.9-douyin-provider-sandbox-metrics-poc.md`](docs/decisions/0039-v0.9-douyin-provider-sandbox-metrics-poc.md)，Batch 5 roadmap alignment ADR 见 [`docs/decisions/0040-v0.9-roadmap-to-v2-commercial-release.md`](docs/decisions/0040-v0.9-roadmap-to-v2-commercial-release.md)，Batch 6 sandbox API contract ADR 见 [`docs/decisions/0041-v0.9-douyin-sandbox-api-contract.md`](docs/decisions/0041-v0.9-douyin-sandbox-api-contract.md)，Batch 7 frontend sandbox POC ADR 见 [`docs/decisions/0042-v0.9-douyin-frontend-sandbox-poc.md`](docs/decisions/0042-v0.9-douyin-frontend-sandbox-poc.md)，Batch 8 readiness finalization ADR 见 [`docs/decisions/0043-v0.9-poc-readiness-finalization.md`](docs/decisions/0043-v0.9-poc-readiness-finalization.md)。v0.9 RC checklist 见 [`docs/releases/v0.9-douyin-provider-poc-rc-checklist.md`](docs/releases/v0.9-douyin-provider-poc-rc-checklist.md)，v0.9 test matrix 见 [`docs/testing/v0.9-douyin-provider-poc-test-matrix.md`](docs/testing/v0.9-douyin-provider-poc-test-matrix.md)。v1.0 到 v2.0 商用路线详见 [`docs/roadmap-v1-to-v2-commercial-release.md`](docs/roadmap-v1-to-v2-commercial-release.md)，对应 readiness checklist 见 [`docs/checklists/v1.0-douyin-user-test-release-readiness.md`](docs/checklists/v1.0-douyin-user-test-release-readiness.md)、[`docs/checklists/v1.5-minimum-production-release-readiness.md`](docs/checklists/v1.5-minimum-production-release-readiness.md) 和 [`docs/checklists/v2.0-multi-tenant-saas-commercial-release-readiness.md`](docs/checklists/v2.0-multi-tenant-saas-commercial-release-readiness.md)。

v0.9 Batch 9 的 release / PR merge preparation ADR 见 [`docs/decisions/0044-v0.9-release-merge-preparation.md`](docs/decisions/0044-v0.9-release-merge-preparation.md)，PR 描述草案见 [`docs/releases/v0.9-pr-description-draft.md`](docs/releases/v0.9-pr-description-draft.md)，release notes 草案见 [`docs/releases/v0.9-release-notes-draft.md`](docs/releases/v0.9-release-notes-draft.md)，merge readiness checklist 见 [`docs/releases/v0.9-merge-readiness-checklist.md`](docs/releases/v0.9-merge-readiness-checklist.md)，tag readiness checklist 见 [`docs/releases/v0.9-tag-readiness-checklist.md`](docs/releases/v0.9-tag-readiness-checklist.md)。v1.0 Batch 0 的规划 ADR 见 [`docs/decisions/0045-v1.0-douyin-user-test-release-planning.md`](docs/decisions/0045-v1.0-douyin-user-test-release-planning.md)，规划文档见 [`docs/plans/v1.0-douyin-user-test-release-plan.md`](docs/plans/v1.0-douyin-user-test-release-plan.md)。v1.0 Batch 1 的 OAuth boundary / callback contract ADR 见 [`docs/decisions/0046-v1.0-oauth-boundary-callback-contract.md`](docs/decisions/0046-v1.0-oauth-boundary-callback-contract.md)，callback contract 见 [`docs/contracts/v1.0-douyin-oauth-callback-contract.md`](docs/contracts/v1.0-douyin-oauth-callback-contract.md)，contract test matrix 见 [`docs/testing/v1.0-oauth-callback-contract-test-matrix.md`](docs/testing/v1.0-oauth-callback-contract-test-matrix.md)。v1.0 Batch 2 的 OAuth state storage / anti-replay ADR 见 [`docs/decisions/0047-v1.0-oauth-state-storage-anti-replay.md`](docs/decisions/0047-v1.0-oauth-state-storage-anti-replay.md)，state storage contract 见 [`docs/contracts/v1.0-douyin-oauth-state-storage-contract.md`](docs/contracts/v1.0-douyin-oauth-state-storage-contract.md)，state storage test matrix 见 [`docs/testing/v1.0-oauth-state-storage-test-matrix.md`](docs/testing/v1.0-oauth-state-storage-test-matrix.md)。v1.0 Batch 3 的 token exchange boundary ADR 见 [`docs/decisions/0048-v1.0-token-exchange-boundary-fake-gated.md`](docs/decisions/0048-v1.0-token-exchange-boundary-fake-gated.md)，token exchange boundary contract 见 [`docs/contracts/v1.0-douyin-token-exchange-boundary-contract.md`](docs/contracts/v1.0-douyin-token-exchange-boundary-contract.md)，test matrix 见 [`docs/testing/v1.0-token-exchange-boundary-test-matrix.md`](docs/testing/v1.0-token-exchange-boundary-test-matrix.md)。

v0.9.0 仍不接真实 Douyin，不实现 OAuth，不新增真实 OAuth callback route，不新增 OAuth state storage，不新增 token exchange，不生成真实 provider authorization URL，不保存 token、secret、API key、credential、authorization code 或 OAuth state，不抓取真实指标，不上传、不发布、不排期发布，也不调用外部服务。v0.9.0 是 POC / Sandbox Integration release，不是 production-ready real Douyin integration，也不是生产部署版本。

当前 v1.0 工作线基于 v0.9.0 release commit `0f5263452b65077f2c70c82e506944dd46e60e96`。v1.0 已推进到 Batch 3 token exchange boundary / fake-gated integration 阶段，用于在 Batch 2 state foundation 之后建立 internal-only token exchange boundary；本阶段仍未开始真实 OAuth、真实 token exchange、credential storage、real provider、publish workflow 或 metrics read 实现。当前仓库仍不接真实 Douyin，不实现 OAuth，不保存 token，不抓取真实指标，不上传、不发布、不排期发布，也不适合作为生产级真实平台集成使用。

v1.0 Batch 3 只新增 internal-only token exchange boundary service、fake-gated exchange simulator、state dependency / replay / expiry / provider isolation 测试和对应文档。Batch 3 不创建 OAuth URL，不新增 OAuth start route，不新增 OAuth callback route，不做真实 token exchange，不保存 token / secret / credential / authorization code / raw OAuth state / OAuth state value，不新增 frontend OAuth UI，不调用 Douyin API 或业务外部服务。后续真实能力必须等平台权限、应用审核、用户授权和单独 ADR / tests / security scan 完成后才能实现。v1.0 不是生产商用版本，不等于 v1.5 Minimum Production Release，也不等于 v2.0 Multi-Tenant SaaS Commercial Release。

## 后续路线

当前已发布版本是 `v0.9.0 - Douyin Provider POC / Sandbox Integration`。v1.0 已进入 Douyin Integration User Test Release 的 Batch 3 token exchange boundary / fake-gated integration 阶段，但尚未开始真实 OAuth runtime 或真实 token exchange。后续路线从 v1.0 小范围用户测试逐步扩展到 v1.5 直接客户受控商用目标，再到 v2.0 面向客户的客户 SaaS 商用目标：

- v0.8.0 Provider & Credential Security Foundation（已发布）：Batch 1-16 已完成 Provider、Credential、OAuth、Secret、token lifecycle、安全审计、source separation、Provider Registry、Connection State、Credential Reference、Security Audit、OAuth Boundary、Token Lifecycle Boundary、Integration Readiness Summary、对应 frontend read-only UI panels、RC checklist 和 closure audit。该 release 只提供 metadata-only / read-only security foundation：不接真实 Douyin、不实现 OAuth、不新增 OAuth callback route、不新增 OAuth state storage、不新增 token exchange、不生成真实 provider authorization URL、不保存 token / secret / API key / credential / authorization code / OAuth state、不抓取真实指标、不上传、不发布、不排期发布、不调用外部服务，也不声明 production-ready real Douyin integration。
- v0.9 Douyin Provider POC / Sandbox Integration（已发布为 v0.9.0）：Batch 0-9 已完成 POC planning、adapter skeleton、sandbox-only deterministic operations、provider registry / factory routing、sandbox metrics / mock workflow、roadmap alignment、sandbox-only backend API contract、frontend sandbox POC panel、RC readiness package 和 release preparation package。v0.9.0 仍不是商用版本，不是真实 provider integration，不调用真实 Douyin API，不实现 OAuth，不创建 OAuth URL，不新增 OAuth callback route，不交换或保存 token，不抓取真实指标，不上传、不发布、不排期发布。
- v1.0 Douyin Integration User Test Release：当前进入 Batch 3 token exchange boundary / fake-gated integration，用于在 Batch 2 state foundation 后建立 metadata-only fake-gated exchange boundary、real provider disabled、sandbox fallback forbidden 和 no token material returned / persisted 基础。目标仍是验证真实 Douyin 授权、发布、状态查询和最小指标回流是否可行；本批不实现真实 OAuth runtime 或真实 token exchange。v1.0 不是生产商用版本，也不承诺 SLA、批量商用或多租户 SaaS。
- v1.1-v1.4：未来依次进行 Real Integration Hardening、Publishing Workflow Beta、Metrics & Feedback Beta 和 Production Release Candidate，为 v1.5 前的安全、可靠性、部署、运营、支持与合规门槛做准备。
- v1.5 Minimum Production Release：未来目标版本，可在 readiness criteria 满足后面向直接客户做受控商用，适合 managed / single-tenant / controlled deployment 或 pilot commercial contract。v1.5 不等于多租户 SaaS，不默认允许客户的客户直接入驻使用，也不承诺 white-label / reseller / marketplace 能力或无限规模 SLA。
- v1.6-v1.9：未来逐步建立 SaaS Tenant Foundation、SaaS Access Control / Billing / Admin Foundation、SaaS Reliability / Compliance / Operations 和 Multi-Tenant SaaS Release Candidate。
- v2.0 Multi-Tenant SaaS Commercial Release：未来目标版本，面向客户的客户进行 SaaS 商用，需要多租户、组织、客户、客户的客户、权限、审计、计费、SLA、运营后台、合规与生产支持能力。

真实 Douyin 接入仍取决于平台开放能力、应用审核、OAuth、API 权限与用户授权。README 中的后续路线是计划和 readiness target，不表示当前已经接入真实抖音，也不表示已经具备真实 OAuth、token storage、真实指标抓取、真实发布、自动发布、批量发布、定时发布、生产级平台 dashboard、v1.5 直接客户受控商用能力或 v2.0 多租户 SaaS 商用能力。

## 本地启动快捷入口

在 Windows PowerShell 中，可以从仓库根目录运行：

```powershell
.\scripts\dev-backend.ps1
```

另开一个 PowerShell：

```powershell
.\scripts\dev-frontend.ps1
```

常用验证命令：

```powershell
.\scripts\test-backend.ps1
.\scripts\build-frontend.ps1
.\scripts\smoke-api.ps1
.\scripts\validate-v0.9-poc.ps1
```

## 计划能力

- 用户显式导入聊天摘要、文本、图片、截图和链接。
- 通过 Provider 边界生成选题、脚本、分镜、字幕和素材方案。
- 通过 `FFmpeg` 流水线生成适合短视频平台发布的 9:16 MP4。
- 支持配置内容计划、账号定位、内容类型和生成频率。
- 按计划基于显式导入素材与可选热点信号自动生成待审核草稿。
- 将自动生成的视频项目放入 `Review Queue`，由用户审核后继续处理。
- 发布后指标回流，用于后续内容复盘和选题优化。
- 以抖音作为首个发布平台，同时通过 Provider 抽象保留多平台扩展能力。

其中 Topic Candidate、Script Draft 和 Storyboard 的生成与选择已在 v0.2 中以本地 fake provider 形式实现；v0.3 已完成 fake render job、fake preview manifest metadata 展示、fake subtitle draft 和 subtitle cues 的 RC 收口；v0.4 已完成 ContentPlan、GenerationSchedule、fake manual GenerationRun 和 Review Draft placeholder 的 RC 收口；v0.5 已完成 PublishIntent / PublicationRecord 后端基础、confirm workflow foundation、fake publisher execution foundation、项目详情页本地 fake publishing workflow、RC checklist、final validation 和 v0.5.0 release。v0.6.0 已完成 Metrics Feedback Loop 边界文档、backend-only fake metrics domain foundation、项目详情页 fake metrics UI foundation、metrics workflow RC checklist 和 release finalization。v0.7.0 已完成 backend-only fake/local metrics review summary foundation、项目详情页 fake/local metrics review summary UI foundation、workflow stabilization、RC checklist 和 release finalization。真实 AI、真实字幕文件、真实音频、素材方案、真实 MP4 渲染与播放、真实 OAuth、真实上传、真实发布、token 保存、自动发布、排期发布、真实 Douyin API、真实 PublisherProvider、真实指标抓取、定时指标同步、数据分析推荐算法、真实平台 dashboard、scheduled GenerationRun、Scheduler / Trigger Engine 和完整 Review Queue 仍属于后续计划方向。

## 当前本地能力

- 本地启动 backend 和 frontend。
- 创建 `ContentProject`。
- 向指定项目显式添加文本、摘要、项目记录、链接、图片和截图素材。
- 查看项目列表、项目详情和素材列表。
- 基于显式导入素材生成并选择 Topic Candidate。
- 基于 selected Topic Candidate 生成并选择 Script Draft。
- 基于 selected Topic Candidate、selected Script Draft 和显式导入素材生成 Storyboard，并查看有序 scenes。
- 基于 selected Storyboard 创建 fake render job，并保存 deterministic fake preview manifest metadata；项目详情页可以展示这些 metadata，但不会读取运行时 manifest 文件或播放真实视频，也不会生成真实 MP4 文件。
- 基于 selected Storyboard 创建 fake subtitle draft，并保存 deterministic subtitle cues metadata；当前不会生成真实 `.srt` / `.vtt` 文件、音频或视频。
- 创建和查看 `ContentPlan`，配置账号定位、内容类型、每周目标频率和偏好文本，并启用或停用计划。
- 创建和查看绑定到 `ContentPlan` 的 `GenerationSchedule` 配置，并启用或停用计划；当前不会执行 scheduled trigger。
- 手动创建 fake `GenerationRun`，并同步创建待审核的 `Review Draft` placeholder；项目详情页会刷新 GenerationRuns 与 Review Drafts。
- 查看 `Review Draft` placeholder，并执行 approve / reject 状态变更；该操作不会发布、上传、渲染或生成媒体。
- 在项目详情页基于同一项目内已 approved 的 `Review Draft` 显式创建 `PublishIntent`，查看发布意图列表与状态，并取消待确认发布意图。
- 在项目详情页确认待确认的 `PublishIntent`，将其状态改为 `confirmed`，并创建 1 条本地 `not_started` 的 `PublicationRecord` placeholder；当前不会执行真实平台动作。
- 在项目详情页查看 `PublicationRecord`，并对 confirmed PublishIntent 执行本地 Fake Publish，将对应记录从 `not_started` 更新为 `succeeded`，写入稳定的 fake external publication id；这不代表真实平台发布成功。
- 查询指定 `PublishIntent` 下的 `PublicationRecord` 列表。
- 在项目详情页为指定 `PublicationRecord` 创建 deterministic fake metrics snapshot，并查询或读取该记录下的 metrics snapshots；`source` 明确为 `fake_local`，UI 显示 fake/local 边界标签，不代表真实平台表现。
- 在项目详情页为指定 `PublicationRecord` 创建 deterministic fake/local metrics review summary，并查询或读取该记录下的 summaries；summary 只用于人工复盘参考，不代表真实平台分析，也不会自动修改选题、脚本或内容计划。
- 归档项目仍可查看已有素材和规划草稿，但不能继续生成或选择。
- 将项目与素材元数据保存到本地 `SQLite`。
- 将用户上传文件保存到本地 `uploads/`，且不提交到 Git。

## 自动化边界

creator-flow 未来可以按照用户配置的频率自动生成草稿，但自动化只能产出待审核内容。任何向抖音或其他平台发布、排期发布、上传用于公开发布的动作，都必须经过用户明确审核与确认。

## 产品原则

- 用户素材必须显式导入，MVP 不自动读取用户私有 ChatGPT 历史。
- 系统不默认扫描本地文件、浏览器会话或私人账号。
- 热点内容只能作为辅助选题信号，账号主线应来自用户真实经验和原创素材。
- 首批内容方向是程序员真实问题、AI 辅助解决方案和开源项目开发日志。
- 外部 AI、热点、TTS、视频渲染和平台发布能力必须通过 Provider 接口抽象。
- 第一版视频生成主路径采用脚本 + 图片或截图 + TTS + 字幕 + `FFmpeg` 合成。
- 昂贵的纯 AI 文生视频能力仅作为后续可选 Provider，不作为 MVP 默认链路。

## 隐私原则

creator-flow 只应处理用户显式提供或明确启用的数据来源。不得向仓库提交密钥、token、上传素材、本地数据库、生成视频、生成音频、生成图片、字幕文件或其他私有内容。

## License

Apache-2.0. See `LICENSE`.
