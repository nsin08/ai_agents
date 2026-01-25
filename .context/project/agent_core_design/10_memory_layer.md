# Memory Layer (Session, Long-Term, Run State)

## Goals

- Separate short-term session state from long-term memory.
- Make persistent memory safe: explicit policies, tenant scoping, retention, redaction.
- Support checkpoint/resume via a run state store interface (even if not implemented in v1).

## Memory types

### Session store (short-term)

Use for:
- current conversation context
- temporary working memory for a run

Typical backends:
- in-memory (local dev)
- Redis (production)

### Long-term store (persistent)

Use for:
- stable facts and preferences
- episodic records (careful: high privacy risk)

Must be protected by:
- explicit write policy
- explicit retrieval policy
- retention and deletion support
- tenant scoping

Typical backends:
- local sqlite/file store (dev)
- Postgres (production baseline)

### Run store (runtime state)

Use for:
- checkpoint/resume support
- replay/debug artifacts
- partial failure recovery

Backends:
- in-memory initially
- file-backed store (local)
- Postgres/object store (production)

## Policies

### Write policy

Defines:
- when to write to long-term memory
- what to write (facts vs raw text)
- extraction and deduplication rules
- redaction rules

### Retrieval policy

Defines:
- what memory may be injected into prompts
- how to prioritize memory vs external retrieval
- injection hygiene constraints

### Retention policy

Defines:
- TTLs per class of memory
- legal/compliance deletion workflows
- audit of deletion actions

## Consolidation pipeline

Avoid "store everything forever".
Recommended pipeline:
- episodes -> extracted candidate facts -> validate -> merge/dedupe -> persist

This pipeline can be:
- synchronous for small scopes
- asynchronous job for production (recommended)

## Multi-tenancy requirements (design now, enforce later)

Even if v1 is single-tenant, the data model should include:
- `tenant_id` on all persistent keys
- tenant-aware filtering as an invariant at store boundaries

