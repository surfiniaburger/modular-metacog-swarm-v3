# shared/messenger.py
import httpx
import logging

logger = logging.getLogger("messenger")

class Messenger:
    """
    Modular communication wrapper ported from med_safety_gym.
    Facilitates A2A interaction between Agent and Executor via MCP/HTTP.
    """
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def call_mcp_tool(self, server: str, tool: str, arguments: dict) -> dict:
        """
        Communicates with a local FastMCP server.
        Note: In a true A2A flow, this would use the A2A client.
        For benchmarking, we use a simplified direct call.
        """
        # Placeholder for A2A routing logic
        logger.info(f"Calling tool {tool} on server {server}...")
        return {"status": "success", "result": "mock_result"}
