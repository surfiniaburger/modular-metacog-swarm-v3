# 2.4) Iteration policy (when to change data vs hyperparams vs stop)

## The main idea
Pioneer uses score bands to choose the next move:
- low score → rework dataset fundamentals
- mid score → tune hyperparameters/recipe with dataset fixed
- high score → add a few targeted examples only
- regression → rollback immediately

## Why this is a big deal for your work
This is the missing “process guardrail” that prevents endless tweaking.

## Suggested port to BARRED (conceptual)
Define explicit bands for:
- “predicate quality” (is the claim falsifiable + grounded?)
- “verification quality” (does judge+verifier agree? how often?)
- “yield” (# accepted samples per seed/hour)

Then decide: repair predicate vs change generator vs change verifier vs stop.

