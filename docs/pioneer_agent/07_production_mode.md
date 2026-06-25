# 2.6) Production mode (failure-driven continual improvement)

## Pioneer’s “production” framing
Input is a deployed model + labeled failures. The loop:
- builds a failure taxonomy
- confirms weaknesses via targeted probing
- builds a corrective dataset (corrections + hard negatives + replay buffer)
- retrains under explicit regression constraints

## Mapping to BARRED later
Once you have a deployed SecurityDecisionGuard:
- failures become seeds
- BARRED generates boundary variants *around real failure modes*
- replay buffer prevents regressions on previously-correct slices

## Why this matters for “B spec”
B shouldn’t only be about “is the sample grounded?”
It should also support “does this fix one failure without regressing others?”

