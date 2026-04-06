# shared/hub_client.py
import httpx
import logging
import asyncio

logger = logging.getLogger("hub_client")

class HubClient:
    """
    Sovereign client for communicating with the Observability Hub.
    Identity-aware: every event is attributed to an agent_id and profile.
    """
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def log_event(self, event_type: str, data: str,
                        agent_id: str = "ANONYMOUS", profile: str = "UNKNOWN",
                        session_id: str = "", token_id: str = "NO_TOKEN", manifest_id: str = "NO_MANIFEST"):
        """Logs an identity-attributed event to the Hub."""
        payload = {
            "event_type": event_type,
            "data": data,
            "agent_id": agent_id,
            "profile": profile,
            "session_id": session_id,
            "token_id": token_id,
            "manifest_id": manifest_id,
        }
        for attempt in range(3):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/log", 
                        json=payload, 
                        timeout=5.0
                    )
                    return response.json()
            except Exception as e:
                if attempt == 2:
                    logger.error(f"Failed to log event to Hub after {attempt+1} attempts: {e}")
                await asyncio.sleep(2)
        return None

