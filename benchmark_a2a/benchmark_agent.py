"""
Benchmark Agent for A2A: runs the local metacognition benchmark and returns results.
"""
import json
import logging
import os
import sys
from typing import Optional
from pydantic import BaseModel

from a2a.server.tasks import TaskUpdater
from a2a.types import Message, TaskState, Part, TextPart, DataPart
from a2a.utils import get_message_text, new_agent_text_message

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from research_env.benchmark import run_benchmark, save_results

logger = logging.getLogger(__name__)

class BenchmarkRequest(BaseModel):
    num_tasks: int = 40
    seed: int = 42
    full_log: bool = False
    iteration: Optional[int] = None

class BenchmarkAgent:
    async def run(self, message: Message, updater: TaskUpdater) -> None:
        input_text = get_message_text(message)
        try:
            request = BenchmarkRequest.model_validate_json(input_text)
        except Exception as e:
            await updater.reject(new_agent_text_message(f"Invalid BenchmarkRequest: {e}"))
            return

        await updater.update_status(
            TaskState.working,
            new_agent_text_message("Benchmark running...")
        )

        results = run_benchmark(
            num_tasks=request.num_tasks,
            seed=request.seed,
            full_log=request.full_log
        )
        save_results(results, iteration=request.iteration, write_latest=True)

        await updater.add_artifact(
            parts=[
                Part(root=TextPart(kind="text", text=f"Benchmark Complete. DGS: {results.get('dgs')}")),
                Part(root=DataPart(kind="data", data=results)),
            ],
            name="Benchmark Results"
        )
        await updater.complete(new_agent_text_message("Benchmark finished successfully."))
