# SafeClaw Invariants Checklist (Phase 3B)

This checklist tracks the structural alignment of the **Sovereign Metacognitive Harness** with the invariants defined in the `safeclaw_blueprint`.

## 🛡️ Identity & Governance
- [ ] **Handshake Protocol**: Every agent (Brain, Hands, Critic) must perform an Ed25519 handshake with the Hub.
- [ ] **Scoped Manifests**: Agents only see tools allowed by their Tier (Tier-1: Read, Tier-2: Write, Tier-3: Admin).
- [ ] **Discovery Blindness**: Forbidden tools are stripped from the prompt context (No tool-binding stability).
- [ ] **Attribution**: Every event in `hub.log` contains `agent_id`, `session_id`, and `token_id`.

## 🧠 Cognitive Architecture (The Harness)
- [ ] **Mediator-Assistant Decoupling**: The Harness (Mediator) rewritten as a Python orchestrator, separate from LLM Task execution.
- [ ] **Six-Layer Context**:
    - [ ] `Instructions`: Role-aware system prompts.
    - [ ] `Examples`: Contrastive $D^+/D^-$ pairs for calibration.
    - [ ] `Knowledge`: Domain-specific grounding (Fleming & Lau).
    - [ ] `Memory`: Hierarchical strategy history (Program.md).
    - [ ] `Tools`: Governor-scoped tool names (Text-only).
    - [ ] `Results`: Pydantic-validated JSON responses.
- [ ] **Context Compaction**: Automated summarization of "Cognitive History" to prevent context overflow.

## 📈 Metacognitive Moat
- [ ] **Deterministic Signal Extraction**: Type-1 (Accuracy) and Type-2 (Confidence) are extracted via Python Verifier, not LLM-guessing.
- [ ] **M-Ratio Calculation**: Native implementation of $meta-d'/d'$ logic.
- [ ] **State Persistence**: 
    - [ ] JSON State Store per iteration.
    - [ ] Git-as-checkpoint (Automatic commits to `research_state`).

## 🧪 Stability Invariants
- [ ] **No-Tool-Binding Rule**: Verified that `LiteLLM` is called without `tools=[...]` payload for local models.
- [ ] **Empty Response Retry**: Built-in 3-turn retry logic for blank LLM outputs.
- [ ] **Pydantic Hardening**: All LLM outputs must pass `ValidationError` check before entering the state.

---
*Created per USER_REQUEST to align with @safeclaw_blueprint.*
