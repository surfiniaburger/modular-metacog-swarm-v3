# 3.1) Stage-based evaluation protocol (evaluate the loop, not just the endpoint)

## Key idea
Benchmarks should test the entire adaptation loop:
- diagnosis
- curriculum synthesis
- retraining
- verification
- regression checking

## Mapping to your work
You can stage-evaluate BARRED like:
1) Seed selection purity (dedup success)
2) Predicate quality (falsifiable, grounded)
3) Variant generation quality (minimal deltas, controlled)
4) Verification quality (judge + tool verifier agreement)
5) Dataset yield + diversity (coverage across dimensions)

