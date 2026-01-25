"""Golden-set style evaluation (offline)."""

from __future__ import annotations

from typing import List

from src.agent_labs.evaluation import BenchmarkCase, BenchmarkRunner, ExactMatchScorer

from dataset import GoldenCase
from vector_agent import VectorRagAgent


def run_golden_set(agent: VectorRagAgent, cases: List[GoldenCase]) -> float:
    scorer = ExactMatchScorer()
    runner = BenchmarkRunner(metric=scorer)

    benchmark_cases = [
        BenchmarkCase(case_id=c.case_id, input_text=c.question, reference=c.reference_answer)
        for c in cases
    ]
    outputs = {}
    for c in cases:
        out = agent.answer(c.question, tenant_id=c.tenant_id, request_id=f"req-{c.case_id}")
        outputs[c.case_id] = out["answer"]

    result = runner.run(benchmark_cases, outputs)
    scores = [float(row["score"]) for row in result.cases]
    return sum(scores) / max(1, len(scores))

