[Previous](05_05_policies_and_guardrails.md) | [Next](06_design_decision_tree.md)

# Observability, Logging, Metrics, and Tracing  

## Table of Contents

- [**5.6 Observability — Logging, Metrics, and Tracing for Agent Systems**](#56-observability-logging-metrics-and-tracing-for-agent-systems)
- [1. What “observability” means for agents](#1-what-observability-means-for-agents)
- [2. Logging architecture](#2-logging-architecture)
  - [2.1 Principles](#21-principles)
  - [2.2 Log streams to produce](#22-log-streams-to-produce)
  - [2.3 Minimal structured log schema (example)](#23-minimal-structured-log-schema-example)
- [3. Agent telemetry (what to measure)](#3-agent-telemetry-what-to-measure)
  - [3.1 Core service metrics (standard)](#31-core-service-metrics-standard)
  - [3.2 Agent-specific metrics](#32-agent-specific-metrics)
  - [3.3 Suggested SLOs (example)](#33-suggested-slos-example)
- [4. Tracing multi-step agent workflows](#4-tracing-multi-step-agent-workflows)
  - [4.1 Use distributed tracing (OpenTelemetry recommended)](#41-use-distributed-tracing-opentelemetry-recommended)
  - [4.2 Trace diagram (conceptual)](#42-trace-diagram-conceptual)
  - [4.3 Trace attributes to attach](#43-trace-attributes-to-attach)
- [5. Debugging agent behavior](#5-debugging-agent-behavior)
  - [5.1 Reproducibility artifacts](#51-reproducibility-artifacts)
  - [5.2 Common failure classes](#52-common-failure-classes)
- [6. Evaluation frameworks (offline + online)](#6-evaluation-frameworks-offline-online)
  - [6.1 Offline evaluation](#61-offline-evaluation)
  - [6.2 Online evaluation](#62-online-evaluation)
  - [6.3 “LLM-as-judge” (use carefully)](#63-llm-as-judge-use-carefully)
- [7. Privacy, retention, and audit](#7-privacy-retention-and-audit)
  - [7.1 Redaction and minimization](#71-redaction-and-minimization)
  - [7.2 Retention policies](#72-retention-policies)
  - [7.3 Audit trail essentials](#73-audit-trail-essentials)
- [8. Summary](#8-summary)


## **5.6 Observability — Logging, Metrics, and Tracing for Agent Systems**

Agentic systems are **multi-step, tool-using, probabilistic** workflows. If you can’t observe them, you can’t:
- debug failures,
- control cost,
- prove compliance,
- or improve reliability.

This chapter defines an observability blueprint for production-grade agents.

---

## 1. What “observability” means for agents

Traditional services mostly need: request logs + latency + error rate.

Agents also need visibility into:
- **model routing decisions** (which LLM, why)
- **planning loops** (how many iterations)
- **tool calls** (inputs/outputs/errors)
- **grounding/RAG** (what was retrieved)
- **policy enforcement** (what was blocked/approved)
- **cost** (tokens, tool usage, retries)

In practice, agent observability spans:
- **application telemetry** (standard)
- **agent telemetry** (agent-specific)
- **audit telemetry** (compliance)

---

## 2. Logging architecture

### 2.1 Principles

- **Structured logs** only (JSON), never “free text”
- **Correlation IDs everywhere** (request_id, trace_id)
- **Redaction by default** (PII, secrets)
- **Separation of concerns**:
  - operational logs (debug/ops)
  - audit logs (immutable, compliance)

### 2.2 Log streams to produce

1. **Request logs**
   - user/session/tenant metadata
   - input size, attachments metadata
   - selected workflow + version

2. **LLM call logs**
   - model name + version
   - prompt template id/version (not necessarily full prompt)
   - token counts (in/out)
   - latency
   - safety flags

3. **Plan / state logs**
   - plan id
   - step index
   - loop count
   - stop reason (success / limit / user clarification)

4. **Tool call logs**
   - tool name + version
   - validated arguments (redacted)
   - tool latency
   - tool result metadata (size, status)
   - error class (timeout, auth, validation)

5. **RAG logs**
   - query (hashed or sanitized)
   - top-k ids/URIs
   - retrieval scores
   - reranker decision (if used)

6. **Policy & guardrail logs**
   - allowed/blocked
   - reason (RBAC fail, scope fail, schema fail, approval required)
   - approval state (pending/approved/denied)

### 2.3 Minimal structured log schema (example)

```json
{
  "ts": "2025-12-13T09:14:22.120Z",
  "level": "INFO",
  "service": "agent-orchestrator",
  "env": "prod",
  "request_id": "req_...",
  "trace_id": "trace_...",
  "tenant_id": "t_...",
  "user_id": "u_...",
  "workflow": "diagnose_incident",
  "workflow_version": "1.3.0",
  "event": "tool_call",
  "tool": {"name": "query_logs", "version": "2.1"},
  "latency_ms": 842,
  "status": "ok",
  "redaction": {"applied": true, "fields": ["arguments.token"]}
}
```

---

## 3. Agent telemetry (what to measure)

### 3.1 Core service metrics (standard)

- request rate (RPS)
- p50/p95/p99 latency
- error rate
- saturation (CPU/memory)

### 3.2 Agent-specific metrics

**Reasoning / control**
- iterations per request (plan/verify/refine loop count)
- tool calls per request
- stop reasons distribution (success / max_steps / needs_user / blocked)

**Tool usage**
- tool success rate by tool
- tool timeouts/retries/backoff
- tool error taxonomy counts

**Model routing**
- model selection distribution
- fallback rate (large → small or vice versa)
- retry rate per model

**RAG quality signals**
- retrieval hit rate
- average top-k score
- reranker acceptance rate
- “no evidence” rate

**Cost**
- tokens in/out per request
- cost per request / per tenant
- cost by workflow

**Safety / policy**
- blocked tool calls count
- approval-required count
- redaction events count

### 3.3 Suggested SLOs (example)

- p95 end-to-end latency < X seconds (per workflow)
- tool failure rate < Y%
- runaway loop rate < Z% (requests hitting max_steps)
- cost/request within budget

---

## 4. Tracing multi-step agent workflows

Agents are not “one request → one handler.” They are a chain of spans.

### 4.1 Use distributed tracing (OpenTelemetry recommended)

Represent the agent run as a single trace:
- root span: `agent.request`
- child spans:
  - `llm.route`
  - `llm.plan`
  - `rag.retrieve`
  - `tool.query_logs`
  - `verify.checks`
  - `llm.finalize`

### 4.2 Trace diagram (conceptual)

```text
agent.request
  ├─ llm.route
  ├─ llm.plan
  ├─ rag.retrieve
  ├─ tool.query_logs
  ├─ tool.query_metrics
  ├─ verify.schema
  ├─ verify.policy
  └─ llm.finalize
```

### 4.3 Trace attributes to attach

- workflow + version
- model ids used
- tool names used
- step_count
- token counts
- safety events (blocked/approved)
- document ids retrieved (not raw content)

---

## 5. Debugging agent behavior

### 5.1 Reproducibility artifacts

To debug reliably, you need “replayable runs”:
- prompt template id + version
- tool versions
- workflow version
- normalized inputs (sanitized)
- captured tool outputs (or references)

### 5.2 Common failure classes

- **planning failure**: wrong tool/sequence
- **tool failure**: auth/timeout/invalid args
- **grounding failure**: poor retrieval or wrong docs
- **policy failure**: blocked actions due to scope/permission
- **format failure**: invalid JSON/schema
- **user ambiguity**: insufficient constraints

Your observability should make these classes obvious.

---

## 6. Evaluation frameworks (offline + online)

### 6.1 Offline evaluation

- golden test sets (queries + expected outcomes)
- tool-mocked runs (deterministic)
- regression tests per workflow
- retrieval evals (precision@k, recall@k)

### 6.2 Online evaluation

- outcome-based KPIs (task success rate)
- human feedback + review queues
- A/B experiments on prompts/models

### 6.3 “LLM-as-judge” (use carefully)

Useful for quick iteration, but should be:
- calibrated against human labels
- restricted to low-stakes judgments

---

## 7. Privacy, retention, and audit

### 7.1 Redaction and minimization

- never log secrets
- avoid logging full prompts/responses in prod unless required
- store sensitive fields encrypted when retention is needed

### 7.2 Retention policies

- operational logs: shorter retention
- audit logs: longer retention, immutable
- memory writes: explicit and reviewable

### 7.3 Audit trail essentials

Audit records should answer:
- who requested the action?
- what did the agent attempt?
- what executed, when, and with which permissions?
- what changed?

---

## 8. Summary

Observability is mandatory for production agents.
A good setup provides:
- **logs** for investigation,
- **metrics** for health + cost control,
- **traces** for end-to-end workflow visibility,
- **eval pipelines** for continuous improvement,
- **audit trails** for trust and compliance.

Next: **06_design_decision_tree.md**

[Previous](05_05_policies_and_guardrails.md) | [Next](06_design_decision_tree.md)
