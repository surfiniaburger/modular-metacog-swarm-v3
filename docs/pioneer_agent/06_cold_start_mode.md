# 2.5) Cold-start mode (from task description to working model)

## What “cold-start” means here
Given only a natural-language task description, the agent:
- acquires/builds training data
- constructs eval sets
- iterates training/eval until it converges

## Mapping to your repo
Your “cold-start” is roughly:
- task = “security predicate adjudication” (or subtask slices)
- seeds = CVEFixes + GEPA predicate discovery
- eval = your clean-room benchmark

## Key risk
Cold-start pipelines can accidentally overfit to the prompt/interface instead of the task.
This reinforces why B must include grounding signals beyond LLM self-judgment.

