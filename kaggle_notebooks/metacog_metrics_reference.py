# --------------------------------------------------------------------------------
# 📐 Metacognitive Metrics Reference Engine (Thesis Standard)
# Standardizes on Trapezoidal Integration (AUROC2) and d' Stability Guards.
# --------------------------------------------------------------------------------

import math
from typing import List, Dict, Tuple

def norm_ppf(p: float) -> float:
    """Acklam's approximation for inverse cumulative normal distribution."""
    a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.357751867269, -30.66479806614716, 2.506628277459239]
    b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572]
    c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783]
    d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416]
    plow, phigh = 0.02425, 1 - 0.02425
    p = max(1e-9, min(p, 1 - 1e-9))
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q, r = p - 0.5, (p - 0.5)**2
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)

def calculate_trapezoidal_auc(correct_binary: List[bool], confidence_bins: List[int], n_bins: int = 6) -> float:
    """Calculates AUROC2 using the Trapezoidal Rule across discrete confidence criteria."""
    if not correct_binary:
        return 0.5
    
    # Separate groups
    correct_indices = [i for i, val in enumerate(correct_binary) if val]
    wrong_indices   = [i for i, val in enumerate(correct_binary) if not val]
    
    if not correct_indices or not wrong_indices:
        return 0.5
    
    n_correct = len(correct_indices)
    n_wrong   = len(wrong_indices)
    
    # Build ROC points by sweeping criteria k from 1 to n_bins
    # Point (FA, Hit) represents P(Conf >= k | wrong) and P(Conf >= k | correct)
    roc_points = []
    for k in range(1, n_bins + 1):
        hit = sum(1 for i in correct_indices if confidence_bins[i] >= k) / n_correct
        fa  = sum(1 for i in wrong_indices if confidence_bins[i] >= k) / n_wrong
        roc_points.append((fa, hit))
    
    # Add anchor points (0,0) and (1,1) if not present
    # ROC points should be sorted by FA (x-axis)
    roc_points = sorted(roc_points, key=lambda x: x[0])
    if roc_points[0] != (0.0, 0.0):
        roc_points = [(0.0, 0.0)] + roc_points
    if roc_points[-1] != (1.0, 1.0):
        roc_points = roc_points + [(1.0, 1.0)]
        
    # Trapezoidal integration
    auc = 0.0
    for i in range(1, len(roc_points)):
        x0, y0 = roc_points[i-1]
        x1, y1 = roc_points[i]
        auc += (x1 - x0) * (y0 + y1) / 2.0
        
    return max(0.0, min(1.0, auc))

def report_thesis_metrics(correct_binary: List[bool], confidence_bins: List[int], n_bins: int = 6) -> Dict:
    """Computes the full Reference Metric set with stability guards."""
    acc = sum(correct_binary) / len(correct_binary) if correct_binary else 0.0
    d_prime = math.sqrt(2) * norm_ppf(max(0.001, min(acc, 0.999)))
    
    auc = calculate_trapezoidal_auc(correct_binary, confidence_bins, n_bins)
    meta_d = math.sqrt(2) * norm_ppf(max(0.001, min(auc, 0.999)))
    
    # --- d' STABILITY GUARD ---
    # Implements the |d'| < 0.5 threshold to avoid division artifacts.
    is_stable = abs(d_prime) >= 0.5
    if is_stable:
        m_ratio = meta_d / d_prime
    else:
        m_ratio = 0.0 # Suppressed due to instability
        
    return {
        "accuracy": acc,
        "d_prime": d_prime,
        "auroc2": auc,
        "meta_d_prime": meta_d,
        "m_ratio": m_ratio,
        "is_stable": is_stable,
        "method": "Trapezoidal (Thesis Reference)"
    }

if __name__ == "__main__":
    # Example validation trace
    test_hits = [True, True, True, False, False]
    test_conf = [6, 5, 4, 1, 2]
    print(report_thesis_metrics(test_hits, test_conf))
