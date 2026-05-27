# 架构

## 技术栈

- Backend: Python + `FastAPI`。
- Frontend: `React` + `Vite` + `Tailwind`。
- MVP Database: `SQLite`。
- Future Database: `PostgreSQL`。
- Video Rendering: `FFmpeg`。
- Deployment: `Docker Compose`。
- CI/CD: `GitHub Actions`。
- License: Apache-2.0。

本文档描述 creator-flow 的目标架构。Documentation Foundation 阶段已完成；v0.1 Local Runnable Skeleton 阶段允许实现最小 `FastAPI`、`React` + `Vite` + `Tailwind` 和 `SQLite` 本地骨架。

## 系统逻辑模块

- Material Import：接收用户显式选择的文本、聊天摘要、项目记录、截图、图片和链接。
- Content Plan：配置账号定位、内容主题、目标频率、内容偏好和发布平台偏好。
- Scheduler / Trigger Engine：按用户配置触发草稿生成，或支持手动触发生成。
- Content Project：跟踪素材、草稿、渲染状态、审核状态和发布意图。
- Topic Studio：基于导入素材和可选热点信号提出选题与角度。
- Script Studio：生成并编辑短视频脚本。
- Storyboard Studio：将脚本映射为画面、字幕、旁白和素材需求。
- Voice and Subtitle Pipeline：准备 TTS 输入、音频和字幕。
- Rendering Pipeline：通过 `FFmpeg` 生成 9:16 MP4。
- Review Queue：统一管理待审核的视频草稿和渲染结果。
- Publishing Preparation：准备平台元数据、发布检查和待确认发布意图。
- Human Review Gate：发布前要求用户明确审核与确认。
- Notification Service：提醒用户存在待审核草稿，当前仅定义接口方向。
- Metrics Feedback：保存发布后的基础表现指标，供后续选题优化和内容复盘。
- Provider Registry：通过稳定接口连接外部 AI、媒体、热点、渲染和发布服务。

## Provider 接口设计方向

Provider 接口用于隔离核心工作流与外部服务。

- `LLMProvider`：选题生成、脚本生成、改写建议、元数据草稿和结构化提取。
- `ImageProvider`：可选图片生成、图片编辑、封面辅助或视觉素材获取。
- `TTSProvider`：基于已审核脚本文本生成旁白音频。
- `VideoRenderer`：视频合成与渲染，MVP 实现方向为 `FFmpeg`。
- `PublisherProvider`：平台发布准备、状态查询和用户确认后的发布动作。
- `TrendSourceProvider`：可选热点信号获取，用于辅助选题和角度判断。
- `MetricsProvider`：平台指标适配层，用于后续读取发布后的基础表现指标。

Provider 实现不得将单一厂商或单一平台假设泄漏到核心领域模型中。

## 发布 Provider 边界

v0.5 的发布方向是 Human-Confirmed Douyin Publishing。抖音是首个平台实现方向，但平台细节必须由 `PublisherProvider`、发布准备模块和平台适配层承接，不能写死到 `ContentProject`、`ContentPlan`、`GenerationRun`、`Review Draft` 或其他核心模型中。

`PublisherProvider` 的职责边界：

- 准备平台元数据、发布检查、平台能力描述和发布状态查询。
- 只在用户明确确认发布后执行真实发布、上传或排期发布动作。
- 将平台返回的发布 id、状态、错误码和诊断信息转换为核心可理解的 `PublicationRecord` 或等价记录。
- 不拥有选题、脚本、分镜、渲染、审核或调度决策。

`Review Draft` 的 `approved` 状态不等于发布确认。它只表示草稿通过人工审核，可以进入后续渲染、发布准备或发布意图创建流程。任何公开发布、上传或排期发布都必须经过单独的 `PublishIntent` 人工确认状态。

后续发布能力应基于 `PublishIntent` / `PublicationRecord` 或等价模型：

- `PublishIntent`：记录平台目标、标题、描述、标签、封面建议、视频或渲染结果引用、待确认状态、确认人和确认时间。
- `PublicationRecord`：记录确认后的执行结果、平台返回 id、平台状态、错误信息、重试信息和查询时间。

凭据必须通过本地配置、环境变量或后续安全存储方案提供，不得进入 Git、测试数据、示例文档或运行时 artifact。v0.5 Batch 1 只定义该边界，不实现真实 OAuth、真实 token 保存、真实发布、真实上传、排期发布或自动发布。

