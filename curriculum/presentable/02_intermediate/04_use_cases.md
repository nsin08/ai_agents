# Level 2 Use Cases — Core Components & Integration

Use these to practice system design decisions (tools, memory, policy, telemetry).

## Use Case 1: Support Triage Agent (Read-Only → Assisted Write)

**Phase 1 (read-only):**
- Tools: ticket read, KB search, logs read
- Output: classification, summary, suggested response with citations

**Phase 2 (assisted write):**
- Add tool: draft_response (no send)
- Add tool: add_internal_note (requires confirmation gate)

Key design focus: tool contracts + safe action gating.

## Use Case 2: Engineering PR Review Assistant (Read-Only)

- Tools: git diff read, tests status read, lints status read
- Output: risk highlights, missing tests, suggested improvements

Key design focus: citations to diff hunks + guardrails against hallucinated code changes.

## Use Case 3: Incident Runbook Assistant (Read-Only with Escalation)

- Tools: alert context read, log search, runbook retrieval (RAG)
- Output: recommended mitigation steps + escalation criteria

Key design focus: retrieval policy + context packing under token constraints.

## Use Case 4: CRM Enrichment (Limited Writes)

- Tools: CRM read, enrichment API, CRM update (write)
- Guardrails: confirmation gates, PII redaction, audit logs

Key design focus: idempotency + rollback strategy for writes.
