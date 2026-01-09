"""
Evaluation helper for RAG outputs using Ollama.
"""

from __future__ import annotations

import asyncio
import os

from src.agent_labs.evaluation import SimilarityScorer, report_markdown
from src.agent_labs.llm_providers import OllamaProvider


async def evaluate(question: str, reference: str) -> str:
    provider = OllamaProvider(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "llama2"),
        timeout=int(os.getenv("OLLAMA_TIMEOUT", "60")),
    )
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
