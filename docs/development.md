# 本地开发

本文档面向 v0.5 Publishing workflow Release Candidate 本地开发状态，说明如何在 Windows 11 和 PowerShell 下启动本地 backend、frontend，并验证内容项目、素材导入、ContentPlan / GenerationSchedule / Manual GenerationRun backend foundation 与 frontend UI foundation、Review Draft backend foundation 与 frontend UI foundation、PublishIntent / PublicationRecord backend foundation、PublishIntent confirm backend workflow、FakePublisherProvider backend workflow、项目详情页本地 fake publishing workflow、Topic Candidate、Script Draft、Storyboard、fake render job、fake subtitle draft 和 fake preview manifest metadata 工作流。v0.5 当前只新增发布意图、发布记录、确认流转、本地 fake publisher execution 和项目详情页 UI 接入，已进入 Release Candidate，并已完成 release validation / tag preparation 文档收口；仍不接真实 Douyin API，不实现 OAuth，不保存 token / secret / API key，不上传、不发布、不排期、不自动发布，也不接真实 PublisherProvider。

## 环境要求

- Windows 11 + PowerShell。
- Python 3.11 或更高版本。
- Node.js 20 或更高版本。
- npm 10 或更高版本。

如果 PowerShell 执行策略拦截 `npm`，请使用 `npm.cmd`。

## 脚本快捷入口

以下脚本都从仓库根目录运行，面向 Windows PowerShell：

```powershell
.\scripts\dev-backend.ps1
.\scripts\dev-frontend.ps1
.\scripts\test-backend.ps1
.\scripts\build-frontend.ps1
.\scripts\smoke-api.ps1
```

- `dev-backend.ps1`：进入 `backend`，确保 `.venv` 可用，安装 backend 依赖并启动 `uvicorn`。
- `dev-frontend.ps1`：进入 `frontend`，缺少 `node_modules` 时执行 `npm.cmd install`，然后启动 Vite dev server。
- `test-backend.ps1`：运行 backend pytest。
- `build-frontend.ps1`：运行 frontend production build。
- `smoke-api.ps1`：假设 backend 已运行在 `http://127.0.0.1:8000`，执行最小 API smoke checks。

如果 PowerShell 拒绝执行本地脚本，可以只对本仓库脚本解除阻止：

```powershell
Get-ChildItem .\scripts\*.ps1 | Unblock-File
```

也可以使用后文的手动命令作为 fallback。

## v0.5 Release Candidate 质量门禁

v0.5 RC 收口不接真实平台、不新增真实发布能力。release readiness 说明见 [`docs/releases/v0.5-rc-checklist.md`](releases/v0.5-rc-checklist.md)。合并或发布候选验收时建议从仓库根目录执行：

```powershell
cd .\backend
.\.venv\Scripts\python.exe -m pytest

cd ..\frontend
npm.cmd run test -- --run
npm.cmd run build

cd ..
git diff --check
git status --short
```

同时执行安全扫描，确认没有真实密钥、token、API key、secret、私钥、本机绝对路径、SQLite DB、`uploads/`、`node_modules/`、`.venv/`、`dist/`、生成媒体或运行时 preview artifacts 进入 Git。若扫描命中文档中的运行时路径说明，例如 `data/local/creator_flow.sqlite3`、`uploads/` 或 `data/local/render_previews/`，应确认它们只是文档说明或测试中的 fake metadata 字符串，而不是实际运行时文件。

## 启动 Backend

```powershell
cd .\backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

预期返回：

```json
{
  "status": "ok"
}
```

## 启动 Frontend

另开一个 PowerShell：

```powershell
cd .\frontend
npm.cmd install
npm.cmd run dev
```

默认访问地址：

```text
http://localhost:5173
```

如果 backend 不是运行在 `http://localhost:8000`，可以在启动 frontend 前设置：

```powershell
$env:VITE_API_BASE_URL = "http://127.0.0.1:8000"
npm.cmd run dev
```

## 本地数据位置

- SQLite 数据库：`data/local/creator_flow.sqlite3`
- 上传文件：`uploads/{project_id}/`

这些运行时数据不得提交到 Git。仓库只保留 `data/local/.gitkeep` 和 `uploads/.gitkeep` 作为目录占位。

## 运行 Backend Tests

```powershell
cd .\backend
.\.venv\Scripts\Activate.ps1
python -m pytest
```

如果使用 `uv` 管理本地 Python 环境，也可以运行：

```powershell
cd .\backend
uv run --extra test pytest
```

当前 backend tests 覆盖：

