# 产品规格

## 产品定位

creator-flow 是一个可开源的 AI 短视频内容流水线。它帮助用户将显式导入的聊天摘要、项目记录、文本、图片、截图和链接，转化为待审核的短视频草稿，并最终生成适合短视频平台发布的 9:16 MP4。

首个发布平台是抖音，但产品架构必须保持平台无关，后续可扩展到其他短视频平台和其他语言用户。

## 用户问题

- 中国内容创作者和开发者有大量真实经验、项目记录和 AI 辅助解决问题的过程，但缺少稳定的短视频生产流水线。
- 程序员将真实问题、解决过程和开源项目进展转化为短视频时，需要反复完成选题、脚本、分镜、字幕和剪辑准备。
- 创作者需要可持续的内容频率，但又不能牺牲对素材、表达和发布动作的控制。
- 平台发布具有隐私、合规、版权和账号声誉风险，必须保留人工审核与确认。

## 目标用户

- 主要面向中国内容创作者与中国开发者。
- 首批场景为使用抖音发布技术型、AI 辅助型短视频的个人创作者。
- 后续仍可支持其他语言用户与其他短视频平台。
- 适合希望围绕真实开发过程、AI 工作流和开源项目持续输出内容的独立创作者。

## 内容方向

初始内容方向包括：

- 程序员真实问题。
- AI 辅助解决方案。
- 开源项目开发日志。

热点内容可以作为辅助选题来源，但账号主线必须来自用户的真实经验和原创素材。

## 核心使用场景

1. 用户配置账号定位、内容类型、目标受众、内容偏好和每周生成频率。
2. 用户显式导入近期聊天摘要、项目记录、图片、截图、文本或链接。
3. 用户可选择是否启用公开热点信号作为辅助输入。
4. 系统按照计划从近期显式导入素材中生成候选草稿。
5. 系统生成选题、脚本、分镜、字幕和素材方案。
6. 系统将自动生成的视频项目放入 `Review Queue`。
7. 用户审核、编辑并确认草稿后，系统才可继续渲染或准备发布。
8. 用户审核最终视频与发布信息后，才可确认发布。
9. 发布后的指标未来可用于辅助下一轮选题优化和内容复盘。

## 核心用户工作流

1. 用户创建或选择 `ContentPlan`。
2. 用户显式导入素材。
3. 用户手动触发生成，或由 `Scheduler / Trigger Engine` 按配置触发生成。
4. 系统基于用户素材和可选热点信号生成候选选题。
5. 用户审核并选择选题。
6. 系统生成脚本、分镜、字幕和素材方案。
7. 系统将草稿放入 `Review Queue`。
8. 用户审核并编辑草稿。
9. 系统通过脚本 + 图片或截图 + TTS + 字幕 + `FFmpeg` 合成 9:16 MP4。
10. 用户审核渲染结果。
11. 用户明确确认后，系统才可执行发布动作。

## MVP 功能范围

- 内容项目管理。
- `ContentPlan` 的基础配置：账号定位、内容类型、目标频率和内容偏好。
- 用户显式导入聊天摘要、文本、图片、截图和链接。
- 基于用户素材和可选热点信号生成选题。
- 脚本、分镜、字幕和素材方案生成与编辑。
- Provider 抽象：`LLMProvider`、`ImageProvider`、`TTSProvider`、`VideoRenderer`、`PublisherProvider`、`TrendSourceProvider`。
- 通过 `FFmpeg` 生成 9:16 MP4。
- `Review Queue` 管理待审核草稿。
- 抖音发布准备与人工确认发布。
- 第一版可先支持手动触发生成。
- 定时生成待审核草稿属于紧随其后的核心阶段。

定时生成草稿不等于静默自动发布。任何发布动作仍必须由用户明确确认。

## 明确非目标

- 不实现静默自动发布。
- 不自动读取用户私有 ChatGPT 历史。
- 不默认扫描本地文件、浏览器状态或私人账号。
- 不在 MVP 默认链路中依赖昂贵的纯 AI 文生视频。
- 不将核心流程绑定到单一 AI 服务或单一发布平台。
- 不向 Git 提交密钥、上传素材、本地数据库或生成媒体。
- 不在 MVP 中假设完整多租户 SaaS 能力。

## 自动化边界

- 自动化只能生成待审核草稿。
- 定时任务不得发布、排期发布或上传公开内容，除非用户在明确审核界面中确认。
- 自动化只能使用用户显式导入的素材，以及用户明确启用的外部热点来源。
- 自动化生成的草稿必须进入 `Review Queue`。
- 用户必须能查看草稿来源、生成时间和使用的主要输入。

## 热点边界

- 热点只能作为选题辅助信号。
- 必须记录热点来源、采集时间和用户是否启用。
- 热点来源应作为外部不可信输入处理。
- 不得直接复制第三方受版权保护的内容、素材、标题或表达。
- 热点不能替代用户真实经验和原创素材。

## 抖音发布人工确认原则

任何向抖音或其他平台发布、排期发布、上传用于公开发布的动作，都必须经过用户审核与明确确认。系统可以准备视频文件、标题、描述、标签、封面建议和平台检查结果，但默认不得发布。

## v0.5 发布 Provider 边界

