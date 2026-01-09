[Previous](07_design_decision_tree.md) | [Next](09_00_current_trends_and_patterns.md)

# Scalability and Performance  

## Table of Contents

- [**8. Scalability & Performance — Making Agents Fast, Stable, and Affordable**](#8-scalability-performance-making-agents-fast-stable-and-affordable)
- [1. Scaling goals and constraints](#1-scaling-goals-and-constraints)
- [2. Horizontal vs vertical scaling](#2-horizontal-vs-vertical-scaling)
  - [2.1 Horizontal scaling (recommended)](#21-horizontal-scaling-recommended)
  - [2.2 Vertical scaling](#22-vertical-scaling)
- [3. Model routing strategies](#3-model-routing-strategies)
  - [3.1 Router-first pattern](#31-router-first-pattern)
  - [3.2 Tiered reasoning modes](#32-tiered-reasoning-modes)
  - [3.3 Dynamic fallback](#33-dynamic-fallback)
  - [3.4 Avoid “always-large-model”](#34-avoid-always-large-model)
- [4. Caching (requests, embeddings, RAG)](#4-caching-requests-embeddings-rag)
  - [4.1 Response caching](#41-response-caching)
  - [4.2 Tool-result caching](#42-tool-result-caching)
  - [4.3 Embedding caching](#43-embedding-caching)
  - [4.4 Retrieval caching](#44-retrieval-caching)
  - [4.5 Prompt-template caching](#45-prompt-template-caching)
- [5. Async workflow design](#5-async-workflow-design)
  - [5.1 Synchronous (interactive)](#51-synchronous-interactive)
  - [5.2 Asynchronous (background jobs)](#52-asynchronous-background-jobs)
  - [5.3 Durable execution](#53-durable-execution)
- [6. Controlling cost explosion](#6-controlling-cost-explosion)
  - [6.1 Budget controls (hard limits)](#61-budget-controls-hard-limits)
  - [6.2 Context compression](#62-context-compression)
  - [6.3 Retrieval discipline](#63-retrieval-discipline)
  - [6.4 “Stop and ask”](#64-stop-and-ask)
- [7. Handling concurrent sessions](#7-handling-concurrent-sessions)
  - [7.1 Session state storage](#71-session-state-storage)
  - [7.2 Concurrency controls](#72-concurrency-controls)
  - [7.3 Work isolation](#73-work-isolation)
- [8. Rate limits, retries, and backoff](#8-rate-limits-retries-and-backoff)
  - [8.1 Rate limits](#81-rate-limits)
  - [8.2 Retries](#82-retries)
  - [8.3 Backoff + jitter](#83-backoff-jitter)
  - [8.4 Idempotency](#84-idempotency)
- [9. Performance tuning checklist](#9-performance-tuning-checklist)
  - [Latency](#latency)
  - [Throughput](#throughput)
  - [Reliability](#reliability)
  - [Cost](#cost)
- [10. Reference architecture (runtime)](#10-reference-architecture-runtime)
- [11. Summary](#11-summary)


## **8. Scalability & Performance — Making Agents Fast, Stable, and Affordable**

Agentic systems are more expensive and failure-prone than typical APIs because they:
- make multiple LLM calls,
- call external tools,
- perform retrieval,
- loop (Plan → Verify → Refine),
- and maintain session state.

This chapter covers the core engineering patterns to scale agents without cost explosions.

---

## 1. Scaling goals and constraints

Define your non-negotiables upfront:
- **Latency SLOs** (p95/p99)
- **Cost per request** (tokens + tools)
- **Throughput** (RPS, concurrent sessions)
- **Reliability** (tool failure tolerance)
- **Safety** (guardrails can’t be bypassed under load)

Agents must be designed with *budgets*.

---

## 2. Horizontal vs vertical scaling

### 2.1 Horizontal scaling (recommended)
Scale out stateless workers.

- Multiple orchestrator instances behind a load balancer
- Shared external state store (Redis/DB)
- Shared tool gateways

Pros:
- elastic throughput
- fault isolation
- easy blue/green

Cons:
- requires careful state design

### 2.2 Vertical scaling
Bigger machines (CPU/RAM/GPU).

Pros:
- simpler for early stages

Cons:
- harder to scale
- single-node bottlenecks

**Rule:** keep compute stateless and scale horizontally; keep state in external stores.

---

## 3. Model routing strategies

Routing is the single most powerful cost + latency lever.

### 3.1 Router-first pattern
A small/cheap model classifies:
- intent
- complexity
- safety tier
- tool need

Then routes to:
- small model for simple answers
- planner model for workflows
- verifier model for high-stakes

### 3.2 Tiered reasoning modes
- **fast mode** for most requests
- **deep mode** only for complex/higher-stakes tasks

### 3.3 Dynamic fallback
If the small model fails schema/verification:
- retry once
- escalate to a stronger model

### 3.4 Avoid “always-large-model”
It is simple, but cost scales linearly with volume.

---

## 4. Caching (requests, embeddings, RAG)

Caching can cut cost by 30–80% in many systems.

### 4.1 Response caching
Cache final responses for:
- identical questions
- stable knowledge queries

Keying options:
- normalized prompt hash
- (intent, user role, tenant, version)

Be careful:
- user-specific data must not leak
- cache must include scope + permissions

### 4.2 Tool-result caching
Cache read-only tool calls:
- inventory lists
- lookup endpoints
- static configs

Use TTLs and include:
- tenant/project scope
- tool version

### 4.3 Embedding caching
For RAG:
- cache embeddings for repeated queries
- cache document embeddings at ingestion

### 4.4 Retrieval caching
Cache top-k retrieval results by query hash.

### 4.5 Prompt-template caching
Reuse prompt templates and compiled schemas; version them.

---

## 5. Async workflow design

Not all agent tasks should run synchronously.

### 5.1 Synchronous (interactive)
Use when:
- user expects immediate response
- quick tool calls
- bounded steps

### 5.2 Asynchronous (background jobs)
Use when:
- long tool operations
- multi-minute data gathering
- report generation
- batch workflows

Pattern:
- submit job → return job id
- stream updates or poll
- store progress in state store

### 5.3 Durable execution
For long workflows, prefer:
- queues (SQS/RabbitMQ/Kafka)
- workflow engines (Temporal, Step Functions)
- idempotent tool calls

---

## 6. Controlling cost explosion

Cost blow-ups happen due to:
- too many LLM calls per request
- large prompts (context bloat)
- runaway loops
- excessive retrieval
- repeated tool retries

### 6.1 Budget controls (hard limits)
Enforce per request/session:
- max steps
- max tool calls
- max retries per tool
- max tokens
- max wall-clock time
- max $ cost

### 6.2 Context compression
- rolling summaries
- state snapshots
- store large tool outputs externally; pass references

### 6.3 Retrieval discipline
- limit top-k
- rerank
- filter by metadata (tenant, doc type, recency)

### 6.4 “Stop and ask”
If ambiguity is high, ask the user early.
Clarification is cheaper than deep reasoning.

---

## 7. Handling concurrent sessions

### 7.1 Session state storage
Store state externally:
- Redis (fast)
- DB (durable)

State should include:
- conversation summary
- plan state
- tool outputs (or references)
- budgets consumed

### 7.2 Concurrency controls
- per-user concurrency limits
- per-tenant concurrency limits
- per-tool concurrency limits

### 7.3 Work isolation
- separate queues per tenant or workload
- prioritize interactive workloads over batch

---

## 8. Rate limits, retries, and backoff

### 8.1 Rate limits
Apply at:
- API gateway (per user/tenant)
- tool gateway (per tool)
- model gateway (per model)

### 8.2 Retries
Retry only when it’s safe:
- network timeouts
- 5xx errors

Do not blindly retry:
- validation errors
- permission errors

### 8.3 Backoff + jitter
Use exponential backoff with jitter to avoid thundering herds.

### 8.4 Idempotency
For write tools:
- idempotency keys
- safe replays
- “dry-run then commit” patterns

---

## 9. Performance tuning checklist

### Latency
- route simple tasks to smaller models
- reduce tool calls
- cache frequent reads
- parallelize independent tool calls (fan-out)
- stream partial responses

### Throughput
- horizontal scale orchestrators
- queues for long tasks
- isolate hot tools

### Reliability
- circuit breakers for flaky tools
- fallback tools or degraded modes
- strict budgets

### Cost
- limit deep mode
- compress context
- cap RAG top-k
- enforce per-tenant quotas

---

## 10. Reference architecture (runtime)

```text
Client
  → API Gateway (auth + rate limits)
    → Orchestrator Pool (stateless)
      → Model Gateway (routing + quotas)
      → Tool Gateway (allow-list + retries)
      → RAG Service (retrieval + caching)
      → State Store (session + workflow state)
      → Queue/Workflow Engine (async jobs)
```

---

## 11. Summary

Scaling agents is about controlling:
- **how many calls happen** (routing + budgets)
- **how much context is sent** (summaries + references)
- **how many tool operations run** (caching + async)
- **how failures behave** (retries, backoff, circuit breakers)

[Previous](07_design_decision_tree.md) | [Next](09_00_current_trends_and_patterns.md)
