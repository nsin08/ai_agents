"""
Evaluation result data structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class EvaluationResult:
    """Represents a scored evaluation result."""

    score: float
    explanation: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "explanation": self.explanation,
            "details": self.details,
        }
