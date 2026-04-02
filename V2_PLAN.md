# V2 Plan: Metacognitive Benchmarking Toward meta-d′

## Goals
- Extend the current stable calibration benchmark into a **true meta-d′ (meta-d prime)** pipeline.
- Add **multi-turn probes** and **diverse calibration traps** without breaking signal stability.
- Produce **human baseline slices** and **calibration plots** (ECE curves, reliability diagrams).
- Preserve reproducibility and low-latency execution.

## Why meta-d′ (vs proxy)
Current V1 uses calibration proxies (ECE/Brier + confidence-weighted accuracy). True meta-d′ requires:
- **Type-2 SDT modeling** over confidence bins
- **Difficulty stratification** (easy/medium/hard)
- **Type-2 ROC** estimation for confidence judgments
- Computing **meta-d′ / d′** (M-ratio)

## Workstreams

### 1) Task Design (Calibration Traps)
- Add **non-logical domains** (ambiguity, commonsense uncertainty, noisy perceptual judgments).
- Introduce **confidence inversion traps** (easy-looking but incorrect).
- Add **multi-turn micro-drills** (3–5 turn) that stress confidence drift.
- Ensure balanced difficulty bins for SDT fitting.

### 2) meta-d′ Pipeline
- Implement confidence **bins** (e.g., 1–4 or 1–6 scale).
- Collect per-bin **type-2 hit/false alarm rates**.
- Fit meta-d′ using established SDT estimation (Maniscalco & Lau).
- Report M-ratio with error bars and bootstrap confidence intervals.

### 3) Human Baseline Slice
- Collect a small human sample (20–50 participants).
- Use the exact same tasks, same confidence bins.
- Compare model distributions to human distribution percentiles.

### 4) Metrics & Visualization
- Reliability diagram (calibration curve)
- ECE and Brier
- meta-d′ vs d′ scatter plot
- DGS trend across runs

### 5) Latency + Scheduling
- Keep benchmark **A2A-decoupled** (as in v1).
- Add **job queue** for benchmarks to avoid GPU contention.
- Introduce **adaptive cadence** (run benchmarks every N iterations or on demand).

## Deliverables
- `benchmark_meta_d.py` with SDT fitting
- `tasks_v2.jsonl` (difficulty-labeled)
- `human_baseline.csv`
- `summary_v2.json` + plots
- `REPORT_V2.md`

## Milestones
1. **Week 1:** task set expansion + confidence binning
2. **Week 2:** meta-d′ implementation + unit tests
3. **Week 3:** human baseline + calibration plots
4. **Week 4:** final report + benchmark packaging

## Risks
- Too few samples per bin → unstable meta-d′
- Multi-turn drift adds noise → must keep single-turn baseline stable
- Latency: mitigate with queue + batch execution

## Success Criteria
- meta-d′ computation stable across 5 runs
- M-ratio variance < 0.2 across runs
- Clear separation between 9B vs 7B (DGS + M-ratio)
- Human baseline percentile placement computed

