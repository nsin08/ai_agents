# Level 2 Use Cases — Intermediate Curriculum

Use these to practice system design decisions (tools, memory, policy, telemetry).

---

## Use Case 1: Support Triage Agent (read-only + assisted write)

**Phase 1 (read-only):**

- Tools: ticket read, KB search (RAG), logs read
- Output: classification, summary, suggested response with citations

**Phase 2 (assisted write):**

- Add tool: draft_response (no send)
- Add tool: add_internal_note (requires confirmation gate)

Key design focus: tool contracts + safe action gating + observability.

---

## Use Case 2: Engineering PR Review Assistant (read-only)

- Tools: git diff read, tests status read, lints status read
- Output: risk highlights, missing tests, suggested improvements

Key design focus: citations to evidence + context packing + multi-turn follow-ups.

---

## Use Case 3: Incident Runbook Assistant (read-only with escalation)

- Tools: alert context read, log search, runbook retrieval (RAG)
- Output: recommended mitigation steps + escalation criteria

Key design focus: retrieval policy + context window control + tracing.

---

## Use Case 4: CRM Enrichment (limited writes)

- Tools: CRM read, enrichment API read, CRM update (write)
- Guardrails: confirmation gates, PII redaction, audit logs

Key design focus: idempotency + rollback strategy for writes.

