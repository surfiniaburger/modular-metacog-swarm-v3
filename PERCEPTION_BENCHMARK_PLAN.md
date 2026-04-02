# Perception Track Plan (Future Benchmark)

## Goal
Design a perception‑focused benchmark that isolates **depth perception**, **visual salience/attention**, and **inhibitory control** using controlled evidence rather than factual recall.

## Why This Track
The “visual cliff” concept highlights a core perceptual faculty: models should respond to *evidence* of depth cues rather than “knowing” the experiment. This track tests **perceptual inference under ambiguity** and **confidence calibration** when evidence is weak or conflicting.

## Core Principle
Tasks must be **evidence‑driven**:
- Provide synthetic cues (even if text‑encoded) that require perceptual inference.
- Avoid questions that can be answered by memorized facts.

## Task Families (Draft)

### 1) Depth Cue Inference (Text‑Encoded)
**Input:** Structured descriptions of scene geometry with conflicting cues (texture gradient, occlusion, size constancy).  
**Output:** Forced choice (near/far) + confidence bin.  
**Trap:** Provide high‑salience but misleading cue (e.g., size cue conflicts with texture gradient).

### 2) Visual Cliff Analogs (Symbolic Grids)
**Input:** ASCII grids with implied drop‑offs (pattern density, horizon breaks).  
**Output:** Safe path choice + confidence bin.  
**Metric:** Correctness + calibration.  
**Trap:** “Glass floor” cases where safe path looks unsafe.

### 3) Attention Filtering
**Input:** Long descriptions with a single critical depth cue buried in irrelevant content.  
**Output:** Identify the decisive cue + forced choice.  
**Metric:** Attention robustness vs length.

### 4) Inhibitory Control under Ambiguity
**Input:** Two plausible actions; one is risky based on subtle perceptual cue.  
**Output:** Action choice + “hesitation” confidence (lower if ambiguous).  
**Metric:** Calibration error vs riskiness.

## Metrics (Aligned with Current Pipeline)
- Accuracy
- ECE / Brier
- Type‑2 ROC + meta‑d′ (approx)
- DGS (strong vs weak model gap)

## Output Artifacts
- `tasks_perception_v1.jsonl`
- `benchmark_perception.py`
- `summary_perception.json` + plots
- `REPORT_PERCEPTION.md`

## Implementation Notes
- Mirror the metacog pipeline: confidence bins, A2A‑decoupled runs, bootstrap CIs.
- Ensure tasks are **held‑out** and not trivially searchable.
- Consider a small human baseline slice (optional).

## Scope Boundaries
- Text‑only analogs are acceptable for now, but should **encode perceptual cues**, not trivia.
- Avoid “name the experiment” prompts.

## Next Steps
1. Define 30–50 prototype tasks with explicit cue conflicts.
2. Build a simple generator for grid‑based depth cues.
3. Run a 9B vs 3B pilot to validate DGS signal.
