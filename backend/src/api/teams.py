"""Team management API routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_session
from ..models import Agent, Team
from ..schemas import (
    TeamCreate,
    TeamDetailResponse,
    TeamListResponse,
    TeamResponse,
    TeamUpdate,
)
from ..services.openclaw_service import get_openclaw_service

router = APIRouter()


@router.get("", response_model=TeamListResponse)
async def list_teams(session: AsyncSession = Depends(get_session)):
    """获取所有团队"""
    query = select(Team).options(selectinload(Team.agents)).order_by(Team.created_at.desc())
    result = await session.execute(query)
    teams = result.scalars().all()

    items = []
    for team in teams:
        team_dict = {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "collaborations": team.collaborations,
            "created_at": team.created_at,
            "updated_at": team.updated_at,
            "agents": [a.id for a in team.agents],
        }
        items.append(TeamResponse(**team_dict))

    return TeamListResponse(items=items, total=len(items))


@router.get("/{team_id}", response_model=TeamDetailResponse)
async def get_team(
    team_id: str,
    session: AsyncSession = Depends(get_session),
):
    """获取单个团队详情"""
    query = select(Team).where(Team.id == team_id).options(selectinload(Team.agents))
    result = await session.execute(query)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")

    return TeamDetailResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        collaborations=team.collaborations,
        created_at=team.created_at,
        updated_at=team.updated_at,
        agents=[a.id for a in team.agents],
        agent_details=[
            {
                "id": a.id,
                "name": a.name,
                "role": a.role,
                "status": a.status.value,
            }
            for a in team.agents
        ],
    )


@router.post("", response_model=TeamResponse, status_code=201)
async def create_team(
    data: TeamCreate,
    session: AsyncSession = Depends(get_session),
):
    """创建团队"""
    # 获取所有指定的智能体
    agents = []
    agent_ids = []
    if data.agent_ids:
        result = await session.execute(select(Agent).where(Agent.id.in_(data.agent_ids)))
        agents = result.scalars().all()
        agent_ids = [a.id for a in agents]

        if len(agents) != len(data.agent_ids):
            raise HTTPException(status_code=400, detail="部分智能体不存在")

    team = Team(
        name=data.name,
        description=data.description,
        collaborations=[c.model_dump() for c in data.collaborations]
        if data.collaborations
        else None,
        agents=agents,
    )
    session.add(team)
    await session.commit()
    await session.refresh(team)

    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        collaborations=team.collaborations,
        created_at=team.created_at,
        updated_at=team.updated_at,
        agents=agent_ids,
    )


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    data: TeamUpdate,
    session: AsyncSession = Depends(get_session),
):
    """更新团队"""
    query = select(Team).where(Team.id == team_id).options(selectinload(Team.agents))
    result = await session.execute(query)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")

    if data.name is not None:
        team.name = data.name
    if data.description is not None:
        team.description = data.description
    if data.collaborations is not None:
        team.collaborations = [c.model_dump() for c in data.collaborations]
    if data.agent_ids is not None:
        result = await session.execute(select(Agent).where(Agent.id.in_(data.agent_ids)))
        team.agents = list(result.scalars().all())

    await session.commit()
    await session.refresh(team)

    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        collaborations=team.collaborations,
        created_at=team.created_at,
        updated_at=team.updated_at,
        agents=[a.id for a in team.agents],
    )


@router.delete("/{team_id}")
async def delete_team(
    team_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除团队"""
    result = await session.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")

    await session.delete(team)
    await session.commit()

    return {"message": "团队已删除"}


@router.post("/{team_id}/deploy")
async def deploy_team(
    team_id: str,
    session: AsyncSession = Depends(get_session),
):
    """部署团队"""
    query = select(Team).where(Team.id == team_id).options(selectinload(Team.agents))
    result = await session.execute(query)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")

    if not team.agents:
        raise HTTPException(status_code=400, detail="团队中没有智能体")

    try:
        openclaw_service = get_openclaw_service()
        deploy_result = await openclaw_service.deploy_team(
            team_name=team.name,
            agents=[
                {
                    "id": a.id,
                    "name": a.name,
                    "role": a.role,
                    "workspace": a.workspace,
                    "config": a.config,
                }
                for a in team.agents
            ],
            collaborations=team.collaborations,
        )
        return {"message": "团队部署成功", "team_id": team_id, "result": deploy_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"部署失败: {str(e)}")


@router.post("/{team_id}/teardown")
async def teardown_team(
    team_id: str,
    session: AsyncSession = Depends(get_session),
):
    """清理团队"""
    query = select(Team).where(Team.id == team_id).options(selectinload(Team.agents))
    result = await session.execute(query)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")

    try:
        openclaw_service = get_openclaw_service()
        teardown_result = await openclaw_service.teardown_team(
            team_id=team_id,
            agent_ids=[a.id for a in team.agents],
        )
        return {"message": "团队清理成功", "team_id": team_id, "result": teardown_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理失败: {str(e)}")
