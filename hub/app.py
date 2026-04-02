# hub/app.py
from fastapi import FastAPI, Request
import json
import logging
import os
from datetime import datetime

app = FastAPI(title="Modular Swarm Observability Hub")
logger = logging.getLogger("hub")

CHRONICLE_PATH = "research_env/docs/research_chronicle.md"
os.makedirs("research_env/docs", exist_ok=True)

@app.on_event("startup")
async def startup():
    if not os.path.exists(CHRONICLE_PATH):
        with open(CHRONICLE_PATH, "w") as f:
            f.write("# Research Chronicle\n\n## Era 1: Initialization\nModular Hub spawned.")

@app.post("/log")
async def log_event(request: Request):
    """
    Structured event logging for the research chronicle.
    """
    data = await request.json()
    event_type = data.get("event_type", "GENERIC")
    content = data.get("data", "")
    timestamp = datetime.utcnow().isoformat()
    
    # Standardized chronicle entry
    entry = f"\n\n### [{timestamp}] {event_type}\n{content}"
    
    with open(CHRONICLE_PATH, "a") as f:
        f.write(entry)
        
    logger.info(f"Logged {event_type} to Chronicle.")
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
