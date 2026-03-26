# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenClaw Multi-Agent Manager - A visual management platform for OpenClaw multi-agent systems. Frontend-backend separated architecture with Python FastAPI backend and Vue 3 frontend.

## Prerequisites

- Python 3.10+
- Node.js 18+
- OpenClaw CLI (`npm install -g openclaw`)
- uv (Python package manager)

## Development Commands

### Backend (Python/FastAPI)
```bash
cd backend
uv sync                          # Install dependencies
uv run uvicorn src.main:app --reload --port 3789   # Start dev server
uv run pytest                    # Run tests
uv run ruff check src            # Lint
```

### Frontend (Vue 3)
```bash
cd frontend
npm install                      # Install dependencies
npm run dev                      # Start dev server (port 5173)
npm run build                    # Build for production
```

### One-command startup
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

## Architecture

### Backend (backend/src/)

```
api/           → FastAPI route handlers (agents.py, teams.py, roles.py, gateway.py)
models/        → SQLAlchemy ORM models (Agent, Team, Role)
schemas/       → Pydantic request/response models
services/      → Business logic layer
  └── openclaw_service.py  → Core integration - wraps OpenClaw CLI commands
```

**Key Pattern**: OpenClawService (`services/openclaw_service.py`) uses `asyncio.create_subprocess_exec` to run local `openclaw` CLI commands. All OpenClaw interactions go through this service, not through any SDK.

**OpenClaw CLI Commands Used**:
- `openclaw agents list --json`
- `openclaw agents add <name> --workspace <dir>`
- `openclaw agents delete <id> --force`
- `openclaw gateway status --json`
- `openclaw gateway start/stop`
- `openclaw agent --agent <id> --message <text>`

### Frontend (frontend/src/)

```
api/           → Axios HTTP clients for each API group
views/         → Page components (AgentsView, TeamsView, RolesView, GatewayView)
stores/        → Pinia state management (agents, teams, roles)
components/    → Reusable components (TopologyGraph for agent collaboration visualization)
types/         → TypeScript interfaces matching backend Pydantic schemas
```

**API Base URL**: `http://localhost:3789/api`

### Database

SQLite database at `backend/data/agents.db`. Auto-created on startup. Models:
- Agent: id, name, role, workspace, status, team_id
- Team: id, name, description, collaborations (JSON)
- Role: id, name, name_en, emoji, description, category, is_builtin

6 builtin roles seeded on first run: steward, dev, content, ops, law, finance.

## Ports

- Backend API: 3789
- Frontend dev: 5173
- OpenClaw Gateway: 18789 (managed by OpenClaw CLI)

## API Documentation

Interactive docs available at `http://localhost:3789/docs` when backend is running.
