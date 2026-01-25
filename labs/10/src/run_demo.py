"""Run the Lab 10 demo end-to-end."""

from __future__ import annotations

from src.agent_labs.retrieval import InMemoryVectorIndex

from dataset import golden_set, sample_docs
from ingest import ingest_docs
from vector_agent import VectorRagAgent
from evaluate import run_golden_set


def main() -> None:
    index = InMemoryVectorIndex()
    count = ingest_docs(index, sample_docs())
    print(f"Ingested chunks: {count}")

    agent = VectorRagAgent(index=index)
    response = agent.answer("What is MCP?", tenant_id="t1", request_id="req-demo")
    print(response["answer"])
    print(response["citations"])
    print(response["manifest"])

    avg = run_golden_set(agent, golden_set())
    print(f"Golden set average score: {avg}")


if __name__ == "__main__":
    main()

