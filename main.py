import asyncio
import logging
import json
import os
from agent.mediator import ResearchMediator
from shared.hub_client import HubClient
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.genai import types
from med_safety_gym.messenger import send_message

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

async def main():
    logger.info("Modular Research Loop starting...")
    
    # 1. Initialize Observability Hub Client
    hub = HubClient(base_url="http://localhost:8000")
    
    # 2. Initialize the Meta-Mediator (The Agent)
    mediator = ResearchMediator()
    
    # 3. Extract Sovereign Identity for attributed logging
    mediator_id = getattr(mediator.brain_guard, 'agent_id', 'mediator-unknown')
    token_id = getattr(mediator.brain_guard, 'token_id', 'NO_TOKEN')
    manifest_id = getattr(mediator.brain_guard, 'manifest_id', 'NO_MANIFEST')
    session_id = "research_run_01"
    
    # 3. Initialize ADK Services for the Runner
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()
    
    # 4. Initialize the Sovereign Runner
    runner = Runner(
        app_name="ModularResearchSwarm",
        agent=mediator,
        session_service=session_service,
        memory_service=memory_service,
        auto_create_session=True
    )
    
    # 5. Iteration Loop
    bench_lock = asyncio.Lock()

    bench_url = os.getenv("A2A_BENCH_URL", "http://localhost:8004")
    bench_tasks = int(os.getenv("BENCH_NUM_TASKS", "10"))
    bench_seed = int(os.getenv("BENCH_SEED", "42"))
    bench_full_log = os.getenv("BENCH_LOG_FULL", "0") == "1"
    bench_timeout = int(os.getenv("A2A_BENCH_TIMEOUT", "600"))
    bench_retries = int(os.getenv("BENCH_RETRIES", "2"))
    bench_sleep = float(os.getenv("BENCH_SLEEP_SECONDS", "2"))

    async def fire_a2a_benchmark(iteration: int):
        request_payload = json.dumps({
            "num_tasks": bench_tasks,
            "seed": bench_seed,
            "full_log": bench_full_log,
            "iteration": iteration
        })
        async with bench_lock:
            logger.info(f"Scheduling A2A benchmark for iteration {iteration} (tasks={bench_tasks})")
            await hub.log_event("BENCHMARK_A2A_SCHEDULED", f"iter={iteration} tasks={bench_tasks}", agent_id=mediator_id, profile="orchestrator", session_id=session_id, token_id=token_id, manifest_id=manifest_id)
            await asyncio.sleep(bench_sleep)
            last_err = None
            for attempt in range(bench_retries + 1):
                try:
                    response = await send_message(
                        message=request_payload,
                        base_url=bench_url,
                        timeout=bench_timeout,
                    )
                    await hub.log_event("BENCHMARK_A2A", response.get("response", ""), agent_id=mediator_id, profile="orchestrator", session_id=session_id, token_id=token_id, manifest_id=manifest_id)
                    logger.info(f"A2A benchmark completed for iteration {iteration}")
                    await hub.log_event("BENCHMARK_A2A_DONE", f"iter={iteration}", agent_id=mediator_id, profile="orchestrator", session_id=session_id, token_id=token_id, manifest_id=manifest_id)
                    return
                except Exception as e:
                    last_err = e
                    logger.error(f"A2A benchmark failed (attempt {attempt+1}): {e}")
                    await hub.log_event("BENCHMARK_A2A_ERROR", f"iter={iteration} err={e}", agent_id=mediator_id, profile="orchestrator", session_id=session_id, token_id=token_id, manifest_id=manifest_id)
                    await asyncio.sleep(2 * (attempt + 1))
            logger.error(f"A2A benchmark failed after retries: {last_err}")

    total_iterations = int(os.getenv("RUN_ITERATIONS", "15"))
    summary_every_n = int(os.getenv("BENCH_SUMMARY_EVERY_N", "10"))
    summary_on_end = os.getenv("BENCH_SUMMARY_ON_END", "1") == "1"

    async def maybe_run_summary(iteration: int, final: bool = False):
        if not (summary_on_end or summary_every_n > 0):
            return
        should_run = final or (summary_every_n > 0 and iteration % summary_every_n == 0)
        if not should_run:
            return
        try:
            from tools import benchmark_summary as bs
            summary = bs.write_summary_outputs()
            if summary:
                await hub.log_event("BENCHMARK_SUMMARY", json.dumps(summary), agent_id=mediator_id, profile="orchestrator", session_id=session_id, token_id=token_id, manifest_id=manifest_id)
        except Exception as e:
            logger.error(f"Benchmark summary failed: {e}")
            await hub.log_event("BENCHMARK_SUMMARY_ERROR", str(e), agent_id=mediator_id, profile="orchestrator", session_id=session_id, token_id=token_id, manifest_id=manifest_id)

    for i in range(1, total_iterations + 1):
        logger.info(f"--- Iteration {i} ---")
        try:
            prompt_text = (
                f"Start research iteration {i}.\n"
                "Review the prior Critic feedback and benchmark results. "
                "You MUST generate a completely new, improved Strategy Tree for this iteration. "
                "Do not yield an empty response."
            )
            
            # Using a unique session_id completely purges ADK chat history, 
            # guaranteeing that open-weights Ollama models never hit context-truncation!
            fresh_session_id = f"research_run_iter_{i}"
            
            async for event in runner.run_async(
                user_id="surfiniaburger",
                session_id=fresh_session_id,
                new_message=types.Content(role="user", parts=[types.Part(text=prompt_text)])
            ):
                if event.content:
                    logger.info(f"Mediator Output: {event.content}")
                    await hub.log_event("MEDIATOR_PULSE", str(event.content), agent_id=mediator_id, profile="orchestrator", session_id=fresh_session_id, token_id=token_id, manifest_id=manifest_id)
                    
        except Exception as e:
            logger.error(f"Iteration {i} failed: {e}")
            await hub.log_event("ERROR", str(e), agent_id=mediator_id, profile="orchestrator", session_id=session_id, token_id=token_id, manifest_id=manifest_id)

        # Optional A2A benchmark every N iterations (queued/awaited)
        if os.getenv("USE_A2A_BENCHMARK", "0") == "1":
            every_n = int(os.getenv("BENCH_EVERY_N", "3"))
            if i % every_n == 0:
                await fire_a2a_benchmark(i)
        
        await asyncio.sleep(5)  # Cooldown between cognitive cycles

        await maybe_run_summary(i, final=False)

    await maybe_run_summary(total_iterations, final=True)

if __name__ == "__main__":
    asyncio.run(main())
