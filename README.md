# Modular Metacognitive Swarm (Gen-2)

This repository implements a **Sovereign Agent** and **Stateless Executor** architecture for AGI research, inspired by `med-safety-gym` and `safeclaw`.

## Architecture
- **Agent/Mediator**: Cognitive strategy and paradoxical intent.
- **Executor (MCP)**: Tool-based benchmark patching and execution.
- **Hub**: Structured observability and session persistence.

## Setup Instructions

1.  **Create Environment**:
    ```bash
    uv venv
    source .venv/bin/python  # Or path to your python
    uv pip install -e .
    ```

2.  **Initialize Sandbox**:
    ```bash
    mkdir -p research_env/docs
    cd research_env
    uv venv
    uv pip install google-adk  # CRITICAL: Pre-install ADK in the sandbox
    ```

3.  **Run the Modular Flow**:
    - Start the Hub: `python hub/app.py`
    - Start the Executor: `python executor/mcp_server.py`
    - Run the Mediator logic (to be implemented).

## Benchmark & Summary

### Quick Run (A2A benchmark + summaries)
```bash
./reset_golden_run.sh
```

This launches:
- Hub (8000)
- MCP executor (stdio)
- A2A Benchmark server (8004)
- Mediator loop

### Validate A2A Benchmark (smoke test)
```bash
A2A_BENCH_URL=http://localhost:8004 uv run python tools/a2a_smoke_test.py
```

### Generate Summary + Plot
```bash
BENCH_MIN_ITERATION=2 uv run python tools/benchmark_summary.py
```

Outputs:
- `research_env/results/summary.json`
- `research_env/results/summary.txt`
- `research_env/results/summary.png` (if matplotlib is installed)

### Key Environment Variables
- `RUN_ITERATIONS`: total swarm iterations (default 10/15 depending on script)
- `BENCH_EVERY_N`: run benchmark every N iterations (default 3)
- `BENCH_NUM_TASKS`: tasks per benchmark run (default 10)
- `BENCH_MIN_ITERATION`: ignore early iterations in summary (default 2)
- `BENCH_LOG_FULL`: include full task logs (0/1)
- `USE_LITELLM`: route benchmark through LiteLLM (0/1)
- `BENCH_PER_MODEL_MAX_SECONDS`: timebox per model (seconds)
- `BENCH_CONF_BINS`: confidence bins for meta-d′ (default 4)
- `BENCH_BOOTSTRAP`: bootstrap samples for meta-d′ CI (default 200)
- `BENCH_TRAP_BOOST`: increase adversarial share (0/1, default 0)
- `BENCH_ADVERSARIAL_SHARE`: manual adversarial share (0–1, default 0.25)

## Key Improvements over Gen-1
- **No AST Hardcoding**: Patching is a delegated tool, not a coordinator duty.
- **Dependency Isolation**: The Hub, Agent, and Executor can have separate environments.
- **Standardized ADK**: Uses native ADK `Agent` classes for all cognitive steps.

## References
This project is grounded in established cognitive science and multi-agent systems research:

- **Metacognitive Efficiency (M-Ratio)**: 
  - Fleming, S. M., & Lau, H. C. (2014). "How to measure metacognition". *Frontiers in Human Neuroscience*. [DOI: 10.3389/fnhum.2014.00443](https://doi.org/10.3389/fnhum.2014.00443)
  - Key concept utilized: `meta-d' / d'` for signal-sharpening in LLM benchmarking.

- **DeepMind AGI Cognitive Framework**:
  - Burnell, R., et al. (2026). "Measuring Progress Toward AGI: A Cognitive Framework". *Google DeepMind Technical Report*.
  - This swarm implements the **Metacognition** and **Executive Function** faculties defined in the Burnell et al. Cognitive Taxonomy to quantify the "Discriminatory Gap" between local models.

- **Project Metadata**: See [chandra_packet.json](research_env/docs/chandra_packet.json) for specific signal-sharpening heuristics.

## V2 Roadmap (Meta-d′)
This repo is the V2 branch for extending the benchmark to true **meta-d′**:
- Confidence binning + type‑2 ROC
- meta‑d′ / d′ (M‑ratio) estimation
- Multi‑turn micro‑drills and diverse calibration traps
- Human baseline slice and calibration plots

See `V2_PLAN.md` for full details.

**Note on meta‑d′ implementation:** The current V2 pipeline uses a **type‑2 ROC AUC → meta‑d′ approximation** for stability at small sample sizes. It is explicitly reported as an approximation (not a full MLE meta‑d′ fit) and accompanied by bootstrap CIs.
