# TODO: Apply Pioneer ideas to BARRED / silver-one

This file is a project-facing checklist derived from `docs/paper.md`.

## A (Determinism) — keep
- [ ] Treat `run record + cassette + outputs` as mandatory artifacts for any “accepted” data.
- [ ] Rollback rule: if a change decreases acceptance quality, revert the change instead of compensating with more data.

## B (Grounding) — next
- [ ] Define a verifier interface (static/dynamic checks) and “unsupported predicate” state.
- [ ] Add a regression set concept for training data acceptance (don’t break previously validated mechanisms).

## C (Scaling) — later
- [ ] Parallelize only after B passes (otherwise you scale noise).
- [ ] Add yield/diversity dashboards so scaling doesn’t silently collapse to one mode.

