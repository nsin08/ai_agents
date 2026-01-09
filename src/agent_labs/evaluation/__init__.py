"""Evaluation framework for agent_labs."""

from .base import Metric
from .scorers import ExactMatchScorer, SimilarityScorer, RougeScorer
from .results import EvaluationResult
from .runner import BenchmarkRunner, BenchmarkCase, BenchmarkResult
from .report import report_json, report_markdown
from .visualization import score_distribution, comparison_chart

__all__ = [
    "Metric",
    "ExactMatchScorer",
    "SimilarityScorer",
    "RougeScorer",
    "EvaluationResult",
    "BenchmarkRunner",
    "BenchmarkCase",
    "BenchmarkResult",
    "report_json",
    "report_markdown",
    "score_distribution",
    "comparison_chart",
]
