"""OpenClaw service layer - uses local CLI commands for agent management"""

import json
import asyncio
import shutil
from typing import Optional, Dict, Any, List
from pathlib import Path

from ..config import settings


class OpenClawService:
    """Service for interacting with OpenClaw via CLI commands"""

    def __init__(self):
        self._workspace = Path(settings.openclaw_workspace)
        self._openclaw_path = shutil.which("openclaw") or "openclaw"

    async def _run_command(self, args: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Run openclaw command and return result

        Args:
            args: Command arguments
            timeout: Timeout in seconds

        Returns:
            Dict with stdout, stderr, and return_code
        """
        cmd = [self._openclaw_path] + args

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            return {
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "return_code": process.returncode,
            }
        except asyncio.TimeoutError:
            return {
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "return_code": -1,
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
            }

    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all configured agents

        Returns:
            List of agent info dicts
        """
        result = await self._run_command(["agents", "list", "--json"])

        if result["return_code"] != 0:
            return []

        try:
            agents = json.loads(result["stdout"])
            return agents
        except json.JSONDecodeError:
            return []

    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get single agent info

        Args:
            agent_id: Agent ID

        Returns:
            Agent info dict or None
        """
        agents = await self.list_agents()
        for agent in agents:
            if agent.get("id") == agent_id:
                return agent
        return None

    async def create_agent(
        self,
        name: str,
        role: str,
        workspace: Optional[str] = None,
        model: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new agent via CLI

        Args:
            name: Agent name
            role: Agent role type
            workspace: Working directory
            model: Model ID
            description: Agent description

        Returns:
            Agent info dict
        """
        # Build command arguments
        args = ["agents", "add", name, "--non-interactive"]

        if workspace:
            ws_path = Path(workspace)
            ws_path.mkdir(parents=True, exist_ok=True)
            args.extend(["--workspace", str(ws_path)])

        if model:
            args.extend(["--model", model])

        # Run command
        result = await self._run_command(args, timeout=60)

        if result["return_code"] != 0:
            return {
                "success": False,
                "error": result["stderr"] or result["stdout"],
                "name": name,
                "role": role,
            }

        # Parse result
        try:
            if result["stdout"].strip().startswith("{"):
                agent_info = json.loads(result["stdout"])
            else:
                # Text output, try to extract agent ID
                agent_info = {"name": name, "role": role}

            # Get full agent info from list
            agents = await self.list_agents()
            for agent in agents:
                if agent.get("identityName") == name or agent.get("id") == name:
                    agent_info = {**agent_info, **agent, "success": True}
                    break

            return agent_info
        except json.JSONDecodeError:
            return {
                "success": True,
                "name": name,
                "role": role,
                "raw_output": result["stdout"],
            }

    async def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Delete an agent via CLI

        Args:
            agent_id: Agent ID to delete

        Returns:
            Result dict
        """
        result = await self._run_command(
            ["agents", "delete", agent_id, "--force", "--json"],
            timeout=30
        )

        if result["return_code"] != 0:
            return {
                "success": False,
                "error": result["stderr"] or result["stdout"],
                "agent_id": agent_id,
            }

        try:
            return json.loads(result["stdout"])
        except json.JSONDecodeError:
            return {
                "success": True,
                "agent_id": agent_id,
                "message": "Agent deleted",
            }

    async def bind_agent(
        self,
        agent_id: str,
        channel: str,
        account_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Bind agent to a channel

        Args:
            agent_id: Agent ID
            channel: Channel type (telegram, whatsapp, discord, etc.)
            account_id: Account ID (optional)

        Returns:
            Result dict
        """
        bind_str = f"{channel}:{account_id}" if account_id else channel

        result = await self._run_command(
            ["agents", "bind", "--agent", agent_id, "--bind", bind_str, "--json"],
            timeout=30
        )

        if result["return_code"] != 0:
            return {
                "success": False,
                "error": result["stderr"] or result["stdout"],
            }

        try:
            return json.loads(result["stdout"])
        except json.JSONDecodeError:
            return {"success": True, "message": f"Agent bound to {bind_str}"}

    async def gateway_status(self) -> Dict[str, Any]:
        """Get gateway status

        Returns:
            Gateway status dict
        """
        result = await self._run_command(["gateway", "status", "--json"], timeout=10)

        if result["return_code"] != 0:
            return {
                "running": False,
                "error": result["stderr"] or result["stdout"],
            }

        try:
            status = json.loads(result["stdout"])
            return {
                "running": status.get("rpc", {}).get("ok", False),
                "port": status.get("gateway", {}).get("port", 18789),
                "url": status.get("gateway", {}).get("probeUrl", ""),
                "details": status,
            }
        except json.JSONDecodeError:
            return {"running": False, "error": "Failed to parse status"}

    async def start_gateway(self, port: Optional[int] = None) -> Dict[str, Any]:
        """Start the gateway service

        Args:
            port: Gateway port (default from config)

        Returns:
            Result dict
        """
        args = ["gateway", "start"]
        if port:
            args.extend(["--port", str(port)])

        result = await self._run_command(args, timeout=30)

        if result["return_code"] != 0:
            return {
                "success": False,
                "error": result["stderr"] or result["stdout"],
            }

        return {
            "success": True,
            "message": "Gateway started",
        }

    async def stop_gateway(self) -> Dict[str, Any]:
        """Stop the gateway service

        Returns:
            Result dict
        """
        result = await self._run_command(["gateway", "stop"], timeout=30)

        if result["return_code"] != 0:
            return {
                "success": False,
                "error": result["stderr"] or result["stdout"],
            }

        return {
            "success": True,
            "message": "Gateway stopped",
        }

    async def send_message(
        self,
        agent_id: str,
        message: str,
        channel: Optional[str] = None,
        target: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send message to an agent

        Args:
            agent_id: Agent ID
            message: Message text
            channel: Delivery channel
            target: Target number/address

        Returns:
            Result dict
        """
        args = ["agent", "--agent", agent_id, "--message", message, "--json"]

        if channel:
            args.extend(["--channel", channel])
        if target:
            args.extend(["--to", target])

        result = await self._run_command(args, timeout=120)

        if result["return_code"] != 0:
            return {
                "success": False,
                "error": result["stderr"] or result["stdout"],
            }

        try:
            return json.loads(result["stdout"])
        except json.JSONDecodeError:
            return {
                "success": True,
                "output": result["stdout"],
            }

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
            collaborations: Collaboration rules (future feature)

        Returns:
            Deployment result
        """
        results = []

        for agent_config in agents:
            result = await self.create_agent(
                name=agent_config.get("name"),
                role=agent_config.get("role"),
                workspace=agent_config.get("workspace"),
                model=agent_config.get("model"),
            )
            results.append(result)

        # Ensure gateway is running
        gateway_status = await self.gateway_status()
        if not gateway_status.get("running"):
            await self.start_gateway()

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
        """Teardown a team and delete all agents

        Args:
            team_id: Team ID
            agent_ids: List of agent IDs to delete

        Returns:
            Teardown result
        """
        results = []

        for agent_id in agent_ids:
            try:
                result = await self.delete_agent(agent_id)
                results.append(result)
            except Exception as e:
                results.append({
                    "agent_id": agent_id,
                    "success": False,
                    "error": str(e),
                })

        return {
            "team_id": team_id,
            "agents": results,
            "status": "teardown_complete",
            "message": f"Team {team_id} teardown complete",
        }


# Singleton instance
_openclaw_service: Optional[OpenClawService] = None


def get_openclaw_service() -> OpenClawService:
    """Get OpenClaw service instance"""
    global _openclaw_service
    if _openclaw_service is None:
        _openclaw_service = OpenClawService()
    return _openclaw_service
