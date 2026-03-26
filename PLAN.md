# OpenClaw Multi-Agent Manager 实现计划

## 项目概述

构建一个可视化的 OpenClaw 多智能体管理平台，支持智能体的创建、配置、启停、协作和通信管理。

## 技术架构

### 后端 (Python)
- **框架**: FastAPI - 高性能异步框架，自动生成API文档
- **数据库**: SQLite + SQLAlchemy ORM
- **环境管理**: uv
- **核心依赖**: openclaw, pydantic

### 前端 (Vue 3)
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI组件库**: Element Plus (中文友好)
- **状态管理**: Pinia
- **HTTP客户端**: Axios
- **可视化**: D3.js 或 @vue-flow/core (协作拓扑图)

### 项目结构

```
openclaw-agent-qq-manger/
├── backend/                    # Python 后端
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── models/            # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── agent.py       # 智能体模型
│   │   │   ├── team.py        # 团队模型
│   │   │   └── role.py        # 角色模型
│   │   ├── schemas/           # Pydantic 模型
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── team.py
│   │   │   └── role.py
│   │   ├── api/               # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── agents.py      # 智能体管理
│   │   │   ├── teams.py       # 团队管理
│   │   │   ├── roles.py       # 角色库
│   │   │   └── init.py        # 初始化/部署
│   │   ├── services/          # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── agent_service.py
│   │   │   ├── team_service.py
│   │   │   └── openclaw_service.py
│   │   └── utils/             # 工具函数
│   │       └── __init__.py
│   ├── tests/
│   ├── data/                  # SQLite 数据库文件
│   ├── pyproject.toml         # uv 项目配置
│   └── uv.lock
│
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── api/               # API 客户端
│   │   ├── components/        # 组件
│   │   │   ├── AgentForm.vue
│   │   │   ├── AgentList.vue
│   │   │   ├── AgentCard.vue
│   │   │   ├── TeamForm.vue
│   │   │   ├── TeamList.vue
│   │   │   ├── TopologyGraph.vue
│   │   │   ├── RoleSelector.vue
│   │   │   └── ConfigPreview.vue
│   │   ├── views/             # 页面
│   │   │   ├── AgentsView.vue
│   │   │   ├── TeamsView.vue
│   │   │   └── RolesView.vue
│   │   ├── stores/            # Pinia 状态
│   │   ├── types/             # TypeScript 类型
│   │   └── router/            # 路由
│   ├── package.json
│   └── vite.config.ts
│
├── shared/                     # 共享类型定义
│   └── types.ts
│
└── README.md
```

## 数据模型设计

### Agent (智能体)
```python
class Agent:
    id: str                    # UUID
    name: str                  # 名称
    role: str                  # 角色类型
    workspace: str             # 工作目录
    agent_dir: str             # 智能体目录
    config: JSON               # OpenClaw 配置
    status: str                # running/stopped/error
    created_at: datetime
    updated_at: datetime
```

### Team (团队)
```python
class Team:
    id: str                    # UUID
    name: str                  # 团队名称
    description: str           # 描述
    agents: List[Agent]        # 包含的智能体
    collaborations: JSON       # 协作规则
    created_at: datetime
    updated_at: datetime
```

### Role (角色模板)
```python
class Role:
    id: str                    # UUID
    name: str                  # 角色名称
    name_en: str               # 英文名
    emoji: str                 # 图标
    description: str           # 描述
    core_mission: str          # 核心使命
    critical_rules: str        # 关键规则
    category: str              # 分类
```

## API 设计

### 智能体管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/agents | 获取所有智能体 |
| GET | /api/agents/{id} | 获取单个智能体 |
| POST | /api/agents | 创建智能体 |
| PUT | /api/agents/{id} | 更新智能体 |
| DELETE | /api/agents/{id} | 删除智能体 |
| POST | /api/agents/{id}/start | 启动智能体 |
| POST | /api/agents/{id}/stop | 停止智能体 |

### 团队管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/teams | 获取所有团队 |
| GET | /api/teams/{id} | 获取单个团队 |
| POST | /api/teams | 创建团队 |
| PUT | /api/teams/{id} | 更新团队 |
| DELETE | /api/teams/{id} | 删除团队 |
| POST | /api/teams/{id}/deploy | 部署团队 |
| POST | /api/teams/{id}/teardown | 清理团队 |

### 角色库
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/roles | 获取所有角色 |
| GET | /api/roles/categories | 获取角色分类 |
| POST | /api/roles | 创建角色 |
| DELETE | /api/roles/{id} | 删除角色 |

## 前端页面设计

### 1. 智能体管理页 (AgentsView)
- 智能体列表（卡片展示）
- 创建/编辑智能体表单
- 启动/停止/删除操作
- 状态指示器

### 2. 团队管理页 (TeamsView)
- 团队列表
- 创建团队向导（选择智能体 → 定义协作 → 预览 → 部署）
- 协作拓扑可视化
- 部署状态

### 3. 角色库页 (RolesView)
- 角色分类浏览
- 预置角色展示
- 自定义角色创建

## 实现步骤

### Phase 1: 后端基础 (Step 1-3)
1. **初始化项目结构** - 创建目录结构，配置 uv
2. **数据库模型** - 定义 SQLAlchemy 模型，初始化数据库
3. **核心 API** - 实现智能体、团队、角色的 CRUD API

### Phase 2: OpenClaw 集成 (Step 4-5)
4. **OpenClaw 服务层** - 封装 openclaw 库的调用
5. **启停与部署** - 实现智能体启停、团队部署功能

### Phase 3: 前端开发 (Step 6-8)
6. **前端项目初始化** - Vue 3 + Vite + Element Plus
7. **核心页面开发** - 智能体管理、团队管理、角色库页面
8. **协作拓扑可视化** - 实现智能体协作关系图

### Phase 4: 完善与测试 (Step 9-10)
9. **集成测试** - 前后端联调
10. **文档与优化** - README、代码优化

## 预置角色

| 角色 | 中文名 | 职责 |
|------|--------|------|
| steward | 大总管 | 任务分发与协调 |
| dev | 开发助理 | 代码、架构、DevOps |
| content | 内容助理 | 文案、内容策划 |
| ops | 运营助理 | 增长、数据分析、活动策划 |
| law | 法务助理 | 合同、合规、风险管理 |
| finance | 财务助理 | 记账、预算、财务分析 |

## 开发优先级

1. **MVP (最小可用产品)**
   - 后端 API 框架
   - 智能体 CRUD
   - 基础前端页面

2. **核心功能**
   - OpenClaw 集成
   - 团队部署
   - 协作拓扑

3. **体验优化**
   - 状态同步
   - 错误处理
   - UI 美化
