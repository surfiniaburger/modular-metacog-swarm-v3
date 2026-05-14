# Fitness Function Spec (Farley-style “Done Means Done”)

This document defines **fitness functions** and **stop conditions** for the BARRED / silver-one pipeline so the project can evolve without drifting into “prompt tweaks forever”.

Core mantra:
> If it can change, it must be an input; if it’s an input, it must be recorded.

Related reading:
- Determinism principle excerpt: `docs/wissy.md`
- BARRED paper notes: `agent_training/BARRED/Barred.md`
- GEPA-first seed notes: `agent_training/silver-one/scenarios/debate/SEED_GENERATION_GUIDE.md`
- Pioneer Agent notes (iteration + rollback motifs): `docs/pioneer_agent/README.md`

---

## Definitions

**Run**: One execution of the pipeline with a specific `run_id`, seed source, model configuration, and acceptance policy.

**External effect**: Anything that can vary between runs without a code change, including:
- LLM provider calls
- network calls (including A2A calls to local/remote agents)
- tool execution (compilers, linters, static analyzers, fuzzers)
- filesystem writes outside the declared artifact set
- time/randomness unless explicitly seeded/recorded

**Artifact set** (minimum):
- `run_record.json`: immutable run configuration + hashes
- `cassette.*`: recorded external effects (LLM I/O, agent turns, tool outputs)
- `attempts.jsonl`: per-attempt log (accepted + rejected) with reasons (required for true B1)
- `training_corpus.jsonl`: accepted samples (the product)
- `metrics.json`: computed metrics used for acceptance gates (optional but recommended)

**Replay**: Re-executing a run using only the artifact set, such that the output artifacts are identical (or equivalent under a declared normalization rule).

---

## A) Determinism (Repeatability)

### Goal
Make the pipeline **repeatable** so refactors are safe, failures are diagnosable, and improvements are measurable.

### Required invariants
- All randomness is seeded (or recorded).
- All external effects are recorded to cassettes.
- Replay fails loudly on any cassette miss (“no silent fallback to live calls”).

### Fitness tests
**A1. Record → Replay Identity**
- Run once in `record` mode, then run the same `run_id` in `replay` mode.
- Output: `training_corpus.jsonl` is **byte-identical under canonical serialization** (or equivalent under a declared normalization rule).

**A2. Zero Provider Calls During Replay**
- In `replay`, any attempt to call an LLM provider or remote agent without a cassette entry is a hard failure.

**A3. Cassette Robustness**
- Cassette writes are atomic and concurrency-safe.
- A crash mid-write must not corrupt existing cassette data.

**A4. Run Record Completeness**
`run_record.json` must capture:
- effective model identifiers for each module (judge/generator/debater/GEPA/verifier)
- all generation parameters that affect outputs (temperature, top_p, max_tokens, response_format, etc.)
- seed selection inputs (seed file hash, sampling method, RNG seeds)
- code version identifiers (git commit / repo hash) and dependency locks (e.g., `uv.lock` hash + Python version)

### Stop condition (“A is done”)
A is done when:
- A1–A4 pass for ≥3 independent runs (different `run_id`s) and
- at least one run includes an intentional interruption/restart (to validate A3).

---

## B) Grounding (Truthfulness via Independent Anchors)

### Goal
Prevent “repeatable hallucination”: ensure accepted samples are grounded in the code and (when possible) corroborated by independent verification.

### Minimal Golden v0 (start here)
Before full Stage-B optimization, define a **minimal golden** bar that is strict enough to prevent drift but small enough to iterate quickly.

**Scope**:
- Curated subset first (small, high-confidence rows), then expand.
- Optimize for reliability of acceptance criteria, not volume.

**Row-level requirements (must all hold)**:
- `support_level == "supported"`.
- At least 2 normalized anchors that are verbatim substrings of input code.
- Mechanism is anchor-first and explicitly names:
  - Source anchor
  - Sink anchor
  - Missing guard/invariant anchor
- `verifier_status.called == true` and `verifier_status.parse_ok == true` for rows where verifier applies.
- `verifier_report` is present (object or explicit `"not_applicable"` only when verifier is intentionally skipped by policy).

