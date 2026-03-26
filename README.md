# OpenClaw Multi-Agent Manager

OpenClaw 多智能体可视化管理平台 - 支持智能体的创建、配置、启停、协作和通信管理。

## 技术栈

### 后端
- **FastAPI** - 高性能异步框架
- **SQLite** + **SQLAlchemy** - 轻量级数据库
- **uv** - Python 环境管理
- **OpenClaw CLI** - 通过命令行调用本地 OpenClaw

### 前端
- **Vue 3** + **TypeScript**
- **Vite** - 构建工具
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Axios** - HTTP 客户端

## 前置要求

- **Python 3.10+**
- **Node.js 18+**
- **OpenClaw CLI** - 安装方式: `npm install -g openclaw`

验证 OpenClaw 安装:
```bash
openclaw --version
openclaw agents list --json
```

## 快速开始

### 一键启动

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh stop.sh
./start.sh
```

### 手动启动

**后端:**
```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload --port 3789
```

**前端:**
```bash
cd frontend
npm install
npm run dev
```

## 功能特性

### 智能体管理
- 创建、编辑、删除智能体（同步到 OpenClaw）
- 启动/停止智能体（管理 Gateway）
- 从 OpenClaw 同步智能体列表
- 向智能体发送消息

### Gateway 管理
- 查看 Gateway 状态
- 启动/停止 Gateway
- 查看 OpenClaw 中的智能体

### 团队管理
- 创建智能体团队
- 部署/清理团队
- 团队成员管理

### 角色库
- 6 个预置角色模板
- 自定义角色创建
- 按分类浏览

## API 接口

### 智能体
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/agents | 获取所有智能体 |
| GET | /api/agents/sync | 从 OpenClaw 同步智能体 |
| POST | /api/agents | 创建智能体 |
| PUT | /api/agents/{id} | 更新智能体 |
| DELETE | /api/agents/{id} | 删除智能体 |
| POST | /api/agents/{id}/start | 启动智能体 |
| POST | /api/agents/{id}/stop | 停止智能体 |
| POST | /api/agents/{id}/message | 发送消息 |

### Gateway
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/gateway/status | 获取 Gateway 状态 |
| POST | /api/gateway/start | 启动 Gateway |
| POST | /api/gateway/stop | 停止 Gateway |
| GET | /api/gateway/agents | 获取 OpenClaw 智能体列表 |

### 团队
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/teams | 获取所有团队 |
| POST | /api/teams | 创建团队 |
| DELETE | /api/teams/{id} | 删除团队 |
| POST | /api/teams/{id}/deploy | 部署团队 |
| POST | /api/teams/{id}/teardown | 清理团队 |

### 角色
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/roles | 获取所有角色 |
| GET | /api/roles/categories | 获取角色分类 |
| POST | /api/roles | 创建角色 |
| DELETE | /api/roles/{id} | 删除角色 |

## OpenClaw CLI 集成

本项目通过调用本地 OpenClaw CLI 命令实现功能：

| 功能 | CLI 命令 |
|------|----------|
| 列出智能体 | `openclaw agents list --json` |
| 创建智能体 | `openclaw agents add <name> --workspace <dir>` |
| 删除智能体 | `openclaw agents delete <id> --force` |
| Gateway 状态 | `openclaw gateway status --json` |
| 启动 Gateway | `openclaw gateway start` |
| 停止 Gateway | `openclaw gateway stop` |
| 发送消息 | `openclaw agent --agent <id> --message <text>` |

## 项目结构

```
openclaw-agent-qq-manger/
├── backend/              # Python 后端
│   ├── src/
│   │   ├── api/          # API 路由
│   │   │   ├── agents.py
│   │   │   ├── teams.py
│   │   │   ├── roles.py
│   │   │   └── gateway.py
│   │   ├── models/       # 数据库模型
│   │   ├── schemas/      # Pydantic 模型
│   │   └── services/
│   │       └── openclaw_service.py  # CLI 调用封装
│   └── pyproject.toml
│
├── frontend/             # Vue 3 前端
│   ├── src/
│   │   ├── api/          # API 客户端
│   │   ├── views/        # 页面组件
│   │   ├── stores/       # Pinia 状态
│   │   └── types/        # TypeScript 类型
│   └── package.json
│
├── start.bat             # Windows 启动脚本
├── start.sh              # Linux/Mac 启动脚本
├── stop.bat              # Windows 停止脚本
├── stop.sh               # Linux/Mac 停止脚本
└── README.md
```

## 预置角色

| 角色 | 中文名 | 职责 |
|------|--------|------|
| steward | 大总管 | 任务分发与协调 |
| dev | 开发助理 | 代码、架构、DevOps |
| content | 内容助理 | 文案、内容策划 |
| ops | 运营助理 | 增长、数据分析、活动策划 |
| law | 法务助理 | 合同、合规、风险管理 |
| finance | 财务助理 | 记账、预算、财务分析 |

## 环境变量

后端 `.env` 文件:

```env
API_HOST=127.0.0.1
API_PORT=3789
DATABASE_URL=sqlite+aiosqlite:///./data/agents.db
OPENCLAW_WORKSPACE=./workspace
```

## License

MIT
