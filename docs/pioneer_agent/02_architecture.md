# 2.1) Architecture (agents, tools, and provenance)

## What Pioneer’s architecture emphasizes
- Orchestrator LLM drives a state machine (LangGraph).
- Runs inside isolated containers with tool access.
- Uses sub-agents for heavy analysis and parallel work.
- Maintains a durable on-disk log (“data-curation.md”) for lineage.

## Mapping to this repo
- Your A-work (determinism) is analogous to Pioneer’s “durable provenance”.
- For B (grounding), the “isolated container with tools” maps well to `agent_training/OpenEnv` (environment boundary).
- For C (scaling), sub-agents/parallelism correspond to running multiple seed pipelines concurrently — but only once B’s verification is reliable.

## Design constraints you can steal
- **Single orchestrator owns acceptance.** Side modules propose; the orchestrator decides and records.
- **Durable run artifacts.** Every run emits a run record + cassette + outputs.
- **Context-loss resilience.** The system must be able to reload its own decisions from disk.

