# executor/m_ratio.py
import math
import random
from typing import List, Dict, Tuple

def calculate_m_ratio(meta_d, d):
    """
    M-Ratio = meta-d' / d'
    Measures how efficiently the model's confidence reflects its accuracy.
    Ideal for AGI context: High M-Ratio (1.0) means perfect self-awareness.
    Low M-Ratio (< 0.5) means the model is guessing blindly or hallucinating sensitivity.
    """
    if d == 0:
        return 0
    return round(meta_d / d, 3)

def quantify_signal(results: List[Dict[str, float]]):
    """
    Takes a list of responses and confidence scores to estimate M-Ratio.
    (Simplified prototype for Gen-2 bootstrap)
    """
    correct = [r for r in results if r['correct']]
    incorrect = [r for r in results if not r['correct']]
    
    # We measure 'd' as total accuracy delta
    d = len(correct) / len(results)
    
    # We estimate meta-d as confidence-weighted correct vs confidence-weighted incorrect
    meta_d = sum([r['confidence'] for r in correct]) / (sum([r['confidence'] for r in results]) or 1)
    
    return calculate_m_ratio(meta_d, d)

def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))

def _norm_ppf(p: float) -> float:
    """
    Approximate inverse CDF for standard normal distribution.
    Peter John Acklam's rational approximation.
    """
    # Coefficients for the approximation
    a = [
        -3.969683028665376e+01,
        2.209460984245205e+02,
        -2.759285104469687e+02,
        1.383577518672690e+02,
        -3.066479806614716e+01,
        2.506628277459239e+00,
    ]
    b = [
        -5.447609879822406e+01,
        1.615858368580409e+02,
        -1.556989798598866e+02,
        6.680131188771972e+01,
        -1.328068155288572e+01,
    ]
    c = [
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e+00,
        -2.549732539343734e+00,
        4.374664141464968e+00,
        2.938163982698783e+00,
    ]
    d = [
        7.784695709041462e-03,
        3.224671290700398e-01,
        2.445134137142996e+00,
        3.754408661907416e+00,
    ]
    # Define break-points.
    plow = 0.02425
    phigh = 1 - plow

    if p <= 0.0:
        return -float("inf")
    if p >= 1.0:
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

def bin_index(confidence: float, bins: int) -> int:
    if bins <= 1:
        return 1
    conf = _clamp(confidence, 0.0, 1.0)
    idx = int(math.ceil(conf * bins))
    return max(1, min(bins, idx))

def _type2_roc(results: List[Dict[str, float]], bins: int) -> Tuple[List[Tuple[float, float]], float]:
    """
    Build a type-2 ROC using confidence bins.
    Returns (roc_points, auc).
    """
    if not results:
        return [], 0.0
    bins = max(1, int(bins))
    # Precompute bin indices without mutating inputs
    indexed = [
        {"correct": r["correct"], "_bin": bin_index(float(r["confidence"]), bins)}
        for r in results
    ]
    correct = [r for r in indexed if r["correct"]]
    incorrect = [r for r in indexed if not r["correct"]]
    if not correct or not incorrect:
        return [], 0.0

    roc = []
    for k in range(1, bins + 1):
        # "High confidence" threshold at bin >= k
        hit = sum(1 for r in correct if r["_bin"] >= k) / len(correct)
        fa = sum(1 for r in incorrect if r["_bin"] >= k) / len(incorrect)
        roc.append((fa, hit))

    # Sort by false alarm rate
    roc = sorted(roc, key=lambda x: x[0])
    # Ensure endpoints
    if roc[0][0] > 0 or roc[0][1] > 0:
        roc = [(0.0, 0.0)] + roc
    if roc[-1][0] < 1.0 or roc[-1][1] < 1.0:
        roc = roc + [(1.0, 1.0)]

    # Trapezoidal AUC
    auc = 0.0
    for i in range(1, len(roc)):
        x0, y0 = roc[i - 1]
        x1, y1 = roc[i]
        auc += (x1 - x0) * (y0 + y1) / 2.0
    return roc, _clamp(auc, 0.0, 1.0)

