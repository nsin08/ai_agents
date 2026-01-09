# Level 3 Use Cases — Production Patterns & Safety

Use these to practice “production posture” design: failure handling, security, HITL, evaluation.

## Use Case 1: Invoice Approval Assistant (High-Risk Writes)

- Tools: invoice retrieval, vendor DB, approval workflow (write)
- Risks: fraud, incorrect approvals, compliance
- Required: HITL, audit trail, regression suite, fraud heuristics

Key focus: approvals + audit + safety tiering.

## Use Case 2: Incident Mitigation Agent (Operational Risk)

- Tools: logs, metrics, runbooks, feature flag service (write), paging (write)
- Risks: making outage worse
- Required: staged rollout, circuit breakers, read-only fallback, supervisor queue

Key focus: failure modes + partial success + rollback.

## Use Case 3: Healthcare Triage Assistant (Regulated + Privacy)

- Tools: policy retrieval, patient record read (scoped), escalation workflow
- Risks: privacy violations, unsafe advice
- Required: strict tenant isolation, redaction, high coverage eval, logging controls

Key focus: compliance controls + evaluation gates.

## Use Case 4: Multi-Tenant Support Platform

- Tools: tenant-scoped KB search, ticket read/write, analytics
- Risks: cross-tenant data leakage, inconsistent policy enforcement
- Required: tenant isolation everywhere, per-tenant policy config, audit logs

Key focus: security boundaries + observability by tenant.
