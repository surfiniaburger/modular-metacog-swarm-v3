# shared/types.py
from enum import Enum, auto
from dataclasses import dataclass

class IntentCategory(Enum):
    NEW_TOPIC = auto()
    FOLLOW_UP = auto()
    REFINEMENT = auto()
    EXPANSION = auto()
    RECOLLECTION = auto()

@dataclass
class IntentResult:
    category: IntentCategory
    is_correction: bool
    confidence: float = 1.0
