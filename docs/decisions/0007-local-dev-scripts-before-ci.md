# ADR 0007: 先做本地开发脚本再做 CI

## 状态

Accepted

## 背景

creator-flow 当前处于 v0.1 Local Runnable Skeleton 阶段。项目已经有本地 backend、frontend、SQLite 存储、基础测试和前端 build，但还没有进入生产部署或协作 CI 阶段。

主要开发环境是 Windows 11 + PowerShell。此时最重要的是让本地启动、测试、构建和 API smoke checks 更容易重复执行。

## 决策

当前先提供 Windows PowerShell 本地脚本：

- `scripts/dev-backend.ps1`
- `scripts/dev-frontend.ps1`
- `scripts/test-backend.ps1`
- `scripts/build-frontend.ps1`
- `scripts/smoke-api.ps1`

本阶段不引入 GitHub Actions，也不引入 Docker 或 Docker Compose。

## 理由

- 本地脚本直接服务当前主要开发环境，能降低启动和验证成本。
- v0.1 仍在快速建立骨架，过早引入 CI 会增加维护面和失败排查成本。
- Docker 会引入额外的运行时边界、镜像构建和数据挂载问题，不符合当前轻量本地优先目标。
- 先稳定本地命令，有助于后续把同一组检查迁移到 CI。

## 后续

当 backend/frontend 结构更稳定、测试命令固定、PR 检查需求明确后，可以再引入 GitHub Actions。

当需要可复现部署、多人协作环境或更接近生产的依赖隔离时，再考虑 Docker Compose。

引入 CI 或 Docker 时仍必须保持隐私边界：不得上传本地 SQLite、用户上传文件、密钥、生成媒体或其他运行时数据。
