# 架构

## 技术栈

- Backend: Python + `FastAPI`。
- Frontend: `React` + `Vite` + `Tailwind`。
- MVP Database: `SQLite`。
- Future Database: `PostgreSQL`。
- Video Rendering: `FFmpeg`。
- Deployment: `Docker Compose`。
- CI/CD: `GitHub Actions`。
- License: Apache-2.0。

本文档描述 creator-flow 的目标架构。Documentation Foundation 阶段已完成；v0.1 Local Runnable Skeleton 阶段允许实现最小 `FastAPI`、`React` + `Vite` + `Tailwind` 和 `SQLite` 本地骨架。

## 系统逻辑模块

- Material Import：接收用户显式选择的文本、聊天摘要、项目记录、截图、图片和链接。
- Content Plan：配置账号定位、内容主题、目标频率、内容偏好和发布平台偏好。
- Scheduler / Trigger Engine：按用户配置触发草稿生成，或支持手动触发生成。
- Content Project：跟踪素材、草稿、渲染状态、审核状态和发布意图。
- Topic Studio：基于导入素材和可选热点信号提出选题与角度。
- Script Studio：生成并编辑短视频脚本。
- Storyboard Studio：将脚本映射为画面、字幕、旁白和素材需求。
- Voice and Subtitle Pipeline：准备 TTS 输入、音频和字幕。
- Rendering Pipeline：通过 `FFmpeg` 生成 9:16 MP4。
- Review Queue：统一管理待审核的视频草稿和渲染结果。
- Publishing Preparation：准备平台元数据、发布检查和待确认发布意图。
- Human Review Gate：发布前要求用户明确审核与确认。
- Notification Service：提醒用户存在待审核草稿，当前仅定义接口方向。
- Metrics Feedback：保存发布后的基础表现指标，供后续选题优化和内容复盘。
- Provider Registry：通过稳定接口连接外部 AI、媒体、热点、渲染和发布服务。

## Provider 接口设计方向

Provider 接口用于隔离核心工作流与外部服务。

- `LLMProvider`：选题生成、脚本生成、改写建议、元数据草稿和结构化提取。
- `ImageProvider`：可选图片生成、图片编辑、封面辅助或视觉素材获取。
- `TTSProvider`：基于已审核脚本文本生成旁白音频。
- `VideoRenderer`：视频合成与渲染，MVP 实现方向为 `FFmpeg`。
- `PublisherProvider`：平台发布准备、状态查询和用户确认后的发布动作。
- `TrendSourceProvider`：可选热点信号获取，用于辅助选题和角度判断。
- `MetricsProvider`：平台指标适配层，用于后续读取发布后的基础表现指标。

Provider 实现不得将单一厂商或单一平台假设泄漏到核心领域模型中。

## 发布 Provider 边界

v0.5 的发布方向是 Human-Confirmed Douyin Publishing。抖音是首个平台实现方向，但平台细节必须由 `PublisherProvider`、发布准备模块和平台适配层承接，不能写死到 `ContentProject`、`ContentPlan`、`GenerationRun`、`Review Draft` 或其他核心模型中。

`PublisherProvider` 的职责边界：

- 准备平台元数据、发布检查、平台能力描述和发布状态查询。
- 只在用户明确确认发布后执行真实发布、上传或排期发布动作。
- 将平台返回的发布 id、状态、错误码和诊断信息转换为核心可理解的 `PublicationRecord` 或等价记录。
- 不拥有选题、脚本、分镜、渲染、审核或调度决策。

`Review Draft` 的 `approved` 状态不等于发布确认。它只表示草稿通过人工审核，可以进入后续渲染、发布准备或发布意图创建流程。任何公开发布、上传或排期发布都必须经过单独的 `PublishIntent` 人工确认状态。

后续发布能力应基于 `PublishIntent` / `PublicationRecord` 或等价模型：

- `PublishIntent`：记录平台目标、标题、描述、标签、封面建议、视频或渲染结果引用、待确认状态、确认人和确认时间。
- `PublicationRecord`：记录确认后的执行结果、平台返回 id、平台状态、错误信息、重试信息和查询时间。

凭据必须通过本地配置、环境变量或后续安全存储方案提供，不得进入 Git、测试数据、示例文档或运行时 artifact。v0.5 Batch 1 只定义该边界，不实现真实 OAuth、真实 token 保存、真实发布、真实上传、排期发布或自动发布。

## 指标 MetricsProvider 边界

v0.6 的指标反馈方向是 Metrics Feedback Loop。`MetricsProvider` 是平台指标适配层，用于后续把抖音或其他平台返回的表现数据转换为核心领域可以理解的指标快照；Douyin 只是未来一个 provider，不能把抖音专有字段、授权流程或接口形状写死到核心模型中。

`MetricsProvider` 的职责边界：

- 基于已存在的 `PublicationRecord` 或等价发布记录读取发布后指标。
- 将平台返回的播放、互动、观看质量和采集时间转换为平台无关的指标快照。
- 标记指标来源，例如 fake/local data 或真实平台数据。
- 允许部分指标为空，因为不同平台、账号权限和内容状态可用的指标不同。
- 不拥有选题、脚本、分镜、渲染、审核、发布确认或自动优化决策。

