"""
Integration tests for evaluation framework using real LLM output (Ollama).
"""

import os
import pytest

from src.agent_labs.evaluation import SimilarityScorer, ExactMatchScorer, BenchmarkRunner, BenchmarkCase
from src.agent_labs.llm_providers import OllamaProvider
from src.agent_labs.config import Config


SKIP_OLLAMA = os.getenv("SKIP_OLLAMA", "false").lower() == "true"
pytestmark = pytest.mark.skipif(SKIP_OLLAMA, reason="Ollama tests disabled (set SKIP_OLLAMA=false to run)")


@pytest.mark.asyncio
async def test_similarity_scorer_with_ollama_output():
    provider = OllamaProvider(model=Config.OLLAMA_MODEL, timeout=120)
    try:
        response = await provider.generate(
            "Answer with one sentence: What is Python?",
            max_tokens=50,
            temperature=0.2,
        )
    finally:
        await provider.close()

    scorer = SimilarityScorer()
    result = scorer.score(
        output=response.text,
        reference="Python is a programming language.",
    )

    assert 0.0 <= result.score <= 1.0
    assert result.explanation


@pytest.mark.asyncio
async def test_exact_match_with_controlled_prompt():
    provider = OllamaProvider(model=Config.OLLAMA_MODEL, timeout=120)
    try:
        response = await provider.generate(
            "Return exactly: OK",
            max_tokens=5,
            temperature=0.0,
        )
    finally:
        await provider.close()

    scorer = ExactMatchScorer()
    result = scorer.score(response.text.strip(), "OK")

    assert result.score in (0.0, 1.0)


@pytest.mark.asyncio
async def test_benchmark_runner_with_llm_outputs():
    provider = OllamaProvider(model=Config.OLLAMA_MODEL, timeout=120)
    try:
        response = await provider.generate(
            "Answer in one word: 2+2",
            max_tokens=5,
            temperature=0.0,
        )
    finally:
        await provider.close()

    runner = BenchmarkRunner(metric=SimilarityScorer())
    cases = [
        BenchmarkCase(case_id="case_1", input_text="2+2", reference="4"),
    ]
    outputs = {"case_1": response.text.strip()}
    result = runner.run(cases, outputs)

    assert len(result.cases) == 1
    assert "score" in result.cases[0]
