# ADR 0014: Human-confirmed publishing provider boundary

## 状态

Accepted

## 背景

v0.4 已经完成 ContentPlan、GenerationSchedule、fake manual GenerationRun 和 Review Draft placeholder 的 local fake/manual workflow release candidate。下一阶段 v0.5 进入 Human-Confirmed Douyin Publishing 方向，但发布动作涉及隐私、版权、账号声誉、平台授权和凭据管理风险。

如果第一批直接接入抖音真实 API、OAuth、token 保存、上传或发布动作，平台细节和凭据边界会过早进入核心模型，且容易把 `Review Draft` 的审核状态误用为发布确认。系统还可能在没有稳定 `PublishIntent`、人工确认状态和发布记录模型的情况下执行公开平台动作。

## 决策

v0.5 Batch 1 只建立 Human-Confirmed Publishing Provider Boundary 的文档基础，不实现任何代码、数据库、OAuth、真实发布、真实上传、排期发布、自动发布或凭据保存。

发布必须由用户明确确认后触发。`Review Draft` approved 只表示草稿通过审核，可以进入后续渲染、发布准备或发布意图创建流程，但不等于发布确认，不得触发发布、上传或排期发布。

后续发布能力必须基于 `PublishIntent` / `PublicationRecord` 或等价模型：

- `PublishIntent` 保存平台目标、发布元数据、待发布内容引用、人工确认状态、确认人和确认时间。
- `PublicationRecord` 保存用户确认后的执行结果、平台返回 id、平台状态、错误信息、重试信息和查询时间。

`PublisherProvider` 必须隔离平台细节。抖音是首个平台实现方向，但核心模型不得写死抖音字段、接口或授权流程；抖音适配应位于 Provider 或平台适配层。

凭据不得进入 Git。OAuth token、API key、secret、平台账号信息和本地私有配置不得出现在仓库文件、测试 fixtures、文档示例、日志样例或运行时 artifact 中。

## 理由

- Human-in-the-loop publishing 是 creator-flow 的核心安全边界，必须先于真实平台接入稳定下来。
- 发布准备、发布确认和实际发布是不同动作；把它们拆开可以避免 approved draft 被误发布。
- `PublishIntent` 与 `PublicationRecord` 可以让后续 UI、审计、失败重试和平台状态查询有清晰模型。
- `PublisherProvider` 隔离平台细节后，抖音可以作为首个平台实现，同时保留扩展其他平台的能力。
- 不在 Batch 1 接入 OAuth 或真实发布，可以避免凭据、网络调用、平台限制和隐私风险提前进入本地 fake/manual workflow。

## 结果

- v0.5 从文档层明确发布 Provider 边界，而不是直接进入平台集成。
- 后续真实发布批次需要先实现发布意图、人工确认状态和发布记录，再接入平台 Provider。
- `Review Draft` approved 与发布确认保持分离。
- v0.4 local fake/manual workflow 和 v0.3 render/subtitle/preview workflow 不受影响。

## 明确不在本批范围内

- 真实抖音 OAuth。
- 真实发布、上传、排期发布或自动发布。
- token、secret、API key 或任何平台凭据保存。
- 后端 API、前端 UI、数据库表或 Provider 实现。
- v0.4 local fake/manual workflow 修改。
- v0.3 render/subtitle/preview workflow 修改。
