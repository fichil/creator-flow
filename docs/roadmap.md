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

状态：v0.2.6 已完成 Batch 1 到 Batch 6 以及稳定性验收与产品复核。

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

状态：v0.3 Batch 7 已完成 fake workflow stabilization 与 Release Candidate review；当前只生成和展示 render job、fake preview manifest metadata、subtitle draft metadata 和 subtitle cues，不生成真实 MP4、音频或字幕文件，不新增真实 video player，不接 `FFmpeg`、TTS、发布能力或真实 AI Provider。

已完成 Batch 1：实现 Rendering domain foundation with FakeRenderer and render artifact metadata。该批次基于 selected Storyboard 创建 fake render job，保存 deterministic fake video artifact metadata，并保留 queued / running / succeeded / failed 状态，为后续真实 `FFmpeg` renderer 或异步任务预留接口。

已完成 Batch 2：实现 Render Job frontend UI for FakeRenderer workflow。该批次在项目详情页展示 render jobs 和 fake artifact metadata，允许在存在 selected Storyboard 时创建 fake render job，并保持 archived 项目只读；仍不生成真实 MP4，不接 `FFmpeg`、TTS、字幕生成或发布能力。

已完成 Batch 3：实现 Subtitle Domain Foundation backend-only。该批次新增 subtitle draft 与 subtitle cue 数据模型、API 和 deterministic `FakeSubtitleGenerator`，基于 selected Storyboard 生成 fake subtitle cues metadata；仍不生成真实 `.srt` / `.vtt` 文件，不接 TTS，不接 `FFmpeg`，不实现前端字幕 UI。

已完成 Batch 4：实现 Subtitle Frontend UI for FakeSubtitle workflow。该批次在项目详情页展示 subtitle drafts 和 subtitle cues，允许在存在 selected Storyboard 时创建并选择 fake subtitle draft，并保持 archived 项目只读；仍不生成真实字幕文件、音频或 MP4，不接 TTS、`FFmpeg` 或发布能力。

已完成 Batch 5：实现 Render Preview Artifact Placeholder backend-only。该批次让 `FakeRenderer` 在 Git 忽略的 `data/local/render_previews/` 路径策略下写入 deterministic fake preview manifest JSON，并在 render artifact metadata 中记录 manifest 路径、checksum、fake video duration / dimensions 以及可选 selected subtitle draft id；仍不生成真实 MP4、音频或字幕文件，不接 TTS、`FFmpeg` 或发布能力，也不实现前端 Preview UI。

已完成 Batch 6：实现 Render Preview Frontend UI for fake preview manifest。该批次在项目详情页的 Render Jobs 区块展示 backend 已返回的 fake preview manifest metadata，包括 manifest path、MIME type、file size、checksum、fake video duration / dimensions 和可选 selected subtitle draft id；前端不读取运行时 manifest 文件，不新增真实 video player，不播放真实视频，仍不生成真实 MP4、音频或字幕文件。

已完成 Batch 7：实现 Fake Workflow Stabilization & Release Candidate Review。该批次只补强 render preview metadata list/read backend tests、empty subtitle cues frontend fallback tests、开发说明和 v0.3 RC checklist，完成 fake workflow RC 收口；仍不生成真实 MP4、音频或字幕文件，不新增真实 video player，不接 `FFmpeg`、TTS、发布能力或真实 AI Provider。

范围：

- `TTSProvider` 集成方向。
- 字幕生成与编辑。
- `FFmpeg` 合成图片或截图、音频、字幕和时间信息。
- 渲染任务状态跟踪。
- MP4 预览与审核状态。

当前 RC 验收边界：

- 用户可以基于 selected Storyboard 创建 fake render job。
- 前后端可以展示 fake preview manifest metadata、subtitle draft metadata 和 subtitle cues。
- fake preview manifest 只能作为 Git 忽略路径下的 runtime metadata 存在。
- 当前不会生成真实 MP4、音频或字幕文件。
- 当前不接 `FFmpeg`、TTS、发布能力或真实 AI Provider。

