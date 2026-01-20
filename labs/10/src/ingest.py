"""Ingestion pipeline: chunk -> record -> upsert."""

from __future__ import annotations

from typing import List

from src.agent_labs.context import chunk_semantic_mock
from src.agent_labs.retrieval import ChunkRecord, VectorIndex

from dataset import Doc


def ingest_docs(index: VectorIndex, docs: List[Doc]) -> int:
    records: list[ChunkRecord] = []
    for doc in docs:
        chunks = chunk_semantic_mock(doc.text, max_chars=200)
        for i, chunk in enumerate(chunks):
            records.append(
                ChunkRecord(
                    doc_id=doc.doc_id,
                    chunk_id=f"c{i+1}",
                    text=chunk,
                    metadata={
                        "tenant_id": doc.tenant_id,
                        "source": doc.source,
                    },
                )
            )
    index.upsert(records)
    return len(records)

