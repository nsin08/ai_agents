# Level 3 Examples: Production Patterns, Safety, and Operations

Use these examples as copy/paste starting points when building advanced agents.

Related materials:

- Pattern library: `implementation_patterns_library.md`
- Case studies: `case_studies/`

---

## Example 1: Failure Mode Matrix (Template)

```text
Failure Mode     | Detection Signal        | Recovery                  | User Message                       | Telemetry
----------------|-------------------------|---------------------------|------------------------------------|-------------------------
Tool timeout     | latency > T             | retry w/ backoff          | "System slow; retrying..."         | tool_timeout_count
Tool 5xx         | status=5xx              | retry + circuit breaker   | "Service unavailable"              | tool_error_rate
Bad args         | schema reject           | re-plan w/ constraints    | "Need different input"             | validation_failures
Context overflow | tokens > budget         | summarize + drop low-signal| "Summarizing context"              | context_compression_events
Partial success  | step N fails after write| checkpoint + compensation | "Completed X; could not do Y"      | partial_success
```

---

## Example 2: Circuit Breaker Policy (Readable Spec)

```text
If tool_failures(tool_X) >= 5 in 2 minutes:
  - open breaker for 10 minutes
  - route to fallback source (cached data / alternate tool)
  - notify operator if high severity
```

---

## Example 3: Release Gate Policy (Golden Tests)

```text
Block release if:
- success_rate drops > 2% on golden set
- safety_blocks_by_rule changes > 20% without explanation
- p95 latency increases > 25%
- cost per success increases > 30%
```

---

## Example 4: HITL Approval Event (Audit)

```json
{
  "request_id": "uuid",
  "action": "update_invoice_status",
  "proposed_change": { "field": "status", "before": "pending", "after": "approved" },
  "approver": "user_id",
  "approved_at": "timestamp",
  "reason": "verified",
  "ticket_ref": "FIN-1234",
  "policy_version": "guardrails-prod-v3"
}
```

---

## Example 5: Tool Boundary Checklist (Pre and Post)

```text
Before executing tool:
- schema validate arguments
- authorize (RBAC + tenant scope)
- apply allowlist/denylist rules
- enforce timeouts and budgets

After tool result:
- validate output schema
- sanity-check constraints (ranges, types)
- redact sensitive values before logging
- attach provenance for downstream reasoning
```

---

## Example 6: Multi-Agent Execution Trace (Human-Readable)

```text
request_id=req-123

subtask_1="Investigate error spike" -> agent=investigator
  tool_call logs_read +120ms (ok)
  tool_call metrics_read +80ms (ok)

subtask_2="Propose mitigation" -> agent=mitigator
  proposed_action="roll back feature flag X"
  requires_approval=true

subtask_3="Draft status update" -> agent=communicator
  output_length=420 chars

final="combined results with evidence and next steps"
```

---

## Example 7: Kubernetes Probe Snippet (Conceptual)

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /readyz
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

---

## Example 8: Observability Event Taxonomy (Starter Set)

```text
agent_started
turn_started
llm_request_sent
llm_response_received
tool_call_initiated
tool_call_completed
guardrail_blocked
agent_completed
agent_failed
```

