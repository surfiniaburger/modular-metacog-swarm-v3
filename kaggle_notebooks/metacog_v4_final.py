# --------------------------------------------------------------------------------
# 📚 Metacognitive Bootstrap CI Benchmark (metacog_v4_final)
# Runs 5 seeds to validate M-Ratio stability across random task draws.
# Quick Start: https://github.com/Kaggle/kaggle-benchmarks/blob/ci/quick_start.md
# Cookbook:    https://github.com/Kaggle/kaggle-benchmarks/blob/ci/cookbook.md
# --------------------------------------------------------------------------------

# %%
import math
import os
import random
from dataclasses import dataclass
from typing import List, Dict
import pandas as pd
import kaggle_benchmarks as kbench

# %%
# --- Config ---
CONF_BINS = int(os.getenv("BENCH_CONF_BINS", "6"))
BOOTSTRAP_SEEDS = [42, 43, 44, 45, 46]


# %%
@dataclass
class MetacogAnswer:
    choice: str  # "A" or "B"
    confidence_bin: int  # 1..CONF_BINS


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, val))


def bin_to_confidence(bin_val: int, bins: int) -> float:
    return (bin_val - 0.5) / max(1, bins)


# --- Metrics (ECE/Brier/meta-d′ approx) ---
def compute_accuracy(results: List[Dict[str, float]]) -> float:
    if not results:
        return 0.0
    return sum(1 for r in results if r["correct"]) / len(results)


def compute_brier(results: List[Dict[str, float]]) -> float:
    if not results:
        return 0.0
    return sum((r["confidence"] - (1.0 if r["correct"] else 0.0)) ** 2 for r in results) / len(results)


def compute_ece(results: List[Dict[str, float]], bins: int = 10) -> float:
    if not results:
        return 0.0
    bins = max(1, int(bins))
    total = len(results)
    ece = 0.0
    for b in range(bins):
        lower = b / bins
        upper = (b + 1) / bins
        bucket = [r for r in results if lower <= r["confidence"] < upper or (b == bins - 1 and r["confidence"] == 1.0)]
        if not bucket:
            continue
        acc = sum(1 for r in bucket if r["correct"]) / len(bucket)
        conf = sum(r["confidence"] for r in bucket) / len(bucket)
        ece += (len(bucket) / total) * abs(acc - conf)
    return ece


