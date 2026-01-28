# SPEC-0001: Embeddings (Deterministic + Ollama)

Status: Draft
Date: 2026-01-28
Audience: Engineers implementing Phase 2 retrieval/memory + evaluation gates
Related ADRs:
- `.context/sprint/sprint-2026-W05/04_DECISIONS/ADR-0001-embeddings.md`

## Abstract
This paper specifies the embedding subsystem for Phase 2+ RAG and semantic memory. It explains what embeddings are, what we use them for, how they are produced, and the engineering patterns required to keep the system production-credible (traceable, testable, operable) instead of a fragile demo. The core design is a two-mode strategy:
- Deterministic embeddings for CI and deterministic evaluation (no network I/O).
- Provider-backed embeddings for local/dev and prod-lite (Ollama).

## 1. Introduction

### 1.1 What is an embedding?
An embedding is a vector (a list of floats) that represents the meaning of text. The goal is that semantic similarity in text becomes geometric similarity in vector space.

Typical workflow:
- embed(document chunk) -> store vector
- embed(query) -> nearest-neighbor search -> retrieve chunks

### 1.2 What embeddings are used for in this system
Embeddings are used for:
1) Retrieval-Augmented Generation (RAG)
   - Index: chunk -> embed -> store in VectorStore
   - Search: query -> embed -> nearest neighbor -> ranked EvidenceItems
   - Audit: EvidenceManifest records what was retrieved and why

2) (Optional) Semantic long-term memory retrieval
   - Index memory facts (or memory summaries) as vectors
   - Search memory semantically with the same embedding interface

### 1.3 Why embeddings are a reliability problem (not just an ML problem)
Most RAG systems fail due to engineering mistakes:
- Index corruption: mixing vectors from different models/dimensions.
- Flaky CI: embedding calls require network/GPU.
- Silent regressions: a model tag changes (":latest") and retrieval quality shifts.
- Inconsistent metric/normalization: cosine vs dot product mismatch.

This spec is designed to prevent those failure modes.

## 2. Goals and Non-goals

### 2.1 Goals (Phase 2)
- Deterministic CI: embedding must be reproducible with no network I/O.
- Real dev experience: local embeddings via Ollama (e.g., `nomic-embed-text`).
- Provider swap capability: embedding provider is a pluggable adapter.
- Strong metadata contract: stored vectors are always attributable to provider/model/dim.

### 2.2 Non-goals (Phase 2)
- Making cloud embeddings mandatory.
- Streaming embeddings.
- Model ensembling.
- Multi-lingual optimization.

## 3. Design Patterns (Required)

### 3.1 Ports and Adapters (Hexagonal Architecture)
Core retrieval/memory code must depend on an interface (port), not on Ollama HTTP calls.

Port:
- `EmbeddingClient`

Adapters:
- `DeterministicEmbeddingClient` (CI)
- `OllamaEmbeddingClient` (local/dev)

Why:
- isolates provider failures
- enables deterministic gates
- prevents HTTP/provider details leaking into core

### 3.2 Strategy Pattern (Mode Selection)
Embedding behavior changes by scenario:
- CI deterministic
- local/dev real embeddings

We select an embedding strategy via config:
- `embeddings.provider = deterministic|ollama|...`

### 3.3 Registry/Factory Pattern (Pluggability)
Embedding providers register by key, consistent with agent_core registries:
- `deterministic` -> DeterministicEmbeddingClient
- `ollama` -> OllamaEmbeddingClient

Why:
- keeps optional providers optional
- avoids hard imports and dependency sprawl

## 4. System Architecture

Data flow:

1) Ingestion
- document -> chunk -> embed(chunks) -> VectorStore.upsert(vectors + metadata)

2) Query/Retrieval
- query -> embed_query(query) -> VectorStore.query(vector) -> EvidenceItems
- EvidenceItems -> EvidenceManifest -> prompt context packing

ASCII diagram:

```
+-------------------+     +------------------+     +-------------------+
| Chunker/Loader    |     | EmbeddingClient  |     | VectorStore       |
| (text + metadata) | --> | (port + adapter) | --> | (pgvector/memory) |
+-------------------+     +------------------+     +-------------------+
            |                      |                      |
            v                      v                      v
     Observability          Observability        EvidenceItems + Manifest
        events                 events
```

## 5. API Contract

### 5.1 Interface
Minimum required API:
- `embed(texts: list[str]) -> list[list[float]]`
- `embed_query(text: str) -> list[float]`

