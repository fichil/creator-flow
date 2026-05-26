# AGENTS.md

本仓库已完成 Documentation Foundation，当前处于 v0.1 Local Runnable Skeleton 阶段。

## 工作规则

- 开发功能前必须阅读 `docs/product-spec.md`、`docs/architecture.md` 和 `docs/roadmap.md`。
- 本阶段允许新增最小必要的 `FastAPI`、`React` + `Vite` + `Tailwind CSS`、`SQLite` 和本地开发依赖。
- 本阶段不得提前实现 AI Provider、视频渲染、定时生成、自动发布、生产部署、`Docker` 文件或 `GitHub Actions`。
- 所有重要修改都应可审查、可测试，并适合形成单独的 Git commit。
- 不得提交密钥、API key、token、账号信息、本地数据库、生成媒体、用户上传素材、虚拟环境、`node_modules` 或用户隐私内容。
- 所有外部 AI、媒体、热点、渲染和发布能力都应通过 Provider 接口设计，避免绑定单一服务。

## 自动化与发布边界

- 定时自动化只能生成待审核草稿，不能自动发布内容。
- 任何定时任务不得绕过用户明确确认进行发布、排期发布或上传用于公开发布的动作。
- 自动化只能使用用户显式导入的素材，以及用户明确启用的外部热点来源。
- 热点来源必须作为外部不可信输入处理，并记录来源、采集时间和用户启用状态。
- 必须保留 human-in-the-loop publishing 原则：任何发布到抖音或其他平台的行为都需要用户审核与明确确认。

## 语言规则

- 面向中国目标用户的产品文档与用户说明默认使用简体中文。
- 代码标识符、接口名、路径、配置键、命令和 Git commit message 使用英文。
- 仓库名 `creator-flow`、文件名、目录名、类名、模块名、Provider 接口名和技术栈名称保持英文。
- 新增或实质修改 README 时，应同步维护 `README.md` 与 `README.en.md` 的关键信息一致性。
