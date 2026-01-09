# Level 4 Examples — Domain Specialization & Scale

## Example 1: Deployment Decision Matrix (Template)

```text
Dimension | Self-managed | Agent-as-a-service
--------- | ----------- | -----------------
Control   | High        | Medium
Compliance| Easier to enforce internally | Depends on vendor controls
Speed     | Slower setup | Faster start
Cost      | Infra + ops burden | Usage-based + vendor margin
Observability | Full control | Depends on provided telemetry
```

## Example 2: Operations Runbook Skeleton (Outline)

```text
1. SLOs (availability, latency, task success rate, safety incidents)
2. Alerts (tool error spikes, cost spikes, success regressions)
3. Rollback playbook (model version, prompt pack, tool schema)
4. Incident triage (who, what logs, what traces)
5. Data handling (PII policy, retention, access controls)
```

## Example 3: Multi-Agent Collaboration (Minimal Protocol)

```text
Roles: Planner, Researcher, Executor, Critic
Shared state: task_id, constraints, artifacts, tool results
Rules:
- Only Executor can call tools that mutate state
- Critic must verify before “done”
- Planner revises plan when Critic fails verification
```

## Example 4: Platform-Scale Requirements (Checklist)

```text
- Tenant isolation for memory and retrieval
- Per-tenant policy configuration (tools allowed, risk tier)
- Cost attribution per tenant/user/workflow
- Eval gates for model/prompt/tool upgrades
- Audit logs with retention and access controls
```

