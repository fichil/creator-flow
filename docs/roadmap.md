# 路线图

## Phase 0 Documentation Foundation

目标：建立产品定位、架构方向、路线图、许可证、贡献约束和关键决策记录。

范围：

- 中文主 README 与英文入口 README。
- `AGENTS.md` 工作规则。
- 产品规格、架构文档和路线图。
- 初始 ADR。
- Apache-2.0 License。

验收标准：

- 仓库可以公开发布，且不暴露密钥、私有路径、生成媒体或用户数据。
- 文档明确说明当前没有可运行应用。
- MVP 原则、自动化边界和非目标清晰可审查。

明确不做事项：

- 不发布 GitHub Release。
- 不实现 backend、frontend、数据库、Docker、CI、Provider 或渲染功能。
- 不安装依赖。
- 不生成媒体。

## v0.1 Local Runnable Skeleton

目标：建立最小可运行的本地应用骨架，为后续功能提供基础。

状态：Release Candidate。

范围：

- `FastAPI` 项目骨架。
- `React` + `Vite` + `Tailwind` 前端骨架。
- `SQLite` 本地元数据设计。
- 基础内容项目与素材导入能力。
- 项目更新与归档。
- 素材上传可靠性测试。
- Windows PowerShell 本地开发脚本。
- API smoke verification。
- 本地质量基线文档。
- 本地开发说明。

验收标准：

- 应用可以在本地启动。
- 用户可以创建内容项目。
- 用户可以更新和归档内容项目。
- 用户可以登记或导入显式选择的素材。
- 文件素材导入有基础成功、大小限制、类型校验和归档边界测试。
- 本地脚本可以启动 backend/frontend，并执行 backend tests、frontend build 和 API smoke checks。
- 基础页面不依赖外部 AI 或发布平台。

明确不做事项：

- 不实现自动发布。
- 不实现定时生成。
- 不接入生产部署。
- 不实现纯 AI 文生视频默认链路。

## v0.2 AI Planning Workflow

目标：支持从用户素材到选题、脚本和分镜的核心策划流程。

状态：v0.2.5 已完成 Batch 1 到 Batch 6，当前进入稳定性验收与产品复核。

已完成 Batch 1：先实现 backend-only 的 Provider interface、`FakeLLMProvider`、Topic Candidate 数据模型、生成 API、选择 API 和测试。该批只使用本地 deterministic fake provider，不接真实 AI，不保存密钥，不实现前端 UI。

已完成 Batch 2：实现 Topic Candidate frontend UI for fake provider workflow，让用户可以在项目详情页查看候选、生成 fake 候选并选择一个候选；archived 项目保持只读。

已完成 Batch 3：实现 Script Draft backend workflow based on selected TopicCandidate and explicit UserMaterial，继续使用本地 deterministic fake provider，不接真实 AI，不实现前端 UI。

已完成 Batch 4：实现 Script Draft frontend UI for fake provider workflow，让用户可以在项目详情页查看脚本草稿、基于已选 Topic Candidate 生成 fake 脚本草稿并选择一个脚本草稿；archived 项目保持只读。

已完成 Batch 5：实现 Storyboard backend workflow based on selected TopicCandidate, selected ScriptDraft, and explicit UserMaterial，继续使用本地 deterministic fake provider，不接真实 AI，不实现前端 UI，不做渲染、TTS、字幕或 FFmpeg。

已完成 Batch 6：实现 Storyboard frontend UI for fake provider workflow，让用户可以在项目详情页查看分镜草稿和 scenes、基于已选 Topic Candidate 与已选 Script Draft 生成 fake storyboards 并选择一个 storyboard；archived 项目保持只读，且仍不做渲染、TTS、字幕或 FFmpeg。

范围：

- Provider 接口定义。
- `LLMProvider` 驱动的选题生成。
- 脚本生成与编辑。
- 分镜生成与编辑。
- 素材方案生成。
- 人工审核状态。

验收标准：

