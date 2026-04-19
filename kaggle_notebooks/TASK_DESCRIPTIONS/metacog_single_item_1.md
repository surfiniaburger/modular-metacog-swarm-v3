# Task: metacog_single_item_1 (Static Logic Baseline)

## 🎯 Objective
Evaluates intrinsic self-monitoring sensitivity via a forced-choice adversarial probe set (N=200). This task establishes the model's "Type-1" reasoning performance and "Type-2" metacognitive efficiency in a single-turn, non-dynamic context.

## 🧠 Description
Models return a choice (A/B) and a confidence bin (1-6). We isolate metacognitive efficiency from raw accuracy using Signal Detection Theory (SDT) metrics.

## 📊 Metrics
* **M-Ratio (meta-d'/d')**: Primary efficiency score.
* **Accuracy (Balanced)**: Raw reasoning capability.
* **Brier Score / ECE**: Confidence calibration.