v0.5 的目标是 Human-Confirmed Douyin Publishing：先建立发布准备、人工确认和平台 Provider 的边界，再逐步进入真实平台实现。抖音是首个平台实现方向，但核心领域模型不得把抖音写死；平台差异必须隔离在 `PublisherProvider`、发布准备模块和平台适配层中。

发布必须由用户在明确的确认动作后触发。`Review Draft` 的 `approved` 只表示草稿通过审核，可以进入后续发布准备或渲染准备，不等于发布、不等于上传、不等于排期发布，也不能绕过最终发布确认。

后续发布能力必须基于 `PublishIntent` / `PublicationRecord` 或等价模型，至少记录平台目标、待发布元数据、人工确认状态、确认时间、执行结果、平台返回状态和错误信息。`PublishIntent` 可以表示“用户准备发布并等待确认”的意图；`PublicationRecord` 或等价记录用于保存确认后的发布执行结果。

凭据不得进入 Git。真实 OAuth、真实发布、真实上传、真实 token 保存、排期发布和自动发布必须作为后续独立批次实现，并继续遵守 human-in-the-loop publishing 原则。v0.5 Batch 1 只定义文档边界，不实现任何真实 OAuth、真实发布、真实上传或凭据保存。

## v0.6 Metrics Feedback Loop 产品边界

v0.6 的目标是为发布后的内容记录指标反馈，帮助用户复盘内容表现，并为后续选题、脚本和内容计划优化提供辅助输入。指标反馈用于复盘和决策支持，不用于自动发布、排期发布、绕过审核或自动修改已确认内容。

后续系统可以围绕每条 `PublicationRecord` 展示一个或多个指标快照，例如播放、点赞、评论、分享、收藏、观看时长或完播率等基础表现字段。不同平台可提供的指标不同，因此指标字段必须允许部分为空，且核心模型不得绑定抖音专有字段。

指标回流必须显式区分真实平台数据与 fake/local data。fake metrics 只能用于本地开发、演示或测试，不得显示为真实平台表现，也不得用于对外宣称内容真实效果。

如果未来接入真实平台指标，必须经过用户授权，并且只能在授权范围内读取必要数据。系统不得未经授权抓取、推断、保存或展示平台账号数据，也不得保存 token、API key、secret 或其他凭据到 Git、示例数据、测试 fixtures、日志样例或运行时 artifact 中。

## v0.8 Provider & Credential Security Foundation 产品边界

v0.8 的产品目标是建立真实平台接入前的安全和架构基础，而不是承诺真实 Douyin 已可用。用户未来可以连接平台账号，但必须经过显式授权；在未授权时，fake/local workflow 仍应可用，且不要求授权。

面向用户的连接能力方向包括：

- 用户可以看到平台账号连接状态，例如未连接、已连接、授权失败、token 过期、权限不足和接口失败。
- 用户可以看到授权失败、权限不足、token 过期等错误状态，但错误信息不得泄漏 secret、authorization code、access token 或 refresh token。
- 用户可以断开连接，并使后续真实 provider 停止使用对应授权。
- 平台能力必须通过 Provider capability metadata 展示，例如是否支持 OAuth、指标读取、发布准备、真实发布或 sandbox。
- UI 不允许暗示尚未实现或未授权的能力已经可用。

v0.8 不承诺：

- 不承诺真实 Douyin 可用。
- 不承诺真实 OAuth 可用。
- 不承诺真实指标读取。
- 不承诺真实发布、上传或排期发布。
- 不承诺生产级 credential storage 已实现。

v0.8 Batch 1 只建立 Provider、Credential、OAuth、Secret 和 token lifecycle 的安全与架构边界；不新增业务功能、不新增 API、不新增数据库表、不保存 token，也不调用真实 Douyin 或其他外部服务。

v0.8 Batch 2 产品边界：

- 用户未来可以看到 provider、source、capability 和 connection status。
- `fake_local` 不要求授权，只代表本地 fake/demo/test workflow。
- `douyin_sandbox` 和 `douyin_real` 当前只是 placeholder metadata，不代表真实平台已接入。
- UI 不得把 planned / unavailable provider 展示为可用真实集成。
- v0.8 Batch 2 不承诺真实 Douyin 可用。
- v0.8 Batch 2 不承诺真实 OAuth。
- v0.8 Batch 2 不承诺真实指标读取。
- v0.8 Batch 2 不承诺真实发布、上传或排期发布。
- v0.8 Batch 2 不承诺生产级 credential storage 已实现。

v0.8 Batch 3 产品边界：

- 用户可以看到 provider、source、capability 和 connection status。
- 用户可以看到 `fake_local` 是当前可用 local fake workflow。
- 用户可以看到 `douyin_sandbox` 和 `douyin_real` 当前只是 placeholder metadata。
- 用户不会看到连接、授权、刷新、撤销、断开、上传、发布或排期发布入口。
- UI 不得让用户误以为真实 Douyin 已接入。
- v0.8 Batch 3 不承诺真实 Douyin 可用。
- v0.8 Batch 3 不承诺真实 OAuth。
- v0.8 Batch 3 不承诺真实指标读取。
- v0.8 Batch 3 不承诺真实发布、上传或排期发布。
- v0.8 Batch 3 不承诺生产级 credential storage 已实现。