- 用户可以从显式导入素材生成候选选题。
- 用户可以编辑并确认脚本和分镜。
- Provider 接口将供应商细节隔离在核心领域之外。
- 所有生成结果进入人工审核流程。

明确不做事项：

- 不静默读取私人账号或 ChatGPT 历史。
- 不直接发布到平台。
- 不默认使用昂贵纯 AI 文生视频 Provider。

## v0.3 Renderable Video MVP

目标：从已审核脚本、素材方案和字幕生成可预览的 9:16 MP4。

范围：

- `TTSProvider` 集成方向。
- 字幕生成与编辑。
- `FFmpeg` 合成图片或截图、音频、字幕和时间信息。
- 渲染任务状态跟踪。
- MP4 预览与审核状态。

验收标准：

- 用户可以从已审核脚本和素材生成 9:16 MP4。
- 渲染结果进入 `Review Queue`。
- 渲染输出保存在 Git 忽略路径中。
- 渲染失败可见且可排查。

明确不做事项：

- 不自动上传或发布。
- 不建设生产级渲染集群。
- 不强制接入纯 AI 视频 Provider。

## v0.4 Scheduled Draft Generation

目标：支持用户配置内容计划和生成频率，并自动生成待审核草稿。

范围：

- `ContentPlan` 配置：账号定位、内容类型、目标频率和内容偏好。
- `GenerationSchedule` 与 `Scheduler / Trigger Engine`。
- 基于近期显式导入素材生成候选草稿。
- 可选热点信号输入。
- `Review Queue` 管理待审核草稿。
- `Notification Service` 接口方向，用于提醒存在待审核草稿。

验收标准：

- 用户可以配置每周生成频率。
- 系统可以按计划创建 `GenerationRun`。
- 自动生成内容只能进入 `Review Queue`。
- 定时任务不能发布、排期发布或上传公开内容。
- 草稿记录生成时间、输入来源和热点来源。

明确不做事项：

- 不实现静默自动发布。
- 不绕过用户审核。
- 不使用用户未明确导入或未明确启用的数据来源。
- 不复制第三方受版权保护内容。

## v0.5 Human-Confirmed Douyin Publishing

目标：在人工确认前提下支持抖音发布准备与发布动作。

范围：

- 抖音 OAuth 或等价授权流程。
- `PublisherProvider` 的抖音实现。
- 发布前元数据准备。
- 人工确认发布界面。
- 发布状态查询。

验收标准：

- 用户可以审核视频、标题、描述、标签和封面建议。
- 用户明确确认后才会触发发布。
- 发布状态可以查询并记录。
- 凭据不会进入仓库。

明确不做事项：

- 不静默发布。
- 不绕过平台授权。
- 不把抖音假设写死到核心模型。

## v0.6 Metrics Feedback Loop

目标：采集基础发布指标，帮助用户复盘并优化下一轮内容。

范围：

- `PublicationMetrics` 数据模型。
- 基础播放、互动和发布时间指标采集。
- 内容复盘视图。
- 指标辅助下一轮选题的接口方向。

验收标准：

- 已发布内容可以关联基础表现指标。
- 用户可以查看内容表现摘要。
- 指标可作为后续选题优化的辅助输入。
- 指标采集不暴露不必要的个人隐私。

明确不做事项：

- 不承诺复杂增长预测。
- 不自动根据指标发布内容。
- 不采集超出用户授权范围的数据。

## v1.0 Extensible Creator Workflow

目标：形成稳定、可扩展、可贡献的创作者工作流。

范围：

- 稳定 Provider 架构。
- 多平台发布扩展文档。
- 完整本地部署与贡献文档。
- 稳定的内容计划、生成、渲染、审核、发布和复盘流程。
- 更完善的错误处理与审计记录。

验收标准：

- 新 Provider 可以按文档接入。
- 抖音之外的平台可以通过扩展方式支持。
- 核心工作流稳定可用。
- 文档足够支持开源贡献者理解和参与。

明确不做事项：

- 不牺牲人工确认发布原则。
- 不引入平台锁定。
- 不把用户私有素材或生成媒体纳入 Git。