- health endpoint。
- 项目创建、更新、归档、列表筛选和详情查询。
- 文本、链接和文件素材导入。
- 图片上传成功后的文件引用与项目状态更新。
- 超过 10 MB 的文件上传拒绝与残留文件清理。
- 非法文件素材类型和不允许的 MIME 类型拒绝。
- archived 项目禁止继续添加文本、链接或文件素材。
- ContentPlan create / list / read / update / enable / disable，以及 missing / archived project 边界。
- GenerationSchedule create / list / read / update / enable / disable，以及 missing / archived project、missing / cross-project content plan 边界。
- GenerationRun backend-only manual trigger create / list / read，以及 missing / archived project、missing / cross-project content plan、missing / cross-project schedule 边界。
- Review Draft list / read / approve / reject，以及 pending_review placeholder、archived project、cross-project 访问和 approve / reject 无副作用边界。
- PublishIntent create / list / read / cancel / confirm / fake publish，以及必须基于同项目 approved Review Draft、archived project 只读、cross-project 访问 404、confirm 创建 `not_started` PublicationRecord placeholder、fake publish 更新为本地 `succeeded`、Review Draft 状态不变和无真实发布 / 上传 / OAuth / 真实 Provider 副作用边界。
- 项目详情页 Publishing / Fake Publishing UI，覆盖 approved Review Draft 创建 PublishIntent、pending 确认与取消、confirmed 后查看 PublicationRecord、执行本地 Fake Publish、fake succeeded 提示，以及 archived 项目只读。
- ContentPlan / GenerationSchedule / Manual GenerationRun frontend UI list/create/enable/disable/manual trigger，以及 trigger 成功后刷新 GenerationRuns 和 Review Drafts。
- Review Draft frontend UI list/status 展示、热点来源 fallback、approve / reject 成功后刷新，以及 archived 项目只读。
- v0.4 project detail frontend component extraction，确保拆分后的 ContentPlan、GenerationSchedule、GenerationRun 和 Review Draft 组件行为不变。
- v0.4 RC checklist 覆盖 local fake/manual workflow、archived read-only、manual run refresh，以及未实现 scheduled `GenerationRun`、Scheduler / Trigger Engine、真实媒体、真实 Provider、发布和上传的边界。
- Topic Candidate、Script Draft、Storyboard、FakeRenderer、FakeSubtitle、fake preview manifest metadata 和对应 frontend UI 的本地 deterministic workflow。

## API Smoke Checklist

先启动 backend：

```powershell
.\scripts\dev-backend.ps1
```

另开一个 PowerShell，运行：

```powershell
.\scripts\smoke-api.ps1
```

smoke 脚本会验证：

- `GET /api/health`。
- 创建项目。
- 更新项目标题和描述。
- 添加文本素材。
- 添加链接素材。
- 查询项目详情和素材列表。
- 归档项目。
- 默认项目列表不返回 archived 项目。
- `include_archived=true` 返回 archived 项目。

smoke 脚本会写入本地 SQLite 运行时数据；这些数据位于 Git 忽略路径中，不得提交。

## Backend ContentPlan API 验证

v0.4 Batch 1 新增了 backend-only 的项目级 ContentPlan API。该后端 API 只保存本地配置，不触发 Scheduler，不创建 `GenerationSchedule` 或 `GenerationRun`，不自动生成草稿，不接热点源、发布能力或真实 AI Provider。

可以在 backend 启动后用 PowerShell 手动验证：

```powershell
$project = Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/projects `
  -ContentType "application/json" `
  -Body '{"title":"ContentPlan API test","description":"Local content plan verification"}'

$plan = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans" `
  -ContentType "application/json" `
  -Body '{"name":"Weekly AI dev log","account_positioning":"Chinese developer sharing practical AI workflow notes","content_type":"programmer_real_problem","target_frequency_per_week":3,"preferences":"{\"tone\":\"practical\"}"}'

Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans"

Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans/$($plan.id)"

Invoke-RestMethod -Method Patch "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans/$($plan.id)" `
  -ContentType "application/json" `
  -Body '{"target_frequency_per_week":5,"preferences":"{\"tone\":\"calm\"}"}'

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans/$($plan.id)/disable"
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans/$($plan.id)/enable"
```

`target_frequency_per_week` 当前限制为 1 到 14。如果项目不存在会返回 `404`；如果项目已归档，create / update / enable / disable 会返回 `409`，但仍允许读取已有 ContentPlan。ContentPlan 只是配置，不会改变项目状态，也不会生成视频、音频、字幕、草稿或任何媒体文件。

## Backend GenerationSchedule API 验证

v0.4 Batch 2 新增了 backend-only 的项目级 GenerationSchedule API。Schedule 必须绑定到同一项目下的现有 ContentPlan；该后端 API 只保存本地配置，不执行定时任务，不创建 `GenerationRun`，不自动生成草稿，不接 Scheduler / Trigger Engine、热点源、Notification Service、发布能力或真实 AI Provider。

可以在 backend 启动后用 PowerShell 手动验证：

