# ADR-0003: Production Persistence Strategy (Phase 2+)

Status: Proposed
Date: 2026-01-28
Owners: Architect/PM

## Context
Phase 2+ requires "real working" RAG and long-term memory. The repo currently has offline/deterministic labs and planning docs, plus a Docker Compose stack for Postgres+pgvector, Redis, MinIO, and optional Chroma.

The hard part is not standing up services; it is choosing a persistence strategy that:
- supports retrieval + metadata filters + provenance
- supports long-term memory policies and deletion/retention
- remains testable (deterministic CI)
- avoids locking us into a dead-end backend

## Decision
Use Postgres + pgvector as the primary production persistence backend for Phase 2+.
- Vector store: Postgres + pgvector
- Long-term memory: Postgres tables
- Run state store (Phase 4+): Postgres tables

Use Redis only for short-term/session cache (optional) and job/queue primitives later.
Use MinIO only for artifact/object storage in service mode (Phase 4+), not required to deliver Phase 2 library+CLI.

Chroma remains an optional dev-only alternate vector backend for quick local experimentation.

## Options Considered

1) Postgres + pgvector (chosen)
- Pros: one durable store for vectors + relational metadata; easy ops story; good for metadata filters and joins; clear migration path.
- Cons: tuning/perf limits vs specialized vector DBs; requires schema/migrations discipline.

2) Chroma persistent as primary
- Pros: fast to prototype; simpler vector features.
- Cons: weaker enterprise ops story; harder to unify long-term memory + run state; higher risk of rework.

3) Qdrant/Weaviate/Pinecone as primary
- Pros: strong retrieval performance and vector features.
- Cons: larger dependency/ops footprint; higher lock-in; forces multi-backend story for memory/run state.

## Consequences
- We must implement migrations, backup/restore assumptions, and a reindex workflow.
- Embedding model changes require reindex; store embed_model + embed_dim metadata.
- Deterministic tests must not require Postgres; keep in-memory vector store and deterministic embedder for CI.

## Implementation Notes (Phase 2)
- Define interfaces: VectorStore, MemoryStore, RunStore.
- Implement backends:
  - InMemoryVectorStore (deterministic tests)
  - PostgresVectorStore (pgvector)
  - PostgresMemoryStore
- Provide Docker Compose for dev.

## Acceptance Criteria
- End-to-end local: ingest -> embed -> upsert -> retrieve with metadata filters.
- Evidence manifest includes provenance for retrieved chunks.
- Long-term memory tables support tenant_id, retention fields, and deletion audit events.

## Open Questions
- Do we standardize on one schema for vectors + documents + chunks, or separate schemas per feature?
- Do we require pgvector HNSW/IVFFlat indexes in Phase 2, or add later?