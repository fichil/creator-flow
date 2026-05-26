# creator-flow

[简体中文](README.md) | [English](README.en.md)

creator-flow 是一个可开源的 AI 短视频内容流水线，帮助用户将显式导入的想法、聊天摘要、文本、图片、截图和链接转化为待审核的短视频草稿。

## 当前状态

`v0.1 Local Runnable Skeleton - Release Candidate`

当前仓库已完成 v0.1 本地可运行骨架的发布候选能力。已具备最小 `FastAPI` backend、`React` + `Vite` + `Tailwind CSS` frontend、`SQLite` 本地元数据存储，以及内容项目和显式导入素材的基础页面与 API。

本地开发说明见 [`docs/development.md`](docs/development.md)。
v0.1.0 release notes 草稿见 [`docs/releases/v0.1.0.md`](docs/releases/v0.1.0.md)。

当前仍未实现 AI Provider、视频渲染、定时生成、平台发布、生产部署或账号体系。
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
- AI 生成选题、脚本、分镜、字幕和素材方案。
- 通过 `FFmpeg` 流水线生成适合短视频平台发布的 9:16 MP4。
- 支持配置内容计划、账号定位、内容类型和生成频率。
- 按计划基于显式导入素材与可选热点信号自动生成待审核草稿。
- 将自动生成的视频项目放入 `Review Queue`，由用户审核后继续处理。
- 发布后指标回流，用于后续内容复盘和选题优化。
- 以抖音作为首个发布平台，同时通过 Provider 抽象保留多平台扩展能力。

以上能力均为计划方向，尚未实现。

## 当前本地骨架能力

- 本地启动 backend 和 frontend。
- 创建 `ContentProject`。
- 向指定项目显式添加文本、摘要、项目记录、链接、图片和截图素材。
- 查看项目列表、项目详情和素材列表。
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
