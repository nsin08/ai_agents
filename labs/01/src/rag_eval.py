"""
Evaluation helper for RAG outputs using Ollama.
"""

from __future__ import annotations

import asyncio
import os

from src.agent_labs.evaluation import SimilarityScorer, report_markdown
from src.agent_labs.llm_providers import OllamaProvider
from src.agent_labs.config import get_config, LLMProvider


async def evaluate(question: str, reference: str) -> str:
    # Load configuration
    config = get_config()
    
    # Ensure we're using a supported provider
    if config.provider not in [LLMProvider.OLLAMA, LLMProvider.MOCK]:
        raise ValueError(
            f"rag_eval requires Ollama or Mock provider, got: {config.provider.value}"
        )
    
    # Create provider
    if config.provider == LLMProvider.OLLAMA:
        provider = OllamaProvider(
            base_url=config.provider_config.base_url,
            model=config.provider_config.model,
            timeout=config.provider_config.timeout,
        )
    else:
        from src.agent_labs.llm_providers import MockProvider
        provider = MockProvider()
    
    try:
        response = await provider.generate(
            f"Answer in one sentence: {question}",
            max_tokens=80,
            temperature=0.2,
        )
    finally:
        await provider.close()

    scorer = SimilarityScorer()
    result = scorer.score(response.text, reference)
    report = report_markdown(
        [
            {
                "case_id": "lab1_eval",
                "score": result.score,
                "explanation": result.explanation,
            }
        ]
    )
    return report


if __name__ == "__main__":
    output = asyncio.run(
        evaluate(
            question="What is retrieval augmented generation?",
            reference="Retrieval augmented generation combines retrieval with generation.",
        )
    )
    print(output)
