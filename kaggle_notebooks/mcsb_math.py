# --------------------------------------------------------------------------------
# 📐 MCSB Math Library (mcsb_math.py)
# Core Signal Detection Theory and Metacognitive Metric Utilities.
# --------------------------------------------------------------------------------

import math
from typing import List, Dict

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

def calculate_sdt_metrics(correct_binary_list: List[bool], confidence_list: List[int]) -> Dict[str, float]:
    """Computes d' and meta-d' using Rank-Sum (WMW) AUC. Includes d' Stability Guard."""
    if not correct_binary_list:
        return {"accuracy": 0, "m_ratio": 0, "is_stable": False}
    
    acc     = sum(correct_binary_list) / len(correct_binary_list)
    d_prime = math.sqrt(2) * norm_ppf(max(min(acc, 0.999), 0.001))
    
    correct_conf = [c for i, c in enumerate(confidence_list) if correct_binary_list[i]]
    wrong_conf   = [c for i, c in enumerate(confidence_list) if not correct_binary_list[i]]
    
    auc = 0.5
    if correct_conf and wrong_conf:
        hits = sum((1 if c > w else 0.5 if c == w else 0) for c in correct_conf for w in wrong_conf)
        auc  = hits / (len(correct_conf) * len(wrong_conf))
    
    meta_d  = math.sqrt(2) * norm_ppf(max(min(auc, 0.999), 0.001))
    
    # --- d' STABILITY GUARD ---
    is_stable = abs(d_prime) >= 0.5
    if is_stable:
        m_ratio = meta_d / d_prime
    else:
        m_ratio = 0.0
        
    return {
        "accuracy": acc, 
        "meta_d_prime": meta_d, 
        "d_prime": d_prime, 
        "m_ratio": m_ratio, 
        "auc": auc,
        "is_stable": is_stable
    }
