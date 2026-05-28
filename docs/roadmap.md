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

状态：Release Candidate，已完成 Final release validation / tag preparation 文档收口。v0.5 Batch 6 已完成 Publishing workflow Release Candidate stabilization / checklist。当前已有发布意图与发布记录数据表、Pydantic schemas、API、`PublishIntent` confirm 状态流转、本地 deterministic `FakePublisherProvider` fake execution，以及项目详情页本地 fake publishing workflow；`Review Draft` approved 仍不等于发布，`PublishIntent` confirmed 也不等于真实发布，fake succeeded 只表示本地 fake execution 成功。本阶段仍不实现真实 OAuth、真实发布、真实上传、排期发布、自动发布、token 保存或真实 PublisherProvider，也不修改 v0.4 local fake/manual workflow 或 v0.3 render/subtitle/preview workflow。

已完成 Batch 1：实现 Human-Confirmed Publishing Provider Boundary documentation foundation。该批次只更新产品规格、架构、路线图和 ADR，明确 v0.5 的目标是 Human-Confirmed Douyin Publishing；发布必须由用户明确确认后触发；`Review Draft` approved 不等于发布；系统不得静默发布、自动发布或绕过用户审核；`PublisherProvider` 必须隔离平台细节；抖音只是首个平台实现方向，不能写死到核心模型；凭据不得进入 Git；后续真实发布能力必须基于 `PublishIntent` / `PublicationRecord` 或等价模型并保留人工确认状态。

已完成 Batch 2：实现 PublishIntent / PublicationRecord backend domain foundation。该批次新增 `publish_intents` 与 `publication_records` 数据表、backend schemas、backend API routes 和测试；只允许基于同一项目内已 `approved` 的 `Review Draft` 显式创建 `PublishIntent`，创建后状态为 `pending_confirmation`，并支持 list / read / cancel 与按 PublishIntent 查询 `PublicationRecord`。本批不提供 confirm / publish API，不自动创建发布记录，不执行真实平台动作，不接真实 Douyin API，不实现 OAuth，不保存 token / secret / API key，不上传、不发布、不排期、不自动发布。

已完成 Batch 3：实现 Publish confirmation backend workflow foundation。该批次新增 `PublishIntent` confirm API，支持 `pending_confirmation` -> `confirmed` 状态流转，并创建 1 条本地 `publication_records` placeholder，`provider_name` 为 `placeholder`，`publication_status` 为 `not_started`，`external_publication_id` 和 `error_message` 为空。confirm 只表示用户已确认进入发布执行准备阶段，不执行真实平台动作，不改变 Review Draft 审核状态，不接真实 Douyin API，不实现 OAuth，不保存 token / secret / API key，不上传、不发布、不排期、不自动发布。

已完成 Batch 4：实现 PublisherProvider fake execution backend foundation。该批次新增本地 `PublisherProvider` 协议与 deterministic `FakePublisherProvider`，并新增 fake publish API；只允许 confirmed PublishIntent 且存在 `not_started` PublicationRecord 时执行 fake publish。fake publish 会把 `PublicationRecord` 更新为 `succeeded`，将 `provider_name` 更新为 `fake_publisher`，写入稳定的 fake external publication id，并保持 `error_message` 为空。本批不接真实 Douyin API，不实现 OAuth，不保存 token / secret / API key，不上传、不发布、不排期、不自动发布；`succeeded` 只表示本地 fake execution 成功，不代表真实平台发布成功。

已完成 Batch 5：实现 Publishing frontend workflow foundation。该批次在项目详情页新增 Publishing / Fake Publishing 区块，接入已有 backend API，让用户可以从已 approved Review Draft 创建 `PublishIntent`、查看发布意图状态、confirm、cancel、查看 `PublicationRecord`，并对 confirmed PublishIntent 执行本地 Fake Publish。UI 明确提示这是本地 fake publishing workflow，不上传、不发布、不排期、不调用 Douyin；fake publish succeeded 只表示本地 fake execution 成功，不代表真实平台发布成功。本批不接真实 Douyin API，不实现 OAuth，不保存 token / secret / API key，不上传、不发布、不排期、不自动发布，也不接真实 PublisherProvider。

已完成 Batch 6：实现 Publishing workflow Release Candidate stabilization / checklist。该批次不新增大功能、不接真实平台、不改变既有业务语义，只统一 README、README.en.md、路线图和本地开发说明中的 v0.5 RC 状态，补充 Publishing frontend workflow 的错误展示与误导性按钮文案边界测试，并确认 v0.5 当前仍是 local fake/manual publishing workflow。本批不接真实 Douyin API，不实现 OAuth，不保存 token / secret / API key，不上传、不发布、不排期、不自动发布，也不接真实 PublisherProvider。

已完成 Final validation：实现 v0.5 Release validation / tag preparation。该批次只新增 v0.5 RC checklist、统一 README / README.en.md / roadmap / development 的 release readiness 说明，并运行最终本地质量门禁；不新增业务功能、不新增 API、不新增数据库表、不改核心业务语义、不创建 Git tag、不 push、不 merge main。

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

当前 RC 验收边界：

- `Review Draft` approved 只表示草稿通过审核，不会触发发布、上传或排期发布。
- `Review Draft` approved 不会自动创建 `PublishIntent`；必须由用户显式创建。
- `PublishIntent` 只能基于同一项目内已 approved 的 Review Draft 创建，创建后进入 `pending_confirmation`。
- `PublishIntent` 支持 list / read / cancel / confirm；archived project 允许读取已有记录，但禁止 create / confirm / cancel / fake publish。
- `PublishIntent` confirmed 只表示用户已确认进入发布执行准备阶段，不等于真实发布。
- confirm 只创建本地 `not_started` 的 `PublicationRecord` placeholder，不执行真实平台动作，不改变 Review Draft 审核状态。
- confirmed PublishIntent 且存在 `not_started` PublicationRecord 时，可以执行本地 Fake Publish。
- Fake Publish 只通过 deterministic `FakePublisherProvider` 更新本地 `PublicationRecord` 为 `succeeded`，写入 fake external publication id，并保持 error message 为空。
- fake publish 的 `succeeded` 不等于真实平台发布成功。
- succeeded / failed PublicationRecord 不允许重复 fake publish；pending_confirmation / cancelled PublishIntent 不允许 fake publish。
- 项目详情页展示 Publishing / Fake Publishing 区块，可创建 PublishIntent、confirm、cancel、查看 PublicationRecord 并执行 Fake Publish；UI 必须明确这是本地 fake workflow。
- cross-project publish intent / publication record 访问返回 404。
- v0.4 local fake/manual workflow 和 v0.3 render/subtitle/preview workflow 保持不变。

