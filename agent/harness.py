# agent/harness.py
import os
import logging
from typing import AsyncGenerator, List, Dict, Any, Optional
from typing_extensions import override

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

from agent.verifier import StrategyTree, CriticReview, MetacogVerifier, TargetResponse
from shared.persistence import StateManager, ExperienceStore

logger = logging.getLogger("harness")

class MetacogHarness(BaseAgent):
    """
    Sovereign Metacognitive Harness (Phase 3B Refactor).
    A 'Thick' ADK Custom Agent that implements a deterministic TAO loop
    with Pydantic validation and Experience Store archiving.
    """
    
    # Declare internal agents for specialized roles
    planner: LlmAgent
    executor: LlmAgent
    auditor: LlmAgent
    
    # Declare internal state fields
    state_manager: Any
    experience_store: Any
    iteration_count: int = 0
    
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, name: str = "metacog_harness_v1"):
        # 1. Models from env
        brain_model = os.getenv("BRAIN_MODEL", "ollama/qwen3.5:9b")
        hands_model = os.getenv("HANDS_MODEL", "ollama/qwen2.5-coder:3b")
        critic_model = os.getenv("CRITIC_MODEL", brain_model)

        # 2. Initialize Internal Specialists (Dumb Loop Components)
        # Note: We do NOT bind tools to avoid local model instability. 
        # Discovery Blindness is text-only.
        planner = LlmAgent(
            name="TheBrain",
            model=brain_model,
            instruction=self._get_brain_system(),
        )
        
        executor = LlmAgent(
            name="TheHands",
            model=hands_model,
            instruction=self._get_hands_system()
        )
        
        auditor = LlmAgent(
            name="TheCritic",
            model=critic_model,
            instruction=self._get_critic_system()
        )

        super().__init__(
            name=name,
            planner=planner,
            executor=executor,
            auditor=auditor,
            sub_agents=[planner, executor, auditor],
            state_manager=StateManager(),
            experience_store=ExperienceStore(),
            iteration_count=0
        )

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        import litellm
        self.iteration_count += 1
        iter_id = self.iteration_count
        logger.info(f"--- Harness [Iteration {iter_id}] Logic Starting ---")
        
        context_data = self._get_context_summary()
        
        # --- PHASE 1: STRATEGY (BRAIN) ---
        brain_prompt = f"Iteration {iter_id}. Review history and generate StrategyTree.\n\nContext:\n{context_data}"
        
        yield Event(author=self.planner.name, content=types.Content(parts=[types.Part(text="Analyzing Strategy...")]))
        
        response = await litellm.acompletion(
            model=self.planner.model,
            messages=[
                {"role": "system", "content": self._get_brain_system()},
                {"role": "user", "content": brain_prompt}
            ],
            temperature=0.0
        )
        strategy_raw = response.choices[0].message.content
        yield Event(author=self.planner.name, content=types.Content(parts=[types.Part(text=strategy_raw)]))
            
        try:
            strategy = MetacogVerifier.validate_strategy(strategy_raw)
            logger.info(f"Strategy Validated: {strategy.level}")
        except Exception as e:
            logger.error(f"Strategy Validation Failed: {e}")
            yield Event(author=self.name, content=types.Content(parts=[types.Part(text=f"ERROR: Strategy REJECTED: {e}")]))
            return

        # --- PHASE 2: IMPLEMENTATION (HANDS) ---
        executor_prompt = f"Strategy Adopted: {strategy.model_dump_json()}\nGenerate Implementation details."
        
        yield Event(author=self.executor.name, content=types.Content(parts=[types.Part(text="Implementing Strategy...")]))
        
        response = await litellm.acompletion(
            model=self.executor.model,
            messages=[
                {"role": "system", "content": self._get_hands_system()},
                {"role": "user", "content": executor_prompt}
            ],
            temperature=0.0
        )
        implementation_raw = response.choices[0].message.content
        yield Event(author=self.executor.name, content=types.Content(parts=[types.Part(text=implementation_raw)]))

        # --- PHASE 3: VERIFICATION (CRITIC) ---
        auditor_prompt = f"Evaluate implementation:\n{implementation_raw}\nAgainst Strategy:\n{strategy.model_dump_json()}"
        
        yield Event(author=self.auditor.name, content=types.Content(parts=[types.Part(text="Auditing Implementation...")]))
        
        response = await litellm.acompletion(
            model=self.auditor.model,
            messages=[
                {"role": "system", "content": self._get_critic_system()},
                {"role": "user", "content": auditor_prompt}
            ],
            temperature=0.0
        )
        critic_raw = response.choices[0].message.content
        yield Event(author=self.auditor.name, content=types.Content(parts=[types.Part(text=critic_raw)]))
            
        try:
            review = MetacogVerifier.validate_review(critic_raw)
            if review.verdict == "APPROVE":
                logger.info(f"Harness: Final Approval [DGS={review.dgs_estimate}]")
                self.state_manager.save_iteration_state(iter_id, {
                    "strategy": strategy.model_dump(),
                    "review": review.model_dump(),
                    "status": "APPROVED"
                })
            else:
                logger.warning(f"Harness: Rejected by Critic: {review.justification}")
                self.experience_store.archive_failure(iter_id, strategy_raw, critic_raw)
        except Exception as e:
            logger.error(f"Review Validation Failed: {e}")

        logger.info(f"--- Harness [Iteration {iter_id}] Logic Complete ---")

    def _get_context_summary(self) -> str:
        program_path = "research_env/program.md"
        if not os.path.exists(program_path): return ""
        try:
            with open(program_path, "r") as f:
                content = f.read()
            return content[-2000:] # Tail of context
        except:
            return ""

    def _get_brain_system(self) -> str:
        tools = "read_file, write_to_file, run_benchmark"
        return f"You are TheBrain. Use StrategyTree Pydantic JSON. Tools Text: {tools}. Output JSON."

    def _get_hands_system(self) -> str:
        return "You are TheHands. Implement the StrategyTree. Output details/code."

    def _get_critic_system(self) -> str:
        return "You are TheCritic. Review via CriticReview JSON schema. Output JSON."