Provider 不应把 token、secret、账号授权细节、平台原始响应或平台专有字段泄漏到 `PublicationRecord`、`ContentProject`、`ContentPlan` 或其他核心模型中。凭据必须由后续独立的授权和安全存储方案处理，不得进入 Git、测试 fixtures、示例文档、日志样例或运行时 artifact。

后续可以实现 `FakeMetricsProvider` 作为本地开发 provider，用 deterministic fake metrics 支持 UI 与模型验证；fake metrics 必须被显式标记为 fake/local data，不能展示为真实平台表现。v0.6 Batch 1 只定义该架构边界，不实现 provider 代码、后端 API、数据库表、前端功能、真实指标抓取、真实 Douyin API、OAuth、token 保存或定时同步。

## Provider / Credential / Douyin integration roadmap

v0.7.0 release 之后的架构路线必须从 fake/local metrics review summary workflow 渐进进入抖音用户测试，而不是一次性跳到真实平台生产能力。

- v0.7.0 已完成 metrics review summary local fake/manual workflow，不改变 Provider 架构，只基于现有 `PublicationMetricSnapshot` 和 fake/local metrics source 做 metrics review summary，将指标转化为人工复盘参考。
- v0.8 建立 Provider registry / credential boundary / OAuth callback / token lifecycle 的安全基础，包括 provider capability metadata、connection status、credential reference metadata、secret redaction、授权失败状态和 audit log 方向。
- v0.9 做 Douyin Provider POC / Sandbox Integration，用 Douyin provider adapter skeleton、OAuth callback smoke test 或 mock/sandbox callback、token refresh dry-run 和最小指标读取 POC 验证边界。
- v1.0 才进入 Douyin Integration User Test Release，用于用户授权、账号连接状态和至少一种真实或 sandbox/manual fallback 指标回流测试。

核心领域模型不能依赖 Douyin 专有字段。`PublicationRecord`、`PublicationMetricSnapshot`、`MetricSource`、`ContentPlan`、`TopicCandidate`、`ScriptDraft` 和其他核心模型只能保存平台无关的必要字段；Douyin 原始响应、平台专有字段、scope 细节和接口差异应留在 provider adapter、provider metadata 或受控附加 metadata 中。

### Provider Registry

v0.8 的 Provider registry 或等价注册表方向用于描述平台能力，而不是直接实现真实平台接入。注册表至少应能表达：

- `provider_id`：稳定 provider 标识，例如 `fake_local`、`douyin_sandbox` 或 `douyin_real`。
- `provider_name`：面向用户或审查者可读的 provider 名称。
- `provider_type`：能力类型，例如 `llm`、`renderer`、`publisher`、`metrics` 或 `platform`。
- `source_type`：数据来源类型，例如 `fake_local`、`sandbox` 或 `real`。
- capability metadata：例如 `supports_oauth`、`supports_metrics_read`、`supports_publish_prepare`、`supports_real_publish` 和 `supports_sandbox`。

Provider adapter 负责隔离平台 API、OAuth scope、错误码、字段差异和原始响应。adapter 不能把 Douyin 或其他平台细节泄漏到核心领域模型中，也不能让 UI 或 API response 暗示未完成能力已经可用。

### Provider Registry Backend Foundation

v0.8 Batch 2 引入 backend-only Provider Registry metadata，作为 provider/source/capability 的只读 source of truth。registry descriptor 包含 `provider_id`、`provider_name`、`provider_type`、`source_type`、`implementation_status`、`connection_status` 和 capability metadata。

本批 registry 至少区分：

- `fake_local`：本地 fake/demo/test provider，`source_type=fake_local`，不要求授权。
- `douyin_sandbox`：sandbox placeholder metadata，`source_type=sandbox`，当前不可用。
- `douyin_real`：future real provider placeholder metadata，`source_type=real`，当前不可用。

Frontend 和 API consumer 只能看到非敏感 metadata、source type、connection status、capability metadata 和 boundary notes。未实现的 OAuth、metrics read、publish prepare、real publish、token refresh、disconnect 和 revoke 能力必须保持 `false`；未来规划只能通过 `implementation_status` 或 `boundary_notes` 表达，不能通过 capability `true` 暗示能力可用。

Provider Registry 不读取 token、secret、credential、API key 或 OAuth client secret，不读取环境变量中的真实密钥，不连接数据库，不调用外部服务。Registry 只描述 metadata，不等于真实 provider adapter，也不执行 OAuth、连接、刷新、撤销、指标读取、上传、发布或排期发布。

### Provider Registry Frontend Read-only Boundary

v0.8 Batch 3 在前端增加只读 Provider Registry UI，但 frontend 只能消费 backend Provider Registry 的只读 metadata。该 UI 展示 provider metadata、source type、implementation status、connection status、capability metadata 和 boundary notes，帮助用户和审查者区分 `fake_local`、`douyin_sandbox` 和 `douyin_real`。

Frontend 不保存、不缓存、不展示 token、secret、credential、authorization code、API key 或 OAuth client secret，也不能从 metadata 推断真实平台已经可用。`fake_local` 可以展示为 local fake/demo/test workflow；`douyin_sandbox` 和 `douyin_real` 必须展示为 placeholder / not available，planned / unavailable provider 不能显示为可用真实集成。

未实现的 OAuth、metrics read、publish prepare、real publish、token refresh、disconnect 和 revoke 能力必须显示为 unavailable / disabled / not implemented。future real provider planning 只能通过 `implementation_status` 和 `boundary_notes` 表达，不能通过 capability `true`、按钮或其他交互暗示已可用。