明确不做事项：

- 不静默发布。
- 不自动发布、排期发布或上传。
- 不实现真实 OAuth 或真实账号授权页。
- 不保存 access token、refresh token、API key、secret 或任何凭据。
- 不调用真实 Douyin API 或任何外部服务。
- 不新增真实 PublisherProvider。
- 不生成真实媒体文件。
- 不把抖音假设写死到核心模型。
- 不把 fake succeeded 描述成真实平台发布成功。

## v0.6 Metrics Feedback Loop

目标：为发布后的内容记录指标反馈，帮助用户复盘内容表现，并为未来根据表现优化 `TopicCandidate`、`ScriptDraft` 和 `ContentPlan` 提供基础输入。指标来源未来可以来自抖音或其他平台 Provider，但核心模型不能写死抖音。

状态：v0.6.0 released。v0.6 Batch 1 已完成 Metrics Feedback Loop documentation foundation；v0.6 Batch 2 已完成 backend-only fake metrics domain foundation；v0.6 Batch 3 已完成 Fake Metrics Frontend UI foundation；v0.6 Batch 4 已完成 Metrics Workflow Stabilization / RC checklist；v0.6.0 release finalization 已完成。v0.6.0 release scope 仅限 local fake/manual metrics feedback loop：项目详情页查看和手动生成本地 deterministic fake/local metrics snapshots，不实现真实指标抓取、真实平台 API、OAuth、token 保存、定时同步、数据分析推荐算法、独立 analytics 页面或真实平台 dashboard。

已完成 Batch 1：实现 Metrics Feedback Loop documentation foundation。该批次只更新产品规格、架构、路线图、README 和 ADR，明确指标反馈用于发布后复盘，不用于自动发布；未来指标快照应与 `PublicationRecord` 关联；平台指标能力通过 `MetricsProvider` 或等价 Provider 抽象隔离；fake/local metrics 与真实平台 metrics 必须显式区分；真实 Douyin API、OAuth、token 保存、定时同步、真实指标抓取和数据分析推荐算法均不在本批实现。

已完成 Batch 2：实现 Metrics Feedback Loop backend-only fake metrics domain foundation。该批次新增 `publication_metric_snapshots` 后端数据表、metrics schemas、metrics API routes、deterministic `FakeMetricsProvider` 和 backend tests；支持基于现有 `PublicationRecord` 创建 `fake_local` metrics snapshot，查询某个 `PublicationRecord` 下的 metrics snapshots，并读取单个 metrics snapshot。指标字段允许部分为空，`completion_rate` 限制在 0 到 1，所有 fake metrics 都明确标记为 fake/local data。该批次不新增前端 UI，不接真实 Douyin API，不实现 OAuth，不保存 token / secret / API key，不调用外部服务，不做定时同步，不抓取真实平台指标，不做数据分析推荐算法，也不修改 v0.5 fake publishing workflow、v0.4 scheduled draft workflow 或 v0.3 rendering workflow 语义。

已完成 Batch 3：实现 Fake Metrics Frontend UI foundation。该批次在项目详情页 Publishing / Fake Publishing 区块附近展示每条 `PublicationRecord` 关联的 metrics snapshots，并支持用户手动点击 `Generate fake metrics` 创建新的 `fake_local` metrics snapshot；创建成功后刷新对应 PublicationRecord 的 metrics list。UI 明确显示 `Fake/local metrics` 和 `Not real platform performance`，archived project 保持只读，不允许创建 fake metrics。该批次不新增复杂 dashboard、不新增图表库、不新增独立 analytics 页面，不接真实 Douyin API，不实现 OAuth，不保存 token / secret / API key，不调用外部服务，不做定时同步，不抓取真实平台指标，不做数据分析推荐算法或自动内容优化，也不修改 backend metrics 业务语义。

已完成 Batch 4：实现 Metrics Workflow Stabilization / Release Candidate checklist。该批次补强 fake metrics backend/frontend workflow 的边界测试，新增 [`docs/checklists/v0.6-metrics-feedback-loop-rc.md`](checklists/v0.6-metrics-feedback-loop-rc.md)，并统一路线图、README 和本地开发说明中的 v0.6 RC 状态。该批次完成后 v0.6 进入 local fake/manual metrics workflow RC candidate；仍不实现真实指标抓取、真实 Douyin API、OAuth、token 保存、定时同步、数据分析推荐算法、真实平台 dashboard 或自动内容优化。

已完成 Release finalization：实现 v0.6.0 release 文档收口。该批次只将 README、README.en.md、路线图、v0.6 RC checklist 和本地开发说明从 RC candidate 更新为 v0.6.0 release 状态，并保留真实平台指标作为未来独立方向；不新增业务功能、不新增 backend API、不新增数据库表、不新增前端功能，也不修改后端、前端、测试、依赖或锁文件。

范围：

- `PublicationMetricSnapshot` 或等价指标快照模型。
- `MetricSource` 或等价指标来源模型，用于区分 fake/local data 与真实平台数据。
- `MetricsProvider` 或等价 Provider 抽象，用于隔离平台指标采集细节。
- `PublicationRecord` 与指标快照的关联。
- 指标采集时间点，例如 `captured_at`。
- 基础播放、互动和观看质量指标方向，例如 `views`、`likes`、`comments`、`shares`、`favorites`、`watch_time` 和 `completion_rate`。
- 内容复盘视图。
- 指标辅助下一轮选题的接口方向。

领域方向：

- 每次指标回流应保存为快照，而不是覆盖唯一的“当前指标”。
- 指标快照应记录来源、平台、采集时间、是否为 fake/local data，以及与 `PublicationRecord` 的关系。
- 不同平台指标能力不同，指标字段必须允许部分为空。
- 核心领域模型只保存平台无关的基础指标；平台专有字段应留在 Provider 适配层或附加 metadata 中。

验收标准：

- 已发布内容可以关联基础表现指标。
- 用户可以查看内容表现摘要。
- 指标可作为后续选题优化的辅助输入。
- 指标采集不暴露不必要的个人隐私。
- fake/local metrics 不会被展示或解释为真实平台表现。

明确不做事项：

