# Level 4 Use Cases — Domain Specialization & Scale

Use these to practice “domain + operations” design.

## Use Case 1: Enterprise Support Agent Platform

- Many tenants, different policies, different tool access
- Requires: tenant isolation, per-tenant configuration, cost attribution, eval gates

## Use Case 2: Coding Agent in a Regulated Codebase

- Requires: strict write approvals, audit logs, reproducible builds, high test coverage
- Must integrate with: CI, codeowners, PR review workflows

## Use Case 3: Medical Assistant with Conservative Autonomy

- Requires: refusal policy, escalation, privacy boundaries, comprehensive logging controls
- Prefer: read-only tools; approvals for any record updates

## Use Case 4: DevOps Mitigation Agent (High Blast Radius)

- Requires: staged actions (suggest → approve → execute), rollback, circuit breakers
- Telemetry must support post-incident analysis (“why did it do that?”)
