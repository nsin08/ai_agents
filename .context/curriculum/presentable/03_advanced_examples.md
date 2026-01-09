# Level 3 Examples — Production Patterns & Safety

## Example 1: Failure Mode Matrix (Template)

```text
Failure Mode | Detection Signal | Recovery | User Message | Telemetry
------------ | ---------------- | -------- | ------------ | ----------
Tool timeout | latency > T      | retry w/ backoff | "System slow; retrying" | tool_timeout_count
Tool 5xx     | status=5xx       | retry + circuit breaker | "Service unavailable" | tool_error_rate
Bad args     | schema reject    | re-plan w/ constraints | "Need different input" | validation_failures
Context overflow | tokens > budget | summarize + drop low-signal | "Summarizing context" | context_compression_events
Partial success | step N fails after writes | checkpoint + compensation | "Completed X; couldn’t do Y" | partial_success
```

## Example 2: Circuit Breaker (Behavior)

```text
If tool_failures(tool_X) >= 5 in 2 minutes:
  - open breaker for 10 minutes
  - route to fallback source (cached data / alternate tool)
  - notify operator if high severity
```

## Example 3: Release Gate Policy (Golden Tests)

```text
Block release if:
- success_rate drops > 2% on golden set
- unsafe_action_blocked rate increases > 20% (guardrail drift)
- p95 latency increases > 25%
- cost per success increases > 30%
```

## Example 4: HITL Approval Event (Audit)

```json
{
  "request_id": "uuid",
  "action": "update_crm_record",
  "proposed_change": { "field": "phone", "before": "***", "after": "***" },
  "approver": "user_id",
  "approved_at": "timestamp",
  "reason": "customer_confirmed",
  "ticket_ref": "INC-1234"
}
```

## Example 5: Security Controls at Tool Boundary (Checklist)

```text
Before executing tool:
- schema validate arguments
- authorize (RBAC + tenant scope)
- apply allowlist/denylist rules
- detect injection patterns in tool inputs

After tool result:
- sanity check outputs (types, ranges, constraints)
- redact sensitive values before logging
- attach provenance for downstream reasoning
```

