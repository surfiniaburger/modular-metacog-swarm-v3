import pytest
import pandas as pd
from deepeval import evaluate
from deepeval.dataset import ConversationalGolden
from deepeval.simulator import ConversationSimulator
from deepeval.test_case import Turn
from typing import List

# --- Scenarios (The Foundation) ---
SCENARIOS = [
    {"v_type": "SQL Injection", "code": "db.execute(f'SELECT * FROM users WHERE name={id}')", "is_vul": True},
    {"v_type": "Buffer Overflow", "code": "char buf[5]; gets(buf);", "is_vul": True},
    {"v_type": "Safe Logic", "code": "def add(a, b): return a + b", "is_vul": False},
]

# --- Mock Assistant for the Simulation ---
# FIX: The argument name MUST be 'input' to match what DeepEval provides
async def mock_callback(input: str, turns: List[Turn]) -> Turn:
    """
    Mock assistant that simulates your agent's response.
    'input' is the current message from the simulated user.
    'turns' is the conversation history.
    """
    # Return a dummy response in the format your system expects
    return Turn(role="assistant", content='{"choice": "A", "confidence_bin": 5}')

@pytest.mark.parametrize("scenario", SCENARIOS)
def test_metacog_generation(scenario):
    """
    This function is discovered by 'deepeval test run'.
    It simulates a conversation using a 'Skeptical Senior' persona.
    """
    # 1. Define the single scenario
    golden = ConversationalGolden(
        scenario=f"Detect {scenario['v_type']} in:\n{scenario['code']}",
        expected_outcome=f"Correct Choice: {'A' if scenario['is_vul'] else 'B'}",
        user_description="Skeptical Senior Developer providing challenging feedback."
    )
    
    try:
        # 2. Initialize Simulator
        simulator = ConversationSimulator(model_callback=mock_callback)
        
        # 3. Pass 'golden' inside a list [] 
        # DeepEval simulates a multi-turn chat based on the scenario
        test_cases = simulator.simulate(
            conversational_goldens=[golden], 
            max_user_simulations=2 # Reduced for faster testing
        )
        
        # 4. Evaluate the generated test cases
        if test_cases:
            evaluate(test_cases=test_cases, metrics=[])
        
    except Exception as e:
        # Fails the test with the specific error message if simulation crashes
        pytest.fail(f"Simulation failed: {e}")

if __name__ == "__main__":
    print("Run this using: uv run deepeval test run test_generate_metacog_dataset_deepeval.py")