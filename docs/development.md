# 本地开发

本文档面向 v0.3 Rendering Workflow，说明如何在 Windows 11 和 PowerShell 下启动本地 backend、frontend，并验证内容项目、素材导入、Topic Candidate、Script Draft、Storyboard、fake render job、fake subtitle draft 和 fake preview manifest metadata 工作流。

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

v0.3 当前只覆盖 fake rendering/subtitle/preview metadata workflow。合并或发布候选验收时应确认：

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
- 未实现 `Review Queue` 完整业务流程。
- 未实现定时生成、`GenerationSchedule` 或 Scheduler。
- 未实现抖音或其他平台发布。
- 未实现 OAuth、用户账号体系、生产部署、`Docker Compose` 或 `GitHub Actions`。
- 未实现自动扫描本地文件、浏览器、私有聊天或私人账号的能力。
