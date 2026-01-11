# Production Deployment Checklist (Agents)

This checklist is used by Level 3 learners to ship a production-grade agent service with safety, observability, and rollback readiness.

**Related chapters:**  
- Deployment: `chapter_03_production_deployment.md`  
- Safety: `chapter_01_safety_guardrails.md`  
- Observability: `chapter_05_monitoring_alerting.md`  
- Security: `chapter_06_security_best_practices.md`

---

## 1) Architecture and Scope

- [ ] Clear scope: what workflows and intents are supported (and not supported)
- [ ] Safety tier defined (Tier 0/1/2) with documented rationale
- [ ] Tool inventory documented (read vs write, risk tier)
- [ ] Data inventory documented (PII, secrets, regulated data)
- [ ] Degraded modes defined for each dependency (LLM, tools, retrieval)

---

## 2) Safety and Guardrails

- [ ] Guardrail checkpoints implemented (pre-request, pre-tool, post-output)
- [ ] Budgets enforced (tokens, time, cost) with graceful fallback behavior
- [ ] Tool allowlist/blocklist enforced in code (not prompt-only)
- [ ] Tool input/output schema validation exists (contract checks)
- [ ] Human approvals required for writes (confirm-before-write or supervisor queue)
- [ ] PII redaction applied before output, logging, and memory writes
- [ ] Guardrail telemetry emitted (blocked_by_rule, redaction_events_count)

---

## 3) Security

- [ ] Threat model documented (prompt injection, tool misuse, exfil, memory poisoning)
- [ ] Authn/authz enforced for every tool call (RBAC + tenant scope)
- [ ] Secrets never enter prompts/logs/memory; secrets stored in a secret manager
- [ ] Multi-tenant isolation enforced in tools, retrieval, caches, and storage keys
- [ ] Audit logs enabled for high-risk actions and privileged reads
- [ ] Logging and tracing access is restricted (privacy controls)

---

## 4) Observability

- [ ] Structured logs with stable event names (agent, turn, tool, guardrail)
- [ ] Correlation IDs for request/session and tool calls
- [ ] Tracing spans for turns, tools, retrieval, and provider calls (sampled)
- [ ] Metrics dashboard includes:
  - success rate
  - p95 latency
  - tool error rate and timeouts
  - safety blocks by rule
  - cost per success (if applicable)
- [ ] Alerting thresholds defined and tested (simulated incident)

---

## 5) Reliability and Operations

- [ ] Timeouts exist at request and tool levels
- [ ] Retries are bounded and use backoff; no infinite loops
- [ ] Circuit breakers for degraded tools/providers
- [ ] Idempotency keys for write actions
- [ ] Resource limits and concurrency caps configured (avoid overload)
- [ ] Runbooks exist for:
  - provider outage
  - tool degradation
  - retry storms
  - prompt injection attempts
  - guardrail drift after rollout

---

## 6) Evaluation and Release Gates

- [ ] Deterministic tests pass (unit + integration with mocks)
- [ ] Golden set evaluation run and stored (baseline vs candidate comparison)
- [ ] Adversarial prompt set run (injection attempts, unsafe tool requests)
- [ ] Release gates defined (example thresholds):
  - success rate drop <= 2%
  - cost per success increase <= 25%
  - safety blocks change <= 20% unless expected
- [ ] Evidence attached to PR (test logs, eval summary, metrics snapshot)

---

## 7) Deployment (Docker/Kubernetes)

- [ ] Reproducible container build with pinned dependencies
- [ ] Environment config is externalized (ConfigMap / env vars)
- [ ] Secrets injected securely (Secret store)
- [ ] Health endpoints exist:
  - /healthz (liveness)
  - /readyz (readiness)
- [ ] Kubernetes probes configured with reasonable thresholds
- [ ] Rolling update strategy defined
- [ ] Canary rollout supported (small % traffic first)

---

## 8) Rollback and Post-Deploy Verification

- [ ] Rollback plan documented and tested (how to revert quickly)
- [ ] Post-deploy verification steps defined:
  - run smoke tests
  - check dashboards
  - validate safety blocks are within expected range
- [ ] Incident response owner defined (on-call or rotation)
- [ ] Retrospective process defined for incidents and regressions

