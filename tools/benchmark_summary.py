import json
import os
import sys
from statistics import mean, pstdev

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from shared.utils import normalize_model_name

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "research_env", "results")
SUMMARY_JSON = os.path.join(RESULTS_DIR, "summary.json")
SUMMARY_PNG = os.path.join(RESULTS_DIR, "summary.png")
SUMMARY_TXT = os.path.join(RESULTS_DIR, "summary.txt")
SUMMARY_RELIABILITY_PNG = os.path.join(RESULTS_DIR, "summary_reliability.png")

def _expected_models_from_env() -> list[str]:
    strong = normalize_model_name(os.getenv("BENCH_MODEL_STRONG", "qwen3.5:9b"))
    weak = normalize_model_name(os.getenv("BENCH_MODEL_WEAK", "qwen2.5-coder:7b"))
    return [strong, weak]

def load_results():
    entries = []
    tasklogs = []
    if not os.path.isdir(RESULTS_DIR):
        return entries, tasklogs
    min_iter = int(os.getenv("BENCH_MIN_ITERATION", "2"))
    for name in os.listdir(RESULTS_DIR):
        if name.startswith("iteration_") and name.endswith("_results.json"):
            try:
                iter_str = name.replace("iteration_", "").replace("_results.json", "")
                iter_num = int(iter_str)
            except ValueError:
                iter_num = None
            if iter_num is not None and iter_num < min_iter:
                continue
            path = os.path.join(RESULTS_DIR, name)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                entries.append((name, data))
            except Exception as e:
                print(f"Warning: could not load or parse {path}: {e}")
        if name.startswith("iteration_") and name.endswith("_tasklog.json"):
            try:
                iter_str = name.replace("iteration_", "").replace("_tasklog.json", "")
                iter_num = int(iter_str)
            except ValueError:
                iter_num = None
            if iter_num is not None and iter_num < min_iter:
                continue
            path = os.path.join(RESULTS_DIR, name)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                tasklogs.append((name, data))
            except Exception as e:
                print(f"Warning: could not load or parse {path}: {e}")
    return sorted(entries, key=lambda x: x[0]), sorted(tasklogs, key=lambda x: x[0])

def summarize(entries):
    dgs_values = []
    meta_series = []
    for name, data in entries:
        dgs = data.get("dgs")
        if isinstance(dgs, (int, float)):
            dgs_values.append((name, float(dgs)))
        models = data.get("models", {})
        if isinstance(models, dict) and models:
            meta_series.append((name, models))
    if not dgs_values:
        return None

    values = [v for _, v in dgs_values]
    avg = mean(values)
    sd = pstdev(values) if len(values) > 1 else 0.0
    cv = (sd / avg) if avg != 0 else float("inf")

    if len(values) < 3:
        signal = "insufficient_samples"
    elif cv < 0.2:
        signal = "clear"
    elif cv < 0.4:
        signal = "moderate"
    else:
        signal = "muffled"

    return {
        "count": len(values),
        "mean_dgs": round(avg, 4),
        "stdev_dgs": round(sd, 4),
        "cv": round(cv, 4) if cv != float("inf") else "inf",
        "signal_quality": signal,
        "values": dgs_values,
        "meta_series": meta_series,
    }

def _reliability_curve(task_log, model_name, bins: int = 10):
    if not task_log:
        return [], []
    bins = max(1, int(bins))
    buckets = [[] for _ in range(bins)]
    for row in task_log:
        model = row.get(model_name, {})
        conf = model.get("confidence")
        correct = model.get("correct")
        if conf is None or correct is None:
            continue
        conf = max(0.0, min(1.0, float(conf)))
        idx = min(bins - 1, int(conf * bins))
        buckets[idx].append((conf, bool(correct)))
    xs = []
    ys = []
    for b in range(bins):
        if not buckets[b]:
            continue
        conf_mean = sum(c for c, _ in buckets[b]) / len(buckets[b])
        acc_mean = sum(1 for _, corr in buckets[b] if corr) / len(buckets[b])
        xs.append(conf_mean)
        ys.append(acc_mean)
    return xs, ys

