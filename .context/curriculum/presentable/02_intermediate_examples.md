# Level 2 Examples — Core Components & Integration

## Example 1: Orchestrator as a State Machine (Pseudocode)

```pseudo
states:
  START -> GATHER_CONTEXT -> PLAN -> EXECUTE -> VERIFY -> DONE
  any -> FAIL (if irrecoverable)

rules:
  - max_steps = 12
  - max_cost_usd = 0.50
  - retries(tool_timeout) = 2 with backoff
  - retries(tool_5xx) = 3 with backoff + jitter
  - circuit_breaker(tool) trips after N failures
```

## Example 2: Tool Contract (Schema + Permissions)

```yaml
tool: create_ticket_comment
description: "Add an internal note to an existing ticket."
inputs:
  ticket_id: { type: string, pattern: "^TCKT-[0-9]+$" }
  body: { type: string, max_length: 2000 }
permissions:
  required_role: "support_agent"
side_effects:
  writes: ["ticketing_system.comment"]
  irreversible: false
validation:
  reject_if:
    - contains_secrets(body)
    - contains_pii(body) and not redacted
```

## Example 3: Memory Policies (Write + Retrieval)

```text
Write policy (long-term):
- Store only stable preferences and validated facts
- Never store secrets, credentials, or raw PII
- Partition by tenant and user

Retrieval policy (RAG/memory):
- Allowlist sources (kb, runbooks, approved docs)
- Add provenance (doc_id, section, timestamp)
- Enforce token budget; summarize when overflow
```

## Example 4: Context Packing Plan (Token Budget)

```text
System + policy:        10%
Tool schemas:           15%
Retrieved docs (RAG):   40%
Conversation summary:   15%
Recent messages:        20%
```

Fallback: if overflow → summarize retrieved docs + drop low-signal history.

## Example 5: Observability Event Model (Minimal)

```json
{
  "request_id": "uuid",
  "workflow_id": "support.triage.v1",
  "tenant": "acme",
  "model_calls": [{ "model": "X", "tokens": 1234, "latency_ms": 840, "cost_usd": 0.02 }],
  "tool_calls": [{ "tool": "search_kb", "status": "ok", "latency_ms": 120 }],
  "safety_events": [{ "type": "blocked_action", "reason": "write_requires_approval" }]
}
```