后续真实渲染方向：

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

状态：v0.4 Batch 8 已完成 Release Candidate stabilization / release candidate review；当前支持项目级 `ContentPlan`、其关联 `GenerationSchedule` 配置、backend-only fake manual `GenerationRun` 记录、由 manual run 同步创建的 `review_drafts` pending_review placeholder，以及项目详情页中的 ContentPlan / GenerationSchedule / GenerationRun / Review Draft 展示、配置创建、启停和 manual trigger 操作。本阶段仍是 local fake/manual workflow，只允许 manual trigger，不执行 scheduled trigger，不实现 Scheduler / Trigger Engine，不自动生成真实草稿，不创建真实 Topic Candidate、Script Draft、Storyboard、Render Job、Subtitle Draft 或媒体文件，不实现完整 `Review Queue` 页面、`Notification Service`、热点源或真实 AI Provider。

已完成 Batch 1：实现 ContentPlan backend-only domain foundation。该批次新增项目级 `content_plans` 数据表、Pydantic schemas、API routes 和 backend tests，支持账号定位、内容类型、每周目标频率、偏好文本和启用状态配置；`target_frequency_per_week` 限制为 1 到 14。ContentPlan 只是本地配置，不触发任何自动生成行为，不接调度、发布、热点源或真实 AI Provider。

已完成 Batch 2：实现 GenerationSchedule backend-only domain foundation。该批次新增项目级且绑定现有 `ContentPlan` 的 `generation_schedules` 数据表、Pydantic schemas、API routes 和 backend tests，支持 frequency、timezone、preferred days、preferred time 与启用状态配置；schedule 只是本地配置，不注册后台任务，不创建 `GenerationRun`，不自动生成草稿，不接 Scheduler、热点源、通知、发布或真实 AI Provider。

已完成 Batch 3：实现 GenerationRun backend-only manual trigger foundation。该批次新增 `generation_runs` 数据表、Pydantic schemas、API routes 和 backend tests，支持基于项目级 `ContentPlan` 与可选 `GenerationSchedule` 创建 fake manual run，并同步标记为 `succeeded`，记录 deterministic input/result summary；本批不执行 schedule，不创建真实草稿或媒体，不接 Scheduler、后台 worker、热点源、发布或真实 AI Provider。

已完成 Batch 4：实现 Review Draft backend-only foundation。该批次新增 `review_drafts` 数据表、Pydantic schemas、API routes 和 backend tests；fake manual `GenerationRun` 成功后同步创建 1 条 `pending_review` review draft placeholder，支持 list / read / approve / reject。approve / reject 只改变 `review_status`，不触发真实生成、渲染、上传、发布或外部 Provider。

已完成 Batch 5：实现 Review Draft frontend UI foundation。该批次在项目详情页新增待审核草稿区块，展示 backend 返回的 `review_drafts` list、审核状态、草稿摘要、输入来源、热点来源 fallback、GenerationRun / GenerationSchedule 信息和创建/更新时间；支持调用已有 approve / reject API 并在成功后刷新列表，archived 项目保持只读。本批不新增后端业务能力，不实现完整 `Review Queue` 页面，不实现 Scheduler / scheduled `GenerationRun`，不创建真实媒体，不接真实 Provider，不发布不上传。

已完成 Batch 6：实现 ContentPlan / GenerationSchedule / Manual GenerationRun frontend UI foundation。该批次在项目详情页新增 Content Plans 区块，调用已有后端 API 展示和创建 `ContentPlan`，启停 `ContentPlan`，展示并创建关联 `GenerationSchedule`，启停 `GenerationSchedule`，并支持基于 ContentPlan 或 ContentPlan + GenerationSchedule 手动创建 fake manual `GenerationRun`；manual run 成功后刷新 GenerationRuns 与 Review Drafts。archived 项目保持只读。本批不新增后端业务能力，不实现 Scheduler / scheduled `GenerationRun`，不接热点源、通知、真实 Provider、`FFmpeg`、TTS、发布或上传能力。

