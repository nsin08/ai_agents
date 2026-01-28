# Phase 2+ Implementation Plan (Detailed)

Based on:
- .context/project/agent_core_design/17_phased_delivery_plan.md
- .context/project/agent_core_design/09_retrieval_layer.md
- .context/project/agent_core_design/10_memory_layer.md
- .context/project/agent_core_design/12_evaluation_gates.md
- .context/project/agent_core_design/14_cli_spec.md
- .context/project/agent_core_design/15_service_spec.md

Status:
- Phase 1 complete (Issue #89: Polish and Release).
- Phase 2+ planning (Issue #82 link/title needed in local context).

## Purpose
Provide a detailed, execution-ready plan for Phase 2+ with clear outcomes, dependencies, and implementation steps. Emphasis is on real, working RAG, persistent memory, and production-credible data stores.

## Scope
Phase 2 through Phase 6:
- Phase 2: Retrieval + long-term memory + evaluation foundations.
- Phase 3: CLI v1 standardization.
- Phase 4: Service v1 (polling-first).
- Phase 5: Optional plugins (LangGraph/LangChain).
- Phase 6: Streaming (optional).

## Assumptions
- Phase 1 artifacts and event schemas are stable and versioned.
- Plugin registries and factories exist and are extensible.
- Two-week sprint cadence.

## Target Outcomes (What we will achieve)
- Working RAG: ingest, embed, store, retrieve, and cite evidence with deterministic tests.
- Working memory: persistent, policy-governed long-term memory with retention and tenant scoping.
- Evaluation gates: repeatable scorecards and gating in CI.
- CLI parity: reliable automation and human-friendly tools.
- Service parity: API mirrors CLI and library outputs.

## Epic Hierarchy (Phase 2+)

Epic #82: Phase 2+ Roadmap (placeholder - link/title required)
  - Epic P2: Retrieval + Memory + Evaluation Foundations
  - Epic P3: CLI v1 Standardization
  - Epic P4: Service v1 (Polling-first)
  - Epic P5: Optional Plugins (LangGraph/LangChain)
  - Epic P6: Streaming (optional)

## Dependency Graph (High-level)

Phase 2 Retrieval + Memory
  -> Evaluation Gates
  -> CLI v1
  -> Service v1

Optional Plugins
  -> Requires stable registries and CLI/service parity

Streaming
  -> Requires Service v1 event pipeline

## EPIC P2: Retrieval + Memory + Evaluation Foundations

### Purpose
Deliver a real, working retrieval and memory system with deterministic testing and auditable evidence.

### Success Criteria
- Evidence manifest included in artifacts and RunResult.
- Retrieval determinism holds under fixtures.
- Vector store backend is swappable via config.
- Long-term memory policies enforced in tests.
- Evaluation gates produce machine-readable scorecards.

### Dependencies
- Phase 1 registries, config loader, artifact writer, event system.

### Stories (Phase 2)

P2-S1: Retrieval Abstractions + Evidence Manifest
- Description: Implement EvidenceItem, EvidenceManifest, Retriever, RetrievalStrategy interfaces.
- How: Add core types and serialization; enforce inclusion in RunResult and artifacts.
- Achieves: Evidence-first retrieval and auditability.
- Dependencies: Artifact bundle format (Phase 1).
- Acceptance:
  - Evidence manifest schema versioned in artifacts.
  - RunResult includes citations derived from manifest.

P2-S2: Embedding Providers + Deterministic Embedder
- Description: Add EmbeddingClient interface and implementations.
- How: Implement deterministic embedder for tests; implement OpenAI/Ollama embedder adapters.
- Achieves: Real embeddings in prod; stable embeddings in tests.
- Dependencies: Provider registry, config.
- Acceptance:
  - Deterministic embedder produces stable vectors for same input.
  - Real embedder works with configured provider and keys.

P2-S3: Vector Store Registry + Backends
- Description: Add VectorStore interface and registry.
- How: Implement in-memory store for deterministic tests; implement persistent store.
- Databases:
  - Default dev: Chroma (chroma_persist) or SQLite-based vector store.
  - Production: Postgres + pgvector.
- Achieves: Real, working RAG database with swappable backends.
- Dependencies: P2-S2 (embedding), config.
- Acceptance:
  - Vector store backend selectable via config key.
  - Persistent backend survives restart and supports metadata filters.

P2-S4: Ingestion Pipeline + Chunking
- Description: Build ingestion pipeline for documents.
- How: Chunking, metadata capture, embedding, upsert to vector store.
- Achieves: Operational ingestion into vector database.
- Dependencies: P2-S2, P2-S3.
- Acceptance:
  - Ingest CLI or API populates vector store with metadata.
  - Evidence items include doc_id, chunk_id, source, timestamp.

P2-S5: Retrieval Strategy + Context Packing
- Description: Implement retrieval gating and context packing with injection hygiene.
- How: Strategy chooses retrieval depth; context packer enforces budgets and ordering.
- Achieves: Safe, predictable retrieval for prompts.
- Dependencies: P2-S1, P2-S3.
- Acceptance:
  - Gating modes (none/light/deep) work via config.
  - Evidence manifest logs dropped items and budgets.

P2-S6: Long-term Memory Store + Policies
- Description: Add persistent memory store with write/retrieval/retention policies.
- How: Implement MemoryStore interface and policy enforcement.
- Databases:
  - Dev: SQLite.
  - Production: Postgres.
- Achieves: Real, working long-term memory database.
- Dependencies: Config, policy engine, storage adapters.
- Acceptance:
  - Write policy controls what can be persisted.
  - Retrieval policy controls what can enter context.
  - Retention policy supports TTL and deletion audit events.

P2-S7: Memory Consolidation Pipeline
- Description: Extract, dedupe, and persist stable facts from episodes.
- How: Define pipeline stages and thresholds; include redaction step.
- Achieves: Safe long-term memory without storing raw conversations.
- Dependencies: P2-S6, tool boundary policies.
- Acceptance:
  - Consolidation pipeline produces canonical facts with metadata.
  - Redaction applied before persistence.

P2-S8: Evaluation Gates v1
- Description: Implement GoldenSuite, Scorecard, GateDecision types.
- How: Add evaluation runner and JSON output for CI.
- Achieves: Regression detection and gating.
- Dependencies: Artifact schema, deterministic mode.
- Acceptance:
  - eval produces JSON scorecard; gate returns non-zero on failure.

## EPIC P3: CLI v1 Standardization

### Purpose
Deliver standard CLI with run, validate-config, eval, gate, serve.

### Success Criteria
- CLI outputs match library artifacts.
- validate-config checks env keys and plugin availability.
- eval and gate commands produce machine-readable outputs.

### Dependencies
- P2 evaluation gates and retrieval/memory for end-to-end tests.

### Stories (Phase 3)

P3-S1: CLI Run + Validate-Config
- Description: Implement run and validate-config with JSON output.
- How: Wire to library API; ensure deterministic mode toggle.
- Achieves: Standardized execution surface.
- Dependencies: Phase 1 API, P2 retrieval/memory.

P3-S2: CLI Eval + Gate
- Description: Implement eval and gate commands.
- How: Use GoldenSuite/Scorecard; exit codes for CI.
- Achieves: Automated regression gating.
- Dependencies: P2-S8.

P3-S3: CLI Serve Skeleton
- Description: Provide service command wiring and config validation.
- How: Minimal server bootstrap, no advanced auth.
- Achieves: Ready for Phase 4 service buildout.
- Dependencies: 15_service_spec.md.

## EPIC P4: Service v1 (Polling-first)

### Purpose
Provide hosted service API that mirrors CLI and library.

### Success Criteria
- Create run, poll status, poll events, download artifacts.
- Service output matches CLI/library artifacts.

### Dependencies
- CLI parity, artifact schema stability, event pipeline.

### Stories (Phase 4)

P4-S1: Service API Skeleton
- Description: Implement HTTP endpoints per spec.
- How: Start with in-memory storage, clear interfaces for persistence.
- Achieves: API contract in place.

P4-S2: Run Worker + Event Stream
- Description: Background execution and event persistence.
- How: Worker queue abstraction with local backend.
- Achieves: Asynchronous runs and pollable events.

P4-S3: Artifact Downloads
- Description: Store artifacts and provide download endpoint.
- How: File store adapter, checksum and integrity checks.
- Achieves: End-to-end service parity.

## EPIC P5: Optional Plugins (LangGraph / LangChain)

### Purpose
Provide optional integrations without coupling core dependencies.

### Success Criteria
- Base install does not require LC/LG.
- Clear error when plugin deps missing.
- Conformance tests pass for policies and events.

### Stories (Phase 5)

P5-S1: LangGraph Engine Plugin
- Description: Implement engine adapter and register via entry points.
- Dependencies: Registry and engine interfaces.

P5-S2: LangChain Tool/Retrieval Plugin
- Description: Implement tool/retrieval adapters.
- Dependencies: Tool and retrieval abstractions.

## EPIC P6: Streaming (optional)

### Purpose
Support streaming events and optional token streaming.

### Success Criteria
- SSE endpoint streams event schema.
- Cancellation emits terminal events.

### Stories (Phase 6)

P6-S1: SSE Events
- Description: Add SSE endpoint with event replay support.
- Dependencies: Service event store.

P6-S2: Token Streaming (Optional)
- Description: Stream token events when supported by provider.
- Dependencies: Provider streaming support.

## Databases and Storage (Real Working RAG and Memory)

Vector Store Options:
- Default: Postgres + pgvector (production).
- Dev/test: in-memory store + optional Chroma persistent store.

Memory Store Options:
- Long-term memory: Postgres (production), SQLite (dev).
- Session store: Redis (production), in-memory (dev).
- Run state store: Postgres or file-backed store.

Implementation Steps:
1. Define storage interfaces (VectorStore, MemoryStore, RunStore).
2. Implement in-memory backends for deterministic tests.
3. Implement Postgres adapters for vector store and long-term memory.
4. Add migrations and schema definitions.
5. Build ingestion and retrieval pipelines with evidence manifest.

## Dependencies Summary

- Retrieval depends on embedding providers and vector store registry.
- Memory policies depend on policy framework and storage adapters.
- Evaluation gates depend on deterministic artifacts and fixtures.
- CLI depends on evaluation and artifacts.
- Service depends on CLI parity and event pipeline.
- Plugins depend on stable registry interfaces.

## Risks and Mitigations

- Risk: Vector DB choice could lock architecture.
  Mitigation: Enforce VectorStore interface and registry.

- Risk: Memory policies underspecified.
  Mitigation: Implement minimal write/retrieval/retention policies and expand.

- Risk: Evaluation gates produce false positives.
  Mitigation: Start with deterministic gates; phase in real-mode stability.

## Definition of Done (Phase 2+)

- Phase 2: RAG and memory operational with persistent storage; eval gates in place.
- Phase 3: CLI commands stable with JSON outputs.
- Phase 4: Service API functional with artifact parity.
- Phase 5: Optional plugins shipped with conformance tests.
- Phase 6: Streaming optional and gated by stability.

## Open Items
- Provide official Issue #82 link/title for the Phase 2+ roadmap.
- Confirm pgvector and/or Chroma dependency policy.
- Confirm target Phase 2 timeline and resourcing.