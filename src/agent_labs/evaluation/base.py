"""
Evaluation base abstractions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from .results import EvaluationResult


class Metric(ABC):
    """Abstract base class for evaluation metrics."""

    name: str

    @abstractmethod
    def score(self, output: str, reference: str, **kwargs: Any) -> EvaluationResult:
        """Score output against reference."""
        raise NotImplementedError
