# shared/hub_client.py
import httpx
import logging
import asyncio

logger = logging.getLogger("hub_client")

class HubClient:
    """
    Sovereign client for communicating with the Observability Hub.
    Built-in retry logic for FastAPI startup latency.
    """
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def log_event(self, event_type: str, data: str):
        """Logs an event to the Hub with a simple retry mechanism."""
        payload = {"event_type": event_type, "data": data}
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