## 指标 MetricsProvider 边界

v0.6 的指标反馈方向是 Metrics Feedback Loop。`MetricsProvider` 是平台指标适配层，用于后续把抖音或其他平台返回的表现数据转换为核心领域可以理解的指标快照；Douyin 只是未来一个 provider，不能把抖音专有字段、授权流程或接口形状写死到核心模型中。

`MetricsProvider` 的职责边界：

- 基于已存在的 `PublicationRecord` 或等价发布记录读取发布后指标。
- 将平台返回的播放、互动、观看质量和采集时间转换为平台无关的指标快照。
- 标记指标来源，例如 fake/local data 或真实平台数据。
- 允许部分指标为空，因为不同平台、账号权限和内容状态可用的指标不同。
- 不拥有选题、脚本、分镜、渲染、审核、发布确认或自动优化决策。

Provider 不应把 token、secret、账号授权细节、平台原始响应或平台专有字段泄漏到 `PublicationRecord`、`ContentProject`、`ContentPlan` 或其他核心模型中。凭据必须由后续独立的授权和安全存储方案处理，不得进入 Git、测试 fixtures、示例文档、日志样例或运行时 artifact。

后续可以实现 `FakeMetricsProvider` 作为本地开发 provider，用 deterministic fake metrics 支持 UI 与模型验证；fake metrics 必须被显式标记为 fake/local data，不能展示为真实平台表现。v0.6 Batch 1 只定义该架构边界，不实现 provider 代码、后端 API、数据库表、前端功能、真实指标抓取、真实 Douyin API、OAuth、token 保存或定时同步。

## Provider / Credential / Douyin integration roadmap

v0.7.0 release 之后的架构路线必须从 fake/local metrics review summary workflow 渐进进入抖音用户测试，而不是一次性跳到真实平台生产能力。

- v0.7.0 已完成 metrics review summary local fake/manual workflow，不改变 Provider 架构，只基于现有 `PublicationMetricSnapshot` 和 fake/local metrics source 做 metrics review summary，将指标转化为人工复盘参考。
- v0.8 建立 Provider registry / credential boundary / OAuth callback / token lifecycle 的安全基础，包括 provider capability metadata、connection status、授权失败状态和 audit log 方向。
- v0.9 做 Douyin Provider POC / Sandbox Integration，用 Douyin provider adapter skeleton、OAuth callback smoke test 或 mock/sandbox callback、token refresh dry-run 和最小指标读取 POC 验证边界。
- v1.0 才进入 Douyin Integration User Test Release，用于用户授权、账号连接状态和至少一种真实或 sandbox/manual fallback 指标回流测试。

核心领域模型不能依赖 Douyin 专有字段。`PublicationRecord`、`PublicationMetricSnapshot`、`MetricSource`、`ContentPlan`、`TopicCandidate`、`ScriptDraft` 和其他核心模型只能保存平台无关的必要字段；Douyin 原始响应、平台专有字段、scope 细节和接口差异应留在 provider adapter、provider metadata 或受控附加 metadata 中。

Credential 与 secret 安全边界：

- token、secret、refresh token、API key 和平台账号凭据不得进入 Git。
- token、secret 和 refresh token 不得写入日志、测试 fixtures、示例数据、错误提示或运行时 artifact。
- 前端不得接收、缓存或展示 token、secret、refresh token 或平台原始凭据。
- OAuth callback 必须校验 state，并在授权失败、权限不足、token 过期和 provider 接口失败时返回可审查的错误状态。
- token 加密保存、刷新、撤销、过期和断开连接策略必须作为 v0.8 之后的独立安全边界处理。

Provider 返回的数据必须明确 source 和授权状态。指标或连接状态至少需要能区分 `fake_local`、`douyin_sandbox`、`douyin_real`、未授权、授权失败、权限不足、token 过期和 provider 错误等情况。fake/local provider 必须继续可用，作为没有平台授权、平台权限不可用或用户只想本地演示时的 fallback。

Douyin 接入不得绕过平台开放能力、应用审核、OAuth、API 权限或用户授权。如果 v0.9 / v1.0 期间真实 API 权限不可用，架构应允许 manual import 或 mock/sandbox provider contract test 作为 fallback，而不是把 fake 或 sandbox 数据伪装成真实平台表现。

