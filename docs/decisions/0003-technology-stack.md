# ADR 0003: 技术栈

## 状态

Accepted

## 背景

creator-flow 需要一个适合本地优先 MVP 的技术栈，并能在未来扩展为更完整的开源应用。项目需要 Web UI、清晰的 backend API、轻量本地存储、可靠的视频合成、可复现部署和 CI/CD。

同时，项目需要支持内容计划、定时生成、人工审核、视频渲染、发布准备和指标回流等能力。技术栈应保持简单、可贡献、可本地运行。

## 决策

计划中的 MVP 技术栈为：

- Backend: Python + `FastAPI`。
- Frontend: `React` + `Vite` + `Tailwind`。
- MVP Database: `SQLite`。
- Future Database: `PostgreSQL`。
- Video Rendering: `FFmpeg`。
- Deployment: `Docker Compose`。
- CI/CD: `GitHub Actions`。

## 理由

- `FastAPI` 适合构建类型清晰的 Python API 和本地服务。
- `React` + `Vite` + `Tailwind` 适合快速构建可交互的创作者工作台。
- `SQLite` 让 MVP 可以低门槛本地运行，并存储内容计划、生成记录、审核任务和文件引用。
- `PostgreSQL` 为后续更持久或协作部署提供升级方向。
- `FFmpeg` 成熟可靠，适合从图片、截图、音频、字幕和时间信息生成确定性的短视频。
- `Docker Compose` 足以支撑可复现的本地或小规模部署。
- `GitHub Actions` 适合开源项目的检查、测试和发布流程。

## 结果

- 第一版实现应保持轻量和本地友好。
- Provider 接口应先于外部服务深度集成设计。
- 调度与发布能力必须在架构上分离。
- documentation foundation 阶段不得提前生成应用骨架。
- 贡献者可以基于清晰技术方向规划后续实现。
