import asyncio
import logging
import os
from agent.harness import MetacogHarness
from shared.hub_client import HubClient
from google.genai import types

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

async def main():
    logger.info("Sovereign Metacognitive Harness launching (Phase 3B)...")
    
    # 1. Initialize Observability Hub Client
    hub = HubClient(base_url="http://localhost:8000")
    
    # 2. Initialize the Thick Harness (The Custom ADK Agent)
    harness = MetacogHarness()
    
    # 3. Initialize ADK Runner for session management
    from google.adk.runners import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="MetacogSwarm",
        agent=harness,
        session_service=session_service,
        auto_create_session=True
    )
    
    total_iterations = int(os.getenv("RUN_ITERATIONS", "15"))

    for i in range(1, total_iterations + 1):
        logger.info(f"--- Iteration {i} ---")
        try:
            # 4. Execute via ADK Runner
            # Using a fresh session ID per iteration purges history for local model stability
            session_id = f"research_run_iter_{i}"
            
            async for event in runner.run_async(
                user_id="surfiniaburger",
                session_id=session_id,
                # We send a trigger message; the Harness logic handles the rest
                new_message=types.Content(role="user", parts=[types.Part(text=f"Start iteration {i}")])
            ):
                if event.content:
                    # Log event pulses to Hub
                    await hub.log_event(
                        "HARNESS_EVENT", 
                        str(event.content.parts[0].text), 
                        agent_id=harness.name, 
                        profile="orchestrator", 
                        session_id=session_id
                    )
            
            await hub.log_event(
                "HARNESS_PULSE", 
                f"Iteration {i} complete.", 
                agent_id=harness.name, 
                profile="orchestrator", 
                session_id=session_id
            )
                    
        except Exception as e:
            logger.error(f"Iteration {i} failed: {e}")
            await hub.log_event("ERROR", str(e), agent_id="harness-v1", profile="orchestrator")

        await asyncio.sleep(5)  # Cooldown between cognitive cycles

    logger.info("Harness run complete. Check latest_results.json and experience.db for the Moat.")

if __name__ == "__main__":
    asyncio.run(main())