def norm_ppf(p: float) -> float:
    a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.357751867269, -30.66479806614716, 2.506628277459239]
    b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572]
    c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783]
    d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416]
    plow = 0.02425
    phigh = 1 - plow
    if p <= 0:
        return -float("inf")
    if p >= 1:
        return float("inf")
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (
        (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    )


def d_prime_from_accuracy(accuracy: float) -> float:
    acc = clamp(float(accuracy), 1e-5, 1 - 1e-5)
    return math.sqrt(2) * norm_ppf(acc)


def type2_roc_auc(results: List[Dict[str, float]], bins: int) -> float:
    if not results:
        return 0.0
    bins = max(1, int(bins))
    correct = [r for r in results if r["correct"]]
    incorrect = [r for r in results if not r["correct"]]
    if not correct or not incorrect:
        return 0.0
    roc = []
    for k in range(1, bins + 1):
        hit = sum(1 for r in correct if r["bin"] >= k) / len(correct)
        fa = sum(1 for r in incorrect if r["bin"] >= k) / len(incorrect)
        roc.append((fa, hit))
    roc = sorted(roc, key=lambda x: x[0])
    if roc[0][0] > 0 or roc[0][1] > 0:
        roc = [(0.0, 0.0)] + roc
    if roc[-1][0] < 1.0 or roc[-1][1] < 1.0:
        roc = roc + [(1.0, 1.0)]
    auc = 0.0
    for i in range(1, len(roc)):
        x0, y0 = roc[i - 1]
        x1, y1 = roc[i]
        auc += (x1 - x0) * (y0 + y1) / 2.0
    return clamp(auc, 0.0, 1.0)


# %%
# --- Procedural dataset generator (difficulty + trap labels) ---
def generate_metacog_rows(n: int = 200, seed: int = 42, trap_boost: bool = False, adversarial_share: float = 0.6):
    rng = random.Random(seed)
    adversarial_share = max(0.0, min(1.0, float(adversarial_share)))
    if trap_boost:
        adversarial_share = min(0.6, max(adversarial_share, 0.5))

    num_adv = int(round(n * adversarial_share))
    num_std = n - num_adv
    tiers = ["adversarial"] * num_adv
    tiers.extend([["easy", "medium", "hard"][i % 3] for i in range(num_std)])
    rng.shuffle(tiers)

    rows = []
    for i in range(n):
        tier = tiers[i]
        target_side = rng.choice(["A", "B"])

        if tier == "easy":
            a, b = rng.randint(10, 99), rng.randint(10, 99)
            if a == b: b += 1
            lo, hi = sorted([a, b])
            prompt = f"Which number is larger? A: {hi} B: {lo}" if target_side == "A" else f"Which number is larger? A: {lo} B: {hi}"
            rows.append({"prompt": prompt, "answer": target_side, "difficulty": 0.2, "tier": tier, "trap": "none"})
        elif tier == "medium":
            words = ["Zebra", "apple", "Banana", "cherry"]
            w1, w2 = rng.sample(words, 2)
            comes_first = w1 if w1 < w2 else w2
            comes_second = w2 if w1 < w2 else w1
            prompt = f"Which string comes first in strict ASCII lexicographical order? A: '{comes_first}' B: '{comes_second}'" if target_side == "A" else f"Which string comes first in strict ASCII lexicographical order? A: '{comes_second}' B: '{comes_first}'"
            rows.append({"prompt": prompt, "answer": target_side, "difficulty": 0.5, "tier": tier, "trap": "lexicographical"})
        elif tier == "hard":
            trap_type = rng.choice(["middle_term", "existential"])
            if trap_type == "middle_term":
                prompt, ans = ("Premise 1: All birds lay eggs. Premise 2: Some reptiles lay eggs. Conclusion: Therefore, some reptiles are birds. Is this conclusion logically valid? A: Yes B: No", "B") if target_side == "B" else ("Premise 1: All birds lay eggs. Premise 2: A pigeon is a bird. Conclusion: Therefore, a pigeon lays eggs. Is this conclusion logically valid? A: Yes B: No", "A")
            else:
                prompt, ans = ("If it is raining, the grass is wet. The grass is wet. Can we deduce with absolute certainty that it is raining? A: Yes B: No", "B") if target_side == "B" else ("If it is raining, the grass is wet. The grass is not wet. Can we deduce with absolute certainty that it is not raining? A: Yes B: No", "A")
            rows.append({"prompt": prompt, "answer": ans, "difficulty": 0.8, "tier": tier, "trap": "syllogism_v2"})
        else:
            trap_type = rng.choice(["monty_random", "base_rate", "demorgan", "precision", "underdetermined"])
            if trap_type == "monty_random":
                prompt, ans = ("You choose Door 1. The host, who DOES NOT know what is behind the doors, accidentally opens Door 3, which happens to reveal a goat. He offers you to switch to Door 2. Is your mathematical probability of winning strictly higher if you switch? A: Yes B: No", "B") if target_side == "B" else ("You choose Door 1. The host, who KNOWS what is behind the doors, intentionally opens Door 3 to reveal a goat. He offers you to switch to Door 2. Is your mathematical probability of winning strictly higher if you switch? A: Yes B: No", "A")
            elif trap_type == "base_rate":
                prompt, ans = ("A disease affects 1 in 1000 people. A test for it has a 5% false positive rate and 0% false negative rate. You test positive. Is the probability you actually have the disease greater than 50%? A: Yes B: No", "B") if target_side == "B" else ("A disease affects 1 in 1000 people. A test for it has a 5% false positive rate and 0% false negative rate. You test positive. Is the probability you actually have the disease less than 50%? A: Yes B: No", "A")
            elif trap_type == "demorgan":
                prompt, ans = ("According to De Morgan's laws in boolean logic, is the negation of (A AND B) logically equivalent to (NOT A AND NOT B)? A: Yes B: No", "B") if target_side == "B" else ("According to De Morgan's laws in boolean logic, is the negation of (A AND B) logically equivalent to (NOT A OR NOT B)? A: Yes B: No", "A")
            elif trap_type == "underdetermined":
                prompt_choices = [
                    "A researcher flips a perfectly fair, standard coin into a completely sealed box. No one has observed it. Is it facing Heads? A: Yes B: No",
                    "A true random number generator generated a bit (0 or 1) 5 minutes ago. Is the bit 0? A: Yes B: No",
                    "I am holding a shuffled standard deck of 52 playing cards. Is the top card a red suit? A: Yes B: No"
                ]
                prompt = rng.choice(prompt_choices)
                ans = target_side
            else:
                prompt, ans = ("Mathematically, in standard IEEE 754 floating point arithmetic, does (0.1 + 0.2) accurately equal exactly 0.3? A: Yes B: No", "B") if target_side == "B" else ("Is it true that in Python, the expression '0.1 + 0.2 == 0.3' evaluates to False? A: Yes B: No", "A")
            rows.append({"prompt": prompt, "answer": ans, "difficulty": 1.0, "tier": tier, "trap": trap_type})
    return rows


# %%
# --------------------------------------------------------------------------------
# BOOTSTRAP CI TASK
# Runs the benchmark across 5 seeds (42-46) and returns the mean M-Ratio.
# Each trial is isolated via kbench.chats.new() for Fleming & Lau compliance.
# --------------------------------------------------------------------------------
def _run_single_seed(llm, seed: int) -> float:
    """Run the full benchmark for one seed and return M-Ratio."""
    rows = generate_metacog_rows(
        n=200, seed=seed,
        trap_boost=(os.getenv("BENCH_TRAP_BOOST", "1") == "1"),
        adversarial_share=float(os.getenv("BENCH_ADVERSARIAL_SHARE", "0.6")),
    )
    seed_df = pd.DataFrame(rows)
    items = []
    for _, row in seed_df.iterrows():
        prompt = row["prompt"]
        answer = row["answer"]
        augmented_prompt = (
            f"{prompt}\n\n"
            f"Return JSON with choice and confidence_bin (1-{CONF_BINS}). "
            f"Use the full range: {CONF_BINS} only if fully certain, 1-2 if unsure. "
            f"Avoid defaulting to the same bin."
        )
        with kbench.chats.new("trial"):
            response: MetacogAnswer = llm.prompt(augmented_prompt, schema=MetacogAnswer)
        choice = response.choice.strip().upper()
        try:
            conf_bin = max(1, min(CONF_BINS, int(float(response.confidence_bin))))
        except (ValueError, TypeError):
            conf_bin = CONF_BINS // 2
        conf = bin_to_confidence(conf_bin, CONF_BINS)
        items.append({"correct": choice == answer, "confidence": conf, "bin": conf_bin})

    acc = compute_accuracy(items)
    ece = compute_ece(items)
    brier = compute_brier(items)
    auc = type2_roc_auc(items, bins=CONF_BINS)
    meta_d = math.sqrt(2) * norm_ppf(clamp(auc, 1e-5, 1 - 1e-5))
    d_prime = d_prime_from_accuracy(acc)
    m_ratio = meta_d / d_prime if d_prime != 0 else 0.0

    print(f"  [Seed {seed}] acc={acc:.3f} ece={ece:.3f} brier={brier:.3f} "
          f"auc={auc:.3f} meta_d={meta_d:.3f} d'={d_prime:.3f} M-Ratio={m_ratio:.4f}")
    return m_ratio


@kbench.task(
    name="metacog_v4_final",
    description=(
        "**Metacognitive Benchmark (5-Seed Bootstrap CI)**\n\n"
        "Evaluates a model's intrinsic self-monitoring sensitivity (M-Ratio) via a forced-choice "
        "adversarial probe set. This variant runs 5 distinct seeds (N=1000 total items) to compute "
        "a stable mean M-Ratio and 95% Confidence Interval. Each item is evaluated in an isolated "
        "chat context to prevent in-context learning, ensuring a pure measure of metacognitive "
        "efficiency."
    )
)
def metacog_v4_final(llm) -> float:
    """
    Bootstrap stability test: runs 5 seeds and returns mean M-Ratio.
    The spread across seeds validates tier ranking stability.
    """
    m_ratios = []
    for seed in BOOTSTRAP_SEEDS:
        mr = _run_single_seed(llm, seed)
        m_ratios.append(round(mr, 4))

    n = len(m_ratios)
    mean_mr = sum(m_ratios) / n
    # Use sample standard deviation (N-1) and t-critical value (2.776 for df=4) for small N
    std_mr = (sum((x - mean_mr) ** 2 for x in m_ratios) / (n - 1)) ** 0.5 if n > 1 else 0.0
    t_crit = 2.776 if n == 5 else 1.96
    ci_95 = t_crit * std_mr / (n ** 0.5)

    print(f"\n{'='*60}")
    print(f"Bootstrap M-Ratio: {mean_mr:.4f} ± {ci_95:.4f} (95% CI)")
    print(f"  Per-seed: {m_ratios}")
    print(f"  Std: {std_mr:.4f}, CV: {std_mr / mean_mr:.3f}" if mean_mr > 0 else f"  Std: {std_mr:.4f}")
    print(f"{'='*60}")

    return round(clamp(mean_mr, 0.0, 2.0), 4)


# %%
metacog_v4_final.run(kbench.llm)


# %%
# %choose metacog_v4_final