已完成 Batch 7：实现 frontend component extraction / stabilization。该批次将项目详情页中的 ContentPlan / GenerationSchedule / Manual GenerationRun 和 Review Draft v0.4 UI 组件拆分到 `frontend/src/pages/project-detail/`，保持现有 UI 行为、API 调用和测试语义不变；本批不新增后端能力，不新增业务能力，不实现 Scheduler / scheduled `GenerationRun`，不创建真实媒体，不接真实 Provider，不发布不上传。

已完成 Batch 8：实现 v0.4 Release Candidate stabilization / checklist。该批次只更新 v0.4 RC checklist、开发说明、路线图和 README 状态，确认 ContentPlan、GenerationSchedule、fake manual GenerationRun、Review Draft placeholder 与项目详情页 UI 的 local fake/manual workflow 已进入 RC 收口；本批不新增后端能力，不新增前端功能，不新增业务能力，不实现 Scheduler / scheduled `GenerationRun`，不创建真实媒体，不接真实 Provider，不发布不上传。

当前 RC 验收边界：

- `ContentPlan` 后端支持 create / list / read / update / enable / disable。
- `GenerationSchedule` 后端支持 create / list / read / update / enable / disable，但只保存配置，不执行定时任务。
- fake manual `GenerationRun` 支持 create / list / read，并在成功后刷新 GenerationRuns 与 Review Drafts。
- `Review Draft` 仍是 placeholder，支持 create / list / read / approve / reject；approve / reject 只改变 `review_status`，不发布、不上传、不渲染、不生成媒体。
- archived project 允许读取已有 ContentPlan、GenerationSchedule、GenerationRun 和 Review Draft，但禁止 create / update / enable / disable / trigger / approve / reject。
- 当前不执行 scheduled `GenerationRun`，不实现 Scheduler / Trigger Engine，不创建真实 Topic Candidate、Script Draft、Storyboard、Render Job、Subtitle Draft 或媒体文件，不接热点源、Notification Service、真实 AI Provider、`FFmpeg`、TTS、发布或上传能力。

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

状态：v0.5 Batch 1 已开始并完成 Human-Confirmed Publishing Provider Boundary documentation foundation。当前只定义发布 Provider 边界、人工确认原则、`PublishIntent` / `PublicationRecord` 或等价模型方向，以及凭据与平台细节隔离要求；本批不实现真实 OAuth、真实发布、真实上传、排期发布、自动发布、token 保存、后端 API、前端功能或数据库表，也不修改 v0.4 local fake/manual workflow 或 v0.3 render/subtitle/preview workflow。

已完成 Batch 1：实现 Human-Confirmed Publishing Provider Boundary documentation foundation。该批次只更新产品规格、架构、路线图和 ADR，明确 v0.5 的目标是 Human-Confirmed Douyin Publishing；发布必须由用户明确确认后触发；`Review Draft` approved 不等于发布；系统不得静默发布、自动发布或绕过用户审核；`PublisherProvider` 必须隔离平台细节；抖音只是首个平台实现方向，不能写死到核心模型；凭据不得进入 Git；后续真实发布能力必须基于 `PublishIntent` / `PublicationRecord` 或等价模型并保留人工确认状态。

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

当前文档边界：

- `Review Draft` approved 只表示草稿通过审核，不会触发发布、上传或排期发布。
- `PublishIntent` 表示等待用户确认的发布意图；`PublicationRecord` 或等价模型记录确认后的执行结果。
- `PublisherProvider` 只能在用户确认后执行平台动作，并必须把抖音等平台细节隔离在适配层。
- OAuth、token 保存、真实发布、真实上传、发布状态查询和错误重试必须在后续独立批次中实现。
- v0.4 local fake/manual workflow 保持不变。

明确不做事项：

- 不静默发布。
- 不自动发布、排期发布或上传。
- 不绕过平台授权。
- 不把抖音假设写死到核心模型。
- 不在本批实现真实 OAuth、真实发布、真实上传或真实 token 保存。

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
