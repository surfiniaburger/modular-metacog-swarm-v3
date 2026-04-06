# Swarm Golden Run Post-Mortem & Log Sweep

*(Raw logs preserved in `after_logs.md`.)*

## Executive Summary
This run captured a **single‑turn benchmark refinement loop** (Iterations 1–15). The swarm successfully booted, enforced identity, and executed periodic A2A benchmarks. The dominant failure mode was **critic output instability** (non‑JSON or timed‑out responses), which stalled patch acceptance for most iterations. Methodologically, several strategies **conflated paradox handling with calibration**, which conflicts with **Fleming & Lau (2014)** and undermines meta‑d′ measurement. This maps directly to **PHASE_3_PLAN.md**: Phase 3 should evaluate **single‑turn reliability** and **process‑level behavior**, not multi‑turn recursion embedded in a single prompt.

## Run Configuration Snapshot
- Models: `qwen3.5:9b` (Brain/Critic), `qwen2.5-coder:3b` (Hands)
- Identity: Planner / Executor / Auditor via sovereign handshake
- Discovery blindness: enforced via identity context
- A2A benchmarks scheduled: Iterations 3, 6, 9, 12, 15
- Summary script: `tools/benchmark_summary.py` returned “Signal Quality: muffled”

---

## What Went As Planned
The sovereign identity boot worked. All three guards handshake successfully and the system stripped unauthorized tools. TheBrain produced coherent three‑level strategy trees (STATIC, RECURSIVE, COGNITIVE_STRESS). A2A benchmarks were actually executed at Iterations 3, 6, 9, 12, and 15, confirming the orchestration loop is functional. When the Critic returned valid JSON (notably Iterations 5 and 15), the critiques were methodologically sound and aligned with the research goal.

---

## What Did Not Go As Planned
**Critic output collapse:** Iterations 3, 4, 7, 10, 12, 13 returned no valid JSON from the Critic. Iteration 14 produced a long meta‑commentary instead of JSON. The mediator then auto‑rejected the patch. This is likely a context‑length failure or prompt‑grounding failure.

**Ollama timeouts:** Iteration 5 produced multiple 600s timeouts before finally returning a verdict. This adds instability and stalls the run.

**Methodology drift:** Several iterations inserted “reflection on previous conclusion” in a single‑turn setup without programmatic context injection. This violates the single‑turn intent and makes the task ill‑posed.

**Signal quality degraded:** The summary reported Mean DGS 1.4093, CV 0.7802, “Signal Quality: muffled,” and a model mismatch warning (expected `qwen2.5-coder:7b`, found `qwen2.5-coder:3b`). This makes the results noisy and not comparable to the multi‑turn report.

---

## Iteration-Level Highlights
- **Iteration 1:** Rejected because recursive reflection required context injection not provided by the benchmark.
- **Iteration 2:** Rejected on procedural grounds (“new tree required”), indicating prompt governance drift.
- **Iterations 3–4:** Critic output invalid or empty; auto‑reject.
- **Iteration 5:** Approved after timeouts; critic demanded stricter grounding.
- **Iteration 6:** Approved with verbose analysis and “RESEARCH_APPROVAL” payload.
- **Iterations 8–9:** Critic rejected paradox‑heavy strategies as semantic traps.
- **Iterations 10–13:** Repeated critic JSON failures; auto‑reject.
- **Iteration 15:** Rejected because the patch conflated multiple metacognitive tasks into one trial, citing Fleming & Lau constraints.

---

## Mapping to `flem.md` (Fleming & Lau, 2014)
Fleming & Lau emphasize that **metacognitive sensitivity** (meta‑d′/d′) requires a stable **Type‑1 signal**. Paradox prompts (e.g., Liar) make correctness undefined, collapsing Type‑1 d′ and corrupting meta‑d′. This explains the “muffled” DGS and the critic’s Iteration‑15 rejection.

Implication for Phase‑3: use **clear correctness tasks** as the Type‑1 signal and measure Type‑2 confidence separately. Paradox tasks should be stressors, not core metrics.

---

## Mapping to `kag.md` (DeepMind Cognitive Taxonomy)
The taxonomy separates **Reasoning** and **Metacognition** as distinct faculties. The run repeatedly required both at once (logic conflict resolution plus calibration). This conflation makes it impossible to attribute observed failure to one faculty or the other.

Implication for Phase‑3: isolate metacognitive monitoring (confidence reliability) from reasoning conflict tasks.

---

## Single‑Turn Run vs Multi‑Turn Report
- **This run:** single‑turn prompt refinement and evaluation of one schema at a time. No Turn‑2 evidence injection.
- **Main report:** true multi‑turn evidence injection and M‑Ratio shift dynamics.

Therefore: use single‑turn logs to design calibration probes; use multi‑turn results to claim dynamic belief updating and resilience.

---

## Alignment with `PHASE_3_PLAN.md`
Phase‑3 is the **single‑turn reliability** track. The logs show repeated attempts to embed multi‑turn reflection inside single prompts, which is the wrong target. The recursive element should live in the Mediator’s process, not inside the prompt itself.

---

## Recommended Next Steps
- Stabilize Critic output by enforcing strict JSON or shortening the critic prompt.
- Fix model mismatch to align `BENCH_MODEL_STRONG/WEAK` with actual runtime models.
- Re‑scope single‑turn benchmarks to use clear correctness tasks + confidence report.
- Keep paradox prompts as optional stressors, not the core signal.
- Treat multi‑turn outcomes as separate from single‑turn diagnostics.

---

## Bottom Line
The swarm infrastructure worked. The primary blockers were **critic JSON instability** and **methodology drift** from single‑turn design into multi‑turn prompt logic. The path forward is clean Type‑1 tasks with separate confidence, aligned with Fleming & Lau and the DeepMind taxonomy, then Phase‑3 evaluation for single‑turn reliability.