## 核心领域模型

- `UserMaterial`：用户导入的文本、图片、截图、链接、聊天摘要或项目记录。
- `ContentPlan`：账号定位、内容主题、目标频率、内容偏好和平台偏好。
- `GenerationSchedule`：计划生成频率、时间窗口、启用状态和触发规则。
- `GenerationRun`：一次手动或定时生成过程，记录输入、状态、输出草稿和错误信息。
- `ContentProject`：聚合素材、草稿、审核状态、渲染状态和发布准备信息。
- `TopicCandidate`：候选选题、角度、受众、开头钩子和生成理由。
- `ScriptDraft`：可编辑的短视频脚本。
- `Storyboard`：按顺序组织的场景、画面、旁白、字幕和时间建议。
- `AssetPlan`：所需图片、截图、生成素材、旁白、字幕和元数据。
- `RenderJob`：渲染请求、状态、日志、输入和输出路径。
- `ReviewTask`：待审核草稿、待审核视频或待确认发布事项。
- `PublishIntent`：平台目标、元数据、检查结果、确认状态和发布结果。
- `PublicationRecord`：用户确认后的一次发布执行记录，保存平台返回状态、结果、错误和查询信息。
- `PublicationMetricSnapshot`：发布后的基础表现指标快照，例如播放、互动、观看质量和采集时间，可与 `PublicationRecord` 关联。
- `MetricSource`：指标来源描述，用于区分 fake/local data 与真实平台数据。
- `ProviderConfig`：Provider 配置引用，不在 Git 中保存密钥。

## 内容项目状态机

计划状态包括：

- `draft`：项目已创建，仍可补充素材。
- `materials_ready`：已有足够显式导入素材用于生成。
- `scheduled_generation_pending`：等待计划任务触发生成。
- `generating`：正在执行一次 `GenerationRun`。
- `draft_generated`：已生成候选草稿。
- `topic_selected`：用户已接受或编辑选题。
- `script_ready`：脚本已生成并可进入分镜。
- `storyboard_ready`：分镜和素材需求已准备。
- `render_ready`：素材、字幕和旁白输入已准备渲染。
- `rendering`：渲染任务运行中。
- `review_ready`：草稿或 MP4 已进入 `Review Queue`。
- `publish_prepared`：平台元数据与检查结果已准备。
- `publish_confirmed`：用户明确确认发布。
- `published`：平台发布动作已完成。
- `metrics_collected`：发布后基础指标已回流。
- `archived`：项目归档。

发布相关流转必须经过 `review_ready`、`publish_prepared` 和 `publish_confirmed`。调度任务只能触发草稿生成，不能在没有人工确认时发布。

## 数据与文件存储边界

- `SQLite` 存储 MVP 本地元数据、项目状态、计划配置、生成运行记录和文件引用。
- `PostgreSQL` 可作为后续更持久或协作部署的数据库选项。
- 用户上传、生成素材、本地渲染结果、旁白音频、字幕和本地数据库属于运行时数据，不得提交到 Git。
- 密钥和 Provider 凭据必须通过本地配置或环境变量提供，不得进入仓库文件。
- 生成视频、音频、图片、字幕和上传素材应放在被忽略的运行时目录中，例如 `data/generated/` 或 `uploads/`。

## 热点来源边界

- 热点来源必须可配置、可关闭。
- 必须记录热点来源、采集时间和用户是否启用。
- 热点应作为外部不可信输入处理。
- 热点只能辅助选题，不得替代用户显式导入素材。
- 系统不得直接复制第三方受版权保护的内容或素材。

## 安全原则

- 只处理用户显式导入的素材和用户明确启用的数据来源。
- 不静默读取私有聊天、本地文件、浏览器状态或平台账号。
- 发布前必须要求用户明确确认。
- `Review Draft` approved 不等于发布确认；发布必须通过单独确认状态。
- 调度任务不得绕过 `Review Queue` 与人工确认。
- 凭据不得进入 Git 或生成文档示例。
- 外部 Provider 视为可替换且不可信的边界。
- 日志应支持调试，但避免不必要地保存私有内容。

## v0.1 暂不实现的技术内容

- 数据库迁移。
- `Docker Compose` 部署。
- `GitHub Actions` 工作流。
- Provider 实现。
- `FFmpeg` 命令编排。
- 抖音发布集成。
- 纯 AI 文生视频生成。
