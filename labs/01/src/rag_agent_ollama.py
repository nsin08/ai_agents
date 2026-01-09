"""
RAG agent using Ollama for generation.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import List

from src.agent_labs.llm_providers import OllamaProvider
from src.agent_labs.orchestrator import Agent

sys.path.insert(0, str(Path(__file__).parent))
from documents import Document, load_documents  # noqa: E402
from rag_agent import retrieve  # noqa: E402


async def answer_question(question: str, docs: List[Document]) -> str:
    provider = OllamaProvider(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "llama2"),
        timeout=int(os.getenv("OLLAMA_TIMEOUT", "60")),
    )
    agent = Agent(provider=provider)
    retrieved = retrieve(question, docs)
    context = "\n\n".join(f"{doc.title}: {doc.content}" for doc in retrieved)
    prompt = (
        "Use the context to answer the question.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\nAnswer:"
    )
    try:
        return await agent.run(prompt, max_turns=1)
    finally:
        await provider.close()


if __name__ == "__main__":
    documents = load_documents("labs/01/data/documents.json")
    query = "What is retrieval augmented generation?"
    answer = asyncio.run(answer_question(query, documents))
    print(answer)
