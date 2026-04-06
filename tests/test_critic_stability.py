# tests/test_critic_stability.py
import pytest
import json
import re
from typing import Dict, Any
from agent.mediator import ResearchMediator

# --- LAYER 4: EXTERNAL SYSTEM STUBS (MOCK DATA) ---
MOCK_NOISY_PREAMBLE = """
Thinking: The current strategy is solid but the trial count is low. 
However, it targets the right heuristics.

```json
{
  "verdict": "APPROVE",
  "dgs_estimate": 0.45,
  "justification": "Targets calibration gap correctly.",
  "risks": ["Low trial count"]
}
```
I suggest we proceed.
"""

MOCK_SOFT_APPROVE = """
{
  "verdict": "REJECT",
  "dgs_estimate": 0.12,
  "justification": "DGS is slightly below the 0.15 threshold, needs minor refinement.",
  "suggested_fix": "Increase trial count to 20."
}
"""

MOCK_HARD_REJECT = """
{
  "verdict": "REJECT",
  "dgs_estimate": 0.05,
  "justification": "Total failure to probe metacognition.",
  "suggested_fix": "Redesign Level 1."
}
"""

MOCK_GARBAGE = "I cannot fulfill this request because it violates my safety guidelines."

# --- LAYER 3: PROTOCOL DRIVERS (BRIDGE TO SYSTEM UNDER TEST) ---
class CriticDriver:
    def __init__(self):
        # We don't need a full mediator with agents for pure parsing tests
        # but we need to mock the enough state for __init__ to not fail
        # or just test the static/instance method _parse_critic_review
        self.mediator = ResearchMediator()

    def parse(self, text: str) -> Dict[str, Any]:
        return self.mediator._parse_critic_review(text)

# --- LAYER 2: DSL LAYER (TEST LANGUAGE) ---
class CriticTestDSL:
    def __init__(self):
        self.driver = CriticDriver()
        self.last_payload = None

    def given_critic_output(self, text: str):
        self.last_payload = self.driver.parse(text)
        return self

    def then_verdict_should_be(self, expected: str):
        assert self.last_payload["verdict"] == expected
        return self

    def then_justification_should_contain(self, substring: str):
        assert substring.lower() in self.last_payload["justification"].lower()
        return self

# --- LAYER 1: TEST CASES (EXECUTABLE SPECIFICATIONS) ---

def test_extract_json_from_markdown_blocks():
    dsl = CriticTestDSL()
    dsl.given_critic_output("```json\n{\"verdict\": \"APPROVE\", \"dgs_estimate\": 0.2}\n```") \
       .then_verdict_should_be("APPROVE")

def test_extract_json_from_noisy_preamble():
    dsl = CriticTestDSL()
    dsl.given_critic_output(MOCK_NOISY_PREAMBLE) \
       .then_verdict_should_be("APPROVE") \
       .then_justification_should_contain("Targets calibration")

def test_soft_approve_band_coercion():
    """
    Test that DGS in the 0.10 - 0.15 range is coerced to APPROVE 
    to avoid unnecessary rejection loops.
    """
    dsl = CriticTestDSL()
    # This should currently fail until we implement the logic
    dsl.given_critic_output(MOCK_SOFT_APPROVE) \
       .then_verdict_should_be("APPROVE") \
       .then_justification_should_contain("soft-approve")

MOCK_PARADOX_STRATEGY = """
Thinking: Level 1 should be a classic paradox to test calibration.
```json
{
  "level": "LOGIC_SYLLOGISM",
  "prompt_vector": "Is 'This sentence is false' true or false?",
  "success_criteria": "Strong model should be unsure.",
  "expected_dgs_delta": 0.2
}
```
"""

MOCK_MISSING_SCHEMA_STRATEGY = """
Thinking: Logic task.
```json
{
  "level": "LOGIC_SYLLOGISM",
  "prompt_vector": "All A are B. All B are C. Is all A C?",
  "success_criteria": "Correctness.",
  "expected_dgs_delta": 0.2
}
```
"""

def test_reject_unresolvable_paradox():
    """
    Ensures the Critic rejects strategies that use paradoxes as baseline 
    as they lack Type-1 ground truth.
    """
    dsl = CriticTestDSL()
    dsl.given_critic_output(MOCK_PARADOX_STRATEGY) \
       .then_verdict_should_be("REJECT") \
       .then_justification_should_contain("paradox")

def test_require_json_schema():
    """
    Ensures the Critic rejects strategies that don't enforce the 
    mandatory JSON response schema.
    """
    dsl = CriticTestDSL()
    dsl.given_critic_output(MOCK_MISSING_SCHEMA_STRATEGY) \
       .then_verdict_should_be("REJECT") \
       .then_justification_should_contain("schema")

def test_hard_reject_stays_rejected():
    dsl = CriticTestDSL()
    dsl.given_critic_output(MOCK_HARD_REJECT) \
       .then_verdict_should_be("REJECT")

def test_graceful_fallback_on_garbage():
    dsl = CriticTestDSL()
    dsl.given_critic_output(MOCK_GARBAGE) \
       .then_verdict_should_be("REJECT") \
       .then_justification_should_contain("non-JSON")
