"""Agent schemas"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from ..models.agent import AgentStatus


class AgentBase(BaseModel):
    """Base agent schema"""

    name: str = Field(..., min_length=1, max_length=100, description="智能体名称")
    role: str = Field(..., min_length=1, max_length=50, description="角色类型")
    workspace: str = Field(default="./workspace", description="工作目录")
    agent_dir: Optional[str] = Field(None, description="智能体目录")
    description: Optional[str] = Field(None, description="描述")
    config: Optional[Dict[str, Any]] = Field(None, description="OpenClaw 配置")


class AgentCreate(AgentBase):
    """Create agent schema"""

    team_id: Optional[str] = Field(None, description="所属团队ID")


class AgentUpdate(BaseModel):
    """Update agent schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = Field(None, min_length=1, max_length=50)
    workspace: Optional[str] = None
    agent_dir: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    team_id: Optional[str] = None


class AgentResponse(AgentBase):
    """Agent response schema"""

    id: str
    status: AgentStatus = AgentStatus.STOPPED
    team_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    """Agent list response"""

    items: List[AgentResponse]
    total: int
