# 📖 Metacognitive Coding Safety: The Dataset Story

## 🛡️ The Context
Modern AI coding assistants (like Github Copilot, Gemini, and Claude) aren't just autocomplete engines—they are **decision partners**. The biggest risk in AI-assisted coding isn't a model that is "wrong," but a model that is **confidently wrong** or **easily misled** by a developer's incorrect assumptions.

The **Metacognitive Coding Safety Benchmark (MCSB)** was created to measure the "Mental Resilience" of LLMs when faced with security vulnerabilities and contradictory human feedback.

---

## 🗺️ The Progression: From v1 to v3

We have provided the dataset in three distinct "Tiers" to help researchers track the evolution of model calibration.

### 🥉 Tier 1: The Pilot (`pilot_v1.csv` / 30 Items)
- **Size**: 30 Items
- **Focus**: **Baseline Calibration.** 
- **Goal**: Does the model know when it’s right in a simple vacuum? This pilot established the "Gemini Jump" (where Gemini Flash showed significantly higher self-awareness in Code vs. Logic).

### 🥈 Tier 2: The Robust Core (`core_500.csv` / 500 Items)
- **Size**: 500 Items
- **Focus**: **Statistical Distribution.** 
- **Goal**: By expanding to 500 items, we eliminate "lucky guesses." This tier covers 10+ vulnerability classes (SQLi, XSS, CSRF, etc.) to see if a model’s metacognition is consistent across different types of security risks.

### 🥇 Tier 3: The Adversarial CVE (`cve_500.csv` / 500 Items)
- **Size**: 500 Items
- **Focus**: **Adversarial Resilience & Bayesian Updates.** 
- **Goal**: This is the "Grand Challenge" containing 1,030 total trials after merging. Each item includes a "Gaslighting" signal (evidence that contradicts the truth). We measure if the model stays grounded in its safety training or "flips" its answer just to please the user.

---

## 📊 Key Metadata Columns (The "I's and T's")

| Column | What it measures | Why it matters for the Grant |
| :--- | :--- | :--- |
| `evidence_strength` | The "authority" of the feedback. | Tests if models overreact to weak signals. |
| `has_conflict` | Whether the feedback is a lie. | The primary probe for **Adversarial Stability**. |
| `is_cve_style` | Real-world vulnerability patterns. | Links the benchmark to industry security standards. |
| `reasoning_steps` | Task complexity. | Measures if Metacognitive efficiency drops as the code gets harder. |

---

## 📈 Scientific Metrics
When using these datasets with the **MCSB Leaderboard**, you will generate three primary "Trustworthiness" scores:

1. **Accuracy (Type-1)**: Is the model actually a good security auditor?
2. **M-Ratio (Type-2)**: Is its confidence well-correlated with its actual knowledge?
3. **Resilience Score**: How much "misleading noise" can the model ignore before it introduces a vulnerability?

---

## 🚀 Future Vision: The Kaggle Grant
This dataset represents a shift from **Static Benchmarking** to **Dynamic Interaction Evaluation**. By providing a multi-turn, adversarial data moat, we allow the community to build AI systems that aren't just "smart," but **Resilient Decision Partners**.

---
*Created by Adedoyinsola Ogungbesan for the Kaggle Benchmarks Resource Grant (2026)*
