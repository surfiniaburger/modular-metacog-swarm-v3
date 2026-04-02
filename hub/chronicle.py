# hub/chronicle.py
import json
import logging
import os
from datetime import datetime

class ResearchChronicle:
    """
    Structured logging for Gen-2 research iterations.
    Ported from the Gen-1 run.log but optimized for modular event streams.
    """
    def __init__(self, log_path: str = "research_env/docs/research_chronicle.md"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_iteration(self, iteration: int, strategy: str, result: float):
        entry = f"""
## Iteration {iteration} - {datetime.utcnow().isoformat()}
- **Strategy**: {strategy}
- **Discriminatory Gap**: {result}
- **Status**: SUCCESS
---
"""
        with open(self.log_path, "a") as f:
            f.write(entry)
