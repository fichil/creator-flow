# ADR 0013: 先实现 fake preview manifest 再接 FFmpeg

## 状态

Accepted

## 背景

v0.3 Batch 1 到 Batch 4 已经建立 fake render job、fake subtitle draft、subtitle cue 和对应前端查看/触发入口。进入预览阶段后，系统需要先稳定 render artifact metadata、运行时输出路径和后续 MP4 预览 API 的契约，再引入真实 `FFmpeg`、音频、字幕文件和 MP4 输出。

如果本批直接接 `FFmpeg` 或生成真实 MP4，会同时引入本地媒体文件、编码失败、字幕/音频同步、清理策略和 Review Queue 状态设计问题，超出 backend-only foundation 的范围。

## 决策

v0.3 Batch 5 先实现 backend-only 的 fake render preview artifact placeholder。`FakeRenderer` 只写入 deterministic JSON manifest，并把 manifest metadata 保存到 `render_artifacts`。

运行时 preview artifact 路径使用 `data/local/render_previews/` 策略。该路径由 `.gitignore` 中的 `data/local/` 覆盖，不得提交运行时 manifest、真实媒体、真实字幕或真实音频。

本批不生成真实 MP4，不调用 `FFmpeg`，不调用 TTS，不生成真实 `.srt` / `.vtt` 文件，不接真实 AI Provider，也不保存任何 API key、secret 或 token。

## 理由

- render artifact metadata 和 preview path contract 需要先稳定，后续真实 MP4 预览和审核队列才能复用。
- deterministic JSON manifest 可以让测试覆盖 artifact metadata、subtitle draft 关联和路径策略，而不依赖任何媒体工具。
- 将 runtime output 固定在 Git 忽略路径下，可以避免运行时产物进入仓库。
- 不接 `FFmpeg` 和 TTS 可以保持本批 backend-only、可重复、无外部依赖的边界。

## 结果

- 后端可以在没有真实媒体工具的情况下，为 fake render job 生成 preview placeholder metadata。
- 有 selected subtitle draft 时，manifest 和 artifact metadata 可以记录 subtitle draft id；没有 selected subtitle draft 时，fake render job 仍可成功，并明确记录为空。
- 后续真实 `FFmpeg` renderer、MP4 预览和 Review Queue 可以沿用该 artifact metadata 与 ignored runtime output 策略。