该 UI 不提供 connect / authorize / refresh / revoke / disconnect / upload / publish / schedule 操作，也不新增写 API。它不等于真实 provider adapter，不等于 OAuth 管理界面，也不等于 Credential 管理界面。

### Provider Connection State Backend Boundary

v0.8 Batch 4 增加 backend-only Provider Connection State metadata layer。该层依赖 Provider Registry 作为 provider source of truth，只为 registry 中已知的 `fake_local`、`douyin_sandbox` 和 `douyin_real` 返回 connection state metadata；数据库中未知 `provider_id` 的记录不得被视为真实 provider，也不得出现在只读 API response 中。

Provider Connection State 可以返回 `connection_status`、`authorization_status`、`sensitive_storage_status`、`safe_status_message` 和 boundary notes，用于表达未连接、未实现、授权失败、权限不足、token 过期或 provider error 等状态方向。该状态层只保存非敏感 metadata，不保存 token、secret、API key、credential material、authorization code、OAuth client secret 或平台原始响应。

该 metadata layer 不读取环境变量中的真实平台密钥，不读取本地凭据文件，不调用外部服务，不实现 OAuth，不执行 token exchange，不等于 Credential storage，也不等于 real provider adapter。frontend 和 API consumer 只能看到非敏感 status metadata；future real provider planning 只能通过 `implementation_status`、`connection_status`、`authorization_status`、`sensitive_storage_status` 和 `boundary_notes` 表达，不能通过 capability `true`、`connected` 状态或写 API 暗示已可用。

Batch 4 新增的 `provider_connection_states` 表只允许保存 provider id、source type、connection status、authorization status、sensitive storage status、safe status message、状态变化原因和创建/更新时间等 metadata。表结构不得出现可承载敏感值的字段名，例如 access token、refresh token、API key、client secret、authorization code、credential material、encrypted credential、private key、raw response、OAuth code 或 password。

### Provider Connection State Frontend Read-only Boundary

v0.8 Batch 5 在前端增加只读 Provider Connection State UI，但 frontend 只能消费 backend Provider Connection State 的只读 metadata。该 UI 可以展示 `connection_status`、`authorization_status`、`sensitive_storage_status`、`safe_status_message` 和 `boundary_notes`，帮助用户和审查者理解 provider connection state 与 sensitive storage status 边界。

Frontend 不保存、不缓存、不展示 token、secret、API key、credential material、authorization code 或 OAuth client secret，也不能从 metadata 推断真实平台已经可用。UI 必须显式区分 `fake_local`、`douyin_sandbox` 和 `douyin_real`；planned / unavailable provider 只能展示为 placeholder / not available / not_connected / not_implemented。

该 UI 不提供 connect / authorize / refresh / revoke / disconnect / upload / publish / schedule 操作，也不新增写 API。future real provider planning 只能通过 `implementation_status`、`connection_status`、`authorization_status`、`sensitive_storage_status` 和 `boundary_notes` 展示，不能通过按钮、`connected` 状态或其他交互暗示已可用。

Provider Connection State UI 不等于真实 provider adapter，不等于 OAuth 管理界面，不等于 Credential 管理界面，也不等于平台账号设置页。

### Provider Credential Reference Backend Boundary

v0.8 Batch 6 增加 backend-only Provider Credential Reference metadata layer。该层依赖 Provider Registry 作为 provider source of truth，只为 registry 中已知的 `fake_local`、`douyin_sandbox` 和 `douyin_real` 返回 credential reference metadata；数据库中未知 `provider_id` 的记录不得被视为真实 provider，也不得出现在只读 API response 中。

Provider Credential Reference 可以返回 `reference_status`、`storage_status`、`redaction_policy_status`、`safe_status_message` 和 boundary notes，用于表达 credential readiness、storage readiness 和 redaction policy readiness 的方向。该 metadata layer 只保存非敏感 metadata，不保存 token、secret、API key、credential material、authorization code、OAuth client secret、private key、平台原始响应或任何可用于真实授权的值。

该 metadata layer 不读取环境变量中的真实平台密钥，不读取本地凭据文件，不调用外部服务，不实现 OAuth，不执行 token exchange，不等于 Credential storage，不等于 encrypted token storage，也不等于 real provider adapter。frontend 和 API consumer 只能看到非敏感 reference metadata；future real provider planning 只能通过 `implementation_status`、`reference_status`、`storage_status`、`redaction_policy_status` 和 `boundary_notes` 表达，不能通过 stored / configured / connected 状态或写 API 暗示已可用。

Batch 6 新增的 `provider_credential_references` 表只允许保存 provider id、source type、reference kind、reference status、storage status、redaction policy status、safe display name、safe status message、状态变化原因和创建/更新时间等 metadata。表结构不得出现可承载敏感值的字段名，例如 access token、refresh token、token value、API key、secret value、client secret、authorization code、credential material、encrypted credential、private key、raw response、OAuth code、password、bearer token 或 session cookie。

### Secret Redaction Boundary

v0.8 Batch 6 增加 backend-only secret redaction helper，用于统一屏蔽敏感 key 和明显敏感文本模式。redaction helper 可以识别 access token、refresh token、token、API key、secret、client secret、authorization code、credential material、encrypted credential、private key、OAuth code、password、bearer、cookie 和 session 等 key，并对 dict / list / tuple 嵌套结构递归替换为固定 `[REDACTED]` 占位。