def d_prime_from_accuracy_2afc(accuracy: float) -> float:
    """
    Convert 2AFC accuracy to d' under equal-variance SDT:
    d' = sqrt(2) * Phi^-1(accuracy)
    """
    acc = _clamp(float(accuracy), 1e-5, 1 - 1e-5)
    return math.sqrt(2) * _norm_ppf(acc)

def meta_d_prime_from_results(
    results: List[Dict[str, float]],
    bins: int = 4,
    bootstrap: int = 200,
    seed: int = 42,
) -> Dict[str, float]:
    """
    Approximate meta-d' using type-2 ROC AUC.
    meta-d' ~= sqrt(2) * Phi^-1(AUC_type2)
    Returns metrics and bootstrap CIs.
    """
    if not results:
        return {
            "d_prime": 0.0,
            "meta_d_prime": 0.0,
            "m_ratio": 0.0,
            "type2_auc": 0.0,
            "m_ratio_ci": (0.0, 0.0),
            "meta_d_ci": (0.0, 0.0),
        }

    accuracy = compute_accuracy(results)
    d_prime = d_prime_from_accuracy_2afc(accuracy)
    roc, auc = _type2_roc(results, bins=bins)
    if auc <= 0.0:
        meta_d = 0.0
    else:
        meta_d = math.sqrt(2) * _norm_ppf(_clamp(auc, 1e-5, 1 - 1e-5))
    m_ratio = calculate_m_ratio(meta_d, d_prime) if d_prime != 0 else 0.0

    # Bootstrap for CI
    rng = random.Random(seed)
    boot_meta = []
    boot_m = []
    n = len(results)
    for _ in range(max(0, int(bootstrap))):
        sample = [results[rng.randrange(n)] for _ in range(n)]
        acc_s = compute_accuracy(sample)
        d_s = d_prime_from_accuracy_2afc(acc_s)
        _, auc_s = _type2_roc(sample, bins=bins)
        if auc_s <= 0.0:
            meta_s = 0.0
        else:
            meta_s = math.sqrt(2) * _norm_ppf(_clamp(auc_s, 1e-5, 1 - 1e-5))
        m_s = calculate_m_ratio(meta_s, d_s) if d_s != 0 else 0.0
        boot_meta.append(meta_s)
        boot_m.append(m_s)
    def _percentile(values: List[float], pct: float) -> float:
        if not values:
            return 0.0
        values = sorted(values)
        k = (len(values) - 1) * pct
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return float(values[int(k)])
        return float(values[f] * (c - k) + values[c] * (k - f))

    meta_ci = (_percentile(boot_meta, 0.025), _percentile(boot_meta, 0.975))
    m_ci = (_percentile(boot_m, 0.025), _percentile(boot_m, 0.975))

    return {
        "d_prime": round(d_prime, 4),
        "meta_d_prime": round(meta_d, 4),
        "m_ratio": round(m_ratio, 4) if isinstance(m_ratio, float) else m_ratio,
        "type2_auc": round(auc, 4),
        "m_ratio_ci": (round(m_ci[0], 4), round(m_ci[1], 4)),
        "meta_d_ci": (round(meta_ci[0], 4), round(meta_ci[1], 4)),
    }

def compute_accuracy(results: List[Dict[str, float]]) -> float:
    if not results:
        return 0.0
    return sum(1 for r in results if r["correct"]) / len(results)

def compute_brier(results: List[Dict[str, float]]) -> float:
    if not results:
        return 0.0
    return sum((r["confidence"] - (1.0 if r["correct"] else 0.0)) ** 2 for r in results) / len(results)

def compute_ece(results: List[Dict[str, float]], bins: int = 10) -> float:
    """
    Expected Calibration Error for binary correctness with confidence in [0,1].
    """
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

if __name__ == "__main__":
    # Test vector
    test_data = [
        {"correct": True, "confidence": 0.9},
        {"correct": True, "confidence": 0.8},
        {"correct": False, "confidence": 0.2},
    ]
    print(f"Calculated Signal M-Ratio: {quantify_signal(test_data)}")