- 不抓取真实指标。
- 不接真实 Douyin API。
- 不实现 OAuth。
- 不保存 token、API key、secret 或平台账号凭据。
- 不做定时同步。
- 不承诺复杂增长预测。
- 不自动根据指标发布内容。
- 不采集超出用户授权范围的数据。
- 不做数据分析推荐算法。
- 不自动优化内容。
- 不把 fake 指标当成真实表现。

## v0.7 Metrics Review Summary

目标：基于 v0.6.0 已有的 local fake/manual metrics snapshots，为每条 `PublicationRecord` 形成内容复盘摘要，把指标变化转化为用户可读的 review insight，并为下一轮 `TopicCandidate`、`ScriptDraft` 和 `ContentPlan` 提供人工参考输入。

状态：v0.7.0 released。Batch 1 backend-only foundation、Batch 2 frontend UI foundation、Batch 3 stabilization / RC checklist 与 Release finalization 已完成。v0.7.0 release scope 仅限 local fake/manual metrics review summary workflow。

已完成 Batch 1：实现 Metrics Review Summary backend-only domain foundation。该批次新增 `publication_metric_review_summaries` 数据表、backend schemas、API routes、deterministic `FakeMetricsReviewSummaryGenerator` 和 backend tests；支持基于同一项目下现有 `PublicationRecord` 的 `PublicationMetricSnapshot` 列表创建 `fake_local` review summary，查询某个 `PublicationRecord` 下的 summaries，并读取单个 summary。指标字段允许部分为空；没有 metrics snapshots 时生成明确的 no-metrics fake/local summary。archived project 允许读取已有 summary，但禁止创建新的 summary。该批次不新增前端 UI，不接真实 Douyin API，不实现 OAuth，不保存 token / secret / API key，不调用外部服务，不抓取真实指标，不做定时同步，不做自动推荐算法，也不会自动修改 `TopicCandidate`、`ScriptDraft` 或 `ContentPlan`。

已完成 Batch 2：实现 Metrics Review Summary frontend UI foundation。该批次在项目详情页 Publishing / Fake Publishing / metrics snapshots 区块附近展示每条 `PublicationRecord` 关联的 review summaries，并支持用户手动生成 `fake_local` metrics review summary；生成成功后只刷新对应 `PublicationRecord` 的 summaries list。UI 明确展示 fake/local insight、local development / demo / test data、not real Douyin performance、not real platform analysis、not automatic recommendation 和 does not modify content automatically 等边界。archived project 允许查看已有 summaries，但不显示生成入口。该批次不新增后端 API、数据库表、provider 语义、图表库或独立 analytics 页面，不接真实 Douyin API，不实现 OAuth，不保存 token / secret / API key，不抓取真实指标，不做自动推荐算法，也不会自动优化内容或触发上传、发布、排期发布、外部服务调用。

已完成 Batch 3：实现 Metrics Review Summary workflow stabilization / RC checklist。该批次新增 [`docs/checklists/v0.7-metrics-review-summary-rc.md`](checklists/v0.7-metrics-review-summary-rc.md)，补强 backend / frontend 边界测试，并统一 README、README.en.md、路线图和本地开发说明中的 v0.7 RC candidate 状态。该批次不新增大功能、不新增真实平台能力、不改变 Batch 1 / Batch 2 业务语义；继续确认 fake/local metrics review summary 只作为人工复盘参考，不是真实平台分析，不是真实 Douyin 表现，不是自动推荐算法结果，不自动修改 `TopicCandidate`、`ScriptDraft` 或 `ContentPlan`，也不触发上传、发布、排期发布或外部服务调用。

已完成 Release finalization：实现 v0.7.0 Metrics Review Summary release 文档收口和最终质量门禁。该批次只将 README、README.en.md、路线图、v0.7 RC checklist 和本地开发说明从 RC candidate 更新为 v0.7.0 released 状态；不新增业务功能、不新增 API、不新增数据库表、不新增前端功能、不新增 Provider，不修改后端、前端、测试、依赖或锁文件，不创建 Git tag，不 push main，也不 merge main。

范围：

- 基于 `PublicationMetricSnapshot` 的内容表现摘要方向。
- `PublicationRecord` 级复盘说明，例如表现亮点、低表现信号和可人工参考的下一步观察。
- 指标趋势的基础展示或摘要，继续允许指标字段部分为空。
- 将 fake/local metrics 转换为 review insight，但不把 insight 描述为自动推荐算法结果。
- 为下一轮选题、脚本和内容计划提供人工参考，不自动改写或生成优化内容。
- 保留 fake/local metrics source label，避免被误解为真实平台表现。

验收标准：

- 用户可以从已有 fake/local metrics snapshots 查看内容复盘摘要。
- 复盘摘要明确关联到 `PublicationRecord` 和指标来源。
- fake/local insight 明确标记为本地开发、演示或测试数据。
- 复盘信息可以作为人工参考输入，但不会自动修改 `TopicCandidate`、`ScriptDraft` 或 `ContentPlan`。
- archived project 仍保持只读。

明确不做事项：

- 不接真实 Douyin API。
- 不实现 OAuth。
- 不保存 token、API key、secret 或平台账号凭据。
- 不做自动推荐算法。
- 不自动优化内容。
- 不做真实平台 dashboard。
- 不抓取真实指标或定时同步指标。

与上一版本的关系：

- v0.7 直接建立在 v0.6.0 的 `PublicationRecord` metrics snapshots、backend fake metrics provider、metrics API、项目详情页 metrics display、manual fake metrics generation 和 fake/local boundary labels 之上。
- v0.7 不改变真实平台接入边界，仍然是 local fake/manual workflow。

进入下一版本的条件：

- 复盘摘要的字段、来源标记和人工参考边界稳定。
- fake/local insight 不会被 UI、文档或接口描述为真实平台分析。
- 已确认复盘摘要不会绕过 human-in-the-loop publishing 原则，也不会触发自动发布或自动优化。

## v0.8 Provider & Credential Security Foundation

目标：为真实平台接入建立 Provider、OAuth、Credential 和 Secret 管理边界，先解决安全基础和架构基础，再进入抖音 POC。

