"""Role library API routes"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_session
from ..models import Role
from ..schemas import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleListResponse,
    RoleCategory,
    RoleCategoryListResponse,
)

router = APIRouter()


@router.get("", response_model=RoleListResponse)
async def list_roles(
    category: Optional[str] = Query(None, description="按分类筛选"),
    session: AsyncSession = Depends(get_session),
):
    """获取所有角色"""
    query = select(Role)

    if category:
        query = query.where(Role.category == category)

    query = query.order_by(Role.created_at.desc())
    result = await session.execute(query)
    roles = result.scalars().all()

    return RoleListResponse(
        items=[RoleResponse.model_validate(r) for r in roles],
        total=len(roles),
    )


@router.get("/categories", response_model=RoleCategoryListResponse)
async def list_role_categories(session: AsyncSession = Depends(get_session)):
    """获取角色分类列表"""
    # 获取所有角色
    result = await session.execute(select(Role).order_by(Role.category, Role.created_at))
    roles = result.scalars().all()

    # 按分类分组
    categories_dict = {}
    for role in roles:
        cat = role.category or "其他"
        if cat not in categories_dict:
            categories_dict[cat] = []
        categories_dict[cat].append(RoleResponse.model_validate(role))

    categories = [
        RoleCategory(id=cat, label=cat, items=items)
        for cat, items in categories_dict.items()
    ]

    return RoleCategoryListResponse(categories=categories)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    session: AsyncSession = Depends(get_session),
):
    """获取单个角色"""
    result = await session.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    return RoleResponse.model_validate(role)


@router.post("", response_model=RoleResponse, status_code=201)
async def create_role(
    data: RoleCreate,
    session: AsyncSession = Depends(get_session),
):
    """创建自定义角色"""
    role = Role(**data.model_dump(), is_builtin=False)
    session.add(role)
    await session.commit()
    await session.refresh(role)

    return RoleResponse.model_validate(role)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    data: RoleUpdate,
    session: AsyncSession = Depends(get_session),
):
    """更新角色"""
    result = await session.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if role.is_builtin:
        raise HTTPException(status_code=400, detail="预置角色不允许修改")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(role, key, value)

    await session.commit()
    await session.refresh(role)

    return RoleResponse.model_validate(role)


@router.delete("/{role_id}")
async def delete_role(
    role_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除角色"""
    result = await session.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if role.is_builtin:
        raise HTTPException(status_code=400, detail="预置角色不允许删除")

    await session.delete(role)
    await session.commit()

    return {"message": "角色已删除"}
