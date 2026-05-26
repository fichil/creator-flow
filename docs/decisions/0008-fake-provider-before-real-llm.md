# ADR 0008: 先实现 Fake Provider 再接真实 LLM

## 状态

Accepted

## 背景

creator-flow 进入 v0.2 AI Planning Workflow 后，需要开始建立从显式导入素材到候选选题的闭环。这个阶段的关键不是尽快接入某一家 AI 服务，而是先确认 Provider 边界、生成记录、候选选题、来源追溯和人工选择流程是否稳定。

如果第一批直接接入 OpenAI、Claude、Gemini 或其他真实 LLM，后端会过早面对密钥保存、请求计费、网络失败、供应商差异、隐私说明和测试不确定性。这会扩大 v0.2 Batch 1 的范围，也会让本地开发和回归测试依赖外部服务。

## 决策

v0.2 Batch 1 先实现 `LLMProvider` 接口和本地 deterministic `FakeLLMProvider`。该 Provider 只基于项目标题、项目描述，以及用户显式导入素材的元数据和文本字段生成候选选题，不联网、不读取密钥、不调用真实 LLM。

本批同时新增 `TopicGenerationRun`、`TopicCandidate` 和 `TopicCandidateSource`，用于记录一次选题生成、候选结果和候选所依据的显式导入素材。

## 理由

- `FakeLLMProvider` 可以让 API、数据库和测试先稳定下来，并保持完全本地、可重复、无费用。
- 不直接接 OpenAI、Claude 或 Gemini，可以避免在 Provider 边界尚未稳定时把供应商细节写入核心业务。
- 不保存 API key，可以继续遵守当前本地骨架阶段的隐私和凭据边界，避免把密钥配置、密钥加密或密钥轮换提前带入仓库。
- 候选选题必须通过 `TopicCandidateSource` 追溯到显式导入素材，确保后续用户能理解生成结果从何而来，也避免自动使用未授权或未明确导入的数据。
- 本批不修改 `ContentProject.status`，因为选题候选和选中行为还没有完整前端审核流程，过早加入 `topic_selected` 会让 v0.1 的状态机和 UI 语义失衡。

## 结果

- 后端可以在无网络、无密钥、无真实 AI 的情况下完成候选选题生成和选择。
- 测试可以稳定覆盖 Provider 输出、数据持久化、来源追溯和 archived 项目边界。
- 后续真实 Provider 接入时，可以复用 `LLMProvider` 接口、生成记录和候选选题 API。
- 真实 Provider 应在后续批次中接入，并且需要先设计本地密钥配置、错误处理、请求日志边界、隐私说明和供应商替换策略。

## 后续

当 v0.2 的选题候选、脚本生成、分镜生成和人工审核边界更清楚后，再接入真实 LLM Provider。接入时仍应保持 Provider 可替换，不把单一供应商写死到核心数据模型或 API 中。