v0.8 Batch 4 产品边界：

- 用户未来可以看到 provider connection state。
- 用户未来可以区分 `connection_status`、`authorization_status` 和 `sensitive_storage_status`。
- `fake_local` 显示为不需要授权、不需要敏感存储，且只代表 local fake workflow。
- `douyin_sandbox` 和 `douyin_real` 当前只是 placeholder metadata，`connection_status=not_connected`。
- 当前不会显示可执行的连接、授权、刷新、撤销、断开、上传、发布或排期发布入口。
- v0.8 Batch 4 不承诺真实 Douyin 可用。
- v0.8 Batch 4 不承诺真实 OAuth。
- v0.8 Batch 4 不承诺真实 Credential storage。
- v0.8 Batch 4 不承诺真实指标读取。
- v0.8 Batch 4 不承诺真实发布、上传或排期发布。
- v0.8 Batch 4 只建立 backend metadata foundation。

v0.8 Batch 5 产品边界：

- 用户可以看到 provider connection state。
- 用户可以区分 `connection_status`、`authorization_status` 和 `sensitive_storage_status`。
- 用户可以看到 `fake_local` 不需要授权、不需要敏感存储。
- 用户可以看到 `douyin_sandbox` 和 `douyin_real` 当前只是 placeholder metadata，`not_connected` / `not_implemented`。
- 用户不会看到连接、授权、刷新、撤销、断开、上传、发布或排期发布入口。
- UI 不得让用户误以为真实 Douyin 已接入。
- v0.8 Batch 5 不承诺真实 Douyin 可用。
- v0.8 Batch 5 不承诺真实 OAuth。
- v0.8 Batch 5 不承诺真实 Credential storage。
- v0.8 Batch 5 不承诺真实指标读取。
- v0.8 Batch 5 不承诺真实发布、上传或排期发布。
- v0.8 Batch 5 只建立 frontend read-only connection state display foundation。

v0.8 Batch 6 产品边界：

- 用户未来可以看到 provider credential reference readiness。
- 用户未来可以区分 `reference_status`、`storage_status` 和 `redaction_policy_status`。
- `fake_local` 显示为不需要 credential、不需要 token、不需要 secret、不需要敏感存储。
- `douyin_sandbox` 和 `douyin_real` 当前只是 placeholder metadata，`reference_status=not_implemented`。
- 当前不会显示可执行的连接、授权、刷新、撤销、断开、上传、发布或排期发布入口。
- 当前不会提供 secret input 表单。
- 当前不会提供 token viewer。
- 当前不会提供 credential 管理界面。
- v0.8 Batch 6 不承诺真实 Douyin 可用。
- v0.8 Batch 6 不承诺真实 OAuth。
- v0.8 Batch 6 不承诺真实 Credential storage。
- v0.8 Batch 6 不承诺 encrypted token storage。
- v0.8 Batch 6 不承诺真实指标读取。
- v0.8 Batch 6 不承诺真实发布、上传或排期发布。
- v0.8 Batch 6 只建立 backend metadata reference 和 redaction foundation。

v0.8 Batch 7 产品边界：

- 用户可以看到 provider credential reference readiness。
- 用户可以区分 `reference_kind`、`reference_status`、`storage_status` 和 `redaction_policy_status`。
- 用户可以看到 `fake_local` 不需要 credential、不需要 token、不需要 secret。
- 用户可以看到 `douyin_sandbox` 和 `douyin_real` 当前只是 placeholder metadata，`not_implemented`。
- 用户不会看到 secret input、token viewer 或 credential 管理界面。
- 用户不会看到连接、授权、刷新、撤销、断开、上传、发布或排期发布入口。
- UI 不得让用户误以为真实 Douyin 已接入。
- v0.8 Batch 7 不承诺真实 Douyin 可用。
- v0.8 Batch 7 不承诺真实 OAuth。
- v0.8 Batch 7 不承诺真实 Credential storage。
- v0.8 Batch 7 不承诺 encrypted token storage。
- v0.8 Batch 7 不承诺生产级 secret manager 或 KMS。
- v0.8 Batch 7 不承诺真实指标读取。
- v0.8 Batch 7 不承诺真实发布、上传或排期发布。
- v0.8 Batch 7 只建立 frontend read-only credential reference display foundation。

v0.8 Batch 8 产品边界：

- 用户未来可以看到 provider security audit event readiness。
- 用户未来可以区分 `event_type`、`event_status`、`event_severity`、`actor_type` 和 `redaction_status`。
- 用户未来可以看到 `fake_local`、`douyin_sandbox` 和 `douyin_real` 的 audit metadata source separation。
- `fake_local` 只表示 local fake/demo/test audit metadata。
- `douyin_sandbox` 和 `douyin_real` 当前只是 placeholder audit metadata。
- 当前不会显示真实 OAuth audit trail。
- 当前不会显示真实 token lifecycle event。
- 当前不会显示真实外部平台返回。
- 当前不会提供连接、授权、刷新、撤销、断开、上传、发布或排期发布入口。
- 当前不会新增 secret input、token viewer 或 credential 管理界面。
- v0.8 Batch 8 不承诺真实 Douyin 可用。
- v0.8 Batch 8 不承诺真实 OAuth。
- v0.8 Batch 8 不承诺真实 Credential storage。
- v0.8 Batch 8 不承诺生产级 SIEM、compliance log 或外部日志系统。
- v0.8 Batch 8 不承诺真实指标读取。
- v0.8 Batch 8 不承诺真实发布。
- v0.8 Batch 8 只建立 backend audit metadata 和 redacted audit log foundation。

