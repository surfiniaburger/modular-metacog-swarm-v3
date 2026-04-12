# Implement Deterministic Core & Imperative Shell for Mediator

Refactor `agent/mediator.py` to align with modern software engineering principles of determinism as advocated by Dave Farley. This transition transforms the mediator from an imperative script into a robust system with a clear separation between "what decides" and "what acts."

## User Review Required

> [!IMPORTANT]
> This refactor introduces a `Clock` abstraction. All time-dependent logic will now be deterministic if a mock clock is provided in tests.

> [!WARNING]
> The internal structure of `ResearchMediator._run_async_impl` will change significantly. While the user-facing behavior (output events) remains the same, the data flow will be more structured (State -> Core -> Effects -> Shell).

## Proposed Changes

### [agent] (file:///Users/surfiniaburger/Desktop/modular-metacog-swarm-v3/agent)

#### [MODIFY] [mediator.py](file:///Users/surfiniaburger/Desktop/modular-metacog-swarm-v3/agent/mediator.py)

1.  **Introduce `Clock` Abstraction**:
    *   Add a simple `Clock` interface/protocol.
    *   Implement `SystemClock` (using `datetime.utcnow()`).
    *   Inject `self.clock` into `ResearchMediator`.

2.  **Define Research State & Effects**:
    *   Define `ResearchState` (typed dictionary or Pydantic model) to track mission, history, iteration, and outputs.
    *   Define `MediatorEffect` (base class for `SaveToVault`, `RunBenchmark`, `AcknowledgeResult`).

3.  **Split Decider from Actor**:
    *   Create a "Core" method (e.g., `_orchestrate_step`) that purely decides the next move based on current state.
    *   The `_run_async_impl` will act as the "Imperative Shell," executing the agents and performing the resulting effects.

4.  **Refactor I/O**:
    *   Move direct file reads/writes from `_persist_results` and `_prepare_contextual_packets` into a "FileSystem" or "ContextManager" abstraction (or just leave them in the Shell methods to keep it simple but separated from the core logic).

## Open Questions

- Should we also abstract the `run_benchmark` tool call into the Effect system? (Proposed: Yes, for full determinism).
- Do you want a `test_mediator_deterministic.py` to verify this behavior?

## Verification Plan

### Automated Tests
- Run internal diagnostics to ensure sub-agent prompts are still correctly formatted.
- Ensure `Mediator` still correctly handles `APPROVE`/`REJECT` verdicts.

### Manual Verification
- Observe a full loop of the swarm to ensure it still correctly reaches the Benchmark phase and persists to the Vault.
- Verify that timestamps in the Vault registry are still correct (relative to the injected clock).

---

# Dave Farley Audit: Determinism & Separation of Concerns

This audit evaluates the `modular-metacog-swarm-v3` codebase against the engineering principles of **Determinism** ("It works everywhere, every time") and **Separation of Concerns** ("Separate what decides from what acts").

## Executive Summary

The codebase currently functions as a collection of **Imperative Scripts**. While logically sound, it suffers from "Temporal Coupling" and "Environment Entanglement." The primary "Scape Goat" is `agent/mediator.py`, which is already slated for refactoring. Other key areas—specifically the Benchmark harness and the Identity Hub—require similar decouplings to reach "State of the Art" engineering quality.

---

## 1. Determinism Violations

### 1.1 Temporal Nondeterminism (The "Clock" Problem)
Almost every major component calls the system clock directly, making history and logs impossible to reproduce exactly without "mocking the universe."
- **Mediator**: Uses `datetime.utcnow()` for registry logs and program history.
- **Benchmark**: Uses `time.time()` for internal timeouts and `datetime.now()` for payload timestamps.
- **Hub**: Uses `datetime.utcnow()` for Chronicle entries.
- **Audit Recommendation**: Inject a `Clock` protocol. Pass `now` as data.

### 1.2 Resource Nondeterminism (The "Filesystem" Problem)
- **Results Aggregator**: Uses `os.listdir("results")`. Filesystem iteration order is nondeterministic. The `results_aggregated.json` may have inconsistent key ordering.
- **Mediator**: Directly reads `MISSION.md` and `program.md` during the "Decide" phase.
- **Audit Recommendation**: Sort filesystem inputs. Move file reading to an "Imperative Shell" that feeds a "Pure Core."

### 1.3 State Nondeterminism (The "Env" Problem)
- **Benchmark Logic**: Behavior shifts based on `BENCH_TRAP_BOOST`, `BENCH_ADVERSARIAL_SHARE`, and `BENCH_BOOTSTRAP` environment variables scattered deep in the calling stack.
- **Audit Recommendation**: Collect all configuration into a single `ResearchConfig` object at the entry point and pass it down.

---

## 2. Separation of Concerns Violations

### 2.1 Deciders vs. Actors
In the current architecture, the code that **decides** how to run a benchmark is the same code that **acts** by making HTTP requests to Ollama or LiteLLM.
- **Benchmark.py**: `_score_model` decides to run a task and also tracks elapsed wall-clock time.
- **Mediator.py**: (Targeted for fix) The orchestrator loop handles both agent logic and filesystem persistence in one block.

### 2.2 Brittle "Log-Parsing" Logic
The `extract_results.py` script "decides" on the state of the research by parsing rendered markdown files with Regex.
- **Violation**: The "Imperative Shell" (the markdown logs) is being used as the "Source of Truth" for the next layer of "Decisions" (aggregation).
- **Audit Recommendation**: Treat raw JSON data as the "Core Storage." Markdown should be a "Read-Only View" (Effect).

---

## 3. High-Impact Refactoring Targets

| Component | Issue Category | Priority | Action |
| :--- | :--- | :--- | :--- |
| `agent/mediator.py` | Coupling | **CRITICAL** | Split into `Orchestrator` (Logic) and `SwarmRunner` (Shell). |
| `research_env/benchmark.py` | Determinism | **HIGH** | Pull all `os.getenv` to top-level; inject `Clock`. |
| `hub/app.py` | Side Effects | **MEDIUM** | Separate Key Generation from API Start; use a deterministic Log Sorter. |
| `extract_results.py` | State/IO | **MEDIUM** | Switch to pure JSON processing; decouple parsing from iteration. |

---

## 4. Proposed "Sovereign" Architecture Pattern

To move toward Dave Farley's vision, we should adopt the **Hexagonal / Ports & Adapters** model specifically for this swarm:

1.  **Pure Core**: A class/function that takes `(State, InputData)` and returns `(NewState, List[Effects])`.
2.  **Effects**: Simple data objects like `RunBenchmark(id="...")`, `SaveToVault(path="...")`, `LogError(msg="...")`.
3.  **Imperative Shell**: A thin wrapper that loops over the `Effects` and performs the real-world I/O (Ollama calls, Disk writes).

> [!TIP]
> This pattern makes the entire Swarm **Testable in Milliseconds** without ever calling an LLM or writing a single file to disk.

---
**Audit Performed By**: Antigravity  
**Principles Applied**: Determinism, Separation of Concerns (Farley, 2026)
