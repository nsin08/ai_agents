import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dataset import golden_set, sample_docs
from evaluate import run_golden_set
from ingest import ingest_docs
from vector_agent import VectorRagAgent

from src.agent_labs.retrieval import InMemoryVectorIndex


def test_ingest_and_query_with_tenant_filter():
    index = InMemoryVectorIndex()
    ingest_docs(index, sample_docs())
    results = index.query("refund", top_k=5, filters={"tenant_id": "t2"})
    assert results
    assert all(r.metadata.get("tenant_id") == "t2" for r in results)


def test_agent_returns_manifest_with_provenance():
    index = InMemoryVectorIndex()
    ingest_docs(index, sample_docs())
    agent = VectorRagAgent(index=index)

    out = agent.answer("What is MCP?", tenant_id="t1", request_id="req-1")
    assert out["answer"]
    assert out["citations"]
    assert out["manifest"]["items"]
    first = out["manifest"]["items"][0]
    assert first["kind"] == "evidence"
    assert "doc_id" in first["metadata"]


def test_golden_set_evaluation_is_deterministic():
    index = InMemoryVectorIndex()
    ingest_docs(index, sample_docs())
    agent = VectorRagAgent(index=index)

    avg = run_golden_set(agent, golden_set())
    assert avg == 1.0

