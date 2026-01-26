# ADR-0009: Evidence-first retrieval with swappable vector store backends

**Date:** 2026-01-25  
**Status:** Accepted

## Context

Retrieval quality and grounding dominate many agent workflows.
We need retrieval to be:
- auditable (what evidence was used)
- reproducible (especially in deterministic mode)
- swappable (vector store backend changes must not rewrite application logic)

## Decision

- Make retrieval produce an `EvidenceManifest` as a first-class artifact.
- Separate retrieval into:
  - vector store backend (`VectorStore`)
  - retrieval strategy (`RetrievalStrategy`)
  - gating policy (`none|light|deep`)
- Select vector store backends by registry key.
- Provide a deterministic in-memory backend in core; allow optional persistent backends (e.g., Chroma) as plugins.

## Consequences

### Positive
- Clear grounding and explainability for results.
- Deterministic tests are possible without external services.
- Backends can evolve (Chroma -> pgvector -> managed DB) without changing the retrieval API.

### Negative / trade-offs
- Requires designing stable evidence and manifest schemas early.