```powershell
$project = Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/projects `
  -ContentType "application/json" `
  -Body '{"title":"GenerationSchedule API test","description":"Local schedule verification"}'

$plan = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans" `
  -ContentType "application/json" `
  -Body '{"name":"Weekly AI dev log","account_positioning":"Chinese developer sharing practical AI workflow notes","content_type":"programmer_real_problem","target_frequency_per_week":3,"preferences":"{\"tone\":\"practical\"}"}'

$schedule = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans/$($plan.id)/generation-schedules" `
  -ContentType "application/json" `
  -Body '{"timezone":"Asia/Shanghai","preferred_days":"[\"mon\",\"wed\",\"fri\"]","preferred_time":"09:30"}'

Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/generation-schedules"

Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/generation-schedules/$($schedule.id)"

Invoke-RestMethod -Method Patch "http://127.0.0.1:8000/api/projects/$($project.id)/generation-schedules/$($schedule.id)" `
  -ContentType "application/json" `
  -Body '{"frequency_per_week":5,"timezone":"Asia/Shanghai","preferred_time":"10:15"}'

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/generation-schedules/$($schedule.id)/disable"
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/generation-schedules/$($schedule.id)/enable"
```

如果创建 schedule 时省略 `frequency_per_week`，后端会沿用 ContentPlan 的 `target_frequency_per_week`；显式传入时仍限制为 1 到 14。`preferred_time` 使用 `HH:mm`。如果项目不存在会返回 `404`；如果 ContentPlan 不存在或属于其他项目，会返回 `404 content plan not found`；如果项目已归档，create / update / enable / disable 会返回 `409`，但仍允许读取已有 schedules。GenerationSchedule 只是配置，不会改变项目状态，也不会创建 `GenerationRun`、草稿、视频、音频、字幕或任何媒体文件。

## Backend GenerationRun API 验证

v0.4 Batch 3 新增了 backend-only 的 fake manual GenerationRun API。GenerationRun 必须绑定到同一项目下的现有 ContentPlan，可选绑定同一 ContentPlan 下的 GenerationSchedule。该后端 API 只记录一次 deterministic fake manual run，不执行 scheduled trigger，不实现 Scheduler / Trigger Engine，不创建真实 Topic Candidate、Script Draft、Storyboard、Render Job、Subtitle Draft、媒体文件、Review Queue 任务，不接热点源、发布能力或真实 AI Provider。

可以在 backend 启动后用 PowerShell 手动验证：

```powershell
$project = Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/projects `
  -ContentType "application/json" `
  -Body '{"title":"GenerationRun API test","description":"Local manual run verification"}'

$plan = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans" `
  -ContentType "application/json" `
  -Body '{"name":"Weekly AI dev log","account_positioning":"Chinese developer sharing practical AI workflow notes","content_type":"programmer_real_problem","target_frequency_per_week":3,"preferences":"{\"tone\":\"practical\"}"}'

$schedule = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans/$($plan.id)/generation-schedules" `
  -ContentType "application/json" `
  -Body '{"timezone":"Asia/Shanghai","preferred_days":"[\"mon\",\"wed\",\"fri\"]","preferred_time":"09:30"}'

$run = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans/$($plan.id)/generation-runs" `
  -ContentType "application/json" `
  -Body "{}"

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans/$($plan.id)/generation-runs" `
  -ContentType "application/json" `
  -Body ('{"generation_schedule_id":' + $schedule.id + '}')

Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/generation-runs"

Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/generation-runs/$($run.id)"
```

POST API 当前只允许 `manual` trigger；如果传入 `scheduled` 会返回 `422`。如果项目不存在会返回 `404`；如果 ContentPlan 不存在或属于其他项目，会返回 `404 content plan not found`；如果 GenerationSchedule 不存在、属于其他项目或不属于当前 ContentPlan，会返回 `404 generation schedule not found`；如果项目已归档，创建 run 会返回 `409`，但仍允许读取已有 GenerationRun。成功创建的 fake manual run 会同步标记为 `succeeded`，写入 deterministic `input_summary` 和 `result_summary`，并创建 1 条 `pending_review` 的 `review_drafts` placeholder；它不会改变项目状态，也不会创建真实 Topic Candidate、Script Draft、Storyboard、Render Job、Subtitle Draft、视频、音频、字幕、上传文件或发布动作。

## Backend Review Draft API 验证

v0.4 Batch 4 新增了 backend-only 的 Review Draft placeholder。Review Draft 用于承接 fake manual GenerationRun 的 deterministic fake output；当前只进入 `pending_review`，不自动发布，不上传，不渲染，不接真实 Provider，也不实现完整 Review Queue UI。

可以在 backend 启动后用 PowerShell 手动验证：

```powershell
$project = Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/projects `
  -ContentType "application/json" `
  -Body '{"title":"ReviewDraft API test","description":"Local review draft verification"}'

$plan = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans" `
  -ContentType "application/json" `
  -Body '{"name":"Weekly AI dev log","account_positioning":"Chinese developer sharing practical AI workflow notes","content_type":"programmer_real_problem","target_frequency_per_week":3,"preferences":"{\"tone\":\"practical\"}"}'

$run = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans/$($plan.id)/generation-runs" `
  -ContentType "application/json" `
  -Body "{}"

$drafts = Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/review-drafts"
$draft = Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/review-drafts/$($drafts[0].id)"

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/review-drafts/$($draft.id)/approve"
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/review-drafts/$($draft.id)/reject"
```

