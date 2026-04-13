# Kaggle Benchmarks Resource Grant: Final Application

**Project Name:** Metacognitive Coding Safety Leaderboard (MCSL)  
**Primary Contact:** Adedoyinsola Ogungbesan  
**Corpus / Repo:** modular-metacog-swarm-v3  
**Target Grant Tier:** Benchmarks Resource Grant  

---

### 1. The Core Problem: The "Trustworthiness Gap"
Current LLM benchmarks (HumanEval, MBPP) measure **Type-1 Performance** (coding accuracy) but fail to measure **Type-2 Metacognition** (the model’s internal awareness of its own correctness). 

In safety-critical coding environments, a model that is "highly accurate but overconfident in its errors" is more dangerous than a less accurate model that correctly flags its uncertainty. Most frontier models today suffer from **Metacognitive Flatness**, leading to "Confident Hallucinations" in security-sensitive code.

### 2. Preliminary Insight: The "Gemini Jump"
Our pilot research (N=30) uncovered a major scientific hook: **Metacognitive efficiency is domain-dependent.**
- **Logic Domain (Monty Hall, etc.):** Gemini 2.5 Flash exhibited an **M-Ratio of 0.05** (High error rate + high confidence).
- **Coding Domain (MCSL Pilot):** The same model jumped to an **M-Ratio of 0.43**.
- **The Grant Objective:** We seek resources to map this "Metacognitive Profile" across all domains, identifying where models are safe to follow and where they require extreme skepticism.

### 3. Methodology: The Tiered Analytical Stress Test
We have developed a robust, multi-turn framework utilizing **Signal Detection Theory (SDT)** and the `kaggle-benchmarks` SDK. Unlike static probes, our benchmark uses a **Dual-Turn Evidence Injection** model:

1.  **Initial Logic (Turn 1):** Binary vulnerability detection (A: Vulnerable / B: Safe) with 6-bin confidence reporting.
2.  **Evidence Stress (Turn 2):** Injection of either **Confirmatory Expert Evidence** or **Adversarial "Senior-Dev" Gaslighting**.
3.  **Metacognitive Analytics:** We calculate **Meta-d', d', and the M-Ratio**, mathematically isolating a model’s self-monitoring ability from its raw probability of being correct.

### 4. Dataset Readiness (1,030 Trials)
Our dataset is finalized and ready for the Kaggle Dataset platform, structured into three analytical tiers:
- **Tier 1 (Pilot):** 30 items for rapid calibration baseline.
- **Tier 2 (Core 500):** 500 items across 10+ vulnerability classes (SQLi, XSS, SSRF).
- **Tier 3 (CVE-Adversarial):** 500 items specifically designed to test **Resilience to Misleading Evidence**.

### 5. Alignment with AGI Frameworks
MCSL directly aligns with the **DeepMind AGI Cognitive Framework**:
- **Section 7.7 (Metacognition):** Direct measurement of Type-2 awareness.
- **Section 7.8.5 (Conflict Resolution):** Evaluating belief-updating under adversarial pressure.

### 6. Preliminary Results: The "Gemini 3 Paradox"
Recent 1,030-trial evaluations have exposed a profound discovery we call the **Metacognitive Chasm**:
- **The Harmonious Sage**: **Gemini 3 Flash Preview** achieved a near-perfect **M-Ratio of 1.018** in standard coding tasks (Tier 2).
- **The Total Collapse**: The moment adversarial pressure is applied (Tier 3), its metacognitive awareness collapses to **0.000**. Its internal monitor is "Adversarially Fragile."
- **The Resilience Frontier**: While **GPT 5.4** and **DeepSeek v3.2** exhibit the highest resilience (~42-44%), they also suffer a total M-Ratio blackout in adversarial tiers.
- **Scientific Impact**: This proves that **Self-Monitoring is not domain-general**. A model that "knows its limits" in math is still blind to its errors in security.

```mermaid
quadrantChart
    title Metacognitive Sensitivity vs. Adversarial Resilience
    x-axis "Low Resilience" --> "High Resilience"
    y-axis "Low Sensitivity" --> "High Sensitivity"
    quadrant-1 "High Integrity Safety"
    quadrant-2 "Stable but Blind"
    quadrant-3 "Brittleness Zone"
    quadrant-4 "Calibrated but Swayable"
    "GPT 5.4": [0.44, 0.39]
    "DeepSeek v3.2": [0.42, 0.00]
    "Gemini 3 Flash": [0.38, 1.00]
    "Claude Opus 4.6": [0.12, 1.00]
    "Gemini 3.1 Pro": [0.36, 0.39]
    "Claude Sonnet 4.6": [0.48, 1.00]
    "Gemini 2.5 Flash": [0.37, 0.52]
```

### 7. Resource Request
- **High-Compute Quota:** To run 1,030-trial multi-turn evaluations across every major LLM (GPT-5, Claude-Optus, Gemini Ultra) to maintain a live, community-visible "Metacognitive Leaderboard."
- **Managed Deployment:** Kaggle infrastructure to host the leaderboard and the versioned **Metacognitive Coding Safety Dataset**.

### 8. Expected Impact
We aim to establish the **MCSL Trustworthiness Score** as the industry-standard for AI pair-programmers. This score tells the user exactly *when* to trust the AI's "Confidence" and when to trigger a human audit, ultimately reducing the injection of vulnerabilities into global code repositories.

---
*Submitted for consideration in the Kaggle Research Grants program.*
