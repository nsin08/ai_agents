from src.agent_labs.retrieval import ChunkRecord, InMemoryVectorIndex


def test_in_memory_vector_index_query_returns_scored_results():
    index = InMemoryVectorIndex()
    index.upsert(
        [
            ChunkRecord(
                doc_id="d1",
                chunk_id="c1",
                text="alpha beta gamma",
                metadata={"tenant_id": "t1", "source": "kb"},
            ),
            ChunkRecord(
                doc_id="d2",
                chunk_id="c1",
                text="unrelated content",
                metadata={"tenant_id": "t1", "source": "kb"},
            ),
        ]
    )

    results = index.query("alpha", top_k=1, filters={"tenant_id": "t1"})
    assert len(results) == 1
    assert results[0].doc_id == "d1"
    assert results[0].chunk_id == "c1"
    assert 0.0 <= results[0].score <= 1.0


def test_in_memory_vector_index_applies_metadata_filters():
    index = InMemoryVectorIndex()
    index.upsert(
        [
            ChunkRecord(doc_id="d1", chunk_id="c1", text="hello", metadata={"tenant_id": "t1"}),
            ChunkRecord(doc_id="d2", chunk_id="c1", text="hello", metadata={"tenant_id": "t2"}),
        ]
    )

    results = index.query("hello", top_k=10, filters={"tenant_id": "t2"})
    assert {r.doc_id for r in results} == {"d2"}

