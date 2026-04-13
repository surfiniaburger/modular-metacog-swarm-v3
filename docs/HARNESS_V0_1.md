# Harness v0.1 — Deterministic, Sovereign, Compiled

**Purpose:** Define a minimal but moat‑grade agent harness for metacognitive evaluation. This spec merges SafeClaw invariants, Dave Farley’s determinism, and Karpathy/Wissy’s compiled‑wiki pattern.

---

## 1) Design Goals
- **Determinism by design**: reproducible runs, predictable outputs.
- **Sovereign governance**: identity, delegation, auditability (SafeClaw).
- **Context stability**: no history bloat; prompt stays small and consistent.
- **Data compounding**: outputs accumulate into a persistent knowledge base.
- **Metacog signal isolation**: clear Type‑1 correctness + Type‑2 confidence.

---

## 2) Core Architectural Principle
**Deterministic Core + Imperative Shell**

- **Core**: Pure logic functions. Input state → decisions → effects.
- **Shell**: Executes effects (LLM calls, file writes, tool calls). No logic.

This ensures tests can validate the core without touching LLMs or the filesystem.

---

## 3) Compilation Model (Karpathy/Wissy)
The harness treats **markdown files as the single source of truth**. No raw chat history is reused.

### Filesystem Layout
```
raw/              # raw logs and model outputs (never in prompt)
wiki/
  index.md        # summary of what exists
  strategy.md     # current strategy tree (single-turn)
  results.md      # latest metrics summary
  diagnostics.md  # failure modes + critic notes
  log.md          # append-only run log
```

### Cycle
1. **Read**: load compact `wiki/*.md` (small, deterministic context)
2. **LLM step**: generate/update strategy or verdict
3. **Write**: update wiki + append logs
4. **Discard chat history**

---

## 4) SafeClaw Compliance Layer
- **Identity**: agent_id + delegation tokens
- **Manifest scoping**: tool discovery blindness enforced
- **Audit logs**: every run written to chronicle
- **Zero‑Injection**: no secrets or tokens in LLM context

---

## 5) Metacog Evaluation Protocol (Phase 3A)
- **Single‑turn only**
- **Type‑1 objective correctness required**
- **Type‑2 confidence always required**
- **Strict output schema**

Schema (required):
```json
{ "answer": "A|B|C", "confidence": 0-100 }
```

---

## 6) Harness Modules (v0.1)

### A. Orchestration Loop
- deterministic, stateless per iteration
- reads compiled wiki state
- writes updated wiki state

### B. Context Builder
- only includes: `index.md`, `strategy.md`, `results.md`, `diagnostics.md`
- excludes raw logs

### C. Output Parser
- strict JSON extraction (last valid object)
- schema enforcement
- reject non‑compliant output

### D. Verification Loop
- rule‑based checks before approving strategy
- optional LLM‑as‑judge, but only as a separate module

---

## 7) Determinism Invariants
- **No direct time calls** in the core (inject Clock)
- **No random seeds** in core without explicit config
- **File iteration order is sorted**
- **Prompt content deterministic** per iteration

---

## 8) Harness Thickness (Intentional)
The harness is **thicker than ADK** in Phase‑3A to maximize reproducibility. The model handles creative generation, but the harness enforces:
- structure
- schema
- state continuity
- evaluation rules

As models improve, harness thickness can be reduced.

---

## 9) Moat Justification
This harness produces **proprietary metacognitive datasets**:
- stable M‑Ratio snapshots
- confidence calibration curves
- evidence‑sensitivity curves (Phase 3B)

These outputs are **not replicable within 12 months** by commodity platforms without your protocol and dataset.

---

## 10) Phase 3B Compatibility
The same harness core will support multi‑turn Bayesian‑N by:
- injecting evidence into `strategy.md`
- recording confidence deltas in `results.md`
- expanding diagnostics with shift curves

---

## 11) Exit Criteria for v0.1
- JSON schema enforced in every run
- Critic outputs always parseable
- Type‑1 and Type‑2 signals isolated
- Single‑turn runs reproducible

---

**Status:** Draft v0.1
