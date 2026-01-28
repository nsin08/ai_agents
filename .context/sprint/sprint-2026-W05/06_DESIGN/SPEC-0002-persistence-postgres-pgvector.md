# SPEC-0002: Production Persistence (Postgres + pgvector)

Status: Draft
Date: 2026-01-28
Related ADRs:
- `.context/sprint/sprint-2026-W05/04_DECISIONS/ADR-0003-persistence-strategy.md`

## Abstract
This spec defines the persistence strategy for a Phase 2+ production system: Postgres as the primary durable store for long-term memory and vector retrieval (via pgvector). It explains why this is chosen, how it is implemented, and how we validate correctness and operability.

## 1. Introduction
### 1.1 What is "persistence" in an agent system?
Persistence is durable storage for the system's state and knowledge across runs:
- documents and chunks
- embeddings and vector indexes
- long-term memory records
- (later) run state and event history

### 1.2 Why persistence matters for Phase 2+
If data disappears on restart, you do not have real RAG or real memory. Persistence is also required for:
- auditability (what evidence was used)
- evaluation reproducibility
- deletion/retention compliance

## 2. Requirements
### 2.1 Functional
- Store document chunks with provenance.
- Store embeddings for chunks.
- Query nearest-neighbors with metadata filters.
- Store long-term memory records with retention and deletion.

### 2.2 Non-functional
- Operability: migrations, backups assumptions, and local-dev tooling.
- Safety: tenant_id in the data model and delete-by-tenant capability.
- Performance: acceptable query latency with appropriate indexes.

## 3. Decision Guidance (Backend choices)

### Option A: Postgres + pgvector (chosen)
Why it wins for Phase 2:
- One durable DB for vectors + relational metadata.
- Strong filtering and joins (metadata filters are not optional in production).
- Standard ops story: backups, migrations, monitoring.

### Option B: Dedicated vector DB (Qdrant/Weaviate/Pinecone)
When to choose:
- You have high QPS, large corpora, and need specialized retrieval features.
Tradeoff:
- You now have 2+ durable systems (vector DB + memory DB), increasing complexity.

### Option C: Chroma persistent
When to choose:
- Prototype only or dev-only local experimentation.
Why not primary:
- Higher risk of rework and unclear enterprise ops posture.

## 4. Technical Design

### 4.1 Core interfaces
- VectorStore:
  - `upsert(chunks)`
  - `query(vector, top_k, filters)`
  - `delete_by_doc_id(doc_id)`

- MemoryStore:
  - `put_fact(fact)`
  - `search_facts(...)`
  - `delete(id|key)`

- RunStore (Phase 4+):
  - `put(run_state)` / `get(run_id)`

These interfaces keep us from vendor lock-in.

### 4.2 Minimum schema (conceptual)
Documents:
- documents(id, tenant_id, source, uri, content_hash, created_at)

Chunks:
- chunks(id, tenant_id, doc_id, chunk_index, text, metadata_json, created_at)

Vectors:
- chunk_vectors(chunk_id, tenant_id, embed_provider, embed_model, embed_dim, embed_norm, embedding, created_at)

Memory:
- memory_facts(id, tenant_id, kind, key, value_json, source, confidence, created_at, expires_at, deleted_at)
- memory_events(id, tenant_id, action, target_id, actor, created_at)

Rationale:
- tenant_id everywhere prevents "oops" multi-tenant leaks later.
- embed metadata prevents index corruption.

### 4.3 Indexing strategy
- pgvector index (HNSW or IVFFlat) on `chunk_vectors.embedding`.
- btree indexes on tenant_id, doc_id, embed_model.

Note: Phase 2 can start with minimal indexing and add HNSW/IVFFlat tuning once correctness is proven.

### 4.4 Migrations
Non-negotiable:
- schema managed by migrations
- dev reset workflow
- production upgrade workflow

### 4.5 Local development
Use the backend stores Compose stack:
- `.context/sprint/sprint-2026-W05/03_ENV/docker-compose.backend-stores.yml`

## 5. Validation (What "done" means)
- Integration:
  - ingest -> embed -> upsert -> query returns expected chunks
  - metadata filters work
- Safety:
  - delete-by-doc_id works
  - delete-by-tenant works
- Operability:
  - migrations apply cleanly from empty DB

## 6. Risks and Mitigations
- Risk: performance issues with pgvector at scale.
  - Mitigation: keep VectorStore interface; migrate to dedicated vector DB later if needed.

- Risk: schema drift without migrations discipline.
  - Mitigation: enforce migrations in CI.

## 7. References
```text
PostgreSQL
https://www.postgresql.org/

pgvector
https://github.com/pgvector/pgvector

HNSW (background)
https://en.wikipedia.org/wiki/Hierarchical_navigable_small_world_graph
```
