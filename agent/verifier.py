# agent/verifier.py
import json
import re
import logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger("verifier")

class StrategyTree(BaseModel):
    level: str = Field(..., pattern="^(LOGIC_SYLLOGISM|QUANTITATIVE|COUNTERFACTUAL)$")
    prompt_vector: str
    success_criteria: str
    chandra_heuristic: str
    expected_dgs_delta: float

class CriticReview(BaseModel):
    verdict: str = Field(..., pattern="^(APPROVE|REJECT)$")
    dgs_estimate: float
    justification: str
    risks: List[str]
    suggested_fix: Optional[str] = None

class TargetResponse(BaseModel):
    answer: str
    confidence: int = Field(..., ge=0, le=100)

class MetacogVerifier:
    @staticmethod
    def extract_json(text: str) -> Optional[Dict[str, Any]]:
        """
        Robust JSON extraction from LLM text (markdown fences or raw braces).
        """
        try:
            # Try markdown fences first
            match = re.search(r"```json\s*([\s\S]*?)```", text)
            if match:
                return json.loads(match.group(1))
            
            # Try raw braces
            match = re.search(r"({[\s\S]*})", text)
            if match:
                return json.loads(match.group(1))
        except Exception as e:
            logger.error(f"JSON extraction failed: {e}")
        return None

    @staticmethod
    def validate_strategy(text: str) -> StrategyTree:
        data = MetacogVerifier.extract_json(text)
        if not data:
            raise ValueError("No JSON found in Strategy input.")
        return StrategyTree(**data)

    @staticmethod
    def validate_review(text: str) -> CriticReview:
        data = MetacogVerifier.extract_json(text)
        if not data:
            raise ValueError("No JSON found in Review input.")
        return CriticReview(**data)

    @staticmethod
    def calculate_m_ratio(results: List[Dict[str, Any]]) -> float:
        """
        Deterministic M-Ratio calculation (meta-d' / d').
        Simplified proxy version for Phase 3B stabilization.
        """
        # 1. Calculate Accuracy (d')
        correct = sum(1 for r in results if r.get("correct", False))
        total = len(results)
        if total == 0: return 0.0
        acc = correct / total
        
        # 2. Calculate Metacognitive Sensitivity (meta-d' proxy)
        # Higher confidence on correct answers, lower on incorrect.
        conf_correct = [r.get("confidence", 0) for r in results if r.get("correct", True)]
        conf_wrong = [r.get("confidence", 0) for r in results if not r.get("correct", False)]
        
        avg_conf_correct = sum(conf_correct) / len(conf_correct) if conf_correct else 0
        avg_conf_wrong = sum(conf_wrong) / len(conf_wrong) if conf_wrong else 0
        
        # The gap between confidence on right vs wrong is a proxy for meta-d'
        sensitivity = (avg_conf_correct - avg_conf_wrong) / 100.0
        
        # M-Ratio = meta-d' / d'
        if acc == 0: return 0.0
        return max(0.0, sensitivity / acc)
