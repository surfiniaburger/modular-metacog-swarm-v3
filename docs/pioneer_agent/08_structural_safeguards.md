# 2.7) Structural safeguards (anti-regression mechanisms)

## What to steal
Even if your metrics are noisy, safeguards should be strict:
- explicit regression gates
- rollback as default reaction to score drops
- provenance logs to reproduce decisions

## Mapping to A (done) and B (next)
- A gives you repeatability.
- B should add *independent anchors* so you’re not repeating the same hallucination.
- Together, A+B yield “repeatable truth-seeking”, not “repeatable storytelling”.

