# Lab 10: Vector DB + Context Packing + Memory Management (Offline, Deterministic)

## Overview
This lab focuses on **vector retrieval patterns** plus **context packing** and **memory consolidation**.

It is intentionally offline-first:
- Uses `src.agent_labs.retrieval.InMemoryVectorIndex` (deterministic embeddings)
- Produces provenance fields (`doc_id`, `chunk_id`, `source`, `timestamp`, metadata)
- Produces a context manifest ("what was included and why")
- Demonstrates a small golden-set evaluation run

## Quick Start

```powershell
# From repo root
$env:PYTHONPATH='.'; python labs/10/src/run_demo.py
$env:PYTHONPATH='.'; pytest labs/10/tests/test_vector_lab.py -v --capture=tee-sys
```

## Exercises
- `exercises/exercise_1.md` - Ingest + metadata filters
- `exercises/exercise_2.md` - Context packing manifest
- `exercises/exercise_3.md` - Memory consolidation + golden set evaluation

## Notes (Production Path)
This lab uses an in-memory vector index for determinism. In production, the same interfaces can be backed by:
- Postgres + pgvector
- Chroma persistent
- Managed vector DB (Pinecone/Qdrant/Weaviate)

