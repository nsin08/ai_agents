"""
Tests for Lab 1 RAG agent.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from documents import load_documents  # noqa: E402
from rag_agent import retrieve, answer_question  # noqa: E402


@pytest.mark.asyncio
async def test_rag_agent_retrieves_and_answers(tmp_path):
    docs = load_documents("labs/01/data/documents.json")
    retrieved = retrieve("What is RAG?", docs, top_k=2)

    assert len(retrieved) == 2
    answer = await answer_question("What is RAG?", docs)
    assert isinstance(answer, str)
    assert len(answer) > 0