Review Draft 内容只来自 ContentPlan、可选 GenerationSchedule 和 GenerationRun summary；`hotspot_source_summary` 当前为空，不读取外部热点、私有账号、ChatGPT 历史、本地文件或浏览器数据。archived 项目仍允许读取已有 review drafts，但 approve / reject 会返回 `409`。approve / reject 只改变 `review_status`，不会创建 render jobs、subtitle drafts、上传文件、媒体文件或发布记录。

## Backend PublishIntent / PublicationRecord API 验证

v0.5 Batch 2 新增了 backend-only 的 PublishIntent / PublicationRecord 领域基础，Batch 3 补充了 confirm backend workflow，Batch 4 补充了本地 FakePublisherProvider execution workflow，Batch 5 接入了项目详情页 Publishing / Fake Publishing UI，Batch 6 完成 RC checklist 收口，Final validation 完成 release readiness 文档收口。PublishIntent 只能基于同一项目内已 `approved` 的 Review Draft 显式创建；Review Draft approved 本身不会自动创建 PublishIntent，也不会触发发布、上传或排期发布。confirm 只把 PublishIntent 状态改为 `confirmed`，并创建 1 条本地 `not_started` 的 PublicationRecord placeholder。fake publish 只调用 deterministic `FakePublisherProvider`，把本地 PublicationRecord 更新为 `succeeded` 并写入 fake external publication id；不接真实 PublisherProvider。

可以在 backend 启动后用 PowerShell 手动验证：

```powershell
$project = Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/projects `
  -ContentType "application/json" `
  -Body '{"title":"PublishIntent API test","description":"Local publishing domain verification"}'

$plan = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans" `
  -ContentType "application/json" `
  -Body '{"name":"Weekly AI dev log","account_positioning":"Chinese developer sharing practical AI workflow notes","content_type":"programmer_real_problem","target_frequency_per_week":3,"preferences":"{\"tone\":\"practical\"}"}'

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/content-plans/$($plan.id)/generation-runs" `
  -ContentType "application/json" `
  -Body "{}"

$drafts = Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/review-drafts"
$draft = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/review-drafts/$($drafts[0].id)/approve"

$intent = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/publish-intents" `
  -ContentType "application/json" `
  -Body ('{"review_draft_id":' + $draft.id + ',"target_platform":"douyin","title":"Publish metadata draft","caption":"Backend-only publish intent."}')

Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/publish-intents"
Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/publish-intents/$($intent.id)"
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/publish-intents/$($intent.id)/confirm"
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/publish-intents/$($intent.id)/fake-publish"
Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/publish-intents/$($intent.id)/publication-records"
```

如果 Review Draft 不存在、属于其他项目或不是 `approved`，创建 PublishIntent 会返回错误；如果项目已归档，create / cancel / confirm / fake publish 会返回 `409`，但仍允许读取已有 PublishIntent 和 PublicationRecord list。创建 PublishIntent 只写入 `publish_intents`；confirm 会写入 1 条 `publication_records` placeholder，`provider_name` 为 `placeholder`，`publication_status` 为 `not_started`，且不带 `external_publication_id`。fake publish 要求 PublishIntent 已 `confirmed` 且存在 `not_started` PublicationRecord；成功后 `provider_name` 为 `fake_publisher`，`publication_status` 为 `succeeded`，`external_publication_id` 是本地 fake id。confirm 和 fake publish 都不会修改 Review Draft 的 `review_status`，不会调用真实 Douyin API，不实现 OAuth，不保存 token、secret 或 API key，不上传、不发布、不排期、不自动发布，也不会创建媒体文件。fake publish 的 `succeeded` 只表示本地 fake execution 成功，不代表真实平台发布成功。

## Frontend ContentPlan / GenerationSchedule / GenerationRun UI 验证

v0.4 Batch 6 在项目详情页新增了 Content Plans 区块。该前端 UI 只调用已有 ContentPlan、GenerationSchedule 和 GenerationRun API，支持查看和创建 ContentPlan、启停 ContentPlan、查看并创建关联 GenerationSchedule、启停 GenerationSchedule，并基于 ContentPlan 或 ContentPlan + GenerationSchedule 手动创建 fake manual GenerationRun。

可以在 backend 和 frontend 启动后，打开 `http://localhost:5173`，进入项目详情页，确认：

- Content Plans 区块展示 ContentPlan list、账号定位、内容类型、每周目标频率、偏好文本、启用状态和创建/更新时间。
- 可以创建 ContentPlan；`target_frequency_per_week` 仍由后端限制为 1 到 14。
- 可以启用 / 停用 ContentPlan。
- 每个 ContentPlan 下展示关联 GenerationSchedule list，包括 frequency、timezone、preferred days、preferred time 和启用状态。
- 可以创建 GenerationSchedule；`frequency_per_week` 留空时由后端继承 ContentPlan 的目标频率。
- 可以启用 / 停用 GenerationSchedule。
- 可以基于 ContentPlan 手动创建 fake manual GenerationRun，也可以基于 ContentPlan + 指定 GenerationSchedule 手动创建 fake manual GenerationRun。
- 手动 GenerationRun 成功后，项目详情页刷新 GenerationRuns list 和 Review Drafts list。
- archived 项目仍可查看 ContentPlan、GenerationSchedule、GenerationRun 和 Review Draft，但不允许 create / enable / disable / trigger run。

