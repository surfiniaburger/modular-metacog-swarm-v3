# 5) Emergent training strategies + trajectory motifs

## What the paper claims the agent discovers
- CoT supervision when it matters
- prompt/interface fixes masquerading as “model issues”
- rollback as a control mechanism
- broad-to-surgical exploration patterns

## Mapping to BARRED
BARRED should explicitly encode these motifs as policies:
- don’t endlessly expand dataset size
- prefer targeted additions late-stage
- when disagreement persists, treat it as a *spec/predicate problem*, not “try harder”

