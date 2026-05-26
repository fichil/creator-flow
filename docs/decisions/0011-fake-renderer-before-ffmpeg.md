# ADR 0011: 先实现 FakeRenderer 再接真实 FFmpeg

## 状态

Accepted

## 背景

v0.2 已经完成从显式导入素材到 Topic Candidate、Script Draft 和 Storyboard 的本地 fake provider 工作流。进入 v0.3 后，下一步需要建立渲染领域边界：项目必须能够从已选分镜创建渲染任务，记录任务状态，并保存可追溯的输出 artifact 元数据。

如果第一批直接接入 `FFmpeg`、TTS、字幕生成或发布流程，后端会过早面对运行时文件、媒体编码失败、系统依赖安装、音视频同步、字幕格式、平台发布和人工审核边界等复杂问题。这会扩大 v0.3 Batch 1 的范围，也会让本地测试依赖真实媒体工具。

## 决策

v0.3 Batch 1 先实现 backend-only 的 `FakeRenderer`。它只基于项目标题、项目描述、已 selected 的 `StoryboardDraft` 以及 `StoryboardScene` 字段生成 deterministic render artifact metadata。

本批新增 `RenderJob` 和 `RenderArtifact` 数据模型与 API，但不生成真实 MP4 文件，不调用 `FFmpeg`，不调用 TTS，不生成字幕，不发布到平台，也不保存任何 API key、secret 或 token。

## 理由

- `FakeRenderer` 可以先稳定 renderer 边界、render job 状态流转、artifact 元数据和 API 合约，同时保持完全本地、可重复、无外部依赖。
- 不直接接 `FFmpeg`，可以避免把系统二进制、媒体编码参数和运行时文件管理提前写入核心业务流程。
- 不直接接 TTS、字幕或发布，可以继续保留 human-in-the-loop publishing 原则，并避免把尚未审核的媒体内容推向公开平台。
- 本批只保存 artifact metadata，不生成真实 MP4 文件，是为了先验证渲染领域模型和追踪能力；真实媒体文件属于运行时产物，不应进入 Git。
- `RenderJob` 保留 `queued`、`running`、`succeeded`、`failed` 状态，是为了给后续真实渲染、异步任务和失败排查预留结构。
- 本批不修改 `ContentProject.status`，因为渲染 UI、审核队列和真实媒体输出尚未稳定，过早加入 `rendered` 或 `render_completed` 会扩大状态机语义。

## 结果

- 后端可以在没有真实媒体工具的情况下，从 selected storyboard 创建 fake render job，并保存 deterministic fake video artifact metadata。
- 测试可以稳定覆盖 renderer 输出、渲染任务持久化、artifact metadata、archived 项目边界和非法请求参数。
- 后续真实 `FFmpeg` renderer 可以复用 renderer interface、render job 状态和 artifact metadata 结构。

## 后续

当 fake rendering workflow、前端渲染 UI、审核边界和运行时文件存储策略稳定后，再接入真实 `FFmpeg` renderer。接入时应单独设计真实媒体文件输出目录、失败日志、清理策略、字幕/TTS 输入边界和用户审核流程。
