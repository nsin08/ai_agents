# ADR-0006: Long-Term Memory Scope and Safety Policy (Phase 2+)

Status: Proposed
Date: 2026-01-28
Owners: Architect/PM

## Context
Phase 2 introduces persistent memory. This is high-risk: most agent systems fail here by either:
- storing raw conversation data unsafely
- injecting irrelevant or unsafe memory into prompts
- lacking deletion/retention and tenant isolation

The design doc calls for write/retrieval/retention policies and a consolidation pipeline.

## Decision
Phase 2 memory will be "facts-first" long-term memory with explicit policies:
- Store extracted facts/preferences, not raw transcripts, by default.
- Store episodic logs only if explicitly enabled and always with retention + redaction.

Enforcement:
- WritePolicy: controls when/what can be persisted.
- RetrievalPolicy: controls what memory can be injected.
- RetentionPolicy: TTL + deletion workflows.

## Options Considered

1) Facts-first memory (chosen)
- Pros: safer; easier to audit; reduces prompt injection and privacy exposure; easier to dedupe.
- Cons: requires extraction and dedupe logic; may miss nuance.

2) Store everything (raw text)
- Pros: simplest; "seems to work" initially.
- Cons: privacy/security nightmare; noisy retrieval; hard to delete; high long-term cost.

## Consequences
- We must implement a consolidation pipeline (episodes -> candidate facts -> validate -> dedupe -> persist).
- We must define a minimum metadata contract:
  - tenant_id, source, created_at, expires_at, confidence
- We must add deletion audit events.

## Acceptance Criteria
- Default configuration does not persist raw conversations.
- Memory writes and retrievals are policy-checked and auditable.
- Tenant scoping exists in the data model (even if enforcement is phased).

## Open Questions
- Do we allow user-visible "forget" commands in Phase 2, or Phase 3?
- What is the minimum retention window for episodic data (if enabled)?