# sentinel/classifier.py
from typing import Optional
from shared.types import IntentCategory, IntentResult

class IntentClassifier:
    """
    Heuristic-based intent classifier ported from med_safety_gym.
    Used by the Sentinel MCP server.
    """
    def __init__(self):
        self.refinement_keywords = ["i meant", "instead", "specifically", "rather", "switching", "switch", "change to"]
        self.expansion_keywords = ["what about", "also", "and for", "how about", "for it"]
        self.follow_up_keywords = ["what are", "how does", "why is", "is it", "does it", "can it"]
        self.correction_keywords = ["no,", "not exactly", "incorrect", "wrong"]

    def classify(self, message: str) -> IntentResult:
        msg = message.lower()
        category = IntentCategory.NEW_TOPIC
        is_correction = any(kw in msg for kw in self.correction_keywords) or msg.startswith("no ")

        if any(kw in msg for kw in self.refinement_keywords):
            category = IntentCategory.REFINEMENT
        elif any(kw in msg for kw in self.expansion_keywords):
            category = IntentCategory.EXPANSION
        elif any(kw in msg for kw in self.follow_up_keywords):
            category = IntentCategory.FOLLOW_UP
            
        return IntentResult(category=category, is_correction=is_correction)
