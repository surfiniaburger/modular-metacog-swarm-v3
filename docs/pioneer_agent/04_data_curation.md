# 2.3) Data curation rules (quality > quantity)

## Core curation principles highlighted
The paper’s curation section focuses on rules like:
- paired examples (“gold” + “hard negative” per tricky case)
- label balancing (avoid dominance)
- context-length matching (training should resemble real inputs)
- entity diversification (avoid memorizing surface forms)
- chain-of-thought annotation for generation tasks (teach the “why”)

## Mapping to your pipeline
Direct analogs:
- “gold + hard negative” ≈ BARRED boundary pairs (True/False) around the same predicate.
- “context-length matching” ≈ keep snippets and debate traces within the distribution your student will see.
- “diversification” ≈ your seed loader + dedup + fuzzy shingling + sharded sampling.

## What to add when you do B
Grounding can become a curation constraint:
- reject samples where the judge can’t cite concrete evidence hooks
- reject samples where an external verifier contradicts the claimed mechanism