v0.8 Batch 9 产品边界：

- 用户可以看到 provider security audit event readiness。
- 用户可以区分 `event_type`、`event_status`、`event_severity`、`actor_type` 和 `redaction_status`。
- 用户可以看到 `fake_local`、`douyin_sandbox` 和 `douyin_real` 的 audit metadata source separation。
- 用户只能看到 `safe_event_message` 和 `safe_metadata`。
- `fake_local` 只表示 local fake/demo/test audit metadata。
- `douyin_sandbox` 和 `douyin_real` 当前只是 placeholder audit metadata。
- 当前不会显示真实 OAuth audit trail。
- 当前不会显示真实 token lifecycle event。
- 当前不会显示真实外部平台返回。
- 当前不会显示 raw request、raw response 或 raw payload。
- 当前不会提供 audit event 写入 UI。
- 当前不会提供连接、授权、刷新、撤销、断开、上传、发布或排期发布入口。
- 当前不会新增 secret input、token viewer 或 credential 管理界面。
- v0.8 Batch 9 不承诺真实 Douyin 可用。
- v0.8 Batch 9 不承诺真实 OAuth。
- v0.8 Batch 9 不承诺真实 Credential storage。
- v0.8 Batch 9 不承诺生产级 SIEM、compliance log 或外部日志系统。
- v0.8 Batch 9 不承诺真实指标读取。
- v0.8 Batch 9 不承诺真实发布。
- v0.8 Batch 9 只建立 frontend read-only audit metadata display foundation。

v0.8 Batch 10 产品边界：

- 用户未来可以看到 provider OAuth boundary readiness。
- 用户未来可以区分 `oauth_policy_status`、`state_policy_status`、`callback_policy_status`、`csrf_protection_status`、`redirect_uri_policy_status`、`token_exchange_policy_status`、`token_storage_policy_status`、`error_redaction_policy_status` 和 `audit_event_policy_status`。
- `fake_local` 显示为不需要 OAuth、不需要 state、不需要 callback、不需要 token。
- `douyin_sandbox` 和 `douyin_real` 当前只是 OAuth boundary placeholder metadata，`not_implemented` / `required_planned`。
- 当前不会显示真实 OAuth 授权入口。
- 当前不会显示真实 OAuth callback。
- 当前不会生成真实授权 URL。
- 当前不会保存 OAuth state value。
- 当前不会保存 authorization code。
- 当前不会执行 token exchange。
- 当前不会保存 access token 或 refresh token。
- 当前不会提供连接、授权、刷新、撤销、断开、上传、发布或排期发布入口。
- 当前不会新增 secret input、token viewer 或 credential 管理界面。
- v0.8 Batch 10 不承诺真实 Douyin 可用。
- v0.8 Batch 10 不承诺真实 OAuth 可用。
- v0.8 Batch 10 不承诺真实 callback route 可用。
- v0.8 Batch 10 不承诺真实 token exchange 可用。
- v0.8 Batch 10 不承诺真实 Credential storage。
- v0.8 Batch 10 不承诺真实指标读取。
- v0.8 Batch 10 不承诺真实发布。
- v0.8 Batch 10 只建立 backend OAuth boundary metadata foundation。

v0.8 Batch 11 产品边界：

- 用户可以看到 provider OAuth boundary readiness。
- 用户可以区分 `oauth_policy_status`、`state_policy_status`、`callback_policy_status`、`csrf_protection_status`、`redirect_uri_policy_status`、`token_exchange_policy_status`、`token_storage_policy_status`、`error_redaction_policy_status`、`audit_event_policy_status`。
- 用户可以看到 `fake_local` 不需要 OAuth、不需要 state、不需要 callback、不需要 token。
- 用户可以看到 `douyin_sandbox` 和 `douyin_real` 当前只是 OAuth boundary placeholder metadata，`not_implemented` / `required_planned`。
- 用户不会看到真实 OAuth 授权入口。
- 用户不会看到真实 OAuth callback。
- 用户不会看到真实授权 URL。
- 用户不会看到 OAuth state value。
- 用户不会看到 authorization code。
- 用户不会执行 token exchange。
- 用户不会看到 access token 或 refresh token。
- 用户不会看到连接、授权、刷新、撤销、断开、上传、发布或排期发布入口。
- 用户不会看到 secret input、token viewer 或 credential 管理界面。
- v0.8 Batch 11 不承诺真实 Douyin 可用。
- v0.8 Batch 11 不承诺真实 OAuth 可用。
- v0.8 Batch 11 不承诺真实 callback route 可用。
- v0.8 Batch 11 不承诺真实 state storage 可用。
- v0.8 Batch 11 不承诺真实 token exchange 可用。
- v0.8 Batch 11 不承诺真实 Credential storage。
- v0.8 Batch 11 不承诺真实指标读取。
- v0.8 Batch 11 不承诺真实发布。
- v0.8 Batch 11 只建立 frontend read-only OAuth boundary metadata display foundation。

