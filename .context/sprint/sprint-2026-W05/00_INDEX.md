# Sprint 2026-W05 (Phase 2+ Planning)

## Single Source Of Truth
- Program plan: `01_PROGRAM/phase2plus_program_plan.md`

## Backlog
- Epics and stories: `05_BACKLOG/phase2plus_epics_stories.md`

## Environment (Docker Stores)
- Compose stack: `03_ENV/docker-compose.backend-stores.yml`
- Stores design: `03_ENV/backend_stores_design.md`
- Docker library plan: `03_ENV/docker_library_plan.md`

## Decisions (ADRs)
- ADR-0001 Embeddings: `04_DECISIONS/ADR-0001-embeddings.md`
- ADR-0002 Rancher/K8s phasing: `04_DECISIONS/ADR-0002-rancher-k8s-phasing.md`

## Archived / Superseded
- Initial sprint plan draft: `99_ARCHIVE/plan.initial.md`

## Open Questions (keep <= 5)
1) What is the Phase 2 target deployment: local-only library+CLI, or service as well?
2) Vector DB decision: pgvector primary, Chroma optional - confirm.
3) Embedding model for dev: `nomic-embed-text` vs `mxbai-embed-large` - decide and document reindex strategy.
4) Memory store scope: facts-only vs episodic memory - decide policy baseline.
5) Evaluation gate scope: deterministic-only in Phase 2, or include real-mode stability runs?

## Working Rules (to prevent re-fragmentation)
- Scope/sequence changes go ONLY in `01_PROGRAM/phase2plus_program_plan.md`.
- Any decision goes in `04_DECISIONS/` as an ADR (1 page, decision + tradeoffs + consequences).
- Environment artifacts live in `03_ENV/`.
- Old drafts go in `99_ARCHIVE/`.
