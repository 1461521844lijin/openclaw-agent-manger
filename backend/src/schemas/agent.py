"""Agent schemas"""

from datetime import datetime
from typing import Any, Dict, List, Optional

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
    feishu_app_id: Optional[str] = Field(None, description="飞书应用 App ID")
    feishu_app_secret: Optional[str] = Field(None, description="飞书应用 App Secret")


class AgentUpdate(BaseModel):
    """Update agent schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = Field(None, min_length=1, max_length=50)
    workspace: Optional[str] = None
    agent_dir: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    team_id: Optional[str] = None
    feishu_app_id: Optional[str] = Field(None, description="飞书应用 App ID")
    feishu_app_secret: Optional[str] = Field(None, description="飞书应用 App Secret")


class FeishuConfig(BaseModel):
    """Feishu Bot configuration schema"""

    app_id: str = Field(..., description="飞书应用 App ID")
    app_secret: str = Field(..., description="飞书应用 App Secret")


class SendMessageRequest(BaseModel):
    """发送消息请求"""

    message: str = Field(..., min_length=1, description="消息内容")


class BindChannelRequest(BaseModel):
    """绑定通道请求"""

    channel: str = Field(..., min_length=1, description="通道类型 (telegram, whatsapp, discord, feishu 等)")
    account_id: Optional[str] = Field(None, description="账户 ID")


class AgentResponse(AgentBase):
    """Agent response schema"""

    id: str
    status: AgentStatus = AgentStatus.STOPPED
    team_id: Optional[str] = None
    feishu_app_id: Optional[str] = Field(None, description="飞书应用 App ID")
    feishu_secret_configured: bool = Field(False, description="飞书 App Secret 是否已配置")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_agent(cls, agent) -> "AgentResponse":
        """从 ORM 模型创建响应，自动脱敏"""
        data = {
            "id": agent.id,
            "name": agent.name,
            "role": agent.role,
            "workspace": agent.workspace,
            "agent_dir": agent.agent_dir,
            "description": agent.description,
            "config": agent.config,
            "status": agent.status,
            "team_id": agent.team_id,
            "feishu_app_id": agent.feishu_app_id,
            "feishu_secret_configured": bool(agent.feishu_app_secret),
            "created_at": agent.created_at,
            "updated_at": agent.updated_at,
        }
        return cls(**data)


class AgentListResponse(BaseModel):
    """Agent list response"""

    items: List[AgentResponse]
    total: int
