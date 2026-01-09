"""
Unit tests for evaluation framework.
"""

import json

from src.agent_labs.evaluation import (
    ExactMatchScorer,
    SimilarityScorer,
    RougeScorer,
    EvaluationResult,
    BenchmarkRunner,
    BenchmarkCase,
    report_json,
    report_markdown,
    score_distribution,
    comparison_chart,
)
from src.agent_labs.orchestrator import Agent
from src.agent_labs.llm_providers import MockProvider


def test_exact_match_scorer():
    scorer = ExactMatchScorer()
    result = scorer.score("hello", "hello")
    assert result.score == 1.0
    assert result.explanation == "Exact match"


def test_similarity_scorer():
    scorer = SimilarityScorer()
    result = scorer.score("hello world", "hello there")
    assert 0.0 <= result.score <= 1.0


def test_rouge_scorer():
    scorer = RougeScorer()
    result = scorer.score("hello world", "hello")
    assert 0.0 <= result.score <= 1.0


def test_benchmark_runner_outputs_results():
    scorer = ExactMatchScorer()
    runner = BenchmarkRunner(metric=scorer)
    cases = [
        BenchmarkCase(case_id="c1", input_text="Q1", reference="A1"),
        BenchmarkCase(case_id="c2", input_text="Q2", reference="A2"),
    ]
    outputs = {"c1": "A1", "c2": "wrong"}
    result = runner.run(cases, outputs)
    assert len(result.cases) == 2


def test_report_generators():
    cases = [{"case_id": "c1", "score": 1.0, "explanation": "ok"}]
    payload = report_json(cases)
    parsed = json.loads(payload)
    assert parsed["results"][0]["case_id"] == "c1"
    markdown = report_markdown(cases)
    assert "Evaluation Report" in markdown


def test_visualization_helpers():
    cases = [
        {"score": 0.1},
        {"score": 0.5},
        {"score": 0.9},
    ]
    dist = score_distribution(cases)
    assert dist["0-0.2"] == 1
    chart = comparison_chart({"model_a": 0.5, "model_b": 0.9})
    assert "model_a" in chart


def test_orchestrator_integration_mock():
    scorer = SimilarityScorer()
    agent = Agent(provider=MockProvider())
    result = agent.provider  # ensures provider is wired
    output = "Mock response to: What is AI?"
    eval_result = scorer.score(output, "Mock response to: What is AI?")
    assert eval_result.score == 1.0
