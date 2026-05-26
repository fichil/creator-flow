# creator-flow

[简体中文](README.md) | [English](README.en.md)

creator-flow 是一个可开源的 AI 短视频内容流水线，帮助用户将显式导入的想法、聊天摘要、文本、图片、截图和链接转化为待审核的短视频草稿。

## 当前状态

`v0.3 Rendering Workflow - Batch 6 Fake Render Preview Frontend UI`

当前仓库已完成 v0.1 本地可运行骨架、v0.2 AI Planning Workflow，以及 v0.3 Batch 1 到 Batch 6 的 fake rendering/subtitle/preview foundation。当前主链路使用本地 deterministic `FakeLLMProvider`，支持从显式导入素材生成并选择 Topic Candidate、Script Draft 和 Storyboard，并在项目详情页查看分镜 scenes；应用也可以基于 selected Storyboard 创建 fake render job、展示 fake preview manifest metadata、创建 fake subtitle draft 和展示 subtitle cues。

本地开发说明见 [`docs/development.md`](docs/development.md)。

当前仍不接真实 OpenAI / Claude / Gemini / 其他 LLM，不保存 API key、secret 或 token，不联网调用真实 AI。v0.3 已开始 fake rendering/subtitle/preview foundation，但真实 MP4 渲染、真实视频播放、FFmpeg、TTS、真实字幕文件、真实音频、定时生成、平台发布、生产部署和账号体系仍未实现。
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

其中 Topic Candidate、Script Draft 和 Storyboard 的生成与选择已在 v0.2 中以本地 fake provider 形式实现；v0.3 已开始支持 fake render job、fake preview manifest metadata 展示、fake subtitle draft 和 subtitle cues。真实 AI、真实字幕文件、真实音频、素材方案、真实 MP4 渲染与播放、发布、调度和指标回流仍属于后续计划方向。

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
