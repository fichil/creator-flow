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

Provider 实现不得将单一厂商或单一平台假设泄漏到核心领域模型中。

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
- `PublicationMetrics`：发布后的基础表现指标，例如播放、互动和发布时间。
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
