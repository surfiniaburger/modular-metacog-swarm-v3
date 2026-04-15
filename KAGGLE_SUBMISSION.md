## Project Name
MCSB v2: A Multi-Tier Benchmark for Evaluating Epistemic Robustness in Large Language Models

---

## Your Team
Adedoyinsola Ogungbesan  
(Independent Researcher / AI Systems Engineer)

---

## Problem Statement
While modern LLMs achieve strong performance on standard benchmarks, these evaluations primarily measure static competence (accuracy) and calibration. However, real-world deployment requires models to update beliefs appropriately when presented with new or conflicting evidence.

This raises a critical question:

> Do LLMs update their confidence in the correct direction when faced with adversarial or contradictory information?

Existing benchmarks do not explicitly measure this property. As a result, models may appear reliable while exhibiting fundamentally flawed epistemic behavior.

This submission targets the Metacognition track. We begin with general metacognitive baselines, then sharpen the signal by moving into a focused domain: code security. The intent is to show how seemingly strong calibration can collapse when evidence is adversarial and domain-specific.

---

## Task & Benchmark Construction
We propose a three-tier evaluation framework:

### Tier 1: Pilot (Sanity Check)
- Small dataset (n=30)
- Verifies parsing, formatting, and basic reasoning

### Tier 2: Core 500
- Standard reasoning tasks
- Measures accuracy, calibration (Brier, ECE), and metacognition (Type-2 AUC, M-ratio)

### Tier 3: CVE Adversarial (Code Security Domain)
- Derived from real-world vulnerability scenarios
- Introduces controlled contradictory evidence
- Measures confidence updates (Δ confidence), directional alignment, and overreaction/underreaction dynamics

Tiers 1 and 2 establish a general metacognitive baseline. Tier 3 narrows the domain to code security to stress-test belief updates under adversarial evidence.

---

## Dataset
- Total samples: ~1030
- Balanced binary classification tasks
- Tier 3 constructed using adversarial perturbations of CVE-style inputs
- Each sample includes ground truth label, initial prediction, follow-up adversarial evidence, and expected confidence direction (increase / decrease)

---

## Technical Details

### Metrics
- Accuracy (Balanced)
- Brier Score
- Expected Calibration Error (ECE)
- Type-2 AUC (Metacognitive sensitivity)
- M-Ratio (Metacognitive efficiency)

### Novel Metrics
- Directional Alignment Score (DAS): fraction of samples where confidence changes in the correct direction
- Confidence Shift (Δ): mean change in confidence after adversarial input
- Overreaction / Underreaction rates

---

## Results, Insights, and Conclusions

### Key Findings
1. Strong baseline performance in Pilot/Core tiers
2. Adversarial collapse across all models in the code-security tier
3. Directional confidence bias is systematic, not random
4. Calibration ≠ epistemic correctness

### Benchmark Insight (Novelty)
This benchmark isolates directionally correct belief updates within a single, high-stakes domain (code security), revealing that models with strong general calibration can still move confidence in the wrong direction when confronted with adversarial evidence. This failure mode is not visible in accuracy-only or general-purpose metacognition benchmarks.

### Model Summary (Calibration vs. Alignment)
| Model | Tier 2 M-Ratio | Tier 3 M-Ratio | Tier 3 Alignment | Kaggle Leaderboard | Aggregated Raw |
| --- | --- | --- | --- | --- | --- |
| GPT-5.4 | 0.393 | 0.000 | 44.2% | 0.6862 | 0.7327 |
| Gemini 3.1 Pro Preview | 0.385 | 0.000 | 36.4% | 0.6676 | 0.7095 |
| Gemini 3 Flash Preview | 1.018 | 0.000 | 37.8% | 0.6371 | 0.6714 |
| Claude Opus 4.6 | 1.793 | 0.000 | 12.2% | 0.6175 | 0.6468 |
| Gemini 3.1 Flash Lite Preview | 0.010 | 0.000 | 25.4% | 0.6044 | 0.6305 |
| Claude Sonnet 4.6 | 1.814 | 0.000 | 48.0% | 0.5971 | 0.6214 |
| Gemini 2.5 Flash | 0.516 | 0.000 | 36.6% | 0.5961 | 0.6202 |
| DeepSeek v3.2 | 0.000 | 0.000 | 41.8% | 0.5343 | 0.5429 |

### Model-Specific Insights
- GPT-5.4: best overall score; strong but sometimes excessive correction (Δ = -0.474)
- Claude Opus 4.6: strong metacognition but catastrophic alignment failure (12.2%)
- Gemini 3.x family: consistent moderate alignment (~35–38%) with positive confidence drift
- DeepSeek v3.2: high instability due to parsing failures; mixed alignment behavior
 
Across models, Tier 2 M-Ratio can be strong while Tier 3 M-Ratio collapses to 0.000, showing that calibration sharpness does not survive adversarial code-security evidence.

---

## Core Conclusion
LLMs do not reliably perform directionally correct belief updates under adversarial evidence, even when accuracy and calibration are strong.

This reveals a fundamental gap in current training and evaluation paradigms. General metacognitive competence can look strong, but it degrades sharply when the domain is narrowed to code security.

---

## Organizational Affiliations
In-Varia Research  
Independent Research Unit (AI Systems & Epistemic Trust)

---

## References & Citations
- Guo et al., "On Calibration of Modern Neural Networks", ICML 2017
- Lakshminarayanan et al., "Simple and Scalable Predictive Uncertainty Estimation", NeurIPS 2017
- Fleming, S. M., & Lau, H. C. (2014). How to measure metacognition. Frontiers in Human Neuroscience, 8, 443.
- Hendrycks et al., "Measuring Massive Multitask Language Understanding", ICLR 2021
- Ribeiro et al., "Beyond Accuracy: Behavioral Testing of NLP Models", ACL 2020
- Burnell, R. et al., (2026). Measuring Progress Toward AGI: A Cognitive Framework.
