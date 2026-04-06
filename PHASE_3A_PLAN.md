# Phase 3A Plan — Single-Turn Stabilization (Metacog Baseline)

## Goal
Stabilize a **single‑turn metacognitive baseline** with clear Type‑1 ground truth and clean Type‑2 confidence signals. Phase 3A is the foundation required before moving to Bayesian‑N multi‑turn evaluation.

## Why Phase 3A First
Multi‑turn Bayesian‑N only makes sense if the single‑turn signal is stable. If Type‑1 correctness is noisy or undefined, any Turn‑2 update will be ambiguous and the M‑Ratio delta will be untrustworthy. Phase 3A therefore focuses on:
- Clear correctness
- Clean confidence capture
- Minimal prompt ambiguity

---

## Scope & Constraints
- **Single‑turn only**: no simulated “previous turn” or reflection prompts.
- **Objective ground truth** required for every item.
- **Confidence required** for every response.
- **No paradox‑only baselines** (paradox tasks are allowed only as optional stressors).

---

## Core Deliverables
1. **Stable Type‑1 Task Suite (v1)**
   - 3–5 task families with objective correctness.
   - Examples: syllogisms, numeric reasoning, counterfactual checks, constrained factual checks.

2. **Response Schema Enforcement**
   - Every model response must include:
     - `answer` (Type‑1)
     - `confidence` (Type‑2)

3. **Baseline Metrics**
   - Accuracy
   - ECE / Brier
   - Type‑2 AUC
   - M‑Ratio (meta‑d′ / d′)

4. **Calibration Curve**
   - Confidence bins from the Type‑2 signal.
   - Reliability diagram for the baseline.

---

## Phased Steps

### Step 1 — Task Selection (Week 1)
Select a minimal objective task set:
- **Logic / syllogism** (formal validity)
- **Quantitative micro‑problems** (small arithmetic, ratio, probability)
- **Counterfactual reasoning** (if‑then with fixed outcomes)

**Acceptance:** every task has a deterministic correct answer.

### Step 2 — Schema Lock (Week 1)
Define and enforce the response format for all benchmarks:
```json
{
  "answer": "A|B|C",
  "confidence": 0-100
}
```
**Acceptance:** benchmark parser rejects any output without both fields.

### Step 3 — Baseline Run (Week 2)
Run the task suite across the target model set.
Collect:
- accuracy
- calibration stats
- M‑Ratio
- reliability bins

**Acceptance:** low variance across re‑runs; clean reliability curve.

### Step 4 — Review & Fix (Week 2)
Inspect failure modes:
- prompt ambiguity
- confidence collapse (always high/always low)
- schema drift

Adjust prompts or task composition until stable.

---

## Exit Criteria (Phase 3A Complete)
- Type‑1 correctness stable (variance below threshold).
- Confidence calibration yields consistent bins.
- M‑Ratio computed without undefined d′.
- No paradox tasks in baseline.

---

## Transition to Phase 3B (Multi‑Turn Bayesian‑N)
Once Phase 3A is stable:
- Introduce evidence injection in Turn‑2.
- Measure update behavior relative to baseline.
- Track M‑Ratio shift as the primary dynamic metric.

---

## Notes
- This is a **baseline stabilization phase**. Publication‑grade multi‑turn claims should wait until these criteria are satisfied.
- Paradox tasks remain valuable as **stressors**, but only after baseline is stable.