状态：Planned。Batch 1 为 Provider & Credential Security documentation foundation，Batch 2 为 Provider Registry & Capability Metadata backend foundation，Batch 3 为 Provider Registry frontend read-only UI foundation，Batch 4 为 Provider Connection State & Sensitive Storage Status backend foundation，Batch 5 为 Provider Connection State frontend read-only UI foundation，Batch 6 为 Provider Credential Reference & Secret Redaction backend foundation，Batch 7 为 Provider Credential Reference frontend read-only UI foundation，Batch 8 为 Provider Security Audit Event & Redacted Audit Log backend foundation，Batch 9 为 Provider Security Audit Event frontend read-only UI foundation，Batch 10 为 Provider OAuth State & Callback Boundary backend foundation，Batch 11 为 Provider OAuth Boundary frontend read-only UI foundation，Batch 12 为 Provider Token Lifecycle Boundary backend foundation，Batch 13 为 Provider Token Lifecycle Boundary frontend read-only UI foundation，Batch 14 为 Provider Integration Readiness Summary backend foundation，Batch 15 为 Provider Integration Readiness Summary frontend read-only UI foundation，Batch 16 为 Provider & Credential Security Foundation RC Audit / Closure Checklist；这些批次不代表 v0.8 release 已完成。

Batch 1（已完成）：

- Provider & Credential Security documentation foundation。
- 只更新 README、产品规格、架构、路线图、本地开发说明和 ADR。
- 不新增业务功能。
- 不新增 API。
- 不新增数据库表。
- 不新增后端代码。
- 不新增前端 UI。
- 不实现真实 OAuth。
- 不保存 token。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。

Batch 2（已完成）：

- Provider Registry & Capability Metadata backend foundation。
- backend-only。
- 新增只读 Provider Registry metadata。
- 新增 capability metadata。
- 明确 `fake_local`、`douyin_sandbox` 和 `douyin_real` source separation。
- 明确未实现真实平台能力不得标记为 available。
- API 只返回非敏感 metadata、`connection_status`、capability metadata 和 boundary notes。
- 不实现 OAuth。
- 不保存 token。
- 不新增 Credential storage。
- 不新增数据库表。
- 不新增前端 UI。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。
- 不调用外部服务。

Batch 3（已完成）：

- Provider Registry frontend read-only UI foundation。
- frontend-only 或 frontend + docs only。
- 基于 Batch 2 的只读 `/api/providers` metadata API。
- 在前端展示 provider metadata、source type、connection status、capability metadata 和 boundary notes。
- 明确区分 `fake_local`、`douyin_sandbox` 和 `douyin_real`。
- 明确 planned / unavailable provider 不得显示为可用真实集成。
- 不新增 backend API。
- 不新增数据库表。
- 不实现 OAuth。
- 不保存 token。
- 不新增 Credential storage。
- 不新增 connect / authorize / refresh / revoke / disconnect 操作。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。
- 不调用外部服务。
- 不修改 v0.7.0 release scope。

Batch 4（已完成）：

- Provider Connection State & Sensitive Storage Status backend foundation。
- backend-only。
- 新增 metadata-only provider connection state table。
- 新增只读 provider connection state API。
- 明确 `connection_status`、`authorization_status` 和 `sensitive_storage_status`。
- 明确 `fake_local`、`douyin_sandbox` 和 `douyin_real` source separation。
- 明确 `fake_local` 不要求授权、不需要敏感存储、不是真实 Douyin。
- 明确 `douyin_sandbox` 和 `douyin_real` 当前只是 placeholder metadata。
- 明确 planned / unavailable provider 不得展示或返回为可用真实集成。
- 不新增前端 UI。
- 不实现 OAuth。
- 不保存 token。
- 不保存 secret。
- 不保存 API key。
- 不保存 credential material。
- 不新增真实 Credential storage。
- 不新增 connect / authorize / refresh / revoke / disconnect 写 API。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。
- 不调用外部服务。
- 不修改 v0.7.0 release scope。

Batch 5（已完成）：

- Provider Connection State frontend read-only UI foundation。
- frontend-only 或 frontend + docs only。
- 基于 Batch 4 的只读 `/api/provider-connections` metadata API。
- 在前端展示 provider connection state、source type、implementation status、`connection_status`、`authorization_status`、`sensitive_storage_status`、`safe_status_message` 和 boundary notes。
- 明确区分 `fake_local`、`douyin_sandbox` 和 `douyin_real`。
- 明确 planned / unavailable provider 不得显示为可用真实集成。
- 明确 `can_connect` / `can_refresh` / `can_revoke` / `can_disconnect` 当前均不可执行。
- 不新增 backend API。
- 不修改数据库表。
- 不实现 OAuth。
- 不保存 token。
- 不保存 secret。
- 不保存 API key。
- 不保存 credential material。
- 不新增 Credential storage。
- 不新增 connect / authorize / refresh / revoke / disconnect 操作。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。
- 不调用外部服务。
- 不修改 v0.7.0 release scope。

Batch 6（已完成）：

- Provider Credential Reference & Secret Redaction backend foundation。
- backend-only。
- 新增 metadata-only provider credential reference table。
- 新增只读 provider credential reference metadata API。
- 新增 secret redaction helper。
- 明确 `reference_status`、`storage_status` 和 `redaction_policy_status`。
- 明确 `fake_local`、`douyin_sandbox` 和 `douyin_real` source separation。
- 明确 `fake_local` 不要求 credential、不需要 token、不需要 secret、不是真实 Douyin。
- 明确 `douyin_sandbox` 和 `douyin_real` 当前只是 placeholder metadata。
- 明确 planned / unavailable provider 不得展示或返回为可用真实集成。
- 不新增前端 UI。
- 不实现 OAuth。
- 不保存 token。
- 不保存 secret。
- 不保存 API key。
- 不保存 authorization code。
- 不保存 OAuth client secret。
- 不保存 credential material。
- 不新增真实 Credential storage。
- 不新增 connect / authorize / refresh / revoke / disconnect 写 API。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。
- 不调用外部服务。
- 不修改 v0.7.0 release scope。

Batch 7（已完成）：

- Provider Credential Reference frontend read-only UI foundation。
- frontend-only 或 frontend + docs only。
- 基于 Batch 6 的只读 `/api/provider-credential-references` metadata API。
- 在前端展示 provider credential reference metadata、source type、implementation status、`reference_kind`、`reference_status`、`storage_status`、`redaction_policy_status`、`safe_display_name`、`safe_status_message` 和 boundary notes。
- 明确区分 `fake_local`、`douyin_sandbox` 和 `douyin_real`。
- 明确 planned / unavailable provider 不得显示为可用真实集成。
- 明确 credential reference metadata 不等于真实 Credential storage。
- 明确 `redaction_policy_status` 不等于生产级 KMS、secret manager 或 encrypted token storage。
- 不新增 backend API。
- 不修改数据库表。
- 不新增 secret input 表单。
- 不新增 token viewer。
- 不新增 credential 管理界面。
- 不实现 OAuth。
- 不保存 token。
- 不保存 secret。
- 不保存 API key。
- 不保存 authorization code。
- 不保存 OAuth client secret。
- 不保存 credential material。
- 不新增真实 Credential storage。
- 不新增 connect / authorize / refresh / revoke / disconnect 操作。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。
- 不调用外部服务。
- 不修改 v0.7.0 release scope。

