"""Agent management API routes"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import Agent, AgentStatus
from ..schemas import AgentCreate, AgentListResponse, AgentResponse, AgentUpdate, BindChannelRequest, SendMessageRequest
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
        items=[AgentResponse.from_agent(a) for a in agents],
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

    return AgentResponse.from_agent(agent)


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

    return AgentResponse.from_agent(agent)


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
    # 不用空字符串覆盖已有的 secret
    if "feishu_app_secret" in update_data and not update_data["feishu_app_secret"]:
        del update_data["feishu_app_secret"]
    for key, value in update_data.items():
        setattr(agent, key, value)

    await session.commit()
    await session.refresh(agent)

    return AgentResponse.from_agent(agent)


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
    """启动智能体（确保 Gateway 运行，并验证智能体可达）"""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")

    try:
        openclaw_service = get_openclaw_service()

        # Check and start gateway if needed
        gateway_status = await openclaw_service.gateway_status()
        if not gateway_status.get("running"):
            gw_result = await openclaw_service.start_gateway()
            if not gw_result.get("success", True):
                raise Exception(f"Gateway 启动失败: {gw_result.get('error')}")

        # 验证智能体在 OpenClaw 中存在
        oc_agent = await openclaw_service.get_agent(agent_id)
        if not oc_agent:
            raise Exception(f"智能体 {agent_id} 在 OpenClaw 中不存在，请先同步")

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
    """停止智能体

    注意: OpenClaw 中智能体由 Gateway 统一管理，不支持单独停止。
    此操作会将状态标记为已停止，如果所有智能体都已停止，则会关闭 Gateway。
    """
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")

    agent.status = AgentStatus.STOPPED
    await session.commit()

    # 检查是否所有智能体都已停止，如果是则关闭 Gateway
    all_agents_result = await session.execute(
        select(Agent).where(Agent.status == AgentStatus.RUNNING)
    )
    running_agents = all_agents_result.scalars().all()

    if not running_agents:
        openclaw_service = get_openclaw_service()
        gateway_status = await openclaw_service.gateway_status()
        if gateway_status.get("running"):
            await openclaw_service.stop_gateway()

    return {"message": "智能体已停止", "agent_id": agent_id}


@router.post("/{agent_id}/message")
async def send_message_to_agent(
    agent_id: str,
    data: SendMessageRequest,
    session: AsyncSession = Depends(get_session),
):
    """向智能体发送消息"""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")

    try:
        openclaw_service = get_openclaw_service()
        result = await openclaw_service.send_message(agent_id, data.message)
        return {"message": "消息已发送", "agent_id": agent_id, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送失败: {str(e)}")


@router.post("/{agent_id}/bind")
async def bind_agent_channel(
    agent_id: str,
    data: BindChannelRequest,
    session: AsyncSession = Depends(get_session),
):
    """绑定智能体到通道"""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")

    try:
        openclaw_service = get_openclaw_service()
        result = await openclaw_service.bind_agent(agent_id, data.channel, data.account_id)
        return {"message": "绑定成功", "agent_id": agent_id, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"绑定失败: {str(e)}")