v0.8 Batch 12 产品边界：

- 用户未来可以看到 provider token lifecycle boundary readiness。
- 用户未来可以区分 `token_lifecycle_policy_status`、`token_storage_policy_status`、`refresh_policy_status`、`expiry_policy_status`、`revoke_policy_status`、`disconnect_policy_status`、`rotation_policy_status`、`error_redaction_policy_status` 和 `audit_event_policy_status`。
- `fake_local` 显示为不需要 token、不需要 refresh、不需要 revoke、不需要 disconnect。
- `douyin_sandbox` 和 `douyin_real` 当前只是 token lifecycle boundary placeholder metadata，`not_implemented` / `required_planned`。
- 当前不会保存 access token 或 refresh token。
- 当前不会执行 token refresh。
- 当前不会执行 token revoke。
- 当前不会执行 disconnect。
- 当前不会执行 token rotation。
- 当前不会显示真实 token lifecycle event。
- 当前不会提供连接、授权、刷新、撤销、断开、上传、发布或排期发布入口。
- 当前不会新增 secret input、token viewer 或 credential 管理界面。
- v0.8 Batch 12 不承诺真实 Douyin 可用。
- v0.8 Batch 12 不承诺真实 OAuth 可用。
- v0.8 Batch 12 不承诺真实 token storage 可用。
- v0.8 Batch 12 不承诺真实 token refresh / revoke / disconnect 可用。
- v0.8 Batch 12 不承诺真实 Credential storage。
- v0.8 Batch 12 不承诺真实指标读取。
- v0.8 Batch 12 不承诺真实发布。
- v0.8 Batch 12 只建立 backend token lifecycle boundary metadata foundation。

v0.8 Batch 13 产品边界：

- 用户可以看到 provider token lifecycle boundary readiness。
- 用户可以区分 `token_lifecycle_policy_status`、`token_storage_policy_status`、`refresh_policy_status`、`expiry_policy_status`、`revoke_policy_status`、`disconnect_policy_status`、`rotation_policy_status`、`error_redaction_policy_status` 和 `audit_event_policy_status`。
- 用户可以看到 `fake_local` 不需要 token、不需要 refresh、不需要 revoke、不需要 disconnect。
- 用户可以看到 `douyin_sandbox` 和 `douyin_real` 当前只是 token lifecycle boundary placeholder metadata，`not_implemented` / `required_planned`。
- 用户不会看到真实 token storage。
- 用户不会看到真实 token refresh。
- 用户不会看到真实 token revoke。
- 用户不会看到真实 disconnect。
- 用户不会看到真实 token rotation。
- 用户不会看到 access token 或 refresh token。
- 用户不会看到 token expiry value、refresh response、revoke response 或 provider token response。
- 用户不会看到连接、授权、刷新、撤销、断开、上传、发布或排期发布入口。
- 用户不会看到 secret input、token viewer 或 credential 管理界面。
- v0.8 Batch 13 不承诺真实 Douyin 可用。
- v0.8 Batch 13 不承诺真实 OAuth 可用。
- v0.8 Batch 13 不承诺真实 token storage 可用。
- v0.8 Batch 13 不承诺真实 token refresh / revoke / disconnect 可用。
- v0.8 Batch 13 不承诺真实 Credential storage。
- v0.8 Batch 13 不承诺真实指标读取。
- v0.8 Batch 13 不承诺真实发布。
- v0.8 Batch 13 只建立 frontend read-only token lifecycle boundary metadata display foundation。

v0.8 Batch 14 产品边界：

- 用户未来可以看到 provider integration readiness summary。
- 用户未来可以区分 local fake readiness、sandbox placeholder readiness、future real provider placeholder readiness。
- 用户未来可以看到 `readiness_items`、`blocking_reasons` 和 `next_safe_steps`。
- `fake_local` 只表示 local fake/demo/test workflow 可用。
- `douyin_sandbox` 和 `douyin_real` 当前只是 metadata-only / placeholder readiness。
- 当前不会显示真实 OAuth 可用。
- 当前不会显示真实 token storage 可用。
- 当前不会显示真实 token refresh / revoke / disconnect 可用。
- 当前不会显示真实 metrics fetching 可用。
- 当前不会显示真实 publish / upload / scheduling 可用。
- 当前不会新增连接、授权、刷新、撤销、断开、上传、发布或排期发布入口。
- 当前不会新增 secret input、token viewer 或 credential 管理界面。
- v0.8 Batch 14 不承诺真实 Douyin 可用。
- v0.8 Batch 14 不承诺真实 OAuth 可用。
- v0.8 Batch 14 不承诺真实 token lifecycle 可用。
- v0.8 Batch 14 不承诺真实 Credential storage。
- v0.8 Batch 14 不承诺真实指标读取。
- v0.8 Batch 14 不承诺真实发布。
- v0.8 Batch 14 只建立 backend readiness summary foundation。

v0.8 Batch 15 产品边界：

