# Phase 2+ Epics and Stories Plan

## Purpose
Break down Phase 2+ roadmap into epics and stories with dependencies and outcomes.

## References
- .context/sprint/sprint-2026-W05/phase2plus_implementation_plan.md
- .context/project/agent_core_design/17_phased_delivery_plan.md

## Epics Overview

Epic P2: Retrieval + Memory + Evaluation Foundations
Epic P3: CLI v1 Standardization
Epic P4: Service v1 (Polling-first)
Epic P5: Optional Plugins (LangGraph/LangChain)
Epic P6: Streaming (Optional)

## Epic P2: Retrieval + Memory + Evaluation Foundations

Outcome:
- Real working RAG pipeline and persistent memory with deterministic tests.

Stories:
P2-S1 Retrieval core types + EvidenceManifest
- Outcome: Evidence-first retrieval and auditability.
- Dependencies: Phase 1 artifacts and event schema.

P2-S2 Embedding providers + deterministic embedder
- Outcome: Stable embeddings in tests, real providers in prod.
- Dependencies: Provider registry, config loader.

P2-S3 VectorStore registry + backends (in-memory + Postgres/pgvector)
- Outcome: Swappable vector DB with persistent backend.
- Dependencies: P2-S2.

P2-S4 Ingestion pipeline + chunking
- Outcome: Document ingestion with metadata and provenance.
- Dependencies: P2-S2, P2-S3.

P2-S5 Retrieval strategy + context packing
- Outcome: Safe prompt injection hygiene and budgeting.
- Dependencies: P2-S1, P2-S3.

P2-S6 Long-term memory store + policies
- Outcome: Persistent memory with write/retrieval/retention controls.
- Dependencies: Config, policy engine.

P2-S7 Memory consolidation pipeline
- Outcome: Extract/dedupe facts for safe persistence.
- Dependencies: P2-S6.

P2-S8 Evaluation gates v1
- Outcome: Scorecards + gate decisions for CI.
- Dependencies: Deterministic artifacts and fixtures.

## Epic P3: CLI v1 Standardization

Outcome:
- CLI parity with library for run/eval/gate/serve/validate-config.

Stories:
P3-S1 CLI run + validate-config
- Outcome: Standard execution surface with JSON output.
- Dependencies: Phase 1 API, P2 retrieval/memory.

P3-S2 CLI eval + gate
- Outcome: CI-friendly gating with machine-readable outputs.
- Dependencies: P2-S8.

P3-S3 CLI serve skeleton
- Outcome: Bootstrap for service mode.
- Dependencies: 15_service_spec.md.

## Epic P4: Service v1 (Polling-first)

Outcome:
- Hosted API parity with CLI/library, artifacts and events.

Stories:
P4-S1 Service API skeleton
- Outcome: API contract in place.
- Dependencies: CLI parity.

P4-S2 Run worker + event stream
- Outcome: Background execution + pollable events.
- Dependencies: P4-S1.

P4-S3 Artifact downloads
- Outcome: End-to-end artifact parity.
- Dependencies: P4-S2.

## Epic P5: Optional Plugins (LangGraph/LangChain)

Outcome:
- Optional plugins without core coupling.

Stories:
P5-S1 LangGraph engine plugin
- Outcome: Optional engine adapter with entry points.
- Dependencies: Engine registry, conformance tests.

P5-S2 LangChain tool/retrieval plugin
- Outcome: Optional tool/retrieval adapter.
- Dependencies: Tool registry, retrieval interfaces.

## Epic P6: Streaming (Optional)

Outcome:
- Streaming events for product UX upgrades.

Stories:
P6-S1 SSE events
- Outcome: Streamed events match polled schema.
- Dependencies: Service event store.

P6-S2 Token streaming (optional)
- Outcome: Token streaming with cancellation semantics.
- Dependencies: Provider streaming support.

## Cross-Cutting Dependencies

- P2 enables P3/P4 (retrieval, memory, eval).
- P3 enables P4 (CLI parity and config validation).
- P4 enables P6 (event streaming).
- P5 depends on stable registries and retrieval interfaces.

## Open Items
- Provide official Issue #82 link/title for Phase 2+ umbrella tracking.
- Confirm pgvector and/or Chroma dependency policy.
- Confirm Phase 2 resourcing and target start date.