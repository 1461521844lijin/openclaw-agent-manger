# OpenClaw Multi-Agent Manager

OpenClaw 多智能体可视化管理平台 - 支持智能体的创建、配置、启停、协作和通信管理。

## 技术栈

### 后端
- **FastAPI** - 高性能异步框架
- **SQLite** + **SQLAlchemy** - 轻量级数据库
- **uv** - Python 环境管理
- **openclaw/cmdop** - OpenClaw SDK

### 前端
- **Vue 3** + **TypeScript**
- **Vite** - 构建工具
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Axios** - HTTP 客户端

## 快速开始

### 后端启动

```bash
cd backend

# 安装依赖
uv sync

# 启动开发服务器
uv run uvicorn src.main:app --reload --port 3789
```

API 文档: http://localhost:3789/docs

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问: http://localhost:5173

## 功能特性

### 智能体管理
- 创建、编辑、删除智能体
- 启动/停止智能体
- 状态监控

### 团队管理
- 创建智能体团队
- 部署/清理团队
- 团队成员管理

### 角色库
- 6 个预置角色模板
- 自定义角色创建
- 按分类浏览

## 预置角色

| 角色 | 中文名 | 职责 |
|------|--------|------|
| steward | 大总管 | 任务分发与协调 |
| dev | 开发助理 | 代码、架构、DevOps |
| content | 内容助理 | 文案、内容策划 |
| ops | 运营助理 | 增长、数据分析、活动策划 |
| law | 法务助理 | 合同、合规、风险管理 |
| finance | 财务助理 | 记账、预算、财务分析 |

## API 接口

### 智能体
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/agents | 获取所有智能体 |
| POST | /api/agents | 创建智能体 |
| PUT | /api/agents/{id} | 更新智能体 |
| DELETE | /api/agents/{id} | 删除智能体 |
| POST | /api/agents/{id}/start | 启动智能体 |
| POST | /api/agents/{id}/stop | 停止智能体 |

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

## 项目结构

```
openclaw-agent-qq-manger/
├── backend/           # Python 后端
│   ├── src/
│   │   ├── api/       # API 路由
│   │   ├── models/    # 数据库模型
│   │   ├── schemas/   # Pydantic 模型
│   │   └── services/  # 业务逻辑
│   └── pyproject.toml
│
├── frontend/          # Vue 3 前端
│   ├── src/
│   │   ├── api/       # API 客户端
│   │   ├── views/     # 页面组件
│   │   ├── stores/    # Pinia 状态
│   │   └── types/     # TypeScript 类型
│   └── package.json
│
└── README.md
```

## 环境变量

后端 `.env` 文件:

```env
API_HOST=127.0.0.1
API_PORT=3789
DATABASE_URL=sqlite+aiosqlite:///./data/agents.db
OPENCLAW_API_KEY=your_api_key
OPENCLAW_WORKSPACE=./workspace
```

## License

MIT
