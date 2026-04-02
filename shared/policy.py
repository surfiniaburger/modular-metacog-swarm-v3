# shared/policy.py
import os
from typing import List, Dict

class ResearchPolicy:
    """
    Research Invariants for the Gen-2 Swarm.
    Ported from med_safety_gym's pure function patterns.
    """
    @staticmethod
    def check_model_allowed(model: str, allowed_prefixes: List[str] = ["ollama/"]) -> bool:
        return any(model.startswith(p) for p in allowed_prefixes)

    @staticmethod
    def check_sandbox_path(path: str, sandbox_root: str) -> bool:
        real_path = os.path.realpath(path)
        real_root = os.path.realpath(sandbox_root)
        try:
            return os.path.commonpath([real_root, real_path]) == real_root
        except:
            return False

    @staticmethod
    def check_node_restricted(node_name: str, allowed_nodes: List[str] = ["benchmark_metacognition"]) -> bool:
        return node_name in allowed_nodes
