# ADR 0017: Fake/local metrics review summary boundary

## 状态

Accepted

## 背景

v0.6.0 已完成 local fake/manual metrics feedback workflow：`PublicationRecord` 可以关联 `PublicationMetricSnapshot`，并可通过 deterministic `FakeMetricsProvider` 手动生成 `fake_local` metrics snapshots。v0.7 需要把这些 snapshots 转换为用户可读的内容复盘摘要，帮助人工复盘内容表现。

如果 summary 被描述成真实平台分析、自动推荐算法或自动优化入口，用户可能误以为 fake/local metrics 代表真实平台表现，或者误以为系统会自动改写选题、脚本和内容计划。这会破坏 v0.5 human-in-the-loop publishing 原则和 v0.6 fake/local metrics source 边界。

## 决策

v0.7 Batch 1 只实现 backend-only fake/local metrics review summary foundation。summary 必须关联同一项目下的 `PublicationRecord`，并基于该记录已有的 `PublicationMetricSnapshot` 列表生成。

新增 summary source 固定为 `fake_local`，并显式保存 `is_fake_local=true`。summary 字段可以包括 `summary_text`、`highlights`、`low_performance_signals`、`next_observations`、`snapshot_count`、`metric_window_start` 和 `metric_window_end`。指标字段允许部分为空；没有 metrics snapshots 时生成明确的 no-metrics fake/local summary，而不是推断真实表现。

`FakeMetricsReviewSummaryGenerator` 必须 deterministic：相同 snapshots 输入应生成稳定 summary 内容。summary 只作为人工复盘参考，不得自动修改 `TopicCandidate`、`ScriptDraft`、`ContentPlan`、`Review Draft`、`PublishIntent` 或 `PublicationRecord`。

## 理由

- v0.7 可以先验证复盘摘要的数据模型和 API 契约，而不引入真实平台 API、OAuth、token 或外部服务风险。
- `fake_local` 和 `is_fake_local` 双重标记可以降低把本地演示数据误解为真实平台分析的风险。
- no-metrics summary 让 API 在缺少快照时语义稳定，便于测试和后续 UI 展示明确空状态。
- 将 summary 限定为人工参考，可以避免演变成未经审查的自动推荐或自动内容优化。

## 结果

- 后续前端可以展示 summary，但必须继续标记 fake/local 边界。
- 后续真实平台 analysis 或 recommendation 能力必须作为独立设计处理，并经过 Provider、Credential、OAuth、source labeling 和用户授权边界。
- v0.5 fake publishing workflow、v0.6 fake metrics workflow、v0.4 scheduled draft workflow 和 v0.3 rendering workflow 语义不变。

## 明确不在本批范围内

- 真实 Douyin API。
- OAuth、账号授权页面或 token 保存。
- token、secret、API key 或任何平台凭据保存。
- 真实指标抓取或定时指标同步。
- 真实平台分析 dashboard。
- 数据分析推荐算法。
- 自动修改 `TopicCandidate`、`ScriptDraft` 或 `ContentPlan`。
- 自动优化内容。
- 真实上传、真实发布、排期发布或自动发布。
- 前端 UI。
