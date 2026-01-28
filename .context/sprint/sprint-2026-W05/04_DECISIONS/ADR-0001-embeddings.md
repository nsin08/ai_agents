# Embedding Model Analysis (Ollama) - Phase 2+

Date: 2026-01-28
Sprint: 2026-W05

## Context
Phase 2+ requires real, working embeddings for RAG:
- Ingestion: chunk -> embed -> upsert into vector store
- Query: embed query -> vector search -> EvidenceItems + EvidenceManifest

We also require deterministic behavior for unit/CI tests.

## Current Local Models
From `ollama list`:
- nomic-embed-text:latest (embedding model)
- other chat models present (Phi, llama2, mistral, gemma3, qwen3, etc.)

## Recommendation

### 1) Deterministic Tests (CI)
Do NOT depend on Ollama embeddings.
- Use a deterministic embedder (hash-based) or fixtures.
- Goal: stable vectors, stable retrieval ordering, reproducible EvidenceManifest.

### 2) Local Dev / Prod-lite Embeddings
`nomic-embed-text:latest` is good enough to implement Phase 2+ end-to-end.
- Pros: already installed; works well for local semantic search/RAG.
- Cons: quality varies by domain; may be outperformed by newer/larger embedding models.

### 3) Potential Upgrades (Ollama-served)
If we need higher retrieval quality or better tradeoffs, evaluate these as drop-in embedding providers via the EmbeddingClient interface:
- `mxbai-embed-large` (common quality upgrade)
- `snowflake-arctic-embed` (multiple sizes)

Note: exact “best” depends on hardware constraints and domain. We keep embeddings behind an interface so we can swap models without changing core retrieval code.

## Key Implementation Constraints
- Store embedding metadata with each vector:
  - embed_model name/version
  - embedding_dim
  - normalization strategy (if used)
  - created_at

This prevents index corruption when switching embedding models.

## Acceptance Criteria (Phase 2 Embeddings)
- Deterministic embedder produces identical vectors for identical text.
- Ollama embedder works end-to-end locally (ingest + query).
- Vector store supports swapping embed models by using separate collections/namespaces or explicit metadata filters.

## Next Actions
- Add an `EmbeddingClient` interface and registry entry for `ollama` embeddings.
- Keep deterministic embedder as the default for tests.
- Run a small bakeoff (10-20 queries) comparing `nomic-embed-text` vs one candidate upgrade when ready.