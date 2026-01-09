[Previous](05_06_observability_logging_metrics_tracing.md) | [Next](07_design_decision_tree.md)

# Core Design Decision Tree  

## Table of Contents

- [**6. Design Decision Tree — Choosing the Right Agent Architecture**](#6-design-decision-tree-choosing-the-right-agent-architecture)
- [1. Start with the problem classification](#1-start-with-the-problem-classification)
- [2. Single LLM vs Multi-LLM](#2-single-llm-vs-multi-llm)
  - [Decision prompts](#decision-prompts)
  - [Practical routing template](#practical-routing-template)
  - [Quick decision flow](#quick-decision-flow)
- [3. RAG vs Long Context](#3-rag-vs-long-context)
  - [Use RAG when](#use-rag-when)
  - [Use Long Context when](#use-long-context-when)
  - [Use a Hybrid (recommended) when](#use-a-hybrid-recommended-when)
  - [Decision flow](#decision-flow)
- [4. When to allow autonomous tool actions](#4-when-to-allow-autonomous-tool-actions)
  - [Allowed autonomy (good candidates)](#allowed-autonomy-good-candidates)
  - [Restricted autonomy](#restricted-autonomy)
  - [Safety gates](#safety-gates)
  - [Decision flow](#decision-flow)
- [5. Choosing Tools vs Internal Code](#5-choosing-tools-vs-internal-code)
  - [Use tools when](#use-tools-when)
  - [Use internal code when](#use-internal-code-when)
  - [Decision flow](#decision-flow)
- [6. Memory: long-term vs ephemeral](#6-memory-long-term-vs-ephemeral)
  - [Ephemeral memory (session-only)](#ephemeral-memory-session-only)
  - [Long-term memory](#long-term-memory)
  - [Safe memory write policy](#safe-memory-write-policy)
  - [Decision flow](#decision-flow)
- [7. Selecting appropriate safety levels](#7-selecting-appropriate-safety-levels)
  - [Tier 0: Informational](#tier-0-informational)
  - [Tier 1: Read-only operational](#tier-1-read-only-operational)
  - [Tier 2: Limited write](#tier-2-limited-write)
  - [Tier 3: High-stakes / regulated](#tier-3-high-stakes-regulated)
- [8. Latency vs Cost vs Accuracy tradeoffs](#8-latency-vs-cost-vs-accuracy-tradeoffs)
  - [How to reduce latency](#how-to-reduce-latency)
  - [How to reduce cost](#how-to-reduce-cost)
  - [How to improve accuracy](#how-to-improve-accuracy)
  - [Decision matrix](#decision-matrix)
- [9. A complete top-down decision tree (condensed)](#9-a-complete-top-down-decision-tree-condensed)
- [10. Summary](#10-summary)


## **6. Design Decision Tree — Choosing the Right Agent Architecture**

Agent systems have many possible configurations (models, tools, memory, safety). This chapter provides a practical decision tree for selecting components based on **risk, complexity, latency, cost, and reliability requirements**.

---

## 1. Start with the problem classification

Before choosing architecture, classify the workload:

- **A. Informational** (Q&A, summaries, explanations)
- **B. Decision support** (recommendations, triage, prioritization)
- **C. Operational** (tool actions: create/update/deploy)
- **D. High-stakes / regulated** (finance, HR, security, compliance)

**Rule:** As you move from A → D, you need more: guardrails, verification, observability, and approvals.

---

## 2. Single LLM vs Multi-LLM

### Decision prompts

Choose **single LLM** when:
- low traffic / prototype
- narrow domain
- minimal tool usage
- cost is not yet optimized
- failures are low impact

Choose **multi-LLM** when:
- you need predictable cost control
- you have a mix of “easy” and “hard” requests
- tool execution is frequent
- correctness and reliability matter
- you want a verifier/critic step

### Practical routing template

- **Router (small model):** intent + complexity classification
- **Planner (strong model):** plan generation and decomposition
- **Executor (mid model):** tool argument formation + tool output interpretation
- **Verifier/Critic (strong model or rules):** correctness and policy checks
- **Finalizer (small/mid model):** user-friendly response

### Quick decision flow

```text
Is this a prototype or low-volume internal tool?
  ├─ Yes → Single LLM
  └─ No  → Do you have multiple request difficulty levels?
           ├─ Yes → Multi-LLM with router
           └─ No  → Single LLM, add verifier later
```

---

## 3. RAG vs Long Context

### Use RAG when
- you have a large knowledge base (docs, policies, manuals)
- content changes frequently
- grounding/citations matter
- you need low token cost at scale
- you need to keep sensitive docs out of prompts (retrieve minimal excerpts)

### Use Long Context when
- task input is large but temporary (one big document)
- sequential reasoning over the whole text is required
- retrieval would miss context relationships

### Use a Hybrid (recommended) when
- you need workflow state + document grounding

**Hybrid pattern:**
- long context for **current task state**
- RAG for **reference knowledge**

### Decision flow

```text
Is the knowledge base large and persistent?
  ├─ Yes → RAG
  └─ No  → Is the current input very large and must be reasoned over end-to-end?
           ├─ Yes → Long context
           └─ No  → RAG or no retrieval (keep it simple)
```

---

## 4. When to allow autonomous tool actions

Autonomy is the largest risk multiplier.

### Allowed autonomy (good candidates)
- read-only inventory queries
- diagnostics (logs/metrics retrieval)
- non-destructive automation (create draft ticket, generate report)

### Restricted autonomy
- updates that affect customers
- role/permission changes
- money movement
- production deployments
- deletion / bulk operations

### Safety gates

- **Read-only mode** by default
- **Confirmation** for write actions
- **Two-step execution** for destructive actions:
  1) propose action plan
  2) require user approval + policy check

### Decision flow

```text
Does the action change external state?
  ├─ No → Allow autonomous execution (with limits)
  └─ Yes → Is it reversible + low impact?
           ├─ Yes → Allow with confirmation gate
           └─ No  → Require approval workflow / human-in-the-loop
```

---

## 5. Choosing Tools vs Internal Code

### Use tools when
- the system-of-record exists elsewhere (APIs/DB)
- you need authoritative data
- actions must be auditable
- results must be deterministic

### Use internal code when
- pure computation or formatting
- deterministic logic that doesn’t need external calls
- sensitive transformations you don’t want to send to the model

**Rule:** Tools should be the boundary for external state. Internal code should be the boundary for deterministic transformation.

### Decision flow

```text
Do you need authoritative external data or side effects?
  ├─ Yes → Tool
  └─ No  → Internal code
```

---

## 6. Memory: long-term vs ephemeral

### Ephemeral memory (session-only)
Use when:
- the task is one-off
- user preferences are not needed
- privacy risk is high
- you want minimal data retention

### Long-term memory
Use when:
- personalization improves outcomes
- users repeat similar workflows
- historical context is required (past incidents/tickets)

### Safe memory write policy
Only persist memory entries that are:
- explicitly useful in the future
- validated (not hallucinated)
- minimal (no raw secrets / excessive PII)

### Decision flow

```text
Will this information be useful across sessions?
  ├─ No → Ephemeral memory only
  └─ Yes → Does it contain sensitive data?
           ├─ Yes → Store minimal structured summary (with controls)
           └─ No  → Store in long-term memory (versioned)
```

---

## 7. Selecting appropriate safety levels

Define safety tiers based on risk and blast radius.

### Tier 0: Informational
- no tools
- no memory writes
- minimal logging

### Tier 1: Read-only operational
- read-only tools
- strict schemas
- rate limits
- audit logs

### Tier 2: Limited write
- write tools allowed
- explicit user confirmation
- approvals for sensitive actions
- stronger monitoring

### Tier 3: High-stakes / regulated
- policy engine + ABAC
- immutable audit trails
- multi-stage approvals
- verifier model + deterministic checks
- strong redaction + retention controls

**Rule:** Default to the lowest tier that meets business needs.

---

## 8. Latency vs Cost vs Accuracy tradeoffs

These three form a triangle: improving one often hurts another.

### How to reduce latency
- route simple queries to smaller models
- reduce tool calls / batch retrieval
- cache results
- stream responses

### How to reduce cost
- multi-LLM routing
- aggressive summarization
- RAG instead of large context
- tool-result caching

### How to improve accuracy
- retrieval grounding
- verifier/critic step
- deterministic validations
- domain tools instead of “guessing”

### Decision matrix

| Priority | Recommended pattern |
|---|---|
| Lowest latency | Router + small model, minimal tools, caching |
| Lowest cost | Router + cheap models, RAG, aggressive summarization |
| Highest accuracy | Planner + verifier, RAG + reranking, deterministic checks |
| High safety | Approval gates, strict ABAC/RBAC, audit logging |

---

## 9. A complete top-down decision tree (condensed)

```text
1) Is the task high-stakes or state-changing?
   ├─ No → (Info/Decision Support)
   │       ├─ Need large knowledge base? → RAG
   │       └─ Simple? → Single LLM or small router
   └─ Yes → (Operational)
           ├─ Read-only? → Autonomous with limits
           └─ Write?
               ├─ Low impact + reversible → Confirmation gate
               └─ High impact → Approval workflow + verifier + strict policy

2) Is workload mixed difficulty at scale?
   ├─ Yes → Multi-LLM routing
   └─ No  → Single LLM (add verifier if needed)

3) Is personalization needed across sessions?
   ├─ Yes → Long-term memory (sanitized)
   └─ No  → Ephemeral memory only
```

---

## 10. Summary

Use this decision tree to choose:
- single vs multi-LLM
- RAG vs long context
- tool autonomy levels
- tools vs internal code
- long-term vs ephemeral memory
- safety tiers
- latency/cost/accuracy strategy

Next: **08_scalability_and_performance.md**

[Previous](05_06_observability_logging_metrics_tracing.md) | [Next](07_design_decision_tree.md)
