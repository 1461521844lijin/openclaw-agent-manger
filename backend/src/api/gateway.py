"""Gateway management API routes"""

from fastapi import APIRouter

from ..services.openclaw_service import get_openclaw_service

router = APIRouter()


@router.get("/status")
async def get_gateway_status():
    """获取 Gateway 状态"""
    openclaw_service = get_openclaw_service()
    status = await openclaw_service.gateway_status()
    return status


@router.post("/start")
async def start_gateway():
    """启动 Gateway"""
    openclaw_service = get_openclaw_service()
    result = await openclaw_service.start_gateway()
    return result


@router.post("/stop")
async def stop_gateway():
    """停止 Gateway"""
    openclaw_service = get_openclaw_service()
    result = await openclaw_service.stop_gateway()
    return result


@router.get("/agents")
async def list_openclaw_agents():
    """获取 OpenClaw 中所有智能体"""
    openclaw_service = get_openclaw_service()
    agents = await openclaw_service.list_agents()
    return {"agents": agents}
