# V2 Tasks (First Milestone)

## Goal
Implement true meta-d′ + stable multi‑turn probes without destabilizing the baseline signal.

## Tasks
1. **Confidence Binning**
   - Decide bin scheme (4‑bin or 6‑bin).
   - Update prompt format to enforce bin output.
   - Add parsing/validation.

2. **Type‑2 ROC + meta‑d′**
   - Implement type‑2 hit/false alarm rates.
   - Add meta‑d′ estimation (Maniscalco & Lau method).
   - Add bootstrap confidence intervals.

3. **Difficulty Stratification**
   - Label tasks by difficulty.
   - Ensure balanced bins for SDT fitting.

4. **Multi‑turn Micro‑drills**
   - Add 3‑turn probes for drift + confidence stability.
   - Keep single‑turn baseline intact.

5. **Human Baseline Slice (Optional in v2‑m1)**
   - Define a small task subset.
   - Draft lightweight collection workflow.

6. **Plots & Reports**
   - Reliability diagram
   - meta‑d′ vs d′ scatter
   - DGS trend by iteration

## Deliverables
- `benchmark_meta_d.py`
- `tasks_v2.jsonl`
- `summary_v2.json`
- `REPORT_V2.md`