该 UI 不实现 Scheduler / Trigger Engine，不执行 scheduled `GenerationRun`，不创建真实 Topic Candidate、Script Draft、Storyboard、Render Job、Subtitle Draft、视频、音频、字幕或媒体文件，不接热点源、Notification Service、真实 AI Provider、`FFmpeg`、TTS、发布或上传能力。

## Frontend Review Draft UI 验证

v0.4 Batch 5 在项目详情页新增了 Review Drafts 区块。该前端 UI 只调用已有 `review_drafts` API，展示 backend-only placeholder 的标题、审核状态、草稿摘要、输入来源、热点来源 fallback、GenerationRun / GenerationSchedule 信息和创建/更新时间；approve / reject 成功后刷新列表。archived 项目仍可查看已有 review drafts，但不显示审核操作。

可以先使用上一节 API 创建 1 条 fake manual GenerationRun 和 `pending_review` review draft，然后打开 frontend：

```powershell
cd .\frontend
npm.cmd run dev
```

访问 `http://localhost:5173`，进入对应项目详情页，确认：

- 待审核草稿区块能展示 `pending_review`、`approved`、`rejected` 的清晰中文状态。
- `hotspot_source_summary` 为空时显示“未启用热点来源 / 无热点来源”。
- 手动运行且没有 schedule 时显示“手动运行 / 无计划”。
- 点击“通过”或“拒绝”只更新 `review_status` 并刷新列表。
- archived 项目只读，不允许 approve / reject。

该 UI 不实现完整 Review Queue 页面，不实现 Scheduler / scheduled `GenerationRun`，不创建真实 Topic Candidate、Script Draft、Storyboard、Render Job、Subtitle Draft、视频、音频、字幕或媒体文件，不接热点源、真实 AI Provider、`FFmpeg`、TTS、发布或上传能力。

## v0.4 Release Candidate 验证

v0.4 Batch 8 是 RC stabilization / checklist，不新增后端能力、前端功能或业务能力。当前 v0.4 只覆盖 local fake/manual workflow：`GenerationSchedule` 只是配置，fake manual `GenerationRun` 只记录 deterministic summary 并同步创建 `Review Draft` placeholder。

本地手动 smoke checklist：

- 启动 backend 与 frontend，确认项目详情页可以打开。
- 创建一个未归档项目，创建 `ContentPlan`，确认 list / read 展示账号定位、内容类型、目标频率、偏好文本和启用状态。
- update / enable / disable `ContentPlan`，确认状态变化；归档项目下 create / update / enable / disable 应保持禁止。
- 在该 `ContentPlan` 下创建 `GenerationSchedule`，确认 list / read 展示 frequency、timezone、preferred days、preferred time 和启用状态。
- update / enable / disable `GenerationSchedule`，确认状态变化；归档项目下 create / update / enable / disable 应保持禁止。
- 手动创建 fake `GenerationRun`，分别验证无 schedule 与指定 schedule 两种路径。
- manual `GenerationRun` 成功后，确认项目详情页刷新 GenerationRuns list 和 Review Drafts list。
- 确认生成的 `Review Draft` 是 `pending_review` placeholder，展示草稿摘要、输入来源、热点来源 fallback、GenerationRun / GenerationSchedule 信息和 created / updated 时间。
- approve / reject 只改变 `review_status` 并刷新列表；归档项目仍可读取 Review Draft，但不允许 approve / reject。
- 确认不会执行 scheduled `GenerationRun`，不会注册 Scheduler / Trigger Engine，不会创建真实 Topic Candidate、Script Draft、Storyboard、Render Job、Subtitle Draft、视频、音频、字幕、上传文件或发布记录。
- 确认不接热点源、Notification Service、真实 AI Provider、`FFmpeg`、TTS、发布或上传能力。

更完整的收口清单见 [`docs/releases/v0.4-rc-checklist.md`](releases/v0.4-rc-checklist.md)。

## Backend Topic Candidate API 验证

v0.2 Batch 1 新增了 backend-only 的候选选题 API。该后端 API 只使用本地 deterministic `FakeLLMProvider`，不联网、不读取密钥、不调用真实 LLM；前端 UI 已在后续 Batch 补充。

可以在 backend 启动后用 PowerShell 手动验证：

```powershell
$project = Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/projects `
  -ContentType "application/json" `
  -Body '{"title":"Topic API test","description":"Local fake provider verification"}'

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/materials/text" `
  -ContentType "application/json" `
  -Body '{"material_type":"text","title":"Imported note","text_content":"A user supplied note for topic planning."}'

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/topic-candidates/generate" `
  -ContentType "application/json" `
  -Body '{"candidate_count":3}'

Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/topic-candidates"
```

生成接口会写入 `topic_generation_runs`、`topic_candidates` 和 `topic_candidate_sources`。如果项目没有素材会返回 `409`；如果项目已归档，生成和选择候选都会返回 `409`，但仍允许查询已有候选。

## Backend Script Draft API 验证

