"""
RAG agent example using mock retrieval.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import List, Tuple

from src.agent_labs.llm_providers import MockProvider
from src.agent_labs.orchestrator import Agent

sys.path.insert(0, str(Path(__file__).parent))
from documents import Document, load_documents  # noqa: E402


def mock_embed(text: str, dim: int = 8) -> List[float]:
    buckets = [0.0] * dim
    for idx, char in enumerate(text.lower()):
        buckets[idx % dim] += float(ord(char))
    total = sum(buckets) or 1.0
    return [value / total for value in buckets]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve(query: str, docs: List[Document], top_k: int = 2) -> List[Document]:
    query_vec = mock_embed(query)
    scored: List[Tuple[float, Document]] = []
    for doc in docs:
        doc_vec = mock_embed(doc.content)
        score = cosine_similarity(query_vec, doc_vec)
        scored.append((score, doc))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]


async def answer_question(question: str, docs: List[Document]) -> str:
    provider = MockProvider()
    agent = Agent(provider=provider)
    retrieved = retrieve(question, docs)
    context = "\n\n".join(f"{doc.title}: {doc.content}" for doc in retrieved)
    prompt = (
        "Use the context to answer the question.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\nAnswer:"
    )
    return await agent.run(prompt, max_turns=1)


def format_retrieved(docs: List[Document]) -> str:
    return "\n".join(f"- {doc.title}" for doc in docs)


if __name__ == "__main__":
    documents = load_documents("labs/01/data/documents.json")
    query = "What is retrieval augmented generation?"
    retrieved_docs = retrieve(query, documents)
    print("Retrieved Documents:")
    print(format_retrieved(retrieved_docs))
