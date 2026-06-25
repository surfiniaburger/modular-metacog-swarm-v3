# 1) Abstract + thesis (why Pioneer exists)

## What problem the paper claims matters
Pioneer’s core claim is that adapting small models is mostly an **engineering loop**, not “just training”:
- decide what data to collect/curate
- diagnose failures
- avoid regressions
- decide when to stop iterating

## Why this matters for BARRED / silver-one
BARRED already has the “generate → verify → refine” loop, but Pioneer adds two strong production-grade ideas:
- **Regression gating**: accept updates only if they fix targeted failures *without breaking previously-correct behavior*.
- **Provenance logging**: a persistent log that survives context loss and captures dataset lineage and decisions.

## Operational takeaway for this repo
When you build B (grounding) and later C (scaling), treat “acceptance” as a *deployment decision*:
- store the evidence (trace/cassette + run record)
- define a regression set (what you refuse to break)
- stop early when marginal data changes risk regressions

