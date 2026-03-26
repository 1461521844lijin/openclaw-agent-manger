"""Team schemas"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class CollaborationRule(BaseModel):
    """协作规则"""

    target_id: str = Field(..., description="目标智能体ID")
    trigger: str = Field(..., description="触发条件")


class TeamBase(BaseModel):
    """Base team schema"""

    name: str = Field(..., min_length=1, max_length=100, description="团队名称")
    description: Optional[str] = Field(None, description="团队描述")
    collaborations: Optional[List[CollaborationRule]] = Field(None, description="协作规则")


class TeamCreate(TeamBase):
    """Create team schema"""

    agent_ids: List[str] = Field(default=[], description="智能体ID列表")


class TeamUpdate(BaseModel):
    """Update team schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    collaborations: Optional[List[CollaborationRule]] = None
    agent_ids: Optional[List[str]] = None


class TeamResponse(TeamBase):
    """Team response schema"""

    id: str
    created_at: datetime
    updated_at: datetime
    agents: List[str] = Field(default=[], description="智能体ID列表")

    class Config:
        from_attributes = True


class TeamDetailResponse(TeamResponse):
    """Team detail response with agents"""

    agent_details: List[Dict[str, Any]] = Field(default=[], description="智能体详情")


class TeamListResponse(BaseModel):
    """Team list response"""

    items: List[TeamResponse]
    total: int
