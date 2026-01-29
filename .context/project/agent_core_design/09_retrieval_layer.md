# Retrieval Layer (Evidence-First)

## Goals

- Retrieval is optional, but when used it must be evidence-first and auditable.
- Retrieval must support deterministic mode (fixtures, deterministic embedder).
- Vector store backends are swappable via registry/factory.

## Core abstractions

### EvidenceItem

Every retrieved item must carry provenance:
- `doc_id`, `chunk_id`
- `source` (uri/path/system)
- `timestamp` (when ingested)
- `metadata` (tenant, tags, etc.)
- `score` and ranking info

### EvidenceManifest

A machine-readable record of:
- what evidence was included
- why it was selected
- what was dropped due to budgets
- what filters were applied

This enables:
- citations in results
- reproducible evaluation
- auditability (what the agent was grounded on)

### Retriever / RetrievalStrategy

Separate "storage" from "algorithm":
- `VectorStore` stores embeddings and metadata
- `Retriever` queries the store
- `RetrievalStrategy` decides how to retrieve (vector-only first; hybrid later)

### Retrieval gating

A policy that chooses retrieval depth:
- `none`: no retrieval
- `light`: few chunks, strict budgets
- `deep`: more chunks + optional reranking (later)

Gating inputs:
- router classification
- budgets
- user intent and uncertainty

## Vector store backends

Built-in deterministic backend:
- `memory` vector store (for deterministic tests)

Optional production backends:
- `chroma_persist` (local persistent dev/prod-lite)
- future: `pgvector`, managed vector DBs

Backends are selected by key and configured via structured config.

## Determinism requirements

Deterministic mode should:
- avoid floating nondeterminism in embeddings
- use deterministic embedder (e.g., hashing-based embedding) or fixtures
- use stable sorting rules for ties

## Output contract

Retrieval outputs must feed into:
- context packing (with injection hygiene)
- evidence manifest (included in RunResult/RunArtifact)

