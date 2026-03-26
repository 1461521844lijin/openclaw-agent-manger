"""Agent management API routes"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_session
from ..models import Agent, AgentStatus
from ..schemas import AgentCreate, AgentUpdate, AgentResponse, AgentListResponse
from ..services.openclaw_service import get_openclaw_service

router = APIRouter()


@router.get("", response_model=AgentListResponse)
async def list_agents(
    status: Optional[AgentStatus] = Query(None, description="按状态筛选"),
    team_id: Optional[str] = Query(None, description="按团队筛选"),
    session: AsyncSession = Depends(get_session),
):
    """获取所有智能体"""
    query = select(Agent)

    if status:
        query = query.where(Agent.status == status)
    if team_id:
        query = query.where(Agent.team_id == team_id)

    query = query.order_by(Agent.created_at.desc())
    result = await session.execute(query)
    agents = result.scalars().all()

    return AgentListResponse(
        items=[AgentResponse.model_validate(a) for a in agents],
        total=len(agents),
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    """获取单个智能体"""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")

    return AgentResponse.model_validate(agent)


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(
    data: AgentCreate,
    session: AsyncSession = Depends(get_session),
):
    """创建智能体"""
    agent = Agent(**data.model_dump())
    session.add(agent)
    await session.commit()
    await session.refresh(agent)

    return AgentResponse.model_validate(agent)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    data: AgentUpdate,
    session: AsyncSession = Depends(get_session),
):
    """更新智能体"""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(agent, key, value)

    await session.commit()
    await session.refresh(agent)

    return AgentResponse.model_validate(agent)


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除智能体"""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")

    await session.delete(agent)
    await session.commit()

    return {"message": "智能体已删除"}


@router.post("/{agent_id}/start")
async def start_agent(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    """启动智能体"""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")

    try:
        openclaw_service = get_openclaw_service()
        await openclaw_service.start_agent(agent_id)
        agent.status = AgentStatus.RUNNING
        await session.commit()
        return {"message": "智能体已启动", "agent_id": agent_id}
    except Exception as e:
        agent.status = AgentStatus.ERROR
        await session.commit()
        raise HTTPException(status_code=500, detail=f"启动失败: {str(e)}")


@router.post("/{agent_id}/stop")
async def stop_agent(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    """停止智能体"""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")

    try:
        openclaw_service = get_openclaw_service()
        await openclaw_service.stop_agent(agent_id)
        agent.status = AgentStatus.STOPPED
        await session.commit()
        return {"message": "智能体已停止", "agent_id": agent_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止失败: {str(e)}")
