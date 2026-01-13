# Level 3 Workbook: Production Patterns, Safety, and Operations (A1-A6)

**Goal:** Make agent systems reliable, testable, secure, and operable.  
**Estimated time:** 4-5 weeks (or 6-10 instructor-led sessions).  
**Prerequisites:** Level 2 outcomes (orchestrator + tools + memory + policies + telemetry).

## How to Use This Level

This Level 3 workbook is the guided path. The deep dives live in the chapter files:

- Chapter 01 (Safety): `chapter_01_safety_guardrails.md`
- Chapter 02 (Multi-agent): `chapter_02_multi_agent_systems.md`
- Chapter 03 (Deployment): `chapter_03_production_deployment.md`
- Chapter 04 (Scaling): `chapter_04_scaling_strategies.md`
- Chapter 05 (Observability): `chapter_05_monitoring_alerting.md`
- Chapter 06 (Security): `chapter_06_security_best_practices.md`

Supporting materials:

- Case studies: `case_studies/`
- ADRs: `adrs/`
- Pattern library: `implementation_patterns_library.md`
- Deployment checklist: `production_deployment_checklist.md`

---

## Level Outcomes

By the end of Level 3, learners can:

- Use decision trees to select architectures and safety posture
- Design failure handling (retries, fallbacks, compensation) as a first-class feature
- Build testing/evaluation harnesses for regression and safety validation
- Threat-model agent systems and implement security/compliance controls
- Implement human-in-the-loop workflows for high-risk actions
- Scale performance without sacrificing safety or debuggability

---

## Production Readiness Checklist (High Level)

Use this before any pilot deployment (see also `production_deployment_checklist.md`):

- **Safety:** RBAC, allowlisted tools, confirmation gates, audit logs, PII redaction
- **Reliability:** retries, timeouts, idempotency, circuit breakers, partial-success handling
- **Evaluation:** golden tests, adversarial tests, regression dashboard, release gates
- **Observability:** request tracing, tool-call logs, cost tracking, alerting
- **Operations:** versioning strategy, rollback, incident playbook, on-call ownership

---

## A1 - Design Decision Trees

**Primary sources:** `../../../../Agents/06_design_decision_tree.md`, `../../../../Agents/07_design_decision_tree.md`  
**Timebox:** 90-120 minutes

### Objectives

- Use decision trees to select orchestration patterns, memory strategy, and safety tier
- Make trade-offs explicit (cost/latency/accuracy/risk)

### Exercises

1. Run your workflow through the decision trees and capture:
   - chosen orchestration style (loop vs graph)
   - memory strategy (RAG-only vs long-term memory)
   - safety tier (read-only vs limited write vs high-stakes)
2. Document 3 trade-offs and why you accepted them.

Recommended artifact: an ADR (one page) capturing your choices and rationale.

---

## A2 - Failure Modes and Recovery Patterns

**Source status:** Synthesized; cross-check with `../../../review/ai_agents_critical_review.md`  
**Timebox:** 120-150 minutes

### Objectives

- Enumerate agent-specific failure modes (beyond normal services)
- Design recovery strategies that are testable and observable

### Failure Mode Taxonomy (Starter Set)

1. **Tool failures:** timeouts, 5xx, invalid schema, partial results
2. **Tool cascade failures:** one failing dependency blocks downstream steps
3. **Non-determinism:** different plans on identical inputs (stability risk)
4. **Context overflow:** tool logs + docs + plan exceed token budget
5. **Hallucinated actions:** model proposes non-existent tool calls or unsafe args
6. **Partial success:** steps 1-3 succeed; step 4 fails; user disconnects
7. **Infinite retry loops:** repeated tool failures without new information

### Recovery Patterns

- **Idempotency keys** for all writes
- **Circuit breakers** per tool/integration
- **Compensating actions** (undo/rollback) when possible
- **Checkpointing** intermediate artifacts (so you can resume safely)
- **Degraded modes**: read-only fallback or "ask user for missing input"

### Exercises

Create a failure-mode matrix for your workflow:

- Rows: failure modes (above + your own)
- Columns: detection signal, recovery action, user messaging, telemetry to capture

---

## A3 - Testing and Evaluation Framework

**Source status:** Synthesized; cross-check with `../../../review/ai_agents_critical_review.md`  
**Timebox:** 150-180 minutes

### Objectives

