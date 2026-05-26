# ADR 0009: 先实现 Fake Script Drafts 再接真实生成

## 状态

Accepted

## 背景

v0.2 Batch 1 和 Batch 2 已经建立了基于 `FakeLLMProvider` 的候选选题后端闭环和前端 UI。下一步需要把已选择的 `TopicCandidate` 转化为可追溯的脚本草稿，但此时脚本编辑、分镜、渲染和发布流程还没有完整实现。

如果这一批直接接入 OpenAI、Claude、Gemini 或其他真实 LLM，后端会过早引入密钥保存、供应商差异、网络失败、计费和隐私边界问题。真实生成还会让测试变得不确定，不利于先稳定数据模型和 API 合约。

## 决策

v0.2 Batch 3 继续使用本地 deterministic `FakeLLMProvider` 生成 `ScriptDraft`。脚本草稿只基于项目标题、项目描述、已 selected 的 `TopicCandidate` 字段，以及用户显式导入素材的元数据和文本字段生成。

本批新增 `ScriptGenerationRun`、`ScriptDraft` 和 `ScriptDraftSource`，用于记录一次脚本生成、脚本草稿结果，以及草稿所依据的显式导入素材。

## 理由

- 继续使用 `FakeLLMProvider` 可以让脚本草稿 API、数据库和测试先稳定下来，并保持本地可重复、无网络、无费用。
- 不直接接 OpenAI、Claude 或 Gemini，可以避免在核心工作流尚未稳定时把供应商细节写入业务模型。
- 不保存 API key，可以继续遵守本地优先和隐私边界，避免提前设计密钥存储、加密和轮换。
- 脚本草稿必须追溯到 selected `TopicCandidate` 和显式导入素材，确保用户能理解脚本草稿从哪个选题和哪些素材而来。
- 本批不修改 `ContentProject.status`，因为脚本选择还没有完整前端审核体验，过早加入 `script_selected` 会扩大状态机和 UI 语义。
- 本批不做前端 UI，是为了先稳定 backend contract，避免 API 和 UI 同时变化导致 review 范围过大。

## 结果

- 后端可以在无真实 AI 的情况下完成从 selected topic 到 script draft 的闭环。
- 测试可以稳定覆盖 Provider 输出、脚本持久化、来源追溯、唯一 selected script draft 和 archived 项目边界。
- 后续前端脚本草稿 UI 可以直接复用本批 API。

## 后续

当脚本草稿 API 和 UI 都稳定后，再考虑真实 LLM Provider。真实 Provider 接入前需要先设计本地密钥配置、错误处理、请求日志边界、隐私说明和供应商替换策略。脚本编辑 UI 应在后续批次中单独实现。