v0.2 Batch 3 新增了 backend-only 的脚本草稿 API。该后端 API 只使用本地 deterministic `FakeLLMProvider`，不联网、不读取密钥、不调用真实 LLM；Script Draft 前端 UI 已在后续 Batch 补充。

可以在 backend 启动后用 PowerShell 手动验证：

```powershell
$project = Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/projects `
  -ContentType "application/json" `
  -Body '{"title":"Script API test","description":"Local fake script draft verification"}'

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/materials/text" `
  -ContentType "application/json" `
  -Body '{"material_type":"text","title":"Imported note","text_content":"A user supplied note for script drafting."}'

$topicResult = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/topic-candidates/generate" `
  -ContentType "application/json" `
  -Body '{"candidate_count":1}'

$topicId = $topicResult.candidates[0].id
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/topic-candidates/$topicId/select"

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/script-drafts/generate" `
  -ContentType "application/json" `
  -Body '{"script_count":2}'

Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/script-drafts"
```

生成接口会写入 `script_generation_runs`、`script_drafts` 和 `script_draft_sources`。如果项目没有素材、没有 selected topic candidate，或项目已归档，会返回 `409`。已归档项目仍允许查询已有脚本草稿。

## Backend Storyboard API 验证

v0.2 Batch 5 新增了 backend-only 的分镜草稿 API。该后端 API 只使用本地 deterministic `FakeLLMProvider`，不联网、不读取密钥、不调用真实 LLM，也不生成图片、音频、字幕或视频；Storyboard 前端 UI 已在后续 Batch 补充。

可以在 backend 启动后用 PowerShell 手动验证：

```powershell
$project = Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/projects `
  -ContentType "application/json" `
  -Body '{"title":"Storyboard API test","description":"Local fake storyboard verification"}'

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/materials/text" `
  -ContentType "application/json" `
  -Body '{"material_type":"text","title":"Imported note","text_content":"A user supplied note for storyboard planning."}'

$topicResult = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/topic-candidates/generate" `
  -ContentType "application/json" `
  -Body '{"candidate_count":1}'

$topicId = $topicResult.candidates[0].id
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/topic-candidates/$topicId/select"

$scriptResult = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/script-drafts/generate" `
  -ContentType "application/json" `
  -Body '{"script_count":1}'

$scriptId = $scriptResult.script_drafts[0].id
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/script-drafts/$scriptId/select"

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/storyboards/generate" `
  -ContentType "application/json" `
  -Body '{"storyboard_count":1}'

Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/storyboards"
```

生成接口会写入 `storyboard_generation_runs`、`storyboard_drafts`、`storyboard_scenes` 和 `storyboard_draft_sources`。如果项目没有素材、没有 selected topic candidate、没有 selected script draft，或项目已归档，会返回 `409`。已归档项目仍允许查询已有分镜草稿。

## Backend Fake Render API 验证

v0.3 Batch 1 新增了 backend-only 的 fake render API。该后端 API 只使用本地 deterministic `FakeRenderer`，不联网、不读取密钥、不调用真实 `FFmpeg`，不调用 TTS，不生成字幕，也不生成真实 MP4 文件；本批只保存 fake render job 和 artifact metadata。

可以在 backend 启动后用 PowerShell 手动验证：

```powershell
$project = Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/projects `
  -ContentType "application/json" `
  -Body '{"title":"Render API test","description":"Local fake renderer verification"}'

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/materials/text" `
  -ContentType "application/json" `
  -Body '{"material_type":"text","title":"Imported note","text_content":"A user supplied note for fake rendering."}'

$topicResult = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/topic-candidates/generate" `
  -ContentType "application/json" `
  -Body '{"candidate_count":1}'

$topicId = $topicResult.candidates[0].id
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/topic-candidates/$topicId/select"

$scriptResult = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/script-drafts/generate" `
  -ContentType "application/json" `
  -Body '{"script_count":1}'

$scriptId = $scriptResult.script_drafts[0].id
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/script-drafts/$scriptId/select"

$storyboardResult = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/storyboards/generate" `
  -ContentType "application/json" `
  -Body '{"storyboard_count":1}'

$storyboardId = $storyboardResult.storyboards[0].id
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/storyboards/$storyboardId/select"

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/projects/$($project.id)/renders" `
  -ContentType "application/json" `
  -Body '{"requested_format":"mp4","requested_aspect_ratio":"9:16","requested_resolution":"1080x1920"}'

Invoke-RestMethod "http://127.0.0.1:8000/api/projects/$($project.id)/renders"
```

创建接口会写入 `render_jobs` 和 `render_artifacts`，并将 render job 同步标记为 `succeeded`。`render_artifacts.storage_path` 指向 Git 忽略的 deterministic fake preview manifest 路径，例如 `data/local/render_previews/project-{project_id}/project-{project_id}-render-{render_job_id}-preview-manifest.json`；后端只写入轻量 JSON manifest，不创建真实 MP4、音频或字幕文件。如果项目没有 selected storyboard、selected storyboard 没有 scenes，或项目已归档，会返回 `409`。已归档项目仍允许查询已有 render jobs。

