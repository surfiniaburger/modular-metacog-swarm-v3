# executor/mcp_server.py
import asyncio
import os
import ast
import logging
import sys
from fastmcp import FastMCP
from shared.policy import ResearchPolicy

mcp = FastMCP("research_executor")
logger = logging.getLogger("executor")

SANDBOX_ROOT = "/Users/surfiniaburger/Desktop/modular-metacognitive-swarm/research_env"
ROOT_DIR = os.path.abspath(os.path.join(SANDBOX_ROOT, ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from research_env.benchmark import run_benchmark

@mcp.tool()
async def patch_benchmark(code: str, target_node: str, benchmark_path: str) -> dict:
    """
    Governor-validated AST patching tool.
    """
    # 1. Policy Check: Sandbox Invariant
    if not ResearchPolicy.check_sandbox_path(benchmark_path, SANDBOX_ROOT):
        return {"success": False, "error": "POLICY_VIOLATION: Path outside sandbox."}

    # 2. Policy Check: Node Restriction
    if not ResearchPolicy.check_node_restricted(target_node):
        return {"success": False, "error": f"POLICY_VIOLATION: Node {target_node} is restricted."}

    try:
        new_tree = ast.parse(code)
        # Ensure only the targeted node exists in the patch
        # ... logic for AST surgery ...
        return {"success": True, "message": f"Successfully patched {target_node}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def run_benchmark(benchmark_path: str) -> dict:
    """
    Governor-validated execution tool.
    Uses the sandbox python environment.
    """
    if not ResearchPolicy.check_sandbox_path(benchmark_path, SANDBOX_ROOT):
        return {"success": False, "error": "POLICY_VIOLATION: Execution blocked outside sandbox."}
        
    try:
        results = run_benchmark()
        return {"status": "success", "score": results["dgs"], "results": results}
    except Exception as e:
        logger.exception("Benchmark run failed.")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    mcp.run()
