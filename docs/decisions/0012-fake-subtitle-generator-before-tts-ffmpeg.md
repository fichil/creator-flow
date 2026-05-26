# ADR 0012: 先实现 FakeSubtitleGenerator 再接 TTS 与 FFmpeg 字幕生成

## 状态

Accepted

## 背景

v0.3 Batch 1 已经建立 fake render job 和 artifact metadata 边界，Batch 2 已经在前端展示并触发 fake render job。进入字幕阶段后，系统需要先稳定 subtitle draft、subtitle cue、选择状态和 API 合约，才能继续设计字幕编辑 UI、TTS 输入、真实字幕文件输出和 `FFmpeg` 渲染集成。

如果本批直接生成 `.srt` / `.vtt` 文件、接入 TTS 或把字幕塞进 `FFmpeg` 流程，会过早引入运行时文件、音频时长同步、字幕格式兼容、编码失败和渲染调试问题，也会扩大 backend-only foundation 的范围。

## 决策

v0.3 Batch 3 先实现 backend-only 的 `FakeSubtitleGenerator`。它只基于 selected `StoryboardDraft` 的 ordered scenes 生成 deterministic subtitle cue metadata，并保存到本地 `SQLite`。

本批新增 `SubtitleDraft` 和 `SubtitleCue` 数据模型与 API，但不生成真实 `.srt` / `.vtt` 文件，不调用 TTS，不调用 `FFmpeg`，不生成音频、视频或 MP4，不接真实 AI Provider，也不保存任何 API key、secret 或 token。

## 理由

- subtitle draft 与 cue 数据结构需要先稳定，后续字幕编辑 UI 和真实渲染才能复用同一 API 合约。
- selected Storyboard 已经包含有序 scenes、narration 和 estimated duration，适合作为 deterministic fake subtitle cue 的输入。
- 只保存 metadata 可以避免运行时字幕文件进入 Git，也避免把格式、编码和清理策略提前写死。
- 不接 TTS 和 `FFmpeg` 可以保留本批 backend-only、可重复、无外部依赖的测试边界。
- 本批不修改 `ContentProject.status`，因为字幕 UI、审核队列、真实音频和真实渲染流程尚未稳定。

## 结果

- 后端可以在没有真实媒体工具的情况下，从 selected Storyboard 创建 fake subtitle draft，并保存 ordered subtitle cues。
- 测试可以稳定覆盖 subtitle draft 创建、list/read/select、archived 边界、缺少 selected storyboard 的错误和不生成真实文件的约束。
- 后续字幕编辑 UI、TTS、真实字幕文件输出和 `FFmpeg` renderer 可以复用 subtitle draft 与 cue 结构。
