# ADR 0005: 本地可运行骨架实现

## 状态

Accepted

## 背景

Documentation Foundation 已经明确 creator-flow 的产品定位、人工确认发布边界和技术栈。v0.1 需要从纯文档进入最小本地可运行应用，但不能扩大到 AI、渲染、调度或发布流程。

## 决策

本次实现采用以下最小结构：

- `backend/`：`FastAPI` 应用、API 路由、配置、SQLite 初始化、Pydantic schema 和 pytest 测试。
- `frontend/`：`React` + `Vite` + `Tailwind CSS` 本地前端，包含项目列表、项目创建和项目详情页面。
- `data/local/`：本地 SQLite 数据目录，实际数据库文件为 `data/local/creator_flow.sqlite3`。
- `uploads/`：用户显式上传图片和截图的本地目录，文件按 `uploads/{project_id}/` 存放。

Backend 使用 `pyproject.toml` 管理 Python 依赖，建议通过本地虚拟环境安装。Frontend 使用 `package.json` 和 `package-lock.json` 管理 Node 依赖。

首批实体限定为：

- `ContentProject`：标题、描述、状态、创建时间和更新时间。
- `UserMaterial`：项目引用、素材类型、标题、文本内容、链接、文件引用、原始文件名和创建时间。

首批 API 限定为：

- `GET /api/health`
- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/{project_id}`
- `POST /api/projects/{project_id}/materials/text`
- `POST /api/projects/{project_id}/materials/link`
- `POST /api/projects/{project_id}/materials/file`

项目创建后状态为 `draft`。项目首次成功添加素材后状态更新为 `materials_ready`。当前不实现后续生成、审核、渲染或发布状态流转。

## 不做事项

本次不加入 `Docker`、CI、Provider、渲染或发布能力，因为 v0.1 的目标只是验证本地端到端骨架和显式素材导入。提前加入这些能力会扩大边界，并增加隐私、凭据、外部服务和发布动作风险。

本次也不实现自动联网抓取链接内容、OCR、AI 分析、图像处理、自动扫描本地文件、浏览器、私有聊天或私人账号。

## 结果

- 用户可以在本地启动 backend 和 frontend。
- 用户可以创建内容项目并显式添加素材。
- 元数据保存在本地 SQLite，上传文件保存在本地 uploads。
- SQLite 文件、上传文件、虚拟环境、`node_modules` 和生成媒体继续被 Git 忽略。
- 后续 v0.2 可以在明确 Provider 边界后继续实现 AI Planning Workflow。
