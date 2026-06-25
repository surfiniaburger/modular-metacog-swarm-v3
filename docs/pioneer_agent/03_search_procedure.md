# 2.2) Search procedure (optimize pipelines, not just weights)

## Pioneer’s key framing
Define a training pipeline as a tuple:
- `D`: dataset spec (composition + curation constraints)
- `H`: hyperparameters (model, LR, epochs, LoRA rank, prompt)
- `S`: learning strategy (format, teacher, eval method)

Then do search over pipelines with:
- a validation score `f(π)`
- a regression counter `r(π; R)` with a strict threshold (paper uses absolute count)

## Mapping to BARRED
BARRED is also pipeline search, just with different knobs:
- `D`: which seeds, which boundary variants, which judge traces
- `H`: which student base, LoRA, etc. (later)
- `S`: debate/judge prompting, verifier strategy, refinement policy

## Practical “stop drift” rule
Don’t let “more data” substitute for understanding.
If your validation score drops, Pioneer’s behavior is: **rollback**.
That’s a strong guard against “hallucinated progress”.

