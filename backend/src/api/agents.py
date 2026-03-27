"""Agent management API routes"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import Agent, AgentStatus
from ..schemas import AgentCreate, AgentListResponse, AgentResponse, AgentUpdate
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


@router.get("/sync")
async def sync_agents(session: AsyncSession = Depends(get_session)):
    """从 OpenClaw 同步智能体列表"""
    openclaw_service = get_openclaw_service()
    openclaw_agents = await openclaw_service.list_agents()

    synced = []
    for oc_agent in openclaw_agents:
        agent_id = oc_agent.get("id")
        # Check if agent exists in our database
        result = await session.execute(select(Agent).where(Agent.id == agent_id))
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing agent
            existing.name = oc_agent.get("identityName", existing.name)
            existing.workspace = oc_agent.get("workspace", existing.workspace)
            existing.agent_dir = oc_agent.get("agentDir", existing.agent_dir)
        else:
            # Create new agent
            agent = Agent(
                id=agent_id,
                name=oc_agent.get("identityName", "Unknown"),
                role="agent",
                workspace=oc_agent.get("workspace", ""),
                agent_dir=oc_agent.get("agentDir"),
                status=AgentStatus.RUNNING if oc_agent.get("isDefault") else AgentStatus.STOPPED,
            )
            session.add(agent)
        synced.append(agent_id)

    await session.commit()
    return {"message": f"同步完成，共 {len(synced)} 个智能体", "agents": synced}


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
    """创建智能体（同时在数据库和 OpenClaw 中创建）"""
    openclaw_service = get_openclaw_service()

    # Create in OpenClaw
    oc_result = await openclaw_service.create_agent(
        name=data.name,
        role=data.role,
        workspace=data.workspace,
    )

    if not oc_result.get("success", True):
        raise HTTPException(status_code=500, detail=f"OpenClaw 创建失败: {oc_result.get('error')}")

    # Get the agent ID from OpenClaw
    agent_id = oc_result.get("id", data.name.lower().replace(" ", "-"))

    # Create in database
    agent = Agent(
        id=agent_id,
        name=data.name,
        role=data.role,
        workspace=data.workspace,
        agent_dir=oc_result.get("agentDir"),
        description=data.description,
        config=data.config,
        team_id=data.team_id,
        feishu_app_id=data.feishu_app_id,
        feishu_app_secret=data.feishu_app_secret,
        status=AgentStatus.STOPPED,
    )
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
    """删除智能体（同时从数据库和 OpenClaw 中删除）"""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")

    # Delete from OpenClaw
    openclaw_service = get_openclaw_service()
    await openclaw_service.delete_agent(agent_id)

    # Delete from database
    await session.delete(agent)
    await session.commit()

    return {"message": "智能体已删除", "agent_id": agent_id}


@router.post("/{agent_id}/start")
async def start_agent(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    """启动智能体（确保 Gateway 运行）"""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")

    try:
        openclaw_service = get_openclaw_service()

        # Check and start gateway if needed
        gateway_status = await openclaw_service.gateway_status()
        if not gateway_status.get("running"):
            await openclaw_service.start_gateway()

        agent.status = AgentStatus.RUNNING
        await session.commit()
        return {
            "message": "智能体已启动",
            "agent_id": agent_id,
            "gateway": gateway_status.get("url", "ws://127.0.0.1:18789"),
        }
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

    # Agent doesn't really "stop" individually in OpenClaw
    # It's managed by the gateway
    agent.status = AgentStatus.STOPPED
    await session.commit()

    return {"message": "智能体已停止", "agent_id": agent_id}


@router.post("/{agent_id}/message")
async def send_message_to_agent(
    agent_id: str,
    message: str,
    session: AsyncSession = Depends(get_session),
):
    """向智能体发送消息"""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")

    try:
        openclaw_service = get_openclaw_service()
        result = await openclaw_service.send_message(agent_id, message)
        return {"message": "消息已发送", "agent_id": agent_id, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送失败: {str(e)}")


@router.post("/{agent_id}/bind")
async def bind_agent_channel(
    agent_id: str,
    channel: str,
    account_id: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """绑定智能体到通道

    Args:
        agent_id: 智能体 ID
        channel: 通道类型 (telegram, whatsapp, discord, feishu 等)
        account_id: 账户 ID (可选)
    """
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")

    try:
        openclaw_service = get_openclaw_service()
        result = await openclaw_service.bind_agent(agent_id, channel, account_id)
        return {"message": "绑定成功", "agent_id": agent_id, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"绑定失败: {str(e)}")