Batch 8（已完成）：

- Provider Security Audit Event & Redacted Audit Log backend foundation。
- backend-only。
- 新增 metadata-only provider security audit events table。
- 新增 backend-only provider security audit event service。
- 新增只读 provider security audit events API。
- 复用 secret redaction helper。
- 明确 `event_type`、`event_status`、`event_severity`、`actor_type` 和 `redaction_status`。
- 明确 `safe_event_message`、`safe_metadata` 和 `boundary_notes` 只能包含非敏感 / redacted metadata。
- 明确 `fake_local`、`douyin_sandbox` 和 `douyin_real` source separation。
- 明确 `fake_local` 只记录 local fake/demo/test audit metadata，不是真实 Douyin。
- 明确 `douyin_sandbox` 和 `douyin_real` 当前只是 placeholder audit metadata。
- 明确 audit log metadata 不等于真实 OAuth audit trail。
- 明确 audit log metadata 不等于生产级 SIEM / compliance log / external log shipping。
- 不新增前端 UI。
- 不实现 OAuth。
- 不新增 OAuth callback route。
- 不新增 OAuth state storage。
- 不保存 token。
- 不保存 secret。
- 不保存 API key。
- 不保存 authorization code。
- 不保存 OAuth client secret。
- 不保存 credential material。
- 不新增真实 Credential storage。
- 不新增 connect / authorize / refresh / revoke / disconnect 写 API。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。
- 不调用外部服务。
- 不修改 v0.7.0 release scope。

Batch 9（已完成）：

- Provider Security Audit Event frontend read-only UI foundation。
- frontend-only 或 frontend + docs only。
- 基于 Batch 8 的只读 `/api/provider-security-audit-events` metadata API。
- 在前端展示 provider security audit events、source type、implementation status、`event_type`、`event_status`、`event_severity`、`actor_type`、`redaction_status`、`safe_event_message`、`safe_metadata`、`boundary_notes` 和 `created_at`。
- 明确区分 `fake_local`、`douyin_sandbox`、`douyin_real`。
- 明确 audit event UI 只展示 redacted / safe metadata。
- 明确 planned / unavailable provider 不得显示为可用真实集成。
- 明确 audit event metadata 不等于真实 OAuth audit trail。
- 明确 `redaction_status` 不等于生产级 SIEM、compliance archive 或 external log shipping。
- 不新增 backend API。
- 不修改数据库表。
- 不新增 audit event 写入 UI。
- 不新增 secret input 表单。
- 不新增 token viewer。
- 不新增 credential 管理界面。
- 不实现 OAuth。
- 不新增 OAuth callback route。
- 不新增 OAuth state storage。
- 不保存 token。
- 不保存 secret。
- 不保存 API key。
- 不保存 authorization code。
- 不保存 OAuth client secret。
- 不保存 credential material。
- 不保存 raw request、raw response 或 raw payload。
- 不新增真实 Credential storage。
- 不新增 connect / authorize / refresh / revoke / disconnect 操作。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。
- 不调用外部服务。
- 不修改 v0.7.0 release scope。

Batch 10（已完成）：

- Provider OAuth State & Callback Boundary backend foundation。
- backend-only。
- 新增 metadata-only provider OAuth boundary table。
- 新增 backend-only provider OAuth boundary metadata service。
- 新增只读 provider OAuth boundary metadata API。
- 明确 `oauth_policy_status`、`state_policy_status`、`callback_policy_status`、`csrf_protection_status`、`redirect_uri_policy_status`、`token_exchange_policy_status`、`token_storage_policy_status`、`error_redaction_policy_status` 和 `audit_event_policy_status`。
- 明确 `fake_local`、`douyin_sandbox`、`douyin_real` source separation。
- 明确 `fake_local` 不要求 OAuth、不要求 state、不要求 callback、不需要 token、不是真实 Douyin。
- 明确 `douyin_sandbox` 和 `douyin_real` 当前只是 OAuth boundary placeholder metadata。
- 明确 OAuth boundary metadata 不等于真实 OAuth implementation。
- 明确 OAuth boundary metadata 不等于真实 callback route。
- 明确 OAuth boundary metadata 不等于真实 state storage。
- 明确 OAuth boundary metadata 不等于 token exchange。
- 不新增前端 UI。
- 不实现 OAuth。
- 不新增 OAuth callback route。
- 不新增 OAuth state storage。
- 不新增 token exchange。
- 不生成真实 provider authorization URL。
- 不保存 token。
- 不保存 secret。
- 不保存 API key。
- 不保存 authorization code。
- 不保存 OAuth client secret。
- 不保存 credential material。
- 不保存 raw request、raw response 或 raw payload。
- 不新增真实 Credential storage。
- 不新增 connect / authorize / refresh / revoke / disconnect 写 API。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。
- 不调用外部服务。
- 不修改 v0.7.0 release scope。

Batch 11（已完成）：

