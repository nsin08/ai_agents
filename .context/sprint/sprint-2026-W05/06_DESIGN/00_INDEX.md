# Phase 2+ Technical Specs (06_DESIGN)

This folder contains "technical-paper style" specifications derived from Sprint 2026-W05 ADRs.

How to read
- ADRs (decisions): `.context/sprint/sprint-2026-W05/04_DECISIONS/`
- Specs (what production expects + why + how): this folder

Specs
- SPEC-0001 Embeddings: `SPEC-0001-embeddings.md`
- SPEC-0002 Persistence (Postgres + pgvector): `SPEC-0002-persistence-postgres-pgvector.md`
- SPEC-0003 Evaluation Gates: `SPEC-0003-evaluation-gates.md`
- SPEC-0004 MCP Remote Tools: `SPEC-0004-mcp-remote-tools.md`
- SPEC-0005 Long-Term Memory: `SPEC-0005-long-term-memory.md`
- SPEC-0006 Rancher/Kubernetes Environment: `SPEC-0006-rancher-k8s-environment.md`

Conventions
- "Production" means: debuggable, testable, operable, and safe-by-default.
- Each spec includes a References section with external docs.