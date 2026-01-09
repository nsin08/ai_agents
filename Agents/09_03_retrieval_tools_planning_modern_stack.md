[Previous](09_02_tool_use_computer_control_autonomous_workflows.md) | [Next](09_04_case_study_customer_support_agent.md)

# Retrieval Tools, Planning, and the Modern Stack  

## Table of Contents

- [**9.3 Retrieval + Tools + Planning — The Modern Agent Stack**](#93-retrieval-tools-planning-the-modern-agent-stack)
- [1. Why this stack emerged](#1-why-this-stack-emerged)
- [2. The core idea: evidence-first reasoning](#2-the-core-idea-evidence-first-reasoning)
- [3. Retrieval is no longer “just vector search”](#3-retrieval-is-no-longer-just-vector-search)
  - [3.1 Vector retrieval (semantic)](#31-vector-retrieval-semantic)
  - [3.2 Metadata filtering (precision)](#32-metadata-filtering-precision)
  - [3.3 Reranking (quality)](#33-reranking-quality)
  - [3.4 Structured retrieval (SQL/Graph)](#34-structured-retrieval-sqlgraph)
  - [3.5 Tool-based retrieval](#35-tool-based-retrieval)
- [4. Planning ties retrieval and tools together](#4-planning-ties-retrieval-and-tools-together)
  - [4.1 Plan types](#41-plan-types)
  - [4.2 Plan constraints (must-have)](#42-plan-constraints-must-have)
  - [4.3 Evidence requirements](#43-evidence-requirements)
- [5. The modern runtime architecture](#5-the-modern-runtime-architecture)
- [6. Patterns that are becoming standard](#6-patterns-that-are-becoming-standard)
  - [6.1 Retrieval-then-tools (knowledge → state)](#61-retrieval-then-tools-knowledge-state)
  - [6.2 Tools-then-retrieval (state → explanation)](#62-tools-then-retrieval-state-explanation)
  - [6.3 Parallel evidence gathering](#63-parallel-evidence-gathering)
  - [6.4 “Retrieval as a tool”](#64-retrieval-as-a-tool)
  - [6.5 Verification as a gate, not a suggestion](#65-verification-as-a-gate-not-a-suggestion)
- [7. Guardrails specific to the modern stack](#7-guardrails-specific-to-the-modern-stack)
  - [7.1 Prevent retrieval leakage](#71-prevent-retrieval-leakage)
  - [7.2 Prevent tool misuse](#72-prevent-tool-misuse)
  - [7.3 Control context bloat](#73-control-context-bloat)
- [8. Evaluation: what to test in this architecture](#8-evaluation-what-to-test-in-this-architecture)
  - [8.1 Retrieval quality](#81-retrieval-quality)
  - [8.2 Tool correctness](#82-tool-correctness)
  - [8.3 Planning reliability](#83-planning-reliability)
  - [8.4 End-to-end outcomes](#84-end-to-end-outcomes)
- [9. Common anti-patterns](#9-common-anti-patterns)
- [10. Summary](#10-summary)


## **9.3 Retrieval + Tools + Planning — The Modern Agent Stack**

The most successful agent architectures today converge on a single pattern:

> **Planning decides what evidence/actions are needed → retrieval and tools gather ground truth → the agent verifies and refines → final output is grounded and auditable.**

This chapter describes the “modern stack” that combines:
- **Retrieval** (RAG + metadata + reranking)
- **Tools** (APIs/DB/logs/metrics/actions)
- **Planning** (structured decomposition + bounded loops)

---

## 1. Why this stack emerged

Pure LLMs fail in production for predictable reasons:
- they don’t have authoritative data
- they hallucinate under ambiguity
- they can’t complete workflows
- they can’t prove correctness

The modern stack fixes this by making the LLM a **controller of evidence gathering**, not the source of truth.

---

## 2. The core idea: evidence-first reasoning

A reliable agent should be able to answer:
- **What evidence did you use?**
- **Which tools did you call?**
- **What constraints were enforced?**
- **Why did you choose this action?**

This leads to an evidence-first pipeline:

1) **Plan** what must be known/done
2) **Retrieve** relevant docs/data
3) **Call tools** for authoritative state
4) **Verify** against constraints and invariants
5) **Refine** if evidence is missing/contradictory
6) **Finalize** with citations/references to evidence

---

## 3. Retrieval is no longer “just vector search”

Modern retrieval usually blends multiple sources:

### 3.1 Vector retrieval (semantic)
- good for unstructured knowledge (docs, runbooks)

### 3.2 Metadata filtering (precision)
- tenant/project
- doc type
- environment
- recency

### 3.3 Reranking (quality)
- cross-encoder rerankers improve relevance
- reduces “top-k noise”

### 3.4 Structured retrieval (SQL/Graph)
- best for factual queries and relationships
- avoids “semantic guessing” when the data is structured

### 3.5 Tool-based retrieval
In ops/enterprise domains, the best retrieval is often a tool:
- query logs
- query metrics
- list resources
- fetch configs

**Trend:** retrieval is increasingly treated as a **tool** within the plan.

---

## 4. Planning ties retrieval and tools together

A modern agent plan is not “steps in English.” It is a **bounded program**.

### 4.1 Plan types

- **Information plan**: retrieve evidence → summarize
- **Diagnostic plan**: gather signals (logs/metrics/config) → correlate → conclude
- **Operational plan**: prepare change → approval gate → execute → verify

### 4.2 Plan constraints (must-have)
- mode: read-only / limited write
- max steps / max tool calls
- allowed tools list
- environment scope
- approval requirements

### 4.3 Evidence requirements
A production-friendly plan also specifies:
- what evidence is needed to accept a conclusion
- what to do if evidence is missing

Example (conceptual):

```json
{
  "goal": "Explain spike in 5xx errors",
  "constraints": {"mode": "read_only", "max_steps": 8},
  "evidence_requirements": [
    "At least one error signature from logs",
    "Metric correlation for 5xx_rate",
    "Recent deploy/change event if available"
  ],
  "steps": [
    {"id": 1, "tool": "query_metrics", "args": {"metric": "5xx_rate", "window": "60m"}},
    {"id": 2, "tool": "query_logs", "args": {"service": "X", "window": "60m", "filter": "status>=500"}},
    {"id": 3, "tool": "get_recent_deploys", "args": {"service": "X", "window": "24h"}},
    {"id": 4, "action": "verify", "checks": ["schema", "policy", "evidence"]},
    {"id": 5, "action": "respond"}
  ]
}
```

---

## 5. The modern runtime architecture

A common production layout:

```text
Client
  → API Gateway (auth + quotas)
    → Orchestrator (state machine)
      → Model Router (choose model/mode)
      → RAG Service (retrieve + rerank + filter)
      → Tool Gateway (allow-list + validation)
      → Verifier (rules + invariants + optional critic)
      → Memory (session + selective long-term)
      → Observability (logs/metrics/traces)
```

Key property: **the tool gateway and verifier are central enforcement points**.

---

## 6. Patterns that are becoming standard

### 6.1 Retrieval-then-tools (knowledge → state)
Use RAG to find the right procedure, then tools to confirm the state.

Example:
- retrieve runbook → call tools → validate → respond

### 6.2 Tools-then-retrieval (state → explanation)
Use tools to identify error signatures, then retrieve docs explaining those signatures.

Example:
- query logs → extract error code → retrieve docs/runbook sections

### 6.3 Parallel evidence gathering
For latency:
- run independent tool calls in parallel
- retrieve docs while tools run

### 6.4 “Retrieval as a tool”
Make retrieval an explicit callable tool with:
- query schema
- filters
- top-k limits
- evidence ids returned

This improves traceability and makes retrieval policies enforceable.

### 6.5 Verification as a gate, not a suggestion
Verification should be deterministic whenever possible:
- schema validation
- permission checks
- invariants
- evidence coverage rules

---

## 7. Guardrails specific to the modern stack

### 7.1 Prevent retrieval leakage
- filter by tenant/project scope
- redact sensitive doc segments
- limit what enters prompts

### 7.2 Prevent tool misuse
- allow-list tools per workflow
- separate read vs write tools
- approval gates for high-impact actions

### 7.3 Control context bloat
- summarize tool outputs
- store large results externally and pass references
- cap top-k retrieval

---

## 8. Evaluation: what to test in this architecture

### 8.1 Retrieval quality
- precision@k / recall@k
- reranker effectiveness
- “no evidence” behavior

### 8.2 Tool correctness
- schema compliance
- error taxonomy handling
- idempotency for writes

### 8.3 Planning reliability
- plan validity rate
- step count distribution
- stop reasons distribution

### 8.4 End-to-end outcomes
- task success rate
- escalation rate
- cost per successful task
- time-to-completion

**Trend:** teams are moving from “prompt eval” to **workflow eval**.

---

## 9. Common anti-patterns

- **Vector-only thinking**: using RAG for everything (even structured facts)
- **No verifier**: trusting the model output without gates
- **Unlimited loops**: cost runaway
- **Unscoped retrieval**: cross-tenant leakage risk
- **Tool sprawl without registry**: inconsistent schemas, brittle behavior

---

## 10. Summary

The modern agent stack is not a single innovation; it’s a convergence:
- **Planning** to decide what’s needed
- **Retrieval** to ground knowledge
- **Tools** to fetch and change real state
- **Verification** to make behavior safe and reliable

This is the architecture pattern most likely to dominate enterprise agents because it is:
- scalable
- auditable
- cost-controllable
- and aligned with real-world workflows.

Next: **10_conclusion_future_directions.md**

[Previous](09_02_tool_use_computer_control_autonomous_workflows.md) | [Next](09_04_case_study_customer_support_agent.md)