- 用户可以看到 provider integration readiness summary。
- 用户可以区分 local fake readiness、sandbox placeholder readiness、future real provider placeholder readiness。
- 用户可以看到 `readiness_items`、`blocking_reasons` 和 `next_safe_steps`。
- 用户可以看到 `fake_local` 只表示 local fake/demo/test workflow 可用。
- 用户可以看到 `douyin_sandbox` 和 `douyin_real` 当前只是 metadata-only / placeholder readiness。
- 用户不会看到真实 OAuth 可用。
- 用户不会看到真实 token storage 可用。
- 用户不会看到真实 token refresh / revoke / disconnect 可用。
- 用户不会看到真实 metrics fetching 可用。
- 用户不会看到真实 publish / upload / scheduling 可用。
- 用户不会看到 readiness override、readiness approval 或 production readiness certification 操作。
- 用户不会看到连接、授权、刷新、撤销、断开、上传、发布或排期发布入口。
- 用户不会看到 secret input、token viewer 或 credential 管理界面。
- v0.8 Batch 15 不承诺真实 Douyin 可用。
- v0.8 Batch 15 不承诺真实 OAuth 可用。
- v0.8 Batch 15 不承诺真实 token lifecycle 可用。
- v0.8 Batch 15 不承诺真实 Credential storage。
- v0.8 Batch 15 不承诺真实指标读取。
- v0.8 Batch 15 不承诺真实发布。
- v0.8 Batch 15 不承诺 v0.9 POC 已完成。
- v0.8 Batch 15 只建立 frontend read-only readiness summary display foundation。

v0.8 Batch 16 产品边界：

- 本批只形成 v0.8 Provider & Credential Security Foundation RC audit / closure checklist。
- 用户不会获得新的业务功能。
- 用户不会看到新的前端 UI。
- 用户不会看到新的连接、授权、刷新、撤销、断开、上传、发布、排期发布、readiness approval、readiness override 或 production readiness certification 操作。
- 本批只梳理 Batch 1-15 的已完成范围、只读 API、frontend panels、metadata-only DB 表、response schema、文档一致性和安全扫描要求。
- Batch 16 执行时当前稳定版本仍是 v0.7.0；v0.8.0 release finalization 后当前稳定版本更新为 v0.8.0。
- v0.8 Batch 16 不创建 v0.8.0 tag。
- v0.8 Batch 16 不声明 v0.8 已 release。
- v0.8 Batch 16 不进入 v0.9 POC 开发。
- v0.8 Batch 16 不承诺真实 Douyin 可用。
- v0.8 Batch 16 不承诺真实 OAuth 可用。
- v0.8 Batch 16 不承诺真实 token storage、token refresh、token revoke 或 disconnect 可用。
- v0.8 Batch 16 不承诺真实 Credential storage。
- v0.8 Batch 16 不承诺真实指标读取。
- v0.8 Batch 16 不承诺真实发布、上传或排期发布。

v0.8.0 Provider & Credential Security Foundation 产品边界：

- 用户现在可以看到 provider/security/readiness 边界，包括 Provider Registry、Connection State、Credential Reference、Security Audit、OAuth Boundary、Token Lifecycle Boundary 和 Integration Readiness Summary。
- 所有 provider panels 均为 read-only metadata display。
- 用户可以区分 `fake_local`、`douyin_sandbox` 和 `douyin_real`。
- 用户可以看到 provider metadata、source type、implementation status、policy/status metadata、safe status message、readiness items、blocking reasons、next safe steps 和 boundary notes。
- 用户不能连接真实 Douyin。
- 用户不能授权 OAuth。
- 用户不能保存 token、secret、API key、credential、authorization code 或 OAuth state。
- 用户不能执行 token exchange、token refresh、token revoke、disconnect 或 token rotation。
- 用户不能抓取真实指标。
- 用户不能上传、发布或排期发布。
- 用户不会看到 secret input、token viewer、credential 管理界面、raw request viewer、raw response viewer、raw payload viewer、readiness approval、readiness override 或 production readiness certification。
- v0.8.0 不承诺真实 Douyin 可用。
- v0.8.0 不承诺真实 OAuth 可用。
- v0.8.0 不承诺真实 token storage 可用。
- v0.8.0 不承诺真实 Credential storage。
- v0.8.0 不承诺真实指标读取。
- v0.8.0 不承诺真实发布。
- v0.8.0 不是 production-ready real Douyin integration。

## v0.9 Douyin Provider POC / Sandbox Integration 产品边界

v0.9 的用户价值目标是为未来抖音接入做 Provider POC 和 sandbox/mock integration 准备，而不是立即给用户真实连接抖音。v0.9 Batch 0 只完成 planning、ADR 和 readiness checklist，不增加用户可操作功能，不新增业务代码，不新增 backend API，不修改数据库表，也不新增前端 UI。

v0.9 第一阶段必须优先验证 sandbox/mock callback planning、provider status transition dry-run 和 read-only mock/sandbox boundary。后续如果展示 sandbox/mock readiness，必须明确标注不是 real Douyin、不是真实账号连接、不是真实 OAuth、不是真实指标，也不是生产可用集成。