**Run-level requirements (minimal golden gate)**:
- `b2_strict_fail_rate <= 0.20`
- `verifier_parse_ok_rate >= 0.95`
- `verifier_pass_rate >= 0.80`
- `unsupported_predicate_rate` measured from attempts is improving iteration-over-iteration (no regression), even if not yet at long-term target.

**Exit condition for Minimal Golden v0**:
- Pass the minimal gate on 2 consecutive runs with distinct `run_id`s.
- Keep at least one small smoke run (4–6 seeds) and one medium run (≈19 seeds).
- Only then move to larger runs (≈50+ seeds).

### Required new fields per accepted sample
Every accepted sample in `training_corpus.jsonl` must contain:
- `predicate`: the claim being judged
- `anchors`: concrete evidence hooks tied to the code (function/variable names, specific operations, “where to look”)
- `counterfactual`: a minimal, concrete change that would flip the verdict
- `verifier_report`: structured output from an independent verifier when applicable (or `"not_applicable"`)
- `support_level`: `"supported" | "unsupported" | "inconclusive"`

**Acceptance policy (Phase B default)**:
- `training_corpus.jsonl` contains only *accepted* samples and, by default in Phase B, acceptance requires `support_level == "supported"`.
- `attempts.jsonl` contains *all attempts* (accepted + rejected) and is the source of truth for attempt-based rates (e.g., B1).

### Fitness tests
**B1. Unsupported Predicate Rate**
- Measure: `unsupported_predicate_rate = unsupported_attempts / total_attempts` computed from `attempts.jsonl`.
- Target: below a pre-set threshold on a held-out seed set (choose threshold upfront; e.g., <20%).

**B2. Anchor Adequacy**
- For accepted samples: anchors must meet a minimum bar (e.g., ≥2 anchors, no generic statements like “memory safety issue exists”).
- Runtime-aligned variant: use strict attempt outcomes from `attempts.jsonl` (e.g., `anchors_too_few_after_normalization`, `anchors_no_match`, `mechanism_evidence_failed`) to compute `b2_strict_fail_rate`.

**B3. Judge ↔ Verifier Agreement (when verifier applies)**
- Measure: disagreement rate where verifier contradicts the judge’s mechanism/verdict.
- Target: below threshold (set upfront; e.g., <10%).
- Coverage companion metric: `verifier_called_on_prowin_rate` (denominator = pro-wins, not total attempts).

**B4. Regression Gate on Quality**
- Any pipeline change must not worsen B1–B3 versus the previous accepted dataset version.
- If it worsens, rollback (don’t compensate with “more data”).

### Stop condition (“B is done”)
B is done when:
- B1–B4 pass on a held-out seed set for **two consecutive iterations** without relaxing thresholds.

### Sequencing rule (to avoid wasted large runs)
When grounding gates are changing:
1. Run smoke (4–6 seeds) until non-zero acceptance and stable failure reasons.
2. Run medium (≈19 seeds) to validate rates.
3. Only then run large (≈50 seeds).

Do **not** run 50-seed sweeps while smoke/medium runs are still failing due to gate-definition or schema mismatches.

---

## C) Scaling (Throughput Without Quality Regression)

### Goal
Increase yield and throughput **without** regressing B-quality metrics.

### Fitness tests
**C1. Throughput**
- Samples/hour and cost/sample meet the target budget.

**C2. Diversity / Coverage**
- Coverage across targeted languages/vulnerability classes meets a declared target distribution.

**C3. Quality Stability**
- B1–B3 remain within thresholds at scale; no regression drift.

### Stop condition (“C is done”)
C is done when:
- throughput targets are met and
- B-quality thresholds hold across ≥N large runs (choose N upfront; e.g., 3–5).

---

## Rollback Rule (Non-negotiable)

If any change causes a measurable regression in the relevant stage metrics, **rollback** to the previous version and treat the regression as evidence that the change was wrong or premature.

This prevents “hallucinated progress” where teams rationalize regressions instead of learning from them.
