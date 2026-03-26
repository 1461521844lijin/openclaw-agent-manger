"""Role schemas"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """Base role schema"""

    name: str = Field(..., min_length=1, max_length=100, description="角色名称")
    name_en: str = Field(..., min_length=1, max_length=100, description="英文名称")
    emoji: Optional[str] = Field(None, max_length=10, description="图标")
    description: Optional[str] = Field(None, description="描述")
    description_en: Optional[str] = Field(None, description="英文描述")
    core_mission: Optional[str] = Field(None, description="核心使命")
    critical_rules: Optional[str] = Field(None, description="关键规则")
    category: Optional[str] = Field(None, max_length=50, description="分类")


class RoleCreate(RoleBase):
    """Create role schema"""

    pass


class RoleUpdate(BaseModel):
    """Update role schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    name_en: Optional[str] = Field(None, min_length=1, max_length=100)
    emoji: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    core_mission: Optional[str] = None
    critical_rules: Optional[str] = None
    category: Optional[str] = None


class RoleResponse(RoleBase):
    """Role response schema"""

    id: str
    is_builtin: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    """Role list response"""

    items: List[RoleResponse]
    total: int


class RoleCategory(BaseModel):
    """Role category with items"""

    id: str
    label: str
    items: List[RoleResponse]


class RoleCategoryListResponse(BaseModel):
    """Role category list response"""

    categories: List[RoleCategory]