用户不会在本批看到 OAuth login、connect、authorize、OAuth callback、token viewer、credential 管理、真实指标、上传、发布或排期发布入口。v0.9 Batch 0 不会保存 token、secret、API key、credential、authorization code 或 OAuth state，也不会调用外部服务。

v0.9 Batch 1 产品边界：

- 用户不会感知新增功能。
- 本批无 UI，不新增前端入口。
- 本批不允许用户连接抖音。
- 本批不允许用户授权 OAuth。
- 本批不允许用户读取真实指标。
- 本批不允许用户上传、发布或排期发布。
- 本批只是后端结构安全准备，新增 backend-only Douyin Provider Adapter Skeleton 和 blocked / not implemented boundary result。
- Skeleton 不调用真实 Douyin API，不实现 OAuth，不新增 OAuth callback route，不交换或保存 token，也不读取环境变量密钥。

v0.9 Batch 2 产品边界：

- 用户不会感知新增功能。
- 本批无 UI，不新增前端入口。
- 本批只为 `douyin_sandbox` 提供 sandbox-only simulated operation result。
- 模拟结果使用 deterministic dry-run 语义和稳定 fake id，不代表真实抖音平台动作。
- `douyin_real` 继续 blocked / not implemented。
- 本批不允许用户连接抖音、授权 OAuth、读取真实指标、上传、发布或排期发布。
- 本批不接真实 Douyin API，不实现 OAuth，不新增 OAuth callback route，不交换或保存 token，也不读取环境变量密钥。

v0.9 Batch 3 产品边界：

- 用户不会感知新增功能。
- 本批无 UI，不新增前端入口。
- 本批只新增 backend-only Douyin Provider Registry / Factory Routing foundation。
- `douyin_sandbox` 可通过 registry / factory 路由到 sandbox-only deterministic simulation。
- `douyin_real` 可被 registry / factory 识别，但仍然 blocked / not implemented。
- unknown provider 明确失败，不 fallback 到 sandbox。
- 本批不允许用户连接抖音、授权 OAuth、读取真实指标、上传、发布或排期发布。
- 本批不接真实 Douyin API，不实现 OAuth，不创建 OAuth URL，不新增 OAuth callback route，不交换或保存 token，也不读取环境变量密钥。

v0.9 Batch 4 产品边界：

- 用户不会感知新增功能。
- 本批无 UI，不新增前端入口。
- 本批只新增 backend-only Douyin Provider Sandbox Metrics / Mock Workflow POC。
- `douyin_sandbox` 可通过 registry / factory 返回 deterministic simulated mock account connection、sandbox metrics payload 和 dry-run publish result。
- `douyin_real` 仍然 blocked / not implemented。
- unknown provider 明确失败，不 fallback 到 sandbox。
- 本批不允许用户连接真实抖音账号、授权 OAuth、读取真实指标、上传、发布或排期发布。
- 本批不接真实 Douyin API，不实现 OAuth，不创建 OAuth URL，不新增 OAuth callback route，不交换或保存 token，也不读取环境变量密钥。
- 本批不表示 v0.9 POC 已完成，不表示已经接入真实抖音开放平台，也不表示用户可以真实发布抖音视频。

v0.9 Batch 5 产品边界：

- 用户不会感知新增功能。
- 本批无 UI，不新增前端入口。
- 本批只做 docs-only / planning-only roadmap alignment。
- 本批把 v1.0 Douyin Integration User Test Release、v1.5 Minimum Production Release 和 v2.0 Multi-Tenant SaaS Commercial Release 的未来目标、商用边界和 readiness checklist 写清楚。
- 本批不接真实 Douyin API，不实现 OAuth，不创建 OAuth URL，不新增 OAuth callback route，不新增 OAuth state storage，不交换或保存 token，也不读取环境变量密钥。
- 本批不新增真实 tenant、billing、RBAC 或 admin console 实现。
- 本批不表示 v0.9 POC 已完成，不表示 v1.0、v1.5 或 v2.0 已完成，也不表示当前可以给直接客户生产商用或给客户的客户 SaaS 商用。

真实 Douyin API、真实 OAuth、真实 OAuth callback route、真实 token exchange、真实 token storage、真实指标读取、上传、发布、排期发布和自动发布都必须等后续单独 ADR、单独分支、单独测试和安全扫描通过后才能进入。

## Road to Douyin user testing

v0.7.0 已完成 local fake/manual metrics review summary workflow。v0.8.0 已完成 Provider & Credential Security Foundation release。v0.8.0 之后的路线不会从 metadata-only / read-only security foundation 直接跳到生产级真实平台能力，而是进入 v0.9 Douyin Provider POC / Sandbox Integration，再进入 v1.0.0 Douyin Integration User Test Release。v1.0.0 的目标是进行用户抖音接入测试，不是生产级自动化发布版本，也不承诺批量发布、定时发布、多账号矩阵运营或自动内容优化。

用户测试目标：

- 验证用户可以在明确知情的前提下完成 Douyin OAuth 授权。
- 验证真实账号连接状态可以被系统识别和展示。
- 验证至少一种真实指标回流，例如 views、likes、comments 或 shares 中的一种或多种，具体取决于平台权限。
- 验证 `fake_local`、`douyin_sandbox` 和 `douyin_real` 等 source 可以被明确区分。
- 验证授权失败、token 过期、权限不足和接口失败等场景有清晰提示。