redaction helper 还会处理明显的 `access_token=...`、`refresh_token=...`、`api_key=...`、`client_secret=...`、`authorization_code=...` 和 `Bearer ...` 文本模式。它用于减少日志、错误消息和测试断言中的泄密风险，但不代表真实 secret manager、生产级 KMS、Credential storage 或 encrypted token storage。helper 不读取环境变量，不读取本地 secret 文件，不连接数据库，也不调用外部服务。

### Provider Credential Reference Frontend Read-only Boundary

v0.8 Batch 7 在前端增加只读 Provider Credential Reference UI，但 frontend 只能消费 backend Provider Credential Reference 的只读 metadata。该 UI 可以展示 `reference_kind`、`reference_status`、`storage_status`、`redaction_policy_status`、`safe_display_name`、`safe_status_message` 和 `boundary_notes`，帮助用户和审查者理解 credential reference readiness、storage readiness 和 redaction policy boundary。

Frontend 不保存、不缓存、不展示 token、secret、API key、authorization code、OAuth client secret、credential material 或 private key，也不能从 reference metadata 推断真实平台已经可用。UI 必须显式区分 `fake_local`、`douyin_sandbox` 和 `douyin_real`；planned / unavailable provider 只能展示为 placeholder / not available / not_implemented。

该 UI 不提供 connect / authorize / refresh / revoke / disconnect / upload / publish / schedule 操作，也不新增写 API。该 UI 不提供 secret input、token viewer、credential viewer 或 credential 管理入口。`redaction_policy_status` 只能作为安全边界 metadata 展示，不能暗示生产级 KMS、secret manager 或 encrypted token storage 已实现。

Future real provider planning 只能通过 `implementation_status`、`reference_status`、`storage_status`、`redaction_policy_status` 和 `boundary_notes` 展示，不能通过按钮、configured 状态、stored 状态或 connected 状态暗示已可用。Provider Credential Reference UI 不等于真实 provider adapter，不等于 OAuth、Credential 管理界面、Secret Manager，也不等于平台账号设置页。

### Provider Security Audit Event Backend Boundary

v0.8 Batch 8 增加 backend-only Provider Security Audit Event metadata layer。该层依赖 Provider Registry 作为 provider source of truth，只为 registry 中已知的 `fake_local`、`douyin_sandbox` 和 `douyin_real` 返回 audit event metadata；数据库中未知 `provider_id` 的记录不得被视为真实 provider audit event，也不得出现在只读 API response 中。

Provider Security Audit Event 可以返回 `event_type`、`event_status`、`event_severity`、`actor_type`、`redaction_status`、`safe_event_message`、`safe_metadata` 和 `boundary_notes`，用于表达 provider security boundary、connection status、authorization status、credential reference、redaction 和错误状态相关的安全审计方向。该 metadata layer 只保存非敏感 / redacted metadata，不保存 token、secret、API key、credential material、authorization code、OAuth client secret、private key、raw request、raw response、raw payload、真实平台返回或任何可用于真实授权的值。

该 metadata layer 不读取环境变量中的真实平台密钥，不读取本地凭据文件，不调用外部服务，不实现 OAuth，不执行 token exchange，不等于 OAuth audit trail，不等于 production SIEM、external log shipping、compliance archive 或 security monitoring platform，也不等于 real provider adapter。frontend 和 API consumer 只能看到非敏感 / redacted audit metadata。

Batch 8 新增的 `provider_security_audit_events` 表只允许保存 audit event id、provider id、source type、event type、event status、event severity、actor type、redaction status、safe event message、safe metadata、boundary notes 和创建时间等 metadata。表结构不得出现可承载敏感值的字段名，例如 access token、refresh token、token value、API key、secret value、client secret、OAuth client secret、authorization code、credential material、encrypted credential、private key、raw request、raw response、raw payload、OAuth code、password、bearer token 或 session cookie。

audit event service 必须复用 secret redaction helper。写入 audit event 时，`source_type` 必须从 Provider Registry 派生，不能信任调用方传入；`safe_event_message` 和 `safe_metadata` 必须先脱敏再保存。future real provider planning 只能通过 `implementation_status`、`event_type`、`event_status`、`redaction_status` 和 `boundary_notes` 表达，不能通过 connected、authorized、stored、published 或 real synced 状态暗示已可用。

### Provider Security Audit Event Frontend Read-only Boundary

v0.8 Batch 9 在前端增加只读 Provider Security Audit Event UI，但 frontend 只能消费 backend Provider Security Audit Event 的只读 metadata。该 UI 可以展示 `event_type`、`event_status`、`event_severity`、`actor_type`、`redaction_status`、`safe_event_message`、`safe_metadata`、`boundary_notes` 和 `created_at`，帮助用户和审查者理解 provider security audit event 与 redacted audit metadata boundary。

Frontend 不保存、不缓存、不展示 token、secret、API key、authorization code、OAuth client secret、credential material、private key、raw request、raw response 或 raw payload，也不能从 audit metadata 推断真实平台已经可用。UI 必须显式区分 `fake_local`、`douyin_sandbox` 和 `douyin_real`；planned / unavailable provider 只能展示为 placeholder / not available / not_implemented。

