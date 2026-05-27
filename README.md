# creator-flow

[简体中文](README.md) | [English](README.en.md)

creator-flow 是一个可开源的 AI 短视频内容流水线，帮助用户将显式导入的想法、聊天摘要、文本、图片、截图和链接转化为待审核的短视频草稿。

## 当前状态

`v0.7.0 - local fake/manual metrics review summary workflow`

当前仓库已完成 v0.1 本地可运行骨架、v0.2 AI Planning Workflow、v0.3 fake rendering/subtitle/preview workflow、v0.4 local fake/manual Scheduled Draft Generation workflow、v0.5 Human-Confirmed Publishing Workflow 与 v0.6.0 local fake/manual metrics feedback workflow。v0.7.0 已完成 Metrics Review Summary local fake/manual workflow：支持基于 `PublicationRecord` 的 fake/local metrics snapshots 创建 deterministic review summaries，项目详情页可以展示 fake/local review summaries，用户可以手动生成 fake/local metrics review summary。fake/local review summary 只作为人工复盘参考，不是真实平台分析，不是真实 Douyin 表现，不是自动推荐算法结果，不会自动修改 `TopicCandidate`、`ScriptDraft` 或 `ContentPlan`，也不会触发上传、发布、排期发布或外部服务调用。archived project 继续保持只读。

本地开发说明见 [`docs/development.md`](docs/development.md)，v0.5 发布候选验收清单见 [`docs/releases/v0.5-rc-checklist.md`](docs/releases/v0.5-rc-checklist.md)，v0.6.0 metrics release checklist 见 [`docs/checklists/v0.6-metrics-feedback-loop-rc.md`](docs/checklists/v0.6-metrics-feedback-loop-rc.md)，v0.7 metrics review summary RC checklist 见 [`docs/checklists/v0.7-metrics-review-summary-rc.md`](docs/checklists/v0.7-metrics-review-summary-rc.md)。

当前仍不接真实 OpenAI / Claude / Gemini / 其他 LLM，不保存 API key、secret 或 token，不联网调用真实 AI。v0.4 当前仍是 local fake/manual workflow：scheduled `GenerationRun`、Scheduler / Trigger Engine、完整 `Review Queue`、真实 MP4 渲染、真实视频播放、FFmpeg、TTS、真实字幕文件、真实音频、生产部署和账号体系仍未实现。Review Draft 仍是 placeholder；approve / reject 只改变审核状态，不发布、不上传、不渲染、不生成媒体。v0.5 发布流程当前也只是本地 fake workflow：confirm 表示用户确认进入发布执行准备阶段，Fake Publish succeeded 只表示本地 fake execution 成功，不代表真实平台发布成功；当前仍不接 Douyin API，不实现 OAuth，不保存凭据，不上传、不发布、不排期、不自动发布，也不接真实 PublisherProvider。v0.6.0 metrics 和 v0.7.0 review summary 也只是 fake/local workflow，不抓取真实 Douyin metrics，不接真实 Douyin API，不实现 OAuth，不保存 token，不定时同步指标，不提供数据分析推荐算法，不提供真实平台 dashboard，不自动优化内容，也不把 fake metrics 或 fake/local review summary 当作真实平台表现、真实平台分析或自动推荐结果。
当前版本不适合作为生产部署使用。

## 后续路线

当前稳定版本仍是 `v0.7.0 - local fake/manual metrics review summary workflow`。下一阶段是 v0.8 Provider & Credential Security Foundation，后续路线继续保持渐进式抖音用户测试路径：

- v0.8 Provider & Credential Security Foundation：Batch 1 已完成 Provider、Credential、OAuth、Secret 和 token lifecycle 的文档 / ADR 边界；Batch 2 已完成 backend-only Provider Registry & Capability Metadata foundation；Batch 3 已完成 frontend read-only Provider Registry UI foundation；Batch 4 已完成 backend-only Provider Connection State & Sensitive Storage Status foundation；Batch 5 已完成 frontend read-only Provider Connection State UI foundation；Batch 6 是 backend-only Provider Credential Reference & Secret Redaction foundation，新增只读 credential reference metadata API、metadata-only table 和 secret redaction helper。本阶段不接真实 Douyin、不实现 OAuth、不保存 token、不保存 secret、不保存 API key、不保存 authorization code、不保存 OAuth client secret、不保存 credential material、不抓取真实指标、不上传、不发布、不排期发布，也不提供连接、授权、刷新、撤销或断开连接操作。
- v0.9 Douyin Provider POC / Sandbox Integration：才进入 Douyin Provider POC / Sandbox Integration，验证 sandbox/mock callback、账号连接状态和最小指标读取预研。
- v1.0 Douyin Integration User Test Release：才进入面向用户测试的抖音接入版本，不是生产级自动化发布版本。

真实 Douyin 接入仍取决于平台开放能力、应用审核、OAuth、API 权限与用户授权。README 中的后续路线不表示当前已经接入真实抖音，也不表示已经具备真实 OAuth、token storage、真实指标抓取、真实发布、自动发布、批量发布、定时发布或生产级平台 dashboard。

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
