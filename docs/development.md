# 本地开发

本文档面向 v0.1 Local Runnable Skeleton，说明如何在 Windows 11 和 PowerShell 下启动本地 backend、frontend，并验证内容项目与素材导入能力。

## 环境要求

- Windows 11 + PowerShell。
- Python 3.11 或更高版本。
- Node.js 20 或更高版本。
- npm 10 或更高版本。

如果 PowerShell 执行策略拦截 `npm`，请使用 `npm.cmd`。

## 启动 Backend

```powershell
cd .\backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

预期返回：

```json
{
  "status": "ok"
}
```

## 启动 Frontend

另开一个 PowerShell：

```powershell
cd .\frontend
npm.cmd install
npm.cmd run dev
```

默认访问地址：

```text
http://localhost:5173
```

如果 backend 不是运行在 `http://localhost:8000`，可以在启动 frontend 前设置：

```powershell
$env:VITE_API_BASE_URL = "http://127.0.0.1:8000"
npm.cmd run dev
```

## 本地数据位置

- SQLite 数据库：`data/local/creator_flow.sqlite3`
- 上传文件：`uploads/{project_id}/`

这些运行时数据不得提交到 Git。仓库只保留 `data/local/.gitkeep` 和 `uploads/.gitkeep` 作为目录占位。

## 运行 Backend Tests

```powershell
cd .\backend
.\.venv\Scripts\Activate.ps1
python -m pytest
```

如果使用 `uv` 管理本地 Python 环境，也可以运行：

```powershell
cd .\backend
uv run --extra test pytest
```

## 验证项目与素材导入

1. 启动 backend。
2. 启动 frontend。
3. 打开 `http://localhost:5173`。
4. 创建一个内容项目。
5. 在项目详情页添加一条文本素材。
6. 添加一条链接素材。
7. 上传一张图片或截图。
8. 刷新页面，确认项目与素材仍然存在。
9. 检查 `git status --short`，确认未跟踪 SQLite 文件、上传文件、`.venv/`、`node_modules/` 或生成媒体。

## 当前未实现能力

- 未实现 `LLMProvider`、`ImageProvider`、`TTSProvider`、`TrendSourceProvider`、`PublisherProvider`。
- 未实现 AI 选题、脚本生成、分镜生成或素材方案生成。
- 未实现 `FFmpeg` 渲染。
- 未实现 `Review Queue` 完整业务流程。
- 未实现定时生成。
- 未实现抖音或其他平台发布。
- 未实现 OAuth、用户账号体系、生产部署、`Docker Compose` 或 `GitHub Actions`。
- 未实现自动扫描本地文件、浏览器、私有聊天或私人账号的能力。
