# ADR 0010: 先实现 Fake Storyboards 再接真实生成与渲染

## 状态

Accepted

## 背景

v0.2 已经建立了基于 `FakeLLMProvider` 的候选选题和脚本草稿闭环。下一步需要把已选择的 `TopicCandidate` 和 `ScriptDraft` 转换为结构化分镜草稿，但分镜编辑 UI、素材方案、TTS、字幕、FFmpeg 渲染和发布流程都还没有进入稳定阶段。

如果这一批直接接入 OpenAI、Claude、Gemini 或其他真实 LLM，会过早引入密钥保存、供应商差异、网络失败、计费、隐私边界和测试不确定性。真实生成还容易把还未稳定的分镜数据结构和渲染需求绑定到供应商输出细节上。

## 决策

v0.2 Batch 5 继续使用本地 deterministic `FakeLLMProvider` 生成 `StoryboardDraft` 和 `StoryboardScene`。分镜草稿只基于项目标题、项目描述、已 selected 的 `TopicCandidate`、已 selected 的 `ScriptDraft`，以及用户显式导入素材的元数据和文本字段生成。

本批新增 `StoryboardGenerationRun`、`StoryboardDraft`、`StoryboardScene` 和 `StoryboardDraftSource`，用于记录分镜生成过程、结构化场景和分镜所依据的显式导入素材。

## 理由

- 继续使用 `FakeLLMProvider` 可以让 storyboard API、SQLite schema、来源追溯和选择行为先稳定下来，并保持本地可重复、无网络、无费用。
- 不直接接 OpenAI、Claude 或 Gemini，可以避免在分镜结构尚未稳定时把供应商输出格式写入核心业务模型。
- 不保存 API key，可以继续遵守本地优先和隐私边界，避免提前设计密钥存储、加密和轮换。
- 分镜草稿必须追溯到 selected `TopicCandidate`、selected `ScriptDraft` 和显式导入素材，确保用户能理解分镜从哪个选题、哪个脚本和哪些素材而来。
- 本批不修改 `ContentProject.status`，因为 storyboard 选择还没有前端审核体验，过早加入 `storyboard_selected` 会扩大状态机和 UI 语义。
- 本批不做前端 UI，是为了先稳定 backend contract，避免 API 和 UI 同时变化导致 review 范围过大。
- 本批不做渲染、TTS、字幕或 FFmpeg，因为当前目标只是保存结构化分镜草稿；媒体生成会引入运行时文件、音频、字幕、渲染失败处理和更复杂的人工审核边界。

## 结果

- 后端可以在无真实 AI 的情况下完成从 selected topic、selected script 到 storyboard draft 的闭环。
- 测试可以稳定覆盖 provider 输出、分镜持久化、scene 顺序、来源追溯、唯一 selected storyboard 和 archived 项目边界。
- 后续分镜前端 UI 可以直接复用本批 API。

## 后续

当 storyboard API 和 UI 都稳定后，再考虑真实 LLM Provider。真实 Provider 接入前需要先设计本地密钥配置、错误处理、请求日志边界、隐私说明和供应商替换策略。

分镜编辑 UI、素材方案、TTS、字幕和 FFmpeg 渲染能力应在后续批次中单独实现，并继续保留 human-in-the-loop publishing 原则。