## Topic Candidate UI 验证

v0.2 Batch 2 在项目详情页新增了 Topic Candidates 区块。当前仍然只使用本地 deterministic `FakeLLMProvider`，不接真实 AI，不提供 Provider 配置，也不保存 API key、secret 或 token。

验证步骤：

1. 在仓库根目录启动 backend：

```powershell
.\scripts\dev-backend.ps1
```

2. 另开一个 PowerShell 启动 frontend：

```powershell
.\scripts\dev-frontend.ps1
```

3. 打开 `http://localhost:5173`，创建一个内容项目。
4. 进入项目详情页，添加至少一条文本、摘要、项目记录、链接、图片或截图素材。
5. 在 Topic Candidates 区块点击 `Generate Topic Candidates`。
6. 确认页面显示候选选题的 title、angle、audience、hook、rationale、status、source material ids、created time 和 selected time。
7. 点击某个候选的 `Select`，确认该候选显示 `Selected`，并且同一项目中只有一个候选保持 selected 状态。
8. 归档项目后，确认已有候选仍可查看，但 `Generate Topic Candidates` 和 `Select` 不可用，并显示 `Archived projects are read-only.`。

## Script Draft UI 验证

v0.2 Batch 4 在项目详情页新增了 Script Drafts 区块。当前仍然只使用本地 deterministic `FakeLLMProvider`，不接真实 AI，不提供 Provider 配置，也不保存 API key、secret 或 token。

验证步骤：

1. 在仓库根目录启动 backend：

```powershell
.\scripts\dev-backend.ps1
```

2. 另开一个 PowerShell 启动 frontend：

```powershell
.\scripts\dev-frontend.ps1
```

3. 打开 `http://localhost:5173`，创建一个内容项目。
4. 进入项目详情页，添加至少一条文本、摘要、项目记录、链接、图片或截图素材。
5. 在 Topic Candidates 区块点击 `Generate Topic Candidates`。
6. 点击某个候选的 `Select`，确认该候选显示 `Selected`。
7. 在 Script Drafts 区块点击 `Generate Script Drafts`。
8. 确认页面显示脚本草稿的 title、opening hook、body、call to action、estimated duration、rationale、status、source material ids、created time 和 selected time。
9. 点击某个脚本草稿的 `Select`，确认该脚本草稿显示 `Selected`，并且同一项目中只有一个脚本草稿保持 selected 状态。
10. 如果未选择 Topic Candidate 就生成脚本草稿，页面会显示 `Select a topic candidate before generating script drafts.`。
11. 如果没有素材就生成脚本草稿，页面会显示 `Add at least one material before generating script drafts.`。
12. 归档项目后，确认已有脚本草稿仍可查看，但 `Generate Script Drafts` 和 `Select` 不可用，并显示 `Archived projects are read-only.`。

## Storyboard UI 验证

v0.2 Batch 6 在项目详情页新增了 Storyboards 区块。当前仍然只使用本地 deterministic `FakeLLMProvider`，不接真实 AI，不提供 Provider 配置，也不保存 API key、secret 或 token；本批只展示结构化分镜草稿和 scenes，不生成图片、音频、字幕或视频。

验证步骤：

1. 在仓库根目录启动 backend：

```powershell
.\scripts\dev-backend.ps1
```

2. 另开一个 PowerShell 启动 frontend：

```powershell
.\scripts\dev-frontend.ps1
```

3. 打开 `http://localhost:5173`，创建一个内容项目。
4. 进入项目详情页，添加至少一条文本、摘要、项目记录、链接、图片或截图素材。
5. 在 Topic Candidates 区块点击 `Generate Topic Candidates`。
6. 点击某个候选选题的 `Select`，确认该候选显示 `Selected`。
7. 在 Script Drafts 区块点击 `Generate Script Drafts`。
8. 点击某个脚本草稿的 `Select`，确认该脚本草稿显示 `Selected`。
9. 在 Storyboards 区块点击 `Generate Storyboards`。
10. 确认页面显示 storyboard 的 title、summary、visual style、status、source material ids、created time、selected time，并按 scene order 显示每个 scene 的 narration、visual description、on-screen text、estimated duration 和 source material id。
11. 点击某个 storyboard 的 `Select`，确认该 storyboard 显示 `Selected`，并且同一项目中只有一个 storyboard 保持 selected 状态。
12. 如果未选择 Topic Candidate 就生成分镜，页面会显示 `Select a topic candidate before generating storyboards.`。
13. 如果未选择 Script Draft 就生成分镜，页面会显示 `Select a script draft before generating storyboards.`。
14. 如果没有素材就生成分镜，页面会显示 `Add at least one material before generating storyboards.`。
15. 归档项目后，确认已有 storyboards 和 scenes 仍可查看，但 `Generate Storyboards` 和 `Select` 不可用，并显示 `Archived projects are read-only.`。
16. 确认本批仍然只使用 fake provider，不接真实 AI，也不生成图片、音频、字幕或视频。

## 验证项目与素材导入

