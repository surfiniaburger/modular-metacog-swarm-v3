import sys
import os

# Ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcsb_math import calculate_sdt_metrics as rank_sum_metrics
from metacog_metrics_reference import report_thesis_metrics as trapezoidal_metrics

def compare_results(correct_binary, confidence_bins):
    rs = rank_sum_metrics(correct_binary, confidence_bins)
    tz = trapezoidal_metrics(correct_binary, confidence_bins)
    
    print("\n" + "="*60)
    print("📈 METRIC COMPARISON: RANK-SUM VS TRAPEZOIDAL")
    print("="*60)
    print(f"{'Metric':<15} | {'Rank-Sum (WMW)':<18} | {'Trapezoidal':<18}")
    print("-" * 60)
    print(f"{'Accuracy':<15} | {rs['accuracy']:<18.4f} | {tz['accuracy']:<18.4f}")
    print(f"{'d-prime':<15} | {rs['d_prime']:<18.4f} | {tz['d_prime']:<18.4f}")
    print(f"{'meta-d-prime':<15} | {rs['meta_d_prime']:<18.4f} | {tz['meta_d_prime']:<18.4f}")
    print(f"{'AUC':<15} | {rs['auc']:<18.4f} | {tz['auroc2']:<18.4f}")
    print(f"{'M-Ratio':<15} | {rs['m_ratio']:<18.4f} | {tz['m_ratio']:<18.4f}")
    print(f"{'Stability':<15} | {str(rs['is_stable']):<18} | {str(tz['is_stable']):<18}")
    print("="*60)
    
    delta = tz['m_ratio'] - rs['m_ratio']
    print(f"Δ M-Ratio (Trap - RankSum): {delta:+.4f}")
    if abs(delta) > 0.1:
        print("⚠️ Warning: Significant methodology delta detected.")
    else:
        print("✅ Methods are in close agreement.")

if __name__ == "__main__":
    # Test with skewed data (where methods often diverge)
    # Model is correct but hesitant on correctness, wrong but confident on errors
    test_hits = [True, True, True, True, False, False, False]
    test_conf = [4, 5, 2, 3, 6, 5, 5]
    compare_results(test_hits, test_conf)
