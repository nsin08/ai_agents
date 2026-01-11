# Level 3 Slides: Production Patterns, Safety, and Operations

Use this as a slide outline. Each "Slide" section is intended to become 1 slide.

This deck aligns to the advanced chapters in `03_advanced/`:

- Safety guardrails: `chapter_01_safety_guardrails.md`
- Multi-agent systems: `chapter_02_multi_agent_systems.md`
- Production deployment: `chapter_03_production_deployment.md`
- Scaling strategies: `chapter_04_scaling_strategies.md`
- Monitoring and alerting: `chapter_05_monitoring_alerting.md`
- Security best practices: `chapter_06_security_best_practices.md`

---

## Slide 01: Title

AI Agents - Advanced: Production Patterns, Safety, and Operations (Level 3)

---

## Slide 02: Audience and Outcomes

- Audience: senior engineers, staff+ engineers, architects
- Outcome: build production-grade agents with safety, observability, and deployment readiness
- Focus: trade-offs and operational reality (not just demos)

---

## Slide 03: The Production Reality

- Most production agent engineering is: failure handling + safety + operations
- Non-determinism is expected; verification and evaluation are required
- "It works on my laptop" is not a deployment strategy

---

## Slide 04: The Agent System View (End-to-End)

- Request -> plan -> tool calls -> response
- Guardrails at boundaries (pre-request, pre-tool, post-output)
- Telemetry everywhere (logs, metrics, traces, audit)

---

## Slide 05: Safety Guardrails (Chapter 01)

- Safety is an enforced envelope around tools, data, and outputs
- Checkpoint model beats prompt-only safety
- Policy is config-driven and versioned

---

## Slide 06: Guardrail Checkpoints (Architecture)

```text
request -> validate_request -> plan -> validate_tool_call -> execute -> validate_output -> response
```

- Pre-request: budgets and sanity checks
- Pre-tool: allowlists, schema, authz
- Post-output: redaction and output policy

---

## Slide 07: PII Detection and Redaction (What to Measure)

- Redaction events count (by tenant/workflow)
- False positives (user reports) vs false negatives (audit findings)
- Redaction applied to: logs, memory writes, and user outputs

---

## Slide 08: Case Study - Invoice Approval Assistant (Safety)

- High-risk writes: approvals required, audit logs mandatory
- Strict allowlist of tools; evidence required for recommendations
- Degraded mode for tool failures (partial summary + next steps)

---

## Slide 09: Multi-Agent Systems (Chapter 02)

- Multi-agent is for ceilings: context, skills, permissions, throughput
- More agents increases failure modes and cost
- Traceability and stop conditions are mandatory

---

## Slide 10: Router + Decomposition (Lab 8 Core Pattern)

```text
subtasks = decompose(task)
for subtask in subtasks:
  agent = route(subtask)
  result = delegate(agent, subtask)
return combine(results)
```

- Deterministic and testable starting point

---

## Slide 11: Multi-Agent Boundaries (Safety by Design)

- Capabilities are permissions (not labels)
- Per-agent tool allowlists and budgets
- Write actions are gated and audited

---

## Slide 12: Case Study - Incident Response Assistant (Multi-Agent)

- Investigator: read-only
- Mitigator: propose-only (writes require approval)
- Communicator: output-limited
- Observability: trace subtask routing and tool durations

---

## Slide 13: Production Deployment (Chapter 03)

- Containerize first for reproducibility
- Config-driven providers: local (Ollama) vs hosted (prod)
- Deploy with rollouts and rollback (Kubernetes recommended at scale)

---

## Slide 14: Kubernetes Readiness (Key Concepts)

- /healthz (liveness), /readyz (readiness)
- Resource limits + concurrency caps
- Degraded modes for dependency failures

---

## Slide 15: Release Gates for Agents (Not Optional)

- Deterministic tests: tools, guardrails, orchestrator
- Eval suite: golden set + adversarial prompts
- Gate rollouts on: success rate, safety blocks, cost per success

---

## Slide 16: Scaling Strategies (Chapter 04)

- Measure first: where do latency and tokens go?
- Caching is powerful but must be safe (tenant-scoped keys)
- Async helps only with backpressure (concurrency limits)

---

## Slide 17: Scaling Levers (Trade-offs)

- Caching vs correctness (scope keys + invalidation)
- Parallelism vs dependency overload (semaphores + timeouts)
- Routing small vs large models (cost vs quality)

---

## Slide 18: Monitoring and Alerting (Chapter 05)

- Observe outcomes, safety, and cost (not only uptime)
- Logs: what happened; metrics: how often; traces: where time went
- Audit events: who did what (writes and privileged reads)

---

## Slide 19: SLOs That Match Agent Reality

- Success rate on golden set (release quality)
- p95 latency (interactive experience)
- Safety blocks by rule (drift signal)
- Cost per success (budget control)

---

## Slide 20: Incident Response for Agents (Runbook Signals)

- Provider outage: timeouts spike, latency spike
- Tool degradation: tool error rate spike
- Injection attempts: guardrail blocks spike
- Guardrail drift: blocks spike for benign inputs after rollout

---

## Slide 21: Security Best Practices (Chapter 06)

- Tools are the core security boundary (authz in code)
- Secrets never enter prompts/logs/memory
- Multi-tenant isolation requires tenant scoping everywhere

---

## Slide 22: Audit Logs (Minimum Fields)

- request_id, actor (user_id, tenant_id)
- tool/action, proposed change (diff)
- approvals (who/when/why)
- policy/config version, outcome

---

## Slide 23: Production Checklist (What "Ready" Looks Like)

- Safety tier defined; approvals and audit in place for writes
- Observability: metrics, traces, dashboards, alerts
- Scaling controls: timeouts, retries, circuit breakers, concurrency caps
- Deployment: canary rollout and rollback plan

---

## Slide 24: Next Steps (Projects and Pro Level)

- Use the case studies and ADRs to practice architecture decisions
- Apply patterns to Level 3 projects (writes, eval harness, cost engineering)
- Prepare for Level 4 (domain specialization and platform scale)