1. 启动 backend。
2. 启动 frontend。
3. 打开 `http://localhost:5173`。
4. 创建一个内容项目。
5. 在项目详情页编辑项目标题或描述，确认刷新后仍然存在。
6. 在项目详情页添加一条文本素材。
7. 添加一条链接素材。
8. 上传一张图片或截图。
9. 返回项目列表，确认素材数量已更新。
10. 归档项目，确认归档前出现浏览器确认。
11. 返回项目列表，确认默认不显示已归档项目。
12. 勾选“显示归档项目”，确认已归档项目可见。
13. 打开已归档项目，确认已有素材仍可查看，且素材导入表单不可用。
14. 刷新页面，确认项目与素材仍然存在。
15. 检查 `git status --short`，确认未跟踪 SQLite 文件、上传文件、`.venv/`、`node_modules/` 或生成媒体。

## 常见问题

### PowerShell 执行策略阻止脚本

如果看到脚本被执行策略阻止，可运行：

```powershell
Get-ChildItem .\scripts\*.ps1 | Unblock-File
```

如果是 `npm.ps1` 被阻止，请使用 `npm.cmd`，本仓库脚本也默认使用 `npm.cmd`。

### Backend 端口被占用

默认 backend 端口是 `127.0.0.1:8000`。如果端口被占用，可以先关闭占用该端口的本地服务，或手动运行：

```powershell
cd .\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

如果 backend 端口不是 `8000`，启动 frontend 前需要设置 `VITE_API_BASE_URL`。

### Frontend 连接不到 Backend

确认 backend 已启动，并检查 frontend 使用的 API 地址：

```powershell
$env:VITE_API_BASE_URL = "http://127.0.0.1:8000"
.\scripts\dev-frontend.ps1
```

### SQLite 文件在哪里

默认 SQLite 文件位于：

```text
data/local/creator_flow.sqlite3
```

该文件是本地运行时数据，不会提交到 Git。

### 如何清理本地运行时数据

确认 backend/frontend 已停止后，可以删除本地运行时数据：

```powershell
Remove-Item .\data\local\creator_flow.sqlite3 -ErrorAction SilentlyContinue
Remove-Item .\uploads\* -Recurse -Force -ErrorAction SilentlyContinue
```

不要删除 `data/local/.gitkeep` 或 `uploads/.gitkeep`。

## v0.3 Fake Workflow Release Candidate 验证

v0.3 Batch 7 已完成 fake workflow stabilization 与 Release Candidate 收口。当前只覆盖 fake rendering/subtitle/preview metadata workflow。合并或发布候选验收时应确认：

- Render Jobs 可以基于 selected Storyboard 创建 fake render job，并展示 fake preview manifest metadata。
- Subtitle Drafts 可以基于 selected Storyboard 创建和选择 fake subtitle draft，并展示 subtitle cues。
- Preview 只展示 backend 返回的 manifest metadata，不读取 `data/local/render_previews/` 文件，不新增真实 `<video>` 播放器。
- archived 项目仍可查看 render jobs、subtitle drafts 和 preview metadata，但不允许 create/select。
- 当前不会生成真实 MP4、音频或 `.srt` / `.vtt` 字幕文件。
- runtime preview manifest 位于 `data/local/render_previews/`，该路径由 `.gitignore` 中的 `data/local/` 覆盖，不得进入 Git。

更完整的收口清单见 [`docs/releases/v0.3-rc-checklist.md`](releases/v0.3-rc-checklist.md)。

## 当前未实现能力

- 未实现真实 OpenAI、Claude、Gemini 或其他 LLM Provider 接入。
- 未实现 API key、secret 或 token 保存，也没有 Provider 配置页面。
- 未实现 `ImageProvider`、`TTSProvider`、`TrendSourceProvider`、`PublisherProvider` 或真实 `VideoRenderer`；当前只有 deterministic `FakeRenderer`、`FakeSubtitle` 和 fake preview manifest metadata workflow。
- 未实现素材方案生成、OCR、图片内容分析或自动抓取链接内容。
- 未实现 `FFmpeg` 渲染、TTS、真实字幕文件生成或真实视频/音频/图片生成；当前字幕和 preview 都只是 metadata workflow。
- 未实现 `Review Queue` 完整业务流程；当前仅有项目详情页中的 Review Draft placeholder 展示与审核状态变更。
- 未实现定时生成、scheduled `GenerationRun` 或 Scheduler；当前 ContentPlan / GenerationSchedule / Manual GenerationRun UI 只调用已有后端 API，manual trigger 只创建 fake GenerationRun 和 Review Draft placeholder，不会触发自动生成、媒体创建、上传或发布。
- 未实现真实抖音或其他平台发布；当前只有 PublishIntent / PublicationRecord backend domain foundation、confirm workflow foundation 和 local fake publisher execution foundation。
- 未实现 OAuth、真实 PublisherProvider、凭据保存、用户账号体系、生产部署、`Docker Compose` 或 `GitHub Actions`。
- 未实现上传、排期发布或自动发布。
- 未实现自动扫描本地文件、浏览器、私有聊天或私人账号的能力。