用户测试前置条件：

- Douyin 平台应用配置完成，并满足用户测试所需的开放能力、应用审核和 API 权限。
- OAuth callback 可用，并具备 state 校验、错误回跳和授权失败处理方向。
- 凭据安全策略可审计，token、secret 和 refresh token 不进入 Git、日志、前端、测试 fixtures 或示例数据。
- fake 指标不能展示成真实平台指标，sandbox/mock 结果也不能伪装成真实用户数据。
- 用户必须明确授权，系统只能读取授权范围内的必要数据。
- 产品需要有撤销授权或断开连接的方向，即使 v1.0.0 只先覆盖用户测试所需的最小路径。
- 如果 Douyin API 权限不可用，v0.9 / v1.0.0 可以使用 manual import 或 sandbox/mock provider contract test 作为 fallback。

不属于 v1.0.0 用户测试范围：

- 生产级自动发布。
- 批量发布。
- 定时发布。
- 多账号矩阵运营。
- 自动内容优化。
- 商业级增长分析或真实平台 dashboard。
- 绕过平台审核、权限或用户授权范围的数据采集。

## 商业版本定位路线

本节描述 future roadmap，不是当前能力声明。当前 v0.9 只有 sandbox/mock workflow、registry / factory foundation 和 roadmap / checklist 文档，不提供真实抖音连接、真实 OAuth、真实发布、生产级部署或多租户 SaaS。

版本定位：

- v1.0 Douyin Integration User Test Release：面向 internal/test users 和小范围用户测试，目标是验证真实 Douyin 授权、发布、状态查询和最小指标回流是否可行；它不是生产商用版本。
- v1.5 Minimum Production Release：未来目标是面向 direct customer operators 的最小生产版本，可在 readiness criteria 满足后面向直接客户做受控商用，适合 managed deployment、single-tenant deployment、limited production 或 pilot commercial contract。v1.5 不默认服务客户的客户，不是多租户 SaaS。
- v2.0 Multi-Tenant SaaS Commercial Release：未来目标是面向 tenant admins、customer operators 和 customer-of-customer end users 的多租户 SaaS 商用版本，支持客户把服务提供给客户的客户。

用户类型演进：

- v1.0：internal/test users，用于验证真实接入路径与失败模式。
- v1.5：direct customer operators，用于直接客户的受控生产与受控商用。
- v2.0：tenant admins、customer operators、customer-of-customer end users，用于多租户 SaaS 商用。

v1.5 商用边界：

- v1.5 可面向直接客户做受控商用是目标门槛，不是当前能力。
- v1.5 需要合同/验收/支持边界、生产部署手册、安全与隐私边界、备份与恢复、监控告警、客户数据隔离说明、人工审核与发布确认，以及 Douyin 平台政策、开放能力、审核状态和 API 限制说明。
- v1.5 不承诺多租户 SaaS，不承诺客户的客户可直接入驻使用，不承诺 white-label / reseller / marketplace 能力，不承诺无限规模或 SLA，除非后续文档和合同明确建立。

v2.0 商用边界：

- v2.0 面向客户的客户 SaaS 商用是最终路线，不是当前能力。
- v2.0 需要 tenant / customer / customer-of-customer 数据边界、强租户隔离、RBAC 与组织管理、审计日志、计费/套餐/用量限制、生产 SLA 与支持流程、安全响应、合规与数据处理说明、运营后台、可扩展部署与监控、真实 provider 接入安全审计，以及平台政策、权限和 API 限制的持续合规检查。
- v2.0 不得被 v0.9、v1.0 或 v1.5 的能力暗示替代。

## 隐私与素材导入边界

MVP 只处理用户显式导入的素材，以及用户明确启用的公开热点来源。系统不得静默扫描本地文件、读取私有聊天历史、抓取私人账号或从浏览器会话推断授权。上传素材、本地数据库、生成视频、音频、图片、字幕和私有笔记必须排除在 Git 之外。

## MVP 验收标准

- 用户可以创建内容项目并显式导入素材。
- 用户可以配置账号定位、内容类型和目标生成频率。
- 用户可以手动触发选题、脚本、分镜、字幕和素材方案生成。
- 系统可以通过 `FFmpeg` 从脚本、图片或截图、TTS 和字幕生成 9:16 MP4。
- 发布到抖音或其他平台前必须出现可见审核与确认步骤。
- 外部能力通过 Provider 接口访问。
- 默认流程不依赖昂贵的纯 AI 文生视频。
- 密钥、私有素材、本地数据库和生成媒体不会被提交。

## Scheduled Draft Generation 阶段验收标准

- 用户可以为 `ContentPlan` 配置每周生成频率。
- `Scheduler / Trigger Engine` 可以按计划创建 `GenerationRun`。
- 每次 `GenerationRun` 只能基于近期显式导入素材和用户启用的热点来源生成草稿。
- 自动生成的草稿进入 `Review Queue`，状态为待审核。
- 调度任务不能绕过用户确认执行发布。
- 系统记录草稿生成时间、输入来源和热点来源。