- Build a test strategy for non-deterministic systems
- Define metrics and release gates for agent upgrades
- Separate unit/integration tests (deterministic) from behavior evals (probabilistic)

### Recommended Test Layers

1. **Tool unit tests:** schema validation, RBAC, side-effect boundaries
2. **Orchestrator tests:** state transitions, retries, stop conditions
3. **Golden behavior tests:** fixed scenarios with expected outcomes
4. **Adversarial tests:** prompt injection, jailbreak attempts, unsafe tool args
5. **Load tests:** concurrency, latency, cost under realistic traffic

### Core Metrics (Pick 6-10)

- Task success rate (overall + by intent type)
- Unsafe action blocked count (should exist; indicates guardrails firing)
- Hallucination rate (unsupported claims without citations)
- Tool failure rate and mean time to recover
- p95 latency and cost per successful task
- Human escalation rate and approval turnaround time

### Exercises

- Draft a golden test set of 25 cases (inputs + required artifacts + expected outputs).
- Define 3 release gates (for example, success rate must not drop more than 2%).

---

## A4 - Security and Compliance

**Source status:** Synthesized; cross-check with `../../../review/ai_agents_critical_review.md`  
**Timebox:** 120-150 minutes

### Objectives

- Threat-model agent systems (prompt injection + tool misuse + data exfiltration)
- Implement least privilege at tool boundaries
- Design auditing suitable for regulated or high-risk environments

### Threat Model (Starter Set)

- Prompt injection via retrieved documents (RAG injection)
- Over-privileged tools enabling unauthorized actions
- Data exfiltration through tool outputs or logs
- Memory contamination (storing untrusted user content as "facts")
- Credential leakage (secrets in prompts or logs)

### Controls (Practical)

- Tool allowlist + schema validation + RBAC for every call
- Secrets management: never in prompts; use vaults and short-lived tokens
- PII redaction in logs and model outputs where required
- Audit logs: who requested, what tool executed, what changed
- Tenant isolation for memory and retrieval

### Exercises

- Write a security checklist for your workflow (inputs, outputs, tools, memory).
- Identify the top 3 abuse cases and your mitigations.

---

## A5 - Human-in-the-Loop (HITL) Patterns

**Source status:** Synthesized; cross-check with `../../../review/ai_agents_critical_review.md`  
**Timebox:** 90-120 minutes

### Objectives

- Design approval workflows that keep users in control of risk
- Avoid approval fatigue while still preventing catastrophic actions
- Make HITL decisions auditable and reversible when possible

### Patterns

- **Confirm-before-write:** user approves the exact diff/patch
- **Supervisor queue:** agent proposes; human reviewer approves/rejects with reasons
- **Two-person rule:** high-stakes actions require two approvals
- **Timeboxed approvals:** if no approval, fall back to read-only summary + next steps

### Exercises

- Add HITL to one write action in your workflow:
  - what is shown to the human (diff, summary, risks)?
  - what is required to approve (role, reason, ticket link)?
  - what is logged (evidence)?

---

## A6 - Scalability and Performance

**Primary source:** `../../../../Agents/08_scalability_and_performance.md`  
**Timebox:** 90-120 minutes

### Objectives

- Reduce latency and cost while preserving reliability and safety
- Scale across tenants/workflows with isolation and observability

### Exercises

For your workflow, propose improvements in:

- caching (RAG results, summaries, tool results)
- routing (small/large model usage)
- concurrency (parallel reads vs serialized writes)
- backpressure (queues, rate limits, timeouts)

---

## Optional: Cost Benchmarks (Guidance)

Directional estimates (vary by model, tokens, tools, and your guardrails):

| Agent Type | Typical Cost / Resolved Task | Common Drivers |
|---|---:|---|
| FAQ bot (RAG only) | $0.001-$0.01 | small model + retrieval |
| Support agent | $0.05-$0.15 | multiple tool calls + longer context |
| Code review assistant | $0.20-$0.50 | larger model + long contexts |
| DevOps troubleshooting | $0.30-$0.80 | log retrieval + multi-step chains |
| Medical assistant | $0.50-$1.50 | deep reasoning + compliance logging |

---

## Level 3 Hands-On Projects

Recommended sequence:

- `projects/P06_support_agent_with_writes.md`
- `projects/P07_testing_harness.md`
- `projects/P11_cost_engineering.md` (optional but high leverage)