该 UI 不提供 connect / authorize / refresh / revoke / disconnect / upload / publish / schedule 操作，也不新增写 API。该 UI 不提供 secret input、token viewer、credential viewer、audit event writer、raw request viewer、raw response viewer 或 raw payload viewer。`redaction_status` 只能作为安全边界 metadata 展示，不能暗示生产级 SIEM、compliance archive、external log shipping 或 security monitoring 已实现。

Future real provider planning 只能通过 `implementation_status`、`event_type`、`event_status`、`redaction_status` 和 `boundary_notes` 展示，不能通过按钮、connected 状态、authorized 状态、stored 状态、synced 状态或 published 状态暗示已可用。Provider Security Audit Event UI 不等于真实 provider adapter，不等于 OAuth、Credential 管理界面、Secret Manager、SIEM、compliance archive，也不等于平台账号设置页。

### Provider OAuth State & Callback Boundary Backend Foundation

v0.8 Batch 10 增加 backend-only Provider OAuth Boundary metadata layer。该层依赖 Provider Registry 作为 provider source of truth，只为 registry 中存在的 `fake_local`、`douyin_sandbox` 和 `douyin_real` 返回 OAuth boundary metadata；数据库中未知 `provider_id` 的记录不得被视为真实 provider OAuth boundary，也不得出现在只读 API response 中。

Provider OAuth Boundary 可以返回 `oauth_policy_status`、`state_policy_status`、`callback_policy_status`、`csrf_protection_status`、`redirect_uri_policy_status`、`token_exchange_policy_status`、`token_storage_policy_status`、`error_redaction_policy_status`、`audit_event_policy_status`、`safe_status_message` 和 `boundary_notes`，用于表达 OAuth readiness、state/callback/CSRF/redirect URI/token exchange/token storage/error redaction/audit event policy 的安全边界。

该 metadata layer 只保存非敏感 OAuth boundary metadata，不保存 token、secret、API key、credential material、authorization code、OAuth client secret、OAuth state value、private key、raw request、raw response 或 raw payload。它不读取环境变量中的真实平台密钥，不读取本地凭据文件，不调用外部服务，不实现 OAuth，不生成真实 provider authorization URL，不实现 callback route，不实现 state storage，不执行 token exchange，不等于 Credential storage，也不等于 real provider adapter。

Frontend 和 API consumer 只能看到非敏感 OAuth boundary metadata。Future real provider planning 只能通过 `implementation_status`、`oauth_policy_status`、`state_policy_status`、`callback_policy_status`、`csrf_protection_status`、`redirect_uri_policy_status`、`token_exchange_policy_status`、`token_storage_policy_status`、`error_redaction_policy_status`、`audit_event_policy_status` 和 `boundary_notes` 表达，不能通过 enabled、connected、authorized、state stored、callback active、token exchanged、token stored 或 real synced 状态暗示已可用。

### Provider OAuth Boundary Frontend Read-only Boundary

v0.8 Batch 11 在前端增加只读 Provider OAuth Boundary UI，但 frontend 只能消费 backend Provider OAuth Boundary 的只读 metadata。该 UI 可以展示 `oauth_policy_status`、`state_policy_status`、`callback_policy_status`、`csrf_protection_status`、`redirect_uri_policy_status`、`token_exchange_policy_status`、`token_storage_policy_status`、`error_redaction_policy_status`、`audit_event_policy_status`、`safe_status_message` 和 `boundary_notes`，帮助用户和审查者理解 provider OAuth state / callback / token boundary。

Frontend 不保存、不缓存、不展示 token、secret、API key、authorization code、OAuth client secret、OAuth state value、credential material、private key、raw request、raw response 或 raw payload，也不能从 OAuth boundary metadata 推断真实平台已经可用。UI 必须显式区分 `fake_local`、`douyin_sandbox` 和 `douyin_real`；planned / unavailable provider 只能展示为 placeholder / not available / not_implemented / required_planned。

该 UI 不提供 connect / authorize / OAuth start / callback / token exchange / refresh / revoke / disconnect / upload / publish / schedule 操作，也不新增写 API。该 UI 不提供 secret input、token viewer、credential viewer、authorization code input、OAuth state input、raw request viewer、raw response viewer 或 raw payload viewer。`required_planned` 只能作为未来边界规划展示，不能暗示 CSRF / state / callback 保护已经启用。

`token_exchange_policy_status` 和 `token_storage_policy_status` 只能作为安全边界 metadata 展示，不能暗示 token exchange 或 token storage 已实现。Future real provider planning 只能通过 `implementation_status`、`oauth_policy_status`、`state_policy_status`、`callback_policy_status`、`csrf_protection_status`、`redirect_uri_policy_status`、`token_exchange_policy_status`、`token_storage_policy_status`、`error_redaction_policy_status`、`audit_event_policy_status` 和 `boundary_notes` 展示，不能通过按钮、connected 状态、authorized 状态、state stored、callback active、token exchanged、token stored 或 real synced 状态暗示已可用。Provider OAuth Boundary UI 不等于真实 provider adapter，不等于 OAuth、Credential 管理界面、Secret Manager、SIEM、callback debugger、token console，也不等于平台账号设置页。

### Provider Token Lifecycle Boundary Backend Foundation

