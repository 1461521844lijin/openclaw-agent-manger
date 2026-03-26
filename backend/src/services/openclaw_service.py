"""OpenClaw service layer - wraps cmdop client for agent management"""

import os
from typing import Optional, Dict, Any, List
from pathlib import Path

from cmdop import CMDOPClient, AsyncCMDOPClient, AgentStatus
from cmdop.exceptions import CMDOPError, ConnectionError, AuthenticationError

from ..config import settings


class OpenClawService:
    """Service for interacting with OpenClaw/CMDOP"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openclaw_api_key
        self._client: Optional[AsyncCMDOPClient] = None
        self._workspace = Path(settings.openclaw_workspace)

    async def get_client(self) -> AsyncCMDOPClient:
        """Get or create CMDOP client"""
        if self._client is None:
            if not self.api_key:
                raise ValueError("OpenClaw API key is required")
            self._client = AsyncCMDOPClient(api_key=self.api_key)
        return self._client

    async def create_agent(
        self,
        name: str,
        role: str,
        workspace: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new agent

        Args:
            name: Agent name
            role: Agent role type
            workspace: Working directory
            config: OpenClaw configuration

        Returns:
            Agent info dict
        """
        client = await self.get_client()

        # Ensure workspace exists
        ws_path = Path(workspace or self._workspace) / name
        ws_path.mkdir(parents=True, exist_ok=True)

        # Create agent configuration
        agent_config = {
            "name": name,
            "role": role,
            "workspace": str(ws_path),
            **(config or {}),
        }

        # TODO: Call actual CMDOP API to create agent
        # This is a placeholder - actual implementation depends on CMDOP API

        return {
            "name": name,
            "role": role,
            "workspace": str(ws_path),
            "status": "created",
        }

    async def start_agent(self, agent_id: str) -> Dict[str, Any]:
        """Start an agent

        Args:
            agent_id: Agent ID to start

        Returns:
            Status dict
        """
        client = await self.get_client()

        # TODO: Call actual CMDOP API to start agent
        # result = await client.start_agent(agent_id)

        return {
            "agent_id": agent_id,
            "status": "running",
            "message": "Agent started successfully",
        }

    async def stop_agent(self, agent_id: str) -> Dict[str, Any]:
        """Stop an agent

        Args:
            agent_id: Agent ID to stop

        Returns:
            Status dict
        """
        client = await self.get_client()

        # TODO: Call actual CMDOP API to stop agent
        # result = await client.stop_agent(agent_id)

        return {
            "agent_id": agent_id,
            "status": "stopped",
            "message": "Agent stopped successfully",
        }

    async def get_agent_status(self, agent_id: str) -> AgentStatus:
        """Get agent status

        Args:
            agent_id: Agent ID

        Returns:
            Agent status
        """
        client = await self.get_client()

        # TODO: Call actual CMDOP API to get status
        return AgentStatus.OFFLINE

    async def deploy_team(
        self,
        team_name: str,
        agents: List[Dict[str, Any]],
        collaborations: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Deploy a team of agents

        Args:
            team_name: Team name
            agents: List of agent configs
            collaborations: Collaboration rules

        Returns:
            Deployment result
        """
        results = []

        for agent_config in agents:
            result = await self.create_agent(
                name=agent_config.get("name"),
                role=agent_config.get("role"),
                workspace=agent_config.get("workspace"),
                config=agent_config.get("config"),
            )
            results.append(result)

        # TODO: Set up collaboration routing between agents

        return {
            "team_name": team_name,
            "agents": results,
            "status": "deployed",
            "message": f"Team '{team_name}' deployed with {len(agents)} agents",
        }

    async def teardown_team(
        self,
        team_id: str,
        agent_ids: List[str],
    ) -> Dict[str, Any]:
        """Teardown a team and stop all agents

        Args:
            team_id: Team ID
            agent_ids: List of agent IDs to stop

        Returns:
            Teardown result
        """
        results = []

        for agent_id in agent_ids:
            try:
                await self.stop_agent(agent_id)
                results.append({"agent_id": agent_id, "status": "stopped"})
            except Exception as e:
                results.append({"agent_id": agent_id, "status": "error", "error": str(e)})

        return {
            "team_id": team_id,
            "agents": results,
            "status": "teardown_complete",
            "message": f"Team {team_id} teardown complete",
        }

    async def list_online_agents(self) -> List[Dict[str, Any]]:
        """List all online agents

        Returns:
            List of agent info
        """
        try:
            client = await self.get_client()
            agents = await client.list_agents()
            return [
                {
                    "id": a.id,
                    "name": a.name,
                    "status": a.status.value if hasattr(a.status, "value") else str(a.status),
                }
                for a in agents
            ]
        except Exception:
            return []


# Singleton instance
_openclaw_service: Optional[OpenClawService] = None


def get_openclaw_service() -> OpenClawService:
    """Get OpenClaw service instance"""
    global _openclaw_service
    if _openclaw_service is None:
        _openclaw_service = OpenClawService()
    return _openclaw_service
