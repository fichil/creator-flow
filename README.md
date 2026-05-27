# creator-flow

[简体中文](README.md) | [English](README.en.md)

creator-flow 是一个可开源的 AI 短视频内容流水线，帮助用户将显式导入的想法、聊天摘要、文本、图片、截图和链接转化为待审核的短视频草稿。

## 当前状态

`v0.6 Metrics Feedback Loop - local fake/manual metrics workflow RC candidate`

当前仓库已完成 v0.1 本地可运行骨架、v0.2 AI Planning Workflow、v0.3 fake rendering/subtitle/preview workflow、v0.4 local fake/manual Scheduled Draft Generation workflow，以及 v0.5 Human-Confirmed Publishing Workflow 并发布 v0.5.0。v0.5 当前支持 local fake/manual publishing workflow：只能基于同一项目内已 approved 的 Review Draft 显式创建 `PublishIntent`，可查询、取消或确认该意图；confirm 只创建本地 `not_started` 的 `PublicationRecord` placeholder；项目详情页已可创建 PublishIntent、confirm、查看 PublicationRecord 并执行本地 Fake Publish；fake publish 只将本地记录推进到 `succeeded`。v0.6 已完成 Metrics Feedback Loop documentation foundation、backend-only fake metrics foundation、Fake Metrics Frontend UI foundation 和 Metrics Workflow Stabilization / RC checklist：项目详情页可以查看 `PublicationRecord` 的 fake/local metrics snapshots，并手动生成新的 fake metrics snapshot；当前只作为 local fake/manual metrics workflow RC candidate。

本地开发说明见 [`docs/development.md`](docs/development.md)，v0.5 发布候选验收清单见 [`docs/releases/v0.5-rc-checklist.md`](docs/releases/v0.5-rc-checklist.md)，v0.6 metrics RC checklist 见 [`docs/checklists/v0.6-metrics-feedback-loop-rc.md`](docs/checklists/v0.6-metrics-feedback-loop-rc.md)。

当前仍不接真实 OpenAI / Claude / Gemini / 其他 LLM，不保存 API key、secret 或 token，不联网调用真实 AI。v0.4 当前仍是 local fake/manual workflow：scheduled `GenerationRun`、Scheduler / Trigger Engine、完整 `Review Queue`、真实 MP4 渲染、真实视频播放、FFmpeg、TTS、真实字幕文件、真实音频、生产部署和账号体系仍未实现。Review Draft 仍是 placeholder；approve / reject 只改变审核状态，不发布、不上传、不渲染、不生成媒体。v0.5 发布流程当前也只是本地 fake workflow：confirm 表示用户确认进入发布执行准备阶段，Fake Publish succeeded 只表示本地 fake execution 成功，不代表真实平台发布成功；当前仍不接 Douyin API，不实现 OAuth，不保存凭据，不上传、不发布、不排期、不自动发布，也不接真实 PublisherProvider。v0.6 metrics 当前也只是 fake/local workflow，不抓取真实指标，不接真实 Douyin API，不实现 OAuth，不保存 token，不定时同步指标，不提供数据分析推荐能力，也没有真实平台 dashboard。
当前版本不适合作为生产部署使用。

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

其中 Topic Candidate、Script Draft 和 Storyboard 的生成与选择已在 v0.2 中以本地 fake provider 形式实现；v0.3 已完成 fake render job、fake preview manifest metadata 展示、fake subtitle draft 和 subtitle cues 的 RC 收口；v0.4 已完成 ContentPlan、GenerationSchedule、fake manual GenerationRun 和 Review Draft placeholder 的 RC 收口；v0.5 已完成 PublishIntent / PublicationRecord 后端基础、confirm workflow foundation、fake publisher execution foundation、项目详情页本地 fake publishing workflow、RC checklist、final validation 和 v0.5.0 release。v0.6 已完成 Metrics Feedback Loop 边界文档、backend-only fake metrics domain foundation、项目详情页 fake metrics UI foundation 和 metrics workflow RC checklist。真实 AI、真实字幕文件、真实音频、素材方案、真实 MP4 渲染与播放、真实 OAuth、真实上传、真实发布、token 保存、自动发布、排期发布、真实 Douyin API、真实 PublisherProvider、真实指标抓取、定时指标同步、数据分析推荐算法、真实平台 dashboard、scheduled GenerationRun、Scheduler / Trigger Engine 和完整 Review Queue 仍属于后续计划方向。

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
- 在项目详情页为指定 `PublicationRecord` 创建 deterministic fake metrics snapshot，并查询或读取该记录下的 metrics snapshots；`source` 明确为 `fake_local`，不代表真实平台表现。
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