v0.8 Batch 12 增加 backend-only Provider Token Lifecycle Boundary metadata layer。该层依赖 Provider Registry 作为 provider source of truth，只能为 registry 中存在的 `fake_local`、`douyin_sandbox` 和 `douyin_real` 返回 token lifecycle boundary metadata；数据库中未知 `provider_id` 的记录不得被视为真实 provider token lifecycle boundary，也不得出现在只读 API response 中。

Provider Token Lifecycle Boundary 可以返回 `token_lifecycle_policy_status`、`token_storage_policy_status`、`refresh_policy_status`、`expiry_policy_status`、`revoke_policy_status`、`disconnect_policy_status`、`rotation_policy_status`、`error_redaction_policy_status`、`audit_event_policy_status`、`safe_status_message` 和 `boundary_notes`，用于表达 token lifecycle、token storage、refresh、expiry handling、revoke、disconnect、rotation、error redaction 和 audit event policy 的安全边界。

该 metadata layer 只保存非敏感 token lifecycle boundary metadata，不保存 access token、refresh token、token value、secret、API key、credential material、authorization code、OAuth client secret、OAuth state value、private key、raw request、raw response 或 raw payload。它不读取环境变量中的真实平台密钥，不读取本地凭据文件，不调用外部服务，不实现 OAuth，不执行 token exchange，不执行 token refresh，不执行 token revoke，不执行 disconnect，也不等于 Credential storage、encrypted token storage 或 real provider adapter。

Frontend 和 API consumer 只能看到非敏感 token lifecycle boundary metadata。Future real provider planning 只能通过 `implementation_status`、`token_lifecycle_policy_status`、`token_storage_policy_status`、`refresh_policy_status`、`expiry_policy_status`、`revoke_policy_status`、`disconnect_policy_status`、`rotation_policy_status`、`error_redaction_policy_status`、`audit_event_policy_status` 和 `boundary_notes` 表达，不能通过 enabled、connected、authorized、token stored、token refreshed、token revoked、disconnected、rotated 或 real synced 状态暗示已可用。

### Provider Token Lifecycle Boundary Frontend Read-only Boundary

v0.8 Batch 13 在前端增加只读 Provider Token Lifecycle Boundary UI，但 frontend 只能消费 backend Provider Token Lifecycle Boundary 的只读 metadata。该 UI 可以展示 `token_lifecycle_policy_status`、`token_storage_policy_status`、`refresh_policy_status`、`expiry_policy_status`、`revoke_policy_status`、`disconnect_policy_status`、`rotation_policy_status`、`error_redaction_policy_status`、`audit_event_policy_status`、`safe_status_message` 和 `boundary_notes`，帮助用户和审查者理解 provider token lifecycle boundary。

Frontend 不保存、不缓存、不展示 access token、refresh token、token value、secret、API key、authorization code、OAuth client secret、OAuth state value、credential material、private key、raw request、raw response、raw payload、token expiry value、token refresh response、token revoke response 或 provider token response，也不能从 Token Lifecycle boundary metadata 推断真实平台已经可用。UI 必须显式区分 `fake_local`、`douyin_sandbox` 和 `douyin_real`；planned / unavailable provider 只能展示为 placeholder / not available / not_implemented / required_planned。

该 UI 不提供 connect / authorize / OAuth start / callback / token exchange / refresh / revoke / disconnect / rotate / mark expired / upload / publish / schedule 操作，也不新增写 API。该 UI 不提供 secret input、token viewer、credential viewer、authorization code input、OAuth state input、raw request viewer、raw response viewer、raw payload viewer、token response viewer、refresh response viewer 或 revoke response viewer。

`required_planned` 只能作为未来边界规划展示，不能暗示 refresh / expiry / revoke / disconnect / rotation 已启用。`token_storage_policy_status`、`refresh_policy_status`、`revoke_policy_status`、`disconnect_policy_status` 和 `rotation_policy_status` 只能作为安全边界 metadata 展示，不能暗示 token storage、token refresh、token revoke、disconnect 或 token rotation 已实现。Future real provider planning 只能通过 `implementation_status`、`token_lifecycle_policy_status`、`token_storage_policy_status`、`refresh_policy_status`、`expiry_policy_status`、`revoke_policy_status`、`disconnect_policy_status`、`rotation_policy_status`、`error_redaction_policy_status`、`audit_event_policy_status` 和 `boundary_notes` 展示，不能通过按钮、connected 状态、authorized 状态、token stored、token refreshed、token revoked、disconnected、rotated 或 real synced 状态暗示已可用。Provider Token Lifecycle Boundary UI 不等于真实 provider adapter，不等于 OAuth、Credential 管理界面、Secret Manager、token console、token lifecycle executor，也不等于平台账号设置页。

### Provider Integration Readiness Summary Backend Foundation

v0.8 Batch 14 增加 backend-only Provider Integration Readiness Summary computed metadata layer。该层依赖 Provider Registry 作为 provider source of truth，并聚合 Provider Registry、Connection State、Credential Reference、Security Audit、OAuth Boundary 和 Token Lifecycle Boundary 的非敏感 metadata。

Provider Integration Readiness Summary 不新增数据库表，不保存 readiness state，不读取环境变量中的真实平台密钥，不读取 token、secret、authorization code、OAuth state value、raw request、raw response 或 raw payload，不调用外部服务，不实现 OAuth，不执行 token exchange、token refresh、token revoke、disconnect 或 rotation，也不等于真实 provider adapter、Credential storage 或 v0.9 POC 已完成。