- Provider OAuth Boundary frontend read-only UI foundation。
- frontend-only 或 frontend + docs only。
- 基于 Batch 10 的只读 `/api/provider-oauth-boundaries` metadata API。
- 在前端展示 provider OAuth boundary metadata、source type、implementation status、`oauth_policy_status`、`state_policy_status`、`callback_policy_status`、`csrf_protection_status`、`redirect_uri_policy_status`、`token_exchange_policy_status`、`token_storage_policy_status`、`error_redaction_policy_status`、`audit_event_policy_status`、`safe_status_message` 和 boundary notes。
- 明确区分 `fake_local`、`douyin_sandbox`、`douyin_real`。
- 明确 OAuth boundary UI 只展示非敏感 policy/status metadata。
- 明确 planned / unavailable provider 不得显示为可用真实集成。
- 明确 OAuth boundary metadata 不等于真实 OAuth implementation。
- 明确 OAuth boundary metadata 不等于真实 callback route。
- 明确 OAuth boundary metadata 不等于真实 state storage。
- 明确 OAuth boundary metadata 不等于 token exchange。
- 明确 frontend 不提供 OAuth authorize / callback / connect / token lifecycle 操作。
- 不新增 backend API。
- 不修改数据库表。
- 不新增 OAuth start / authorize / callback UI。
- 不新增 secret input 表单。
- 不新增 token viewer。
- 不新增 credential 管理界面。
- 不实现 OAuth。
- 不新增 OAuth callback route。
- 不新增 OAuth state storage。
- 不新增 token exchange。
- 不生成真实 provider authorization URL。
- 不保存 token。
- 不保存 secret。
- 不保存 API key。
- 不保存 authorization code。
- 不保存 OAuth client secret。
- 不保存 OAuth state value。
- 不保存 credential material。
- 不保存 raw request、raw response 或 raw payload。
- 不新增真实 Credential storage。
- 不新增 connect / authorize / refresh / revoke / disconnect 操作。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。
- 不调用外部服务。
- 不修改 v0.7.0 release scope。

Batch 12（已完成）：

- Provider Token Lifecycle Boundary backend foundation。
- backend-only。
- 新增 metadata-only provider token lifecycle boundary table。
- 新增 backend-only provider token lifecycle boundary metadata service。
- 新增只读 provider token lifecycle boundary metadata API。
- 明确 `token_lifecycle_policy_status`、`token_storage_policy_status`、`refresh_policy_status`、`expiry_policy_status`、`revoke_policy_status`、`disconnect_policy_status`、`rotation_policy_status`、`error_redaction_policy_status` 和 `audit_event_policy_status`。
- 明确 `fake_local`、`douyin_sandbox`、`douyin_real` source separation。
- 明确 `fake_local` 不要求 token、不要求 refresh、不要求 revoke、不要求 disconnect、不是真实 Douyin。
- 明确 `douyin_sandbox` 和 `douyin_real` 当前只是 token lifecycle boundary placeholder metadata。
- 明确 token lifecycle boundary metadata 不等于真实 token storage。
- 明确 token lifecycle boundary metadata 不等于真实 token refresh。
- 明确 token lifecycle boundary metadata 不等于真实 token revoke。
- 明确 token lifecycle boundary metadata 不等于 disconnect implementation。
- 不新增前端 UI。
- 不实现 OAuth。
- 不新增 OAuth callback route。
- 不新增 OAuth state storage。
- 不新增 token exchange。
- 不生成真实 provider authorization URL。
- 不保存 access token。
- 不保存 refresh token。
- 不保存 token value。
- 不保存 secret。
- 不保存 API key。
- 不保存 authorization code。
- 不保存 OAuth client secret。
- 不保存 OAuth state value。
- 不保存 credential material。
- 不保存 raw request、raw response 或 raw payload。
- 不新增真实 Credential storage。
- 不新增 token refresh / revoke / disconnect 写 API。
- 不新增 connect / authorize / refresh / revoke / disconnect 写 API。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。
- 不调用外部服务。
- 不修改 v0.7.0 release scope。

Batch 13（已完成）：

- Provider Token Lifecycle Boundary frontend read-only UI foundation。
- frontend-only 或 frontend + docs only。
- 基于 Batch 12 的只读 `/api/provider-token-lifecycle-boundaries` metadata API。
- 在前端展示 provider token lifecycle boundary metadata、source type、implementation status、`token_lifecycle_policy_status`、`token_storage_policy_status`、`refresh_policy_status`、`expiry_policy_status`、`revoke_policy_status`、`disconnect_policy_status`、`rotation_policy_status`、`error_redaction_policy_status`、`audit_event_policy_status`、`safe_status_message` 和 boundary notes。
- 明确区分 `fake_local`、`douyin_sandbox`、`douyin_real`。
- 明确 Token Lifecycle UI 只展示非敏感 policy/status metadata。
- 明确 planned / unavailable provider 不得显示为可用真实集成。
- 明确 token lifecycle boundary metadata 不等于真实 token storage。
- 明确 token lifecycle boundary metadata 不等于真实 token refresh。
- 明确 token lifecycle boundary metadata 不等于真实 token revoke。
- 明确 token lifecycle boundary metadata 不等于 disconnect implementation。
- 明确 frontend 不提供 refresh / revoke / disconnect / rotation 操作。
- 不新增 backend API。
- 不修改数据库表。
- 不新增 refresh token UI。
- 不新增 revoke token UI。
- 不新增 disconnect UI。
- 不新增 token viewer。
- 不新增 secret input 表单。
- 不新增 credential 管理界面。
- 不实现 OAuth。
- 不新增 OAuth callback route。
- 不新增 OAuth state storage。
- 不新增 token exchange。
- 不生成真实 provider authorization URL。
- 不保存 access token。
- 不保存 refresh token。
- 不保存 token value。
- 不保存 secret。
- 不保存 API key。
- 不保存 authorization code。
- 不保存 OAuth client secret。
- 不保存 OAuth state value。
- 不保存 credential material。
- 不保存 raw request、raw response 或 raw payload。
- 不保存 token expiry value、token refresh response、token revoke response 或 provider token response。
- 不新增真实 Credential storage。
- 不新增 connect / authorize / refresh / revoke / disconnect 操作。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。
- 不调用外部服务。
- 不修改 v0.7.0 release scope。

Batch 14（已完成）：

- Provider Integration Readiness Summary backend foundation。
- backend-only。
- 新增 backend-only provider integration readiness summary service。
- 新增只读 provider readiness summary API。
- 不新增数据库表。
- 聚合 Provider Registry、Connection State、Credential Reference、Security Audit、OAuth Boundary、Token Lifecycle Boundary 的非敏感 metadata。
- 明确 `overall_readiness_status`、`v0_9_poc_readiness_status`、`readiness_items`、`blocking_reasons`、`next_safe_steps`、`safe_summary` 和 `boundary_notes`。
- 明确 `fake_local`、`douyin_sandbox`、`douyin_real` source separation。
- 明确 `fake_local` 只代表 local fake/demo/test workflow，不是真实 Douyin readiness。
- 明确 `douyin_sandbox` 和 `douyin_real` 当前只是 placeholder / metadata-only readiness。
- 明确 readiness summary 不等于真实 OAuth、真实 token storage、真实指标读取、真实发布或真实 v0.9 POC 已完成。
- 不新增前端 UI。
- 不实现 OAuth。
- 不新增 OAuth callback route。
- 不新增 OAuth state storage。
- 不新增 token exchange。
- 不生成真实 provider authorization URL。
- 不保存 access token。
- 不保存 refresh token。
- 不保存 token value。
- 不保存 secret。
- 不保存 API key。
- 不保存 authorization code。
- 不保存 OAuth client secret。
- 不保存 OAuth state value。
- 不保存 credential material。
- 不保存 raw request、raw response 或 raw payload。
- 不保存 token expiry value、token refresh response、token revoke response 或 provider token response。
- 不新增真实 Credential storage。
- 不新增 token refresh / revoke / disconnect 写 API。
- 不新增 connect / authorize / refresh / revoke / disconnect 写 API。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。
- 不调用外部服务。
- 不修改 v0.7.0 release scope。

