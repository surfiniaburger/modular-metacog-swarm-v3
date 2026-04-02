# ARC‑AGI‑3 Integration Plan (Single‑Page)

## Objective
Wrap the existing **faculty‑based stack** (metacognition now, perception next) into an **interactive agent loop** compatible with ARC‑AGI‑3’s evaluation harness. This allows us to use our diagnostic benchmarks to guide improvements while competing on the interactive benchmark.

## Why This Fits
ARC‑AGI‑3 evaluates **interactive reasoning efficiency** (actions vs human baseline). Our stack can be mapped to the required agent loop: **perceive → plan → act → learn**, with **metacognitive calibration** guiding exploration.

## Minimal Agent Loop (Phase 1)
1. **Perceive:** parse environment observation into a structured state.
2. **Attention:** filter salient features (optional at first).
3. **Executive Functions:** generate a short action plan.
4. **Metacognition:** calibrate confidence and decide when to explore vs exploit.
5. **Act:** execute an action.
6. **Learn/Memory:** update state and store discovered rules.

## Faculty → ARC‑AGI‑3 Mapping
- **Perception:** environment parsing and state abstraction
- **Attention:** salience selection / cue extraction
- **Learning:** update rules from state transitions
- **Memory:** store discovered rules & partial maps
- **Executive Functions:** plan multi‑step action sequences
- **Metacognition:** confidence‑based exploration control
- **Social Cognition:** optional (only if multi‑agent tasks appear)

## Deliverables (Phase 1–2)
- `arc_agi3_agent.py`: minimal agent loop using the current stack
- `arc_agi3_adapter.py`: interface glue to ARC‑AGI‑3 harness
- `arc_agi3_run.md`: run instructions + reproducibility settings
- `REPORT_ARC_AGI3.md`: results snapshot, efficiency notes, failure modes

## Metrics to Track
**Primary:** ARC‑AGI‑3 completion + action efficiency  
**Secondary:** internal diagnostics (ECE, meta‑d′, DGS) for each run

## Integration Steps
1. **Build a thin adapter** to call our stack in ARC‑AGI‑3’s agent loop.
2. **Reuse metacog diagnostics** to decide exploration rate.
3. **Add perception module** (from `PERCEPTION_BENCHMARK_PLAN.md`) when stable.
4. **Run a pilot** on a small environment subset to validate loop.

## Risk Controls
- Avoid overfitting to specific environments.
- Keep a separate diagnostics suite (our benchmarks) to guard against regressions.
- Log action traces for post‑hoc analysis.

## Next Step (If Approved)
Create the minimal agent wrapper and adapter skeletons, then run a pilot on a small ARC‑AGI‑3 subset.