API consumer 只能看到非敏感 readiness metadata，例如 `overall_readiness_status`、`v0_9_poc_readiness_status`、`readiness_items`、`blocking_reasons`、`next_safe_steps`、`safe_summary` 和 `boundary_notes`。`fake_local` 的 local readiness 只代表 local fake/demo/test workflow 可用，不得解释为 real provider readiness。`douyin_sandbox` / `douyin_real` 的 metadata readiness 不得解释为真实 OAuth、真实 token lifecycle 或真实 metrics readiness。

Future real provider planning 只能通过 readiness statuses、`blocking_reasons`、`next_safe_steps` 和 `boundary_notes` 表达，不能通过 ready、connected、authorized、token stored、token refreshed、real synced 或 published 状态暗示已可用。

### Provider Integration Readiness Summary Frontend Read-only Boundary

v0.8 Batch 15 在前端增加只读 Provider Integration Readiness Summary UI，但 frontend 只能消费 backend Provider Integration Readiness Summary 的只读 metadata。Frontend 不保存、不缓存、不展示 access token、refresh token、token value、secret、API key、authorization code、OAuth client secret、OAuth state value、credential material、private key、raw request、raw response、raw payload、token expiry value、token refresh response、token revoke response 或 provider token response，也不能从 readiness summary metadata 推断真实平台可用。

UI 必须显式区分 `fake_local`、`douyin_sandbox` 和 `douyin_real`。`fake_local` 的 `local_fake_ready` 只能展示为 local fake workflow readiness，不得展示为 real provider readiness。`douyin_sandbox` / `douyin_real` 的 `metadata_only` 或 `placeholder_not_ready` 不得展示为 OAuth ready、token ready、metrics ready、publish ready 或 production ready。

该 UI 可以展示 `overall_readiness_status`、`v0_9_poc_readiness_status`、`readiness_items`、`blocking_reasons`、`next_safe_steps`、`safe_summary` 和 `boundary_notes`。该 UI 不提供 connect / authorize / OAuth start / callback / token exchange / refresh / revoke / disconnect / rotate / mark expired / upload / publish / schedule 操作，也不提供 readiness approve、override、certify、production readiness declaration 或 v0.9 POC start 操作。

该 UI 不提供 secret input、token viewer、credential viewer、authorization code input、OAuth state input、raw request viewer、raw response viewer、raw payload viewer、token response viewer、refresh response viewer 或 revoke response viewer。Readiness summary 只能作为 review aid 展示，不能暗示 production readiness certification。

Future real provider planning 只能通过 readiness statuses、`blocking_reasons`、`next_safe_steps` 和 `boundary_notes` 展示，不能通过按钮、connected 状态、authorized 状态、token stored、token refreshed、real synced、published 或 production ready 状态暗示已可用。Provider Integration Readiness Summary UI 不等于真实 provider adapter，也不等于 OAuth、Credential 管理界面、Secret Manager、token console、token lifecycle executor、production readiness dashboard 或平台账号设置页。

### Credential Boundary

- token、secret、refresh token、API key 和平台账号凭据不得进入 Git。
- token、secret、authorization code、refresh token 和 API key 不得写入日志、测试 fixtures、测试快照、示例数据、错误响应或运行时 artifact。
- 前端不得接收、缓存或展示 token、secret、refresh token 或平台原始凭据。
- 前端只能看到 connection status、provider display name、source type、capability metadata 和非敏感账号 metadata。
- 后端只允许保存加密或引用化后的 credential material；生产级保存策略仍需后续独立实现和审查。
- 本地开发可以使用 fake/local placeholder，但 placeholder 必须明确不是真实 token，也不能被文档、UI 或测试描述成真实凭据。
- 本地安全存储策略方向可以包括环境变量、操作系统 secret store、开发专用 ignored config 或后续加密存储，但所有策略都必须排除 Git、日志、前端和测试快照。

### OAuth Boundary

- OAuth `state` 参数必须用于 CSRF 防护。
- OAuth callback 必须校验 `state`，并拒绝缺失、过期或不匹配的回调。
- callback 错误必须对用户和日志排查可见，但不能泄漏 token、secret、authorization code、refresh token、API key 或平台原始凭据。
- redirect URI 必须有明确配置边界，不能由不可信输入任意覆盖。
- token exchange 只能在后端完成。
- access token / refresh token 不得暴露给前端。
- access token / refresh token 加密保存策略必须在真实 OAuth 前完成设计；v0.8 Batch 1 只定义方向，不保存真实 token。
- token refresh、expiry、revoke 和 disconnect 必须有生命周期策略，并能表达未连接、授权失败、token 过期、权限不足和 provider 接口失败等状态。

### Audit / Logging

- 后续 audit log 应记录 connection status 变化方向，例如未连接、已连接、断开连接和重新授权。
- 后续 audit log 应记录授权失败、断开连接、token 过期、权限不足和 provider 接口失败等事件方向。
- 日志不得包含 token、secret、authorization code、refresh token、API key、OAuth client secret 或真实平台凭据。
- 错误消息必须可排查但不泄密；面向用户的错误应描述状态和下一步，而不是暴露平台原始响应或 credential material。

### Fake / Real Isolation