Batch 15（已完成）：

- Provider Integration Readiness Summary frontend read-only UI foundation。
- frontend-only 或 frontend + docs only。
- 基于 Batch 14 的只读 `/api/provider-readiness-summaries` metadata API。
- 在前端展示 provider readiness summary metadata、source type、implementation status、`overall_readiness_status`、`v0_9_poc_readiness_status`、`readiness_items`、`blocking_reasons`、`next_safe_steps`、`safe_summary` 和 boundary notes。
- 明确区分 `fake_local`、`douyin_sandbox`、`douyin_real`。
- 明确 Readiness Summary UI 只展示非敏感 readiness metadata。
- 明确 `fake_local` local readiness 不等于真实 Douyin readiness。
- 明确 `douyin_sandbox` 和 `douyin_real` 当前只是 metadata-only / placeholder readiness。
- 明确 readiness summary 不等于真实 OAuth、真实 token storage、真实指标读取、真实发布或真实 v0.9 POC 已完成。
- 明确 frontend 不提供 readiness override / approve / certify 操作。
- 不新增 backend API。
- 不修改数据库表。
- 不新增 readiness 写入 UI。
- 不新增 secret input 表单。
- 不新增 token viewer。
- 不新增 credential 管理界面。
- 不实现 OAuth。
- 不新增 OAuth callback route。
- 不新增 OAuth state storage。
- 不新增 token exchange。
- 不生成真实 provider authorization URL。
- 不保存 access token。
- 不保存 refresh token。
- 不保存 token value。
- 不保存 secret。
- 不保存 API key。
- 不保存 authorization code。
- 不保存 OAuth client secret。
- 不保存 OAuth state value。
- 不保存 credential material。
- 不保存 raw request、raw response 或 raw payload。
- 不保存 token expiry value、token refresh response、token revoke response 或 provider token response。
- 不新增真实 Credential storage。
- 不新增 connect / authorize / refresh / revoke / disconnect 操作。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不上传、不发布、不排期发布。
- 不调用外部服务。
- 不修改 v0.7.0 release scope。

Batch 16（本批）：

- Provider & Credential Security Foundation RC Audit / Closure Checklist。
- docs-only。
- 新增 v0.8 Provider & Credential Security Foundation RC checklist。
- 新增 v0.8 closure / RC audit ADR。
- 梳理 Batch 1-15 的 branch、commit、scope、测试门禁和边界确认。
- 梳理只读 API：`/api/providers`、`/api/provider-connections`、`/api/provider-credential-references`、`/api/provider-security-audit-events`、`/api/provider-oauth-boundaries`、`/api/provider-token-lifecycle-boundaries`、`/api/provider-readiness-summaries`。
- 梳理只读 frontend panels：Provider Registry、Connection State、Credential Reference、Security Audit、OAuth Boundary、Token Lifecycle Boundary、Integration Readiness Summary。
- 梳理 metadata-only DB 表与 response schema 的敏感字段禁入边界。
- 明确 v0.8 仍不等于真实 Douyin 接入、不等于 OAuth implementation、不等于 token storage、不等于真实指标读取、不等于真实发布、不等于 v0.9 POC 已完成。
- 明确 README 仍保持当前稳定版本为 `v0.7.0`。
- 明确 v0.9 才进入 Douyin Provider POC / Sandbox Integration。
- 不新增业务代码。
- 不新增 backend API。
- 不修改数据库表。
- 不新增前端 UI。
- 不新增真实 Provider。
- 不实现 OAuth。
- 不新增 token lifecycle workflow。
- 不接真实 Douyin。
- 不创建 `v0.8.0` tag。
- 不声明 v0.8 已 release。
- 不进入 v0.9 POC 开发。
- 不修改 v0.7.0 release scope。

范围：

- `PlatformProvider` registry 或等价 Provider registry 抽象方向。
- Provider capability metadata，例如 `supports_oauth`、`supports_metrics_read`、`supports_publish_prepare`、`supports_real_publish` 和 `supports_sandbox`。
- Credential model、secret boundary 和本地安全存储策略方向。
- OAuth state、callback、CSRF 防护、错误回跳和授权状态边界设计。
- access token / refresh token 加密保存策略方向。
- token refresh、expiry、revoke 和 disconnect 生命周期策略方向。
- audit log、connection status、授权失败状态和断开连接方向。
- fake/local provider 与 future real provider 的隔离，确保 `fake_local`、`douyin_sandbox` 和 `douyin_real` 等 source 不会互相伪装。
- 错误状态方向：未连接、授权失败、token 过期、权限不足和 provider 接口失败。

验收标准：

- Provider registry 和 capability metadata 的边界可审查。
- Credential 与 secret 不进入 Git、不进入日志、不暴露给前端、不进入测试快照或错误响应。
- OAuth state / callback 安全边界有明确设计。
- token 保存、刷新、过期、撤销和断开连接的生命周期有明确策略。
- fake/local、sandbox/mock 和 future real provider 的 source、授权状态和错误语义清晰隔离。

明确不做事项：

- 不新增真实平台业务 workflow。
- 不新增写 API 或真实平台数据 API。
- 不新增可承载敏感值的数据库表。
- 不新增真实 Provider adapter、OAuth 实现或 Credential storage 代码。
- 不新增会改变连接、授权、credential、发布或真实平台数据状态的前端 UI。
- 不实现真实 OAuth。
- 不保存 token、API key、secret、refresh token 或 credential。
- 不接真实 Douyin API。
- 不抓取真实指标。
- 不定时同步指标。
- 不调用外部服务。
- 不真实发布。
- 不上传真实视频。
- 不排期发布。
- 不自动发布。
- 不绕过平台授权。
- 不把 token、API key、secret 或 refresh token 写入 Git。
- 不把真实平台能力伪装成已完成。
- 不做生产部署、Docker 文件或 GitHub Actions。

