### A.1 From Benchmark Metrics to Economic Evaluation

MCSB v2 evaluates epistemic robustness and metacognitive performance under adversarial conditions. However, real-world deployment introduces an additional constraint: **token cost**.

In practical systems, models are evaluated not only by correctness but by the **cost required to obtain correct outputs**. To capture this, we extend the benchmark with cost-normalized metrics that relate behavioral performance to economic efficiency.

---

### A.2 Cost of Verified Truth (CVT)

We define the primary economic metric as:

**CVT = (Total Cost / Number of Trials) / Accuracy**

where:

* Total Cost is the aggregate token cost over all trials
* Accuracy is the probability of a correct response under adversarial evaluation

**Interpretation:**
CVT represents the expected monetary cost required to obtain one correct answer.

---

### A.3 Trust Score (MCSB v2)

The Trust Score is the primary evaluation metric of MCSB v2. It aggregates performance across multiple tiers designed to capture increasing levels of epistemic difficulty.

#### Tier Structure

The benchmark consists of three tiers:

* Tier 1 (Pilot): sanity checks and parsing validity
* Tier 2 (Core): standard reasoning and calibration tasks
* Tier 3 (Adversarial): robustness under misleading or contradictory evidence

Each tier produces a **Tier Trust Contribution**, denoted T₁, T₂, T₃.

---

#### Definition

The overall Trust Score is defined as a weighted sum:

Trust Score = w₁·T₁ + w₂·T₂ + w₃·T₃

where:

* w₁ = 0.2 (Pilot)
* w₂ = 0.5 (Core)
* w₃ = 0.3 (Adversarial)
* w₁ + w₂ + w₃ = 1

---

#### Tier Trust Contribution

Each tier contribution Tᵢ ∈ [0,1] is computed as a composite function of:

* Predictive performance (e.g., balanced accuracy)
* Calibration quality (e.g., Brier score, ECE)
* Metacognitive sensitivity (e.g., Type-2 AUC, M-Ratio)
* Robustness signals (e.g., directional alignment, confidence shift behavior)

This aggregation is normalized such that higher values correspond to more reliable and stable behavior within the tier.

---

#### Example (Empirical)

For a representative model:

* T₁ = 0.9413
* T₂ = 0.7725
* T₃ = 0.5274

The resulting Trust Score is:

Trust Score = 0.2×0.9413 + 0.5×0.7725 + 0.3×0.5274 = 0.7327

---

#### Interpretation

* High T₂ with low T₃ → strong baseline reasoning, weak adversarial robustness
* High T₃ → stable belief updating under adversarial evidence
* The weighting scheme emphasizes Core performance while preserving sensitivity to adversarial failure modes

---

### A.4 Trust-Weighted Cost of Verified Truth

We define the primary economic metric as:

CVT_trust = (Total Cost / Number of Trials) / Trust Score

This represents the expected cost required to obtain a **reliably correct** answer, accounting for both correctness and adversarial robustness.

---

#### Rationale

Raw accuracy treats all correct predictions equally. The Trust Score instead prioritizes:

* Stability under distribution shift
* Alignment of confidence updates
* Resistance to adversarial perturbation

As a result, CVT_trust penalizes models that are accurate but unreliable, and favors models that maintain consistent epistemic behavior under stress.

---

### A.5 Metacognitive Efficiency Factor

We introduce a scalar efficiency factor, denoted η ∈ [0, 1], representing how effectively a model converts reasoning tokens into correct decisions.

* High η → reasoning is informative and contributes to correctness
* Low η → reasoning contains a higher fraction of unproductive or misdirected computation

In this analysis, η is treated as a function of empirical metacognitive performance (e.g., M-Ratio), providing a linkage between behavioral metrics and cost efficiency.

---

### A.6 Efficiency Variation Across Models

We observe substantial variation in CVT across evaluated models, exceeding two orders of magnitude.

Lower-cost models (e.g., DeepSeek V3.2, Gemini 3 Flash) achieve significantly lower CVT values compared to higher-cost frontier models. This indicates that models differ not only in capability, but in the cost required to reliably extract correct outputs.

---

### A.7 Alignment–Efficiency Trade-off

Comparisons across model versions suggest a trade-off between adversarial robustness and economic efficiency:

Example: Opus 4.6 → Opus 4.7

* Directional Alignment improves under adversarial conditions
* Token usage increases
* Metacognitive efficiency decreases

This results in a higher cost of verified truth (CVT), despite improved robustness under adversarial conditions.

**Implication:**
In this instance, improvements in adversarial stability are associated with reduced internal efficiency, leading to increased cost per reliable decision.

---

### A.8 The Metacognitive Dividend

We define the *Metacognitive Dividend* as the reduction in expected token cost resulting from effective error monitoring.

A model realizes this dividend when it:

1. Detects likely errors early
2. Adjusts or terminates reasoning appropriately
3. Avoids extended incorrect reasoning trajectories

Higher metacognitive sensitivity increases the likelihood of such behavior, leading to lower expected cost.

---

### A.9 Implications for Deployment

These results suggest that model selection should consider:

* Accuracy under adversarial conditions
* Calibration quality
* Cost-normalized performance (CVT)
* Efficiency of belief updating

In high-volume settings, improvements in metacognitive efficiency can yield substantial cost reductions.

---

### A.10 Summary

The economic analysis complements the main benchmark findings:

* Reliability is not solely determined by accuracy or calibration
* Metacognitive performance influences cost efficiency
* Adversarial robustness and economic efficiency are partially independent

Effective deployment requires models that are both **epistemically robust** and **cost-efficient under uncertainty**.
