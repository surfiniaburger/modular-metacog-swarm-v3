# Pioneer Agent (Fastino Labs) — Working Notes

Source paper: `docs/paper.md` (arXiv:2604.09791v1, Apr 10, 2026, CC BY 4.0).

Goal of this folder: break the paper into *reusable engineering notes* that map directly onto:
- `agent_training/BARRED/Barred.md`
- `agent_training/silver-one/scenarios/debate/SEED_GENERATION_GUIDE.md`
- ART / other agentic training loops in this repo

## Index
- `docs/pioneer_agent/01_abstract_and_thesis.md`
- `docs/pioneer_agent/02_architecture.md`
- `docs/pioneer_agent/03_search_procedure.md`
- `docs/pioneer_agent/04_data_curation.md`
- `docs/pioneer_agent/05_iteration_policy.md`
- `docs/pioneer_agent/06_cold_start_mode.md`
- `docs/pioneer_agent/07_production_mode.md`
- `docs/pioneer_agent/08_structural_safeguards.md`
- `docs/pioneer_agent/09_stage_based_evaluation.md`
- `docs/pioneer_agent/10_experiments_and_results.md`
- `docs/pioneer_agent/11_emergent_strategies_and_motifs.md`
- `docs/pioneer_agent/12_cost_failure_limits.md`
- `docs/pioneer_agent/13_related_work_map.md`
- `docs/pioneer_agent/todo.md`

## How to use these notes
Treat each file as a “design constraint capture”:
- Keep the *why* (what problem the section solves).
- Extract the *operational rule* (what to do in code).
- Record the *stop condition* (when to stop iterating to avoid drift/hallucination).