Provider 返回的数据必须明确 source 和授权状态。指标或连接状态至少需要能区分 `fake_local`、`douyin_sandbox`、`douyin_real`、未授权、授权失败、权限不足、token 过期和 provider 错误等情况。fake/local provider 必须继续可用，作为没有平台授权、平台权限不可用或用户只想本地演示时的 fallback。

`fake_local` 不能伪装成真实平台来源，`douyin_sandbox` 不能伪装成 `douyin_real`。所有 UI、API response 和文档都必须能区分 fake/local、sandbox/mock 和 real data。v0.7 fake/local metrics review summary workflow 在没有授权时仍应可用，并且仍然只代表本地开发、演示或测试数据。

Douyin 接入不得绕过平台开放能力、应用审核、OAuth、API 权限或用户授权。如果 v0.9 / v1.0 期间真实 API 权限不可用，架构应允许 manual import 或 mock/sandbox provider contract test 作为 fallback，而不是把 fake 或 sandbox 数据伪装成真实平台表现。

## 核心领域模型

- `UserMaterial`：用户导入的文本、图片、截图、链接、聊天摘要或项目记录。
- `ContentPlan`：账号定位、内容主题、目标频率、内容偏好和平台偏好。
- `GenerationSchedule`：计划生成频率、时间窗口、启用状态和触发规则。
- `GenerationRun`：一次手动或定时生成过程，记录输入、状态、输出草稿和错误信息。
- `ContentProject`：聚合素材、草稿、审核状态、渲染状态和发布准备信息。
- `TopicCandidate`：候选选题、角度、受众、开头钩子和生成理由。
- `ScriptDraft`：可编辑的短视频脚本。
- `Storyboard`：按顺序组织的场景、画面、旁白、字幕和时间建议。
- `AssetPlan`：所需图片、截图、生成素材、旁白、字幕和元数据。
- `RenderJob`：渲染请求、状态、日志、输入和输出路径。
- `ReviewTask`：待审核草稿、待审核视频或待确认发布事项。
- `PublishIntent`：平台目标、元数据、检查结果、确认状态和发布结果。
- `PublicationRecord`：用户确认后的一次发布执行记录，保存平台返回状态、结果、错误和查询信息。
- `PublicationMetricSnapshot`：发布后的基础表现指标快照，例如播放、互动、观看质量和采集时间，可与 `PublicationRecord` 关联。
- `MetricSource`：指标来源描述，用于区分 fake/local data 与真实平台数据。
- `ProviderConfig`：Provider 配置引用，不在 Git 中保存密钥。

## 内容项目状态机

计划状态包括：

- `draft`：项目已创建，仍可补充素材。
- `materials_ready`：已有足够显式导入素材用于生成。
- `scheduled_generation_pending`：等待计划任务触发生成。
- `generating`：正在执行一次 `GenerationRun`。
- `draft_generated`：已生成候选草稿。
- `topic_selected`：用户已接受或编辑选题。
- `script_ready`：脚本已生成并可进入分镜。
- `storyboard_ready`：分镜和素材需求已准备。
- `render_ready`：素材、字幕和旁白输入已准备渲染。
- `rendering`：渲染任务运行中。
- `review_ready`：草稿或 MP4 已进入 `Review Queue`。
- `publish_prepared`：平台元数据与检查结果已准备。
- `publish_confirmed`：用户明确确认发布。
- `published`：平台发布动作已完成。
- `metrics_collected`：发布后基础指标已回流。
- `archived`：项目归档。

发布相关流转必须经过 `review_ready`、`publish_prepared` 和 `publish_confirmed`。调度任务只能触发草稿生成，不能在没有人工确认时发布。

## 数据与文件存储边界

- `SQLite` 存储 MVP 本地元数据、项目状态、计划配置、生成运行记录和文件引用。
- `PostgreSQL` 可作为后续更持久或协作部署的数据库选项。
- 用户上传、生成素材、本地渲染结果、旁白音频、字幕和本地数据库属于运行时数据，不得提交到 Git。
- 密钥和 Provider 凭据必须通过本地配置或环境变量提供，不得进入仓库文件。
- 生成视频、音频、图片、字幕和上传素材应放在被忽略的运行时目录中，例如 `data/generated/` 或 `uploads/`。

## 热点来源边界

- 热点来源必须可配置、可关闭。
- 必须记录热点来源、采集时间和用户是否启用。
- 热点应作为外部不可信输入处理。
- 热点只能辅助选题，不得替代用户显式导入素材。
- 系统不得直接复制第三方受版权保护的内容或素材。

## 安全原则

- 只处理用户显式导入的素材和用户明确启用的数据来源。
- 不静默读取私有聊天、本地文件、浏览器状态或平台账号。
- 发布前必须要求用户明确确认。
- `Review Draft` approved 不等于发布确认；发布必须通过单独确认状态。
- 调度任务不得绕过 `Review Queue` 与人工确认。
- 凭据不得进入 Git 或生成文档示例。
- 外部 Provider 视为可替换且不可信的边界。
- 日志应支持调试，但避免不必要地保存私有内容。

## v0.1 暂不实现的技术内容

- 数据库迁移。
- `Docker Compose` 部署。
- `GitHub Actions` 工作流。
- Provider 实现。
- `FFmpeg` 命令编排。
- 抖音发布集成。
- 纯 AI 文生视频生成。
