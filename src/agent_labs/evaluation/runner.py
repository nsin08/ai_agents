"""
Benchmark runner for batch evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from .base import Metric
from .results import EvaluationResult


@dataclass
class BenchmarkCase:
    """Single benchmark case."""

    case_id: str
    input_text: str
    reference: str


@dataclass
class BenchmarkResult:
    """Results for a benchmark run."""

    cases: List[Dict[str, object]]


class BenchmarkRunner:
    """Run evaluation for a set of benchmark cases."""

    def __init__(self, metric: Metric) -> None:
        self.metric = metric

    def run(self, cases: Iterable[BenchmarkCase], outputs: Dict[str, str]) -> BenchmarkResult:
        results = []
        for case in cases:
            output = outputs.get(case.case_id, "")
            result = self.metric.score(output, case.reference)
            results.append(
                {
                    "case_id": case.case_id,
                    "input": case.input_text,
                    "reference": case.reference,
                    "output": output,
                    "score": result.score,
                    "explanation": result.explanation,
                    "details": result.details,
                }
            )
        return BenchmarkResult(cases=results)