def write_summary_outputs():
    entries, tasklogs = load_results()
    summary = summarize(entries)
    if not summary:
        return None

    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(SUMMARY_JSON, "w") as f:
        json.dump(summary, f, indent=2)

    lines = []
    lines.append("Benchmark Summary")
    lines.append(f"Count: {summary['count']}")
    lines.append(f"Mean DGS: {summary['mean_dgs']}")
    lines.append(f"Stdev DGS: {summary['stdev_dgs']}")
    lines.append(f"CV: {summary['cv']}")
    lines.append(f"Signal Quality: {summary['signal_quality']}")
    lines.append("")
    lines.append("Per-iteration DGS:")
    for name, val in summary["values"]:
        lines.append(f"{name}: {val}")
    if summary.get("meta_series"):
        # Include latest meta-d' snapshot if available
        latest_name, latest_models = summary["meta_series"][-1]
        expected_models = _expected_models_from_env()
        latest_model_names = [normalize_model_name(n) for n in latest_models.keys()]
        if set(expected_models) != set(latest_model_names):
            lines.append("")
            lines.append("WARNING: Model names in results do not match BENCH_MODEL_STRONG/WEAK.")
            lines.append(f"Expected: {expected_models}")
            lines.append(f"Found: {latest_model_names}")
        lines.append("")
        lines.append(f"Latest Meta-d' Snapshot ({latest_name}):")
        for model_name, metrics in latest_models.items():
            if not isinstance(metrics, dict):
                continue
            d_prime = metrics.get("d_prime")
            meta_d = metrics.get("meta_d_prime")
            m_ratio = metrics.get("m_ratio")
            if d_prime is None and meta_d is None and m_ratio is None:
                continue
            lines.append(f"{model_name}: d'={d_prime} meta-d'={meta_d} m_ratio={m_ratio}")
    with open(SUMMARY_TXT, "w") as f:
        f.write("\n".join(lines))

    # Optional trend plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        xs = list(range(1, len(summary["values"]) + 1))
        ys = [v for _, v in summary["values"]]
        fig, axes = plt.subplots(3, 1, figsize=(7, 7))
        axes[0].plot(xs, ys, marker="o")
        axes[0].set_title("DGS Trend")
        axes[0].set_xlabel("Iteration")
        axes[0].set_ylabel("DGS")

        # Meta-d' and M-ratio trends (if available)
        if summary.get("meta_series"):
            model_names = list(summary["meta_series"][0][1].keys())
            for model_name in model_names:
                d_primes = []
                meta_ds = []
                m_ratios = []
                for _, models in summary["meta_series"]:
                    metrics = models.get(model_name, {})
                    d_primes.append(metrics.get("d_prime"))
                    meta_ds.append(metrics.get("meta_d_prime"))
                    m_ratios.append(metrics.get("m_ratio"))
                axes[1].plot(xs, meta_ds, marker="o", label=f"{model_name} meta-d'")
                axes[2].plot(xs, m_ratios, marker="o", label=f"{model_name} M-ratio")
            axes[1].set_title("Meta-d' Trend")
            axes[1].set_xlabel("Iteration")
            axes[1].set_ylabel("meta-d'")
            axes[1].legend()
            axes[2].set_title("M-ratio Trend")
            axes[2].set_xlabel("Iteration")
            axes[2].set_ylabel("M-ratio")
            axes[2].legend()
        else:
            axes[1].set_visible(False)
            axes[2].set_visible(False)

        plt.tight_layout()
        plt.savefig(SUMMARY_PNG)
        plt.close()
    except Exception:
        pass

    # Optional reliability diagram (latest tasklog)
    try:
        if tasklogs:
            latest_name, latest_log = tasklogs[-1]
            task_log = latest_log.get("task_log", [])
            if task_log:
                import matplotlib
                matplotlib.use("Agg")
                import matplotlib.pyplot as plt
                # Infer model names from first row
                model_names = []
                for key in task_log[0].keys():
                    if key in ("task_index", "prompt", "choices", "correct_index", "difficulty"):
                        continue
                    if isinstance(task_log[0].get(key), dict):
                        model_names.append(key)
                plt.figure(figsize=(5, 5))
                plt.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1)
                for model_name in model_names:
                    xs, ys = _reliability_curve(task_log, model_name, bins=10)
                    if xs and ys:
                        plt.plot(xs, ys, marker="o", label=model_name)
                plt.title(f"Reliability Diagram ({latest_name})")
                plt.xlabel("Mean Confidence")
                plt.ylabel("Empirical Accuracy")
                plt.legend()
                plt.tight_layout()
                plt.savefig(SUMMARY_RELIABILITY_PNG)
                plt.close()
    except Exception:
        pass

    return summary

def main():
    summary = write_summary_outputs()
    if not summary:
        print("No benchmark results found.")
        return
    print("Benchmark Summary")
    print(f"Count: {summary['count']}")
    print(f"Mean DGS: {summary['mean_dgs']}")
    print(f"Stdev DGS: {summary['stdev_dgs']}")
    print(f"CV: {summary['cv']}")
    print(f"Signal Quality: {summary['signal_quality']}")
    print(f"Wrote: {SUMMARY_JSON}")
    expected_models = _expected_models_from_env()
    if summary.get("meta_series"):
        latest_name, latest_models = summary["meta_series"][-1]
        latest_model_names = [normalize_model_name(n) for n in latest_models.keys()]
        if set(expected_models) != set(latest_model_names):
            print("WARNING: Model names in results do not match BENCH_MODEL_STRONG/WEAK.")
            print(f"Expected: {expected_models}")
            print(f"Found: {latest_model_names}")
    if os.path.exists(SUMMARY_PNG):
        print(f"Wrote: {SUMMARY_PNG}")
    if os.path.exists(SUMMARY_RELIABILITY_PNG):
        print(f"Wrote: {SUMMARY_RELIABILITY_PNG}")

if __name__ == "__main__":
    main()
