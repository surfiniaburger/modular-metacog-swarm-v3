# Metacognitive Token Economics: Verified Truth & The Efficiency Frontier
*Appendix A: Economic Efficiency Analysis (MCSB v2 Framework)*

---

### A.1 From Benchmark Metrics to Economic Evaluation
MCSB v2 evaluates epistemic robustness and metacognitive performance under adversarial conditions. However, real-world deployment introduces an additional constraint: **token cost**. 

In practical systems, models are evaluated not only by correctness but by the **cost required to obtain correct outputs**. To capture this, we extend the benchmark with cost-normalized metrics that relate behavioral performance to economic efficiency.

### A.2 Cost of Verified Truth (CVT)
We define the primary economic metric as the expected monetary cost required to obtain one correct answer:
$$CVT = \frac{(\text{Total Cost} / \text{Number of Trials})}{\text{Accuracy}}$$

*Interpretation: CVT represents the monetary investment required per unit of verified truth.*

### A.3 Trust Score (MCSB v2)
The Trust Score is the primary evaluation metric of MCSB v2. It aggregates performance across three tiers of increasing epistemic difficulty:
- **Tier 1 (Pilot)**: Sanity checks and parsing validity ($w_1 = 0.2$)
- **Tier 2 (Core)**: Standard reasoning and calibration tasks ($w_2 = 0.5$)
- **Tier 3 (Adversarial)**: Robustness under misleading evidence ($w_3 = 0.3$)

$$\text{Trust Score} = 0.2 \cdot T_1 + 0.5 \cdot T_2 + 0.3 \cdot T_3$$

### A.4 Trust-Weighted Cost of Verified Truth ($CVT_{trust}$)
This represents the expected cost to obtain a **reliably correct** answer, accounting for both correctness and adversarial robustness.
$$CVT_{trust} = \frac{(\text{Total Cost} / \text{Number of Trials})}{\text{Trust Score}}$$
*Rationale: $CVT_{trust}$ penalizes models that are accurate but brittle, favoring those that maintain consistent epistemic behavior under stress.*

---

### A.5 Audit Registry: The Penny Standard
Results are computed over a full run of the **MCSB v2 dataset (N = 1,030 trials)**. Pricing is predicated on April 2026 API rates.

| Model | Total Cost ($) | Trust Score | CVT (cents ¢) | **$CVT_{trust}$ (cents ¢)** |
| :--- | :--- | :--- | :--- | :--- |
| **Claude Opus 4.7** | $9.48 | 0.6405 | 1.44 ¢ | **1.44 ¢** |
| **Claude Opus 4.6** | $6.22 | 0.6482 | 0.94 ¢ | **0.94 ¢** |
| **GPT-5.4 Standard** | $1.58 | 0.7327 | 0.21 ¢ | **0.21 ¢** |
| **Gemini 3.1 Pro** | $0.82 | 0.7102 | 0.11 ¢ | **0.11 ¢** |
| **GPT-5.4 Mini** | $0.40 | 0.6305 | 0.06 ¢ | **0.06 ¢** |
| **DeepSeek V3.1** | $0.076 | 0.5673 | 0.013 ¢ | **0.013 ¢** |
| **DeepSeek V3.2** | $0.075 | 0.5429 | 0.013 ¢ | **0.013 ¢** |
| **Gemini 3 Flash** | $0.18 | 0.6721 | 0.026 ¢ | **0.026 ¢** |

---

### A.6 Metacognitive Efficiency Factor ($\eta$)
We introduce a scalar efficiency factor, $\eta \in [0, 1]$, representing how effectively a model converts reasoning tokens into correct decisions.
- **High $\eta$**: Reasoning is informative and contributes to correctness.
- **Low $\eta$**: Reasoning contains a higher fraction of unproductive/misdirected computation.

### A.7 Alignment–Efficiency Trade-off
We observe a critical trade-off at the frontier (e.g., **Opus 4.7**). While adversarial robustness (T3) improves, token usage increases and $\eta$ decreases.
*Implication: Improvements in adversarial stability often reduce internal efficiency, increasing the cost per reliable decision.*

### A.8 The Metacognitive Dividend
We define the *Metacognitive Dividend* as the reduction in expected token cost resulting from effective error monitoring (e.g., detecting errors early and terminating reasoning trajectories). High metacognitive sensitivity ($M-Ratio$) increases the likelihood of realizing this dividend.

---

### A.9 Implications for Deployment
Model selection should prioritize models that are both **epistemically robust** and **cost-efficient under uncertainty**. In high-volume settings, improvements in metacognitive efficiency can yield substantial cumulative cost reductions.

---
**License**: Apache 2.0
**Contact**: ade@in-varia.com