Rules:
- `embed([])` returns `[]`.
- Each vector MUST be a list of floats with a fixed length for the configured model.
- `embed_query()` may delegate to `embed([text])[0]`.

### 5.2 Error contract
Providers MUST raise typed errors and MUST NOT leak raw exceptions across boundaries:
- `EmbeddingTimeout`
- `EmbeddingUnauthorized`
- `EmbeddingProviderError`
- `EmbeddingInvalidResponse`

Rationale:
- prevents transport/library coupling
- supports consistent error handling and policy decisions

### 5.3 Batch behavior
Batch embedding must exist, even if initially naive.
Rationale:
- ingestion performance
- fewer round-trips to Ollama

## 6. Data and Metadata Contract (Prevents Index Corruption)

### 6.1 Required metadata per stored vector
Every stored vector record MUST include:
- `embed_provider` (e.g., `ollama`, `deterministic`)
- `embed_model` (e.g., `nomic-embed-text:latest`)
- `embed_dim` (int)
- `embed_norm` (`none|l2`)
- `created_at` (timestamp)

### 6.2 Index separation rules
We MUST NOT query across mixed embedding models or dimensions.
Enforce one of:
1) Separate namespaces/collections per (provider, model, dim), OR
2) Hard filter on (provider, model, dim) for every query

Note: Option (2) is simpler to start but must be enforced in code, not by convention.

### 6.3 Model versioning rule
Do not rely on moving tags (":latest") for production environments.
- For dev: acceptable.
- For production/staging: pin a specific model tag and treat changes as a reindex event.

## 7. Metric and Normalization

### 7.1 Similarity metrics
Common choices:
- Cosine similarity
- Dot product
- L2 distance

### 7.2 Normalization
If cosine similarity is used, vectors SHOULD be L2-normalized.
- Record the normalization approach in `embed_norm`.
- Ensure query vectors and stored vectors follow the same rule.

## 8. Provider Specifications

### 8.1 DeterministicEmbeddingClient (CI default)
Purpose:
- Make CI and deterministic evaluation gates stable.

Requirements:
- No network I/O.
- Deterministic mapping: (text, seed) -> vector.
- Fixed `embed_dim`.

Acceptable implementation:
- hash text -> seeded PRNG -> generate float vector -> optional L2 normalize.

### 8.2 OllamaEmbeddingClient (local/dev and prod-lite)
Purpose:
- Provide real semantic embeddings without cloud dependency.

Requirements:
- Calls Ollama embeddings endpoint.
- Supports configurable model (e.g., `nomic-embed-text`).
- Timeouts, bounded retries, and typed error mapping.
- Propagates correlation IDs (request_id/tool_call_id/run_id) via headers.

## 9. Decision Guidance (How we choose models/providers)

### Scenario A: CI and deterministic gates
Use deterministic embeddings.
- Reason: network dependencies and model variance make gates untrustworthy.

### Scenario B: local development
Use Ollama embeddings with a known model.
- Reason: fast iteration + realistic retrieval behavior.

### Scenario C: production accuracy focus
Choose based on measured retrieval performance on a domain golden suite.
Decision factors:
- Quality: top-k retrieval success on representative queries.
- Latency: embedding and retrieval time on target hardware.
- Dimensionality: storage and index cost.
- Operational stability: version pinning and migration plan.

Minimum recommended practice:
- run a 10-50 query bakeoff suite before switching models
- treat model changes as a migration with reindex

## 10. Observability
Emit (at minimum) the following events:
- `embedding.requested` {provider, model, count}
- `embedding.succeeded` {provider, model, count, embed_dim, duration_ms}
- `embedding.failed` {provider, model, error_code, duration_ms}

Why:
- debugging retrieval regressions
- performance monitoring

## 11. Validation and Testing

### 11.1 Unit tests
- deterministic: same input+seed -> identical vectors
- deterministic: correct vector length
- adapter: error mapping is typed

### 11.2 Contract tests
- reject or isolate mixed `embed_dim` for the same collection/index
- stored vectors always carry required metadata

### 11.3 Integration tests (optional)
- Ollama embedding works against a running Ollama
- tests must be skippable in CI

## 12. Rollout and Migration

Embeddings are not forward-compatible across model changes.
If embed_model or embed_dim changes:
- reindex is required

Recommended playbook:
- create new namespace/collection
- re-ingest and re-embed
- switch config
- run evaluation gate

## References
```text
Ollama embeddings
https://docs.ollama.com/capabilities/embeddings

Cosine similarity
https://en.wikipedia.org/wiki/Cosine_similarity

pgvector
https://github.com/pgvector/pgvector
```