与上一版本的关系：

- v0.8 接在 v0.7 的 metrics review summary 之后，补齐真实平台接入前必须具备的安全和 Provider 边界。
- v0.8 可以继续保留 fake/local workflow 作为默认可用路径，真实平台能力仍不承诺可用。

进入下一版本的条件：

- Credential、OAuth、token lifecycle 和 provider capability metadata 的设计经过审查。
- 安全边界能够支持 Douyin sandbox/mock POC，而不要求真实 token 进入仓库或前端。
- fake/local workflow 在没有授权时仍可用。

## v0.9 Douyin Provider POC / Sandbox Integration

目标：进行抖音 Provider 最小可行接入预研与 POC，验证 Provider contract、OAuth 回调和最小指标读取路径；该版本面向开发者/内部测试，不承诺用户级稳定可用。

状态：Planned。

范围：

- Douyin provider adapter skeleton，遵守 v0.8 的 Provider registry、credential boundary 和 capability metadata。
- Douyin open platform app configuration guide。
- OAuth callback smoke test 或 mock/sandbox callback 验证。
- account connection status 和授权错误状态方向。
- token refresh dry-run 或 sandbox 验证，前提是平台权限允许。
- 最小真实指标读取 POC，前提是平台开放能力、应用审核、OAuth scope 和 API 权限允许。
- 如果真实 API 权限不可用，则使用 manual import 或 mock/sandbox provider contract test 作为 fallback。
- 明确区分 `fake_local`、`douyin_sandbox` 和 `douyin_real` source，不混淆来源。

验收标准：

- Douyin provider POC 可以在 sandbox/mock 条件下验证 Provider contract。
- OAuth callback 或 mock callback 的 smoke test 能明确成功、失败和 state 校验路径。
- account connection status 能表达未连接、已连接、授权失败、token 过期或权限不足等状态方向。
- 在平台权限允许时，至少一种真实指标读取路径被 POC 验证；权限不可用时，有 manual import 或 mock/sandbox contract test fallback。
- 文档明确 Douyin API 权限、应用审核和平台可用性是风险项。

明确不做事项：

- 不承诺生产级真实发布。
- 不做自动发布。
- 不做大规模定时同步。
- 不做多账号矩阵运营。
- 不做商业 dashboard。
- 不绕过平台 API 权限或审核。
- 不采集未授权账号数据。
- 不把 sandbox/mock 结果描述成真实用户可用能力。

与上一版本的关系：

- v0.9 使用 v0.8 建立的 Provider、Credential、OAuth 和 token lifecycle 边界进行 Douyin POC。
- v0.9 仍保留 fake/local workflow；当 Douyin 权限不可用或授权失败时，系统必须能回退到 manual import 或 mock/sandbox provider contract test。

进入下一版本的条件：

- Douyin app 配置、OAuth callback、授权状态和 token refresh 风险已被验证或明确记录。
- 至少一种指标读取路径完成真实、sandbox、mock 或 manual import fallback 验证。
- source 标记、授权状态和错误提示不会混淆 `fake_local`、`douyin_sandbox` 与 `douyin_real`。
- 平台 API 权限风险已形成 v1.0 用户测试 checklist 的前置条件。

## v1.0 Douyin Integration User Test Release

目标：达到可以进行用户抖音接入测试的 v1.0.0 版本，验证用户授权、账号连接状态和至少一种真实或 sandbox/manual fallback 指标回流路径。v1.0.0 是 User Test Release，不是生产级自动化运营或自动发布版本。

状态：Planned。

范围：

- 用户可以配置 Douyin provider，前提是平台应用配置和权限满足用户测试要求。
- 用户可以完成 OAuth 授权，所有真实平台能力都必须经过用户授权。
- 系统可以安全保存并刷新 token，且 token、secret、refresh token 不进入 Git、日志或前端。
- 系统可以验证授权账号状态，并展示连接、授权失败、token 过期、权限不足或接口失败等错误提示。
- 系统可以读取至少一种真实指标，例如 `views`、`likes`、`comments` 或 `shares` 中的一种或多种，具体取决于平台权限。
- 真实或 sandbox/manual fallback 指标可以保存为 `PublicationMetricSnapshot`，并明确显示 source，例如 `douyin_real`、`douyin_sandbox` 或 `fake_local`。
- 没有授权或授权失败时，fake/local workflow 仍可用。
- 具备 Douyin integration user test checklist。

验收标准：

- 用户测试人员可以按文档配置 Douyin provider 并完成授权或明确看到失败原因。
- 授权账号状态可验证，token 过期、权限不足和接口失败有明确错误提示。
- 在平台权限允许时，至少一种真实 Douyin 指标可以回流为 `PublicationMetricSnapshot`；权限不可用时，manual import 或 sandbox/mock provider contract test fallback 可用于验证流程边界。
- UI 和文档不会混淆 `fake_local` 与 `douyin_real` / `douyin_sandbox`。
- 未授权状态下，本地 fake/manual workflow 继续可用。
- human-in-the-loop publishing 原则仍保留，任何公开发布、上传或排期发布都需要用户审核与明确确认。

明确不做事项：

- 不承诺生产级自动发布。
- 不承诺批量发布。
- 不承诺定时发布。
- 不承诺大规模定时指标同步。
- 不承诺多账号矩阵运营。
- 不承诺自动内容优化。
- 不承诺商业级 dashboard。
- 不绕过平台审核、权限或授权范围。
- 不采集未授权账号数据。

与上一版本的关系：

- v1.0 基于 v0.9 的 Douyin Provider POC / Sandbox Integration，把已验证的 Provider、OAuth、token lifecycle、connection status 和 metrics fallback 边界整理为用户测试版本。
- v1.0 不是把 sandbox/mock 能力直接宣布为生产能力；真实 Douyin 接入仍取决于平台开放能力、应用审核、OAuth、API 权限与用户授权。

进入下一版本的条件：

- 用户测试 checklist 完成，真实或 fallback 指标回流路径、错误提示和 source 标记经过验证。
- token 和 secret 安全边界经过审查，确认不会进入 Git、日志、前端或测试 fixtures。
- 平台权限风险、授权失败风险和 fallback 方案已记录。
- v1.0 用户测试反馈可以支持后续定义生产级能力，但后续版本仍必须保留人工确认发布原则。
