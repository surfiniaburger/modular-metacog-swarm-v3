import argparse
import logging
import os
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from med_safety_gym.executor import Executor
from benchmark_a2a.benchmark_agent import BenchmarkAgent

logger = logging.getLogger(__name__)

def create_app(host="0.0.0.0", port=8004, card_url=None):
    skill = AgentSkill(
        id="metacog-benchmark",
        name="Metacognition Benchmark",
        description="Runs the local metacognition benchmark and returns results.",
        tags=["benchmarking", "metacognition", "evaluation"],
        examples=[
            "{\"num_tasks\": 40, \"seed\": 42, \"full_log\": true, \"iteration\": 1}"
        ]
    )

    agent_card = AgentCard(
        name="MetacogBenchmarkServer",
        description="A2A benchmark service for the metacognitive swarm.",
        url=card_url or f"http://{host}:{port}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text", "data"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=Executor(BenchmarkAgent),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    return server.build()

def main():
    parser = argparse.ArgumentParser(description="Run the A2A Metacognition Benchmark Server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8004, help="Port to bind")
    parser.add_argument("--card-url", type=str, help="URL to advertise in the agent card")
    args = parser.parse_args()

    card_url = args.card_url or os.environ.get("CARD_URL")
    app = create_app(host=args.host, port=args.port, card_url=card_url)
    logger.info(f"Benchmark Server serving on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
