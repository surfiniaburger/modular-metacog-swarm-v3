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
- Output: `training_corpus.jsonl` is **byte-identical**.

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
- code version identifiers (git commit / repo hash) and dependency locks when available

### Stop condition (“A is done”)
A is done when:
- A1–A4 pass for ≥3 independent runs (different `run_id`s) and
- at least one run includes an intentional interruption/restart (to validate A3).

---

## B) Grounding (Truthfulness via Independent Anchors)

### Goal
Prevent “repeatable hallucination”: ensure accepted samples are grounded in the code and (when possible) corroborated by independent verification.

### Required new fields per accepted sample
Every accepted sample in `training_corpus.jsonl` must contain:
- `predicate`: the claim being judged
- `anchors`: concrete evidence hooks tied to the code (function/variable names, specific operations, “where to look”)
- `counterfactual`: a minimal, concrete change that would flip the verdict
- `verifier_report`: structured output from an independent verifier when applicable (or `"not_applicable"`)
- `support_level`: `"supported" | "unsupported" | "inconclusive"`

### Fitness tests
**B1. Unsupported Predicate Rate**
- Measure: `unsupported_predicate_rate = unsupported / total_attempts`.
- Target: below a pre-set threshold on a held-out seed set (choose threshold upfront; e.g., <20%).

**B2. Anchor Adequacy**
- For accepted samples: anchors must meet a minimum bar (e.g., ≥2 anchors, no generic statements like “memory safety issue exists”).

**B3. Judge ↔ Verifier Agreement (when verifier applies)**
- Measure: disagreement rate where verifier contradicts the judge’s mechanism/verdict.
- Target: below threshold (set upfront; e.g., <10%).

**B4. Regression Gate on Quality**
- Any pipeline change must not worsen B1–B3 versus the previous accepted dataset version.
- If it worsens, rollback (don’t compensate with “more data”).

### Stop condition (“B is done”)
B is done when:
- B1–B4 pass on a held-out seed set for **two consecutive iterations** without relaxing thresholds.

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
