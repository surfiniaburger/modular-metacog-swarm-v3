# Phase 3 Gaps (Snapshot)

This note captures the current gaps and open questions before moving work to `modular-metacog-swarm-v3`.

## Benchmark Validity Gaps
- **Multi‑turn diversity**: question pool expanded to 36 items, but still repeats at N=150 (~4–5x). Consider expanding to 50–60 items or lowering N.
- **Confidence expressiveness**: some models collapse to a single bin (type‑2 AUC = 0.5). Consider bin‑diversity checks or explicit constraints.
- **Class balance**: evidence polarity and strength are randomized; consider fixed ratios per run for tighter comparisons.
- **Class‑specific meta‑d′**: positive class can hit acc=1.0, making type‑2 metrics degenerate. Consider resampling or adding hard positives.

## Measurement Gaps
- **Multi‑seed in Kaggle**: keep single‑seed for leaderboard determinism; use multi‑seed locally for CI and stability checks.
- **Composite score**: currently Bayesian resilience is the only returned score; Fleming/Lau metrics are diagnostics. Decide if composite should ever be exposed.
- **Reporting standard**: need consistent log summary block for all runs (accuracy, ECE, Brier, type‑2 AUC, meta‑d′, m‑ratio, bin usage).

## Engineering Gaps
- **Kaggle portability**: maintain a self‑contained notebook with no git dependency; ensure deterministic imports and seed control.
- **Run scripts vs Kaggle parity**: keep prompt and confidence bin instruction synchronized across local and Kaggle.
- **Results hygiene**: decide on a minimal set of files to keep/publish to avoid log bloat.

## Research Gaps
- **Grounding to flem.md**: ensure the multi‑turn design still respects independent‑trial assumptions (isolated chat per item).
- **Grounding to kag.md**: articulate why this benchmark reveals signal beyond accuracy, especially for high‑accuracy SOTA models.
- **Faculty isolation**: ensure multi‑turn task is metacognition (monitoring/control) and not drifting into learning/strategy‑adaptation.

## Phase 3 Focus (Proposed)
- Increase item diversity and add a controlled difficulty ladder.
- Add bin‑diversity metric and warn/penalize flat confidence.
- Add local multi‑seed evaluation to produce CI for stability claims.
- Prepare clean Kaggle submission path + writeup narrative.
