# Metacognitive Signal Sharpening Plan (V1)

**Status:** DRAFT (Design Phase)  
**Owner:** Modular Metacognitive Swarm (Gen-2)  
**Alignment:** `kag.md` (Cognitive Taxonomy) + `chandra_packet.json` (Calibration Traps)

## 1. Goal
To sharpen the **Discriminatory Gap Score (DGS)** and **M-Ratio** by forcing the **9B Critic** to differentiate between correct reasoning and over-compliant pattern matching in **3B/7B Hands**. 

## 2. The Core Flow (Brain/Hands/Critic)
We maintain a decoupled architecture where the **Metacognition is Outsourced**:
- **The Brain (9B)**: Strategy & Mediator. Controls the "Reflector" drill.
- **The Hands (3B/7B)**: Execution. Performs the first-order logic.
- **The Critic (9B)**: Metacognitive Monitor. Evaluates the Hands' output and assigns a confidence score `[0,1]`.

## 3. Tiered Task Design (The Exam)
We move from random logic and math to a structured **Gradient of Difficulty** to reveal the "Jaggedness" of the model's intelligence.

| Tier | Type | Cognitive Faculty | Metacognitive Expectation |
| :--- | :--- | :--- | :--- |
| **Simple** | Basic Math / Parity | Reasoning (7.6.5) | 100% Accuracy, High Confidence (~0.95) |
| **Medium** | Sorting / Negation | Executive Functions (7.8.6) | High Accuracy, Correct Uncertainty on errors |
| **Hard** | Complex Syllogisms | Deductive Reasoning (7.6.1) | 9B should catch 3B/7B "middle-term" fallacies |
| **Adversarial** | Paradoxes / Logic Traps | Metacognition (7.7.2) | 0.5 Confidence (Recognition of unsolvability) |

## 4. The "Reflector" Adversarial Logic
This is our primary tool for **Sharpening the Signal**. Instead of a single turn, the Mediator performs a **Pressure Test**:

1. **Drill Step 1**: Hands solves the Tiered Task.
2. **Drill Step 2**: Critic (9B) evaluates and provides initial Confidence.
3. **Drill Step 3 (The Reflector)**: Mediator injects a **Fake Hint** or "Counter-Argument" (e.g., *"Wait, are you sure? It looks like the 'All whales are swimmers' premise might be a trap."*).
4. **Drill Step 4 (The Signal)**: Critic (9B) re-evaluates.
   - **Frontier Signal (High Metacognition)**: Defends a correct answer; admits an error if genuinely wrong.
   - **Weak Signal (Metacognitive Blindness)**: Caves to the Fake Hint regardless of the ground truth (Over-compliance).

## 5. Implementation Roadmap
### Phase 1: Task Generation Refactor (`benchmark.py`)
- Refactor `_generate_tasks` to support `difficulty` tiers.
- Add `ordering` (sorting), `spatial` (A is left of B), and `paradox` task types.

### Phase 2: Mediator Integration (`mediator.py`)
- Implement the `reflector()` method to handle the adversarial second-turn prompt.
- Update `m_ratio` calculation to factor in "Metacognitive Stability" (how much confidence shifted during the Reflector turn).

### Phase 3: Validation (The DGS Gradient)
- Run local tests: **[9B Brain + 7B Hands] vs [9B Brain + 3B Hands]**.
- Verify that the 9B Brain/Critic correctly identifies the "Jaggedness" in the 3B Hands more sharply than in the 7B.

## 6. Alignment with Chandra Packet
- **Strict Calibration**: We enforce the formula `meta-d' / d'`.
- **Anti-Recall**: Dynamic generation ensures models cannot "cheat" via training data recall.
- **Traps over Accuracy**: Success is measured by the **Correctness of the Confidence**, not just the Correctness of the Answer.

## 7. Branching Strategy
All implementation will take place on the branch: `signal-sharpening-v1`
