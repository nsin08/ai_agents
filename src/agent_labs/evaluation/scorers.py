"""
Built-in scorers for evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base import Metric
from .results import EvaluationResult


@dataclass
class ExactMatchScorer(Metric):
    """Scores 1.0 if output matches reference exactly."""

    name: str = "exact_match"

    def score(self, output: str, reference: str, **kwargs: Any) -> EvaluationResult:
        match = output.strip() == reference.strip()
        return EvaluationResult(
            score=1.0 if match else 0.0,
            explanation="Exact match" if match else "Mismatch",
            details={"output": output, "reference": reference},
        )


@dataclass
class SimilarityScorer(Metric):
    """Mock similarity scorer using token overlap."""

    name: str = "similarity"

    def score(self, output: str, reference: str, **kwargs: Any) -> EvaluationResult:
        out_tokens = set(output.lower().split())
        ref_tokens = set(reference.lower().split())
        if not ref_tokens:
            return EvaluationResult(
                score=0.0,
                explanation="Empty reference",
                details={"output_tokens": len(out_tokens)},
            )
        overlap = len(out_tokens & ref_tokens)
        score = overlap / max(1, len(ref_tokens))
        return EvaluationResult(
            score=round(score, 3),
            explanation="Token overlap similarity",
            details={"overlap": overlap, "reference_tokens": len(ref_tokens)},
        )


@dataclass
class RougeScorer(Metric):
    """Mock ROUGE scorer (approximation)."""

    name: str = "rouge_mock"

    def score(self, output: str, reference: str, **kwargs: Any) -> EvaluationResult:
        out_tokens = output.lower().split()
        ref_tokens = reference.lower().split()
        if not ref_tokens:
            return EvaluationResult(
                score=0.0,
                explanation="Empty reference",
                details={"output_tokens": len(out_tokens)},
            )
        overlap = len(set(out_tokens) & set(ref_tokens))
        score = overlap / max(1, len(set(ref_tokens)))
        return EvaluationResult(
            score=round(score, 3),
            explanation="Mock ROUGE overlap",
            details={"overlap": overlap, "reference_tokens": len(set(ref_tokens))},
        )
