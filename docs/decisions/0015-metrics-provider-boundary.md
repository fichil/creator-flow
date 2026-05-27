# ADR 0015: Metrics provider boundary

## 状态

Accepted

## 背景

v0.5 已完成本地 fake publishing workflow：用户可以从已 approved 的 `ReviewDraft` 创建 `PublishIntent`，确认后创建本地 `PublicationRecord` placeholder，并通过 `FakePublisherProvider` 把记录推进到 fake `succeeded`。该流程仍不包含真实 OAuth、真实上传、真实发布、token 保存或真实 Douyin API。

v0.6 需要为发布后的指标反馈建立边界，让后续系统可以围绕 `PublicationRecord` 记录表现快照、支持内容复盘，并为未来优化 `TopicCandidate`、`ScriptDraft` 和 `ContentPlan` 提供输入。指标数据涉及平台授权、账号隐私、平台差异和 fake/local data 误用风险，因此必须先定义 Provider 和领域模型边界。

## 决策

v0.6 Batch 1 只建立 Metrics Feedback Loop 的文档基础，不实现后端 API、数据库表、前端功能、Provider 代码、真实指标抓取、真实 Douyin API、OAuth、token 保存、定时同步或数据分析推荐算法。

后续指标能力应引入 `MetricsProvider` 或等价边界。`MetricsProvider` 负责把抖音或其他平台返回的发布后表现数据转换为核心领域可以理解的指标快照；Douyin 只是未来一个 provider，核心模型不得写死抖音专有字段、接口形状或授权流程。

指标快照应与 `PublicationRecord` 或等价发布记录关联。领域模型方向包括 `PublicationMetricSnapshot`、`MetricSource`、`captured_at`、平台无关的基础指标字段，以及用于区分 fake/local data 与真实平台数据的来源标记。基础指标可以包括 `views`、`likes`、`comments`、`shares`、`favorites`、`watch_time` 和 `completion_rate`，并且必须允许部分字段为空。

fake metrics 与真实 metrics 必须显式区分。fake/local metrics 只能用于本地开发、演示或测试，不得展示为真实平台表现，也不得作为真实增长分析或对外效果证明。

## 理由

- 指标反馈属于发布后的复盘输入，不应影响 human-in-the-loop publishing 原则。
- 平台指标能力和字段差异较大，先定义平台无关快照可以避免核心模型被单一平台锁定。
- 指标读取通常需要账号授权和凭据管理，必须与本地 fake workflow 隔离。
- 将 fake/local metrics 显式标记，可以避免用户误以为本地演示数据代表真实平台表现。
- 快照模型保留多个采集时间点，便于后续复盘趋势，而不是只保存一个覆盖式当前值。

## 结果

- 后续可以先实现 deterministic `FakeMetricsProvider`，用于本地开发和 UI 验证。
- 真实 Douyin metrics 需要独立实现用户授权、token 管理、平台 API 接入、错误处理和隐私边界。
- `PublicationRecord` 成为发布结果与指标快照之间的稳定关联点。
- 核心指标模型保持平台无关，并允许不同平台指标字段缺失。
- fake metrics 不得被当成真实平台表现。

## 明确不在本批范围内

- 后端 API。
- 数据库表。
- 前端功能。
- Provider 代码实现。
- 真实指标抓取。
- 真实 Douyin API。
- OAuth、账号授权页面或 token 保存。
- token、secret、API key 或任何平台凭据保存。
- 定时同步。
- 数据分析推荐算法或自动内容优化。
- 自动发布、排期发布、真实上传或真实发布。
- v0.5 fake publishing workflow 语义修改。
- v0.4 scheduled draft workflow 语义修改。
- v0.3 rendering workflow 语义修改。
