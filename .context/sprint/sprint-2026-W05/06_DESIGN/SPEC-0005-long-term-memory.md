# SPEC-0005: Long-Term Memory (Facts-first + Policies)

Status: Draft
Date: 2026-01-28
Related ADRs:
- `.context/sprint/sprint-2026-W05/04_DECISIONS/ADR-0006-long-term-memory-scope.md`
Design references:
- `.context/project/agent_core_design/10_memory_layer.md`

## Abstract
This spec defines a production long-term memory system for agents. It introduces memory types, risks, and the rationale for a facts-first approach. It specifies required policies (write/retrieval/retention), a consolidation pipeline, and decision guidance on when to store facts versus episodic records.

## 1. Introduction
### 1.1 What is "memory" in an agent system?
Memory is stored information the agent can use across turns and across runs.
- Session memory: short-term conversation state.
- Long-term memory: durable facts/preferences.
- Run state: checkpoint/resume and replay (later).

### 1.2 Why long-term memory is risky
Long-term memory failures are typically catastrophic:
- privacy leaks (storing sensitive user data)
- prompt injection amplification (storing malicious content and replaying it)
- irreproducible behavior ("why did it answer that?")
- compliance failures (no delete/retention story)

### 1.3 Design stance
Phase 2 memory is facts-first by default.
- We store extracted facts/preferences.
- We do not store raw transcripts unless explicitly enabled.

## 2. Requirements
### 2.1 Functional
- Persist safe memory records.
- Retrieve memory with tenant scoping.
- Support deletion and retention.
- Emit auditable events for writes/retrieval/deletes.

### 2.2 Non-functional
- Safe-by-default configuration.
- Deterministic behavior under fixtures for CI.
- Clear invariants and observability.

## 3. Technical Design

### 3.1 Data model (minimum)
Each memory record MUST include:
- `tenant_id`
- `kind`: `fact|preference|episode`
- `key` (optional)
- `value` (structured JSON)
- `source` (origin)
- `confidence`
- `created_at`, `expires_at`, `deleted_at`

Rationale:
- Tenant scoping prevents data bleed.
- Retention/deletion fields make compliance possible.

### 3.2 Policies

#### 3.2.1 WritePolicy
Controls:
- whether the system may write at all
- what kinds are allowed
- redaction requirements
- dedupe/merge rules

Default policy:
- deny raw transcript persistence
- allow extracted facts/preferences after redaction

#### 3.2.2 RetrievalPolicy
Controls:
- what can be injected into prompts
- prioritization relative to external retrieval
- injection hygiene constraints
- token budgets

Default policy:
- limit quantity and size
- include provenance
- allow explicit "user confirmed" facts to rank higher

#### 3.2.3 RetentionPolicy
Controls:
- TTL by kind
- deletion workflows
- audit of deletion actions

### 3.3 Consolidation pipeline
Pipeline:
- episodes -> candidate facts -> validate -> dedupe/merge -> persist

Key properties:
- deterministic under fixtures
- auditable transformations
- prevents "store everything forever"

### 3.4 Observability and auditing
Emit events:
- `memory.write_attempted`
- `memory.write_blocked`
- `memory.write_succeeded`
- `memory.retrieved`
- `memory.deleted`

## 4. Decision Guidance (What to store)

### Scenario A: user preferences (safe)
Store as `preference` facts with explicit source and TTL.

### Scenario B: personal/sensitive details
Default deny; require explicit consent + redaction + retention constraints.

### Scenario C: episodic logs (high risk)
Only if explicitly enabled and short TTL.
- Used for debugging or limited personalization.

### Scenario D: enterprise multi-tenant deployments
Treat tenant scoping as a hard invariant at store boundaries from day 1.

## 5. Validation (What "done" means)
- Default config does not persist raw transcripts.
- Writes blocked by policy are auditable.
- Deletion works and emits audit events.
- Retrieval output is bounded and safe to inject.

## 6. References
```text
Data minimization principle (privacy)
https://en.wikipedia.org/wiki/Data_minimization

NIST Privacy Framework (high-level guidance)
https://www.nist.gov/privacy-framework
```