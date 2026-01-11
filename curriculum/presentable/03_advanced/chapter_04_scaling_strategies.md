# Chapter 04: Scaling Strategies (Load, Caching, Async Patterns)

**Level:** 3 (Advanced)  
**Target audience:** Senior engineers, staff+ engineers, architects  
**Prerequisites:** You understand the agent lifecycle (prompt -> tool calls -> response) and basic observability.  
**Primary internal references:** `Agents/08_scalability_and_performance.md`, `labs/06/README.md` (Observability)

## Learning Objectives (3-5)

By the end of this chapter, you will be able to:

1. Identify the dominant scaling bottlenecks in agent systems (LLM latency, tool latency, retrieval, context size, and retries).
2. Apply caching, batching, and routing strategies to reduce cost and latency while preserving safety.
3. Implement async execution patterns with backpressure and concurrency limits (and know where async makes things worse).
4. Design a scaling plan for multi-tenant systems (isolation, quotas, fairness).
5. Use decision trees and trade-off matrices to pick scaling techniques with clear operational consequences.

## Chapter Outline

1. What "scale" means for agents
2. Bottleneck map: LLM, tools, retrieval, memory, and retries
3. Caching strategies (and cache safety)
4. Async patterns and backpressure
5. Load balancing and routing (models, tools, tenants)
6. Decision trees and trade-off matrices
7. Case studies (production scenarios)
8. One-page takeaway

---

## 1) What "Scale" Means for Agents

Scaling an agent system is not only about QPS. It is about:

- **Latency** (p50/p95) under load
- **Cost per success** (not cost per request)
- **Reliability under partial failure** (tool timeouts, degraded dependencies)
- **Policy compliance under load** (guardrails still enforced)
- **Fairness** across tenants and user segments

Agents have unique scaling behaviors:

- retries can amplify load (a small incident becomes a storm)
- context growth increases token usage and latency
- long tool chains produce tail latency

Before adding replicas, measure where time and tokens go.

### Scaling must preserve safety (do not optimize away guardrails)

Under load, teams are tempted to "turn off guardrails" to reduce latency and cost. This is almost always the wrong move. Production systems fail when they sacrifice:

- approvals for writes ("we will add approvals later")
- redaction ("logs are internal, it's fine")
- schema validation ("it slows down tool calls")

Better scaling approach:

- keep safety controls deterministic and efficient
- reduce the number of expensive steps (fewer tool calls, smaller context)
- add degraded modes that are safe (read-only summaries instead of writes)

If safety controls are too expensive to run at scale, treat that as a design bug: the system architecture is not ready for production traffic.

One practical technique is to separate "safety enforcement" from "expensive reasoning": keep guardrails and validation deterministic and always-on, and scale by reducing expensive steps (fewer LLM calls, fewer tool calls, smaller prompts). This preserves safety even when the system is under stress.

---

## 2) Bottleneck Map: Where Your Time and Money Go

Most agent latency comes from:

1. LLM call time (especially for long prompts)
2. Tool call time (external APIs, DB queries)
3. Retrieval time (vector search, reranking)
4. Orchestration overhead (planning loops, retries)
5. Serialization and logging overhead (traces, audit logs)

### A practical scaling workflow

1. Instrument end-to-end latency and cost by step.
2. Identify the top 1-2 contributors (often: LLM + one slow tool).
3. Apply the smallest scaling lever that reduces the bottleneck without breaking safety.
4. Re-measure after each change.

Do not optimize blind. Agents are expensive; instrumentation pays for itself quickly.

### Bottleneck scorecard (practical metrics)

Before you change architecture, capture a simple scorecard per workflow:

- average prompt tokens and completion tokens
- number of tool calls per request (p50/p95)
- retries per tool call (and why)
- retrieval top_k and average chunk size
- p95 latency by step (LLM, retrieval, top 2 tools)
- cost per success (not cost per request)

This scorecard gives you a baseline. Without it, you will optimize the wrong thing.

### Token scaling and context growth (the silent cost driver)

Token usage scales with:

- longer user conversations
- more retrieval chunks
- more tool output appended to context
- verbose tracing injected into prompts

Common production anti-pattern:

- The agent logs everything and then feeds those logs back into the next turn.

Fixes that scale:

1. **Summarize tool outputs** before adding to context (store full output separately with a reference).
2. **Cap retrieval** (top_k and max tokens per chunk) and use reranking instead of "more chunks".
3. **Use structured context blocks** (templates) so prompts do not grow unbounded.
4. **Checkpoint context**: keep a short "working context" and a separate long trace for debugging.

When in doubt, treat tokens like memory in a distributed system: you must budget, measure, and manage growth.

### Context compression patterns (keep signal, drop noise)

Context compression is the practice of keeping the minimum information needed to continue the workflow safely.

Common patterns:

1. **Summarize then reference**
   - store full tool output in a restricted store
   - inject a short summary into the prompt
   - include a reference ID for traceability
2. **Extract structured fields**
   - parse tool output into a schema (facts)
   - only include the schema fields the next step requires
3. **Prioritize recent and relevant**
   - keep the last N turns of conversation
   - keep only the top K retrieved chunks
   - drop low-signal tool logs

Conceptual "summarize then reference" pattern:

```python
def compress_tool_output(tool_name: str, raw: str) -> dict:
    # In production: redact sensitive data first.
    summary = raw[:500]  # replace with real summarizer
    ref_id = f"{tool_name}-output-123"
    store_full_output(ref_id, raw)  # restricted store
    return {"ref_id": ref_id, "summary": summary}
```

The key is the interface: the agent consumes summaries, operators can retrieve full outputs using references when debugging.

Compression trade-offs:

- too aggressive -> the agent loses critical details and makes mistakes
- too weak -> prompts grow unbounded and cost spikes

This is why you need measurement: track prompt size, response quality, and error rates before and after compression changes.

---

## 3) Caching Strategies (and Cache Safety)

Caching is the highest leverage scaling technique, but it is easy to do unsafely.

### What you can cache safely

- **Retrieval results** for identical queries (with tenant scoping)
- **Tool results** for idempotent read-only tools
- **Summaries** of long documents (with provenance)
- **Embedding vectors** (avoid recompute)

### What is risky to cache

- write tool results (unless idempotency and correct invalidation exist)
- anything containing secrets or PII (unless you encrypt and strictly scope access)
- anything that is time-sensitive (pricing, inventory, incident state)

### Cache keys must include context

Common bug: caching only by "query text". In multi-tenant systems, cache keys must include:

- tenant_id
- user role / permission scope
- tool configuration version
- data version (if available)

If you cannot form a safe cache key, do not cache.

### Cache invalidation strategies

- TTL-based (simplest)
- event-driven (harder, more accurate)
- versioned data keys (best if you can attach data versions)

Production rule: prefer correctness over caching. A wrong cached answer can be worse than a slow answer.

### TTL cache implementation (conceptual, in-memory)

In production you might use Redis or a dedicated cache, but the logic is the same:

```python
import time
from dataclasses import dataclass


@dataclass
class CacheEntry:
    value: object
    expires_at: float


class TTLCache:
    def __init__(self):
        self._data: dict[str, CacheEntry] = {}

    def get(self, key: str):
        entry = self._data.get(key)
        if not entry:
            return None
        if time.time() > entry.expires_at:
            self._data.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: object, ttl_sec: int):
        self._data[key] = CacheEntry(value=value, expires_at=time.time() + ttl_sec)
```

The hard part is not the TTL. The hard part is safe keys and invalidation.

### Cache poisoning and correctness drift

Caching can introduce new failure modes:

- **poisoning:** attacker causes the system to cache a harmful response
- **drift:** cached summaries become stale and mislead future answers
- **scope bugs:** tenant A sees tenant B's cached results

Mitigations:

- include tenant_id and auth scope in cache keys
- only cache tool outputs that are safe to reuse (read-only, idempotent)
- attach provenance to cached artifacts (what tool, what data version, when)
- invalidate caches on data updates where possible

### Cache layers (L1/L2) and practical invalidation

Most production systems end up with multiple cache layers:

- **L1 (in-process):** fastest, per-pod, resets on deploy
- **L2 (shared cache):** Redis/memcache, shared across pods

L1 is great for:

- hot read-only tool calls
- repeated retrieval queries in bursts

L2 is great for:

- multi-replica reuse
- smoothing spikes across pods

Invalidation approaches:

- TTL only: simplest and often enough for FAQ-like content
- explicit version keys: include `data_version` in the key (best when available)
- event-driven invalidation: invalidate keys on document updates (most complex)

Rule of thumb:

- start with TTL
- add version keys when you can
- use event-driven invalidation only when the business requires strong freshness

For agents, correctness and safety matter more than raw cache hit rate. A stale answer with false confidence is worse than a slower answer with correct caveats.

---

## 4) Async Patterns and Backpressure

Async can reduce wall-clock latency by overlapping I/O, but it can also increase failure rates if you overload dependencies.

### Pattern A: Concurrency limits with semaphores

If you execute multiple tool calls concurrently, enforce a concurrency cap:

```python
import asyncio


class ToolExecutor:
    def __init__(self, max_concurrency: int = 5):
        self._sem = asyncio.Semaphore(max_concurrency)

    async def run_tool(self, tool_fn, *args, **kwargs):
        async with self._sem:
            return await tool_fn(*args, **kwargs)
```

This prevents the "fan-out collapse" where one request triggers 50 concurrent calls and melts your dependencies.

### Pattern A2: Bulkheads (per-tool and per-tenant limits)

A single semaphore for all work is better than nothing, but real systems need bulkheads:

- limit concurrency per tool (slow tool cannot starve everything)
- limit concurrency per tenant (noisy neighbor control)

Conceptual bulkhead map:

```python
class Bulkheads:
    def __init__(self):
        self.by_tool = {"logs_read": asyncio.Semaphore(2), "kb_search": asyncio.Semaphore(10)}
        self.by_tenant = {}

    def tenant_sem(self, tenant_id: str):
        return self.by_tenant.setdefault(tenant_id, asyncio.Semaphore(5))
```

Bulkheads turn a global outage into a contained outage.

### Pattern B: Timeouts per step

Timeouts should exist at multiple levels:

- overall request timeout (SLO budget)
- per-tool timeout (protects the chain)
- per-LLM timeout (provider-level)

Timeouts are not only to stop waiting. They are signals:

- tool degraded: switch to fallback mode
- provider degraded: route to alternate model

Implementation hint: use cancellation correctly. In async systems, timeouts should cancel in-flight work to avoid resource leaks.

### Pattern C: Queue-based execution for heavy workflows

If your workflow is long-running (minutes) or expensive, consider:

- queue the job
- return a job_id to the user
- stream partial status updates

This turns tail latency into an explicit product experience and protects your API from timeouts.

### Pattern D: Partial results and progressive responses

In interactive systems, a safe scaling technique is returning partial progress:

- return the parts that are already verified
- clearly label missing parts ("dependency unavailable")
- avoid fabricating missing evidence

This improves user experience and reduces "retry spam" during incidents.

---

## 5) Load Balancing and Routing (Models, Tools, Tenants)

Scaling often requires routing:

### A) Model routing (small vs large models)

Use smaller, cheaper models for:

- classification
- simple extraction
- summarization (when quality is sufficient)

Use larger models for:

- complex reasoning
- high-stakes planning (with verification)

In production, you route based on:

- intent type
- risk tier
- latency budget
- cost budget

### B) Tool routing (primary vs fallback)

For critical dependencies, provide fallbacks:

- primary API -> cached read-only fallback
- vector store -> keyword search fallback

Fallbacks must be explicit and observable. Silent fallbacks create correctness drift.

### C) Tenant fairness and quotas

Multi-tenant scaling requires fairness:

- per-tenant QPS limits
- per-tenant cost budgets
- per-tenant concurrency caps

Without quotas, one tenant can starve others.

### D) Scaling retrieval systems (vector store realities)

Retrieval often becomes a bottleneck at scale. Common scaling techniques:

- pre-compute embeddings and store them (batch ingestion)
- separate write and read paths (ingestion workers vs query service)
- cache frequent queries (tenant-scoped)
- cap top_k and apply reranking instead of retrieving more
- shard by tenant or domain if the dataset is large

Retrieval tuning checklist:

- **Chunking:** smaller chunks improve precision but increase retrieval count; larger chunks reduce calls but increase tokens.
- **Top_k:** keep it small; prefer better ranking over "more context".
- **Reranking:** if you can rerank, retrieve fewer and rerank smarter.
- **Citation discipline:** require evidence references so retrieval quality is observable.

Operational considerations:

- warm caches for common queries (startup and after deploys)
- measure retrieval latency separately (do not hide inside "LLM latency")
- treat retrieval as untrusted input (prompt injection via docs is common)

Failure mode to plan for:

- vector store degraded -> fallback to keyword search or "no retrieval" mode

### E) Rate limiting and token buckets (fairness mechanics)

Quotas become real when you implement them. A practical approach is token buckets:

- each tenant has a token budget per minute
- each request "spends" tokens based on estimated cost (prompt + tools)
- if budget is exceeded, degrade or reject with a clear message

This aligns scaling with cost: expensive tenants cannot starve everyone else.

### F) Cost engineering in practice (routing, compression, caching)

Scaling is inseparable from cost. In many agent systems, cost is the first limit you hit, not CPU.

High-leverage cost controls:

1. **Context budgets (hard caps):**
   - limit retrieval tokens per request
   - summarize long tool outputs
   - cap conversation history injected into prompts
2. **Model routing (small vs large):**
   - small model for classification, extraction, and simple summaries
   - large model only for complex reasoning and high-stakes planning
3. **Prompt templates (reduce verbosity):**
   - remove repeated instructions
   - use structured sections and short system guidance
4. **Cache safe intermediates:**
   - cache embeddings and retrieval results (tenant-scoped)
   - cache summaries with provenance

The goal is "cost per successful outcome". A cheap system that fails often is expensive in human time and trust.

### G) Load testing and chaos experiments (make scaling real)

Agents behave differently under load because retries and external dependencies create nonlinear effects.

Recommended tests:

- **Load test:** realistic traffic shape (spiky bursts), measure p95 latency and cost per success.
- **Dependency chaos:** inject tool timeouts and 5xx responses and verify:
  - circuit breakers open
  - fallbacks trigger explicitly
  - error budgets do not collapse
- **Budget pressure:** reduce token/time budgets and verify:
  - graceful degradation (partial results, safe messaging)
  - no runaway loops

If a scaling technique only works when everything is healthy, it is not a production technique.

### H) Batching and bulk operations (reduce round trips)

Many tool chains are slow because they are chatty:

- N separate calls for N items
- repeated retrieval for similar queries

Batching is a scaling technique that reduces both latency and load:

- add bulk read endpoints where feasible (fetch 20 tickets in one call)
- batch embedding generation for ingestion
- batch retrieval queries for multi-question workflows

Risks:

- batch calls can return larger payloads (token bloat)
- batch failures can be harder to isolate (partial success handling)

Mitigations:

- cap batch sizes (config)
- validate outputs and handle partial failures explicitly
- summarize large results before adding to prompts

---

## 6) Decision Trees and Trade-off Matrices

### Decision tree: Which scaling lever to pull first

```
Start
  |
  |-- Is p95 latency dominated by a single external tool?
  |      |
  |      |-- Yes -> add timeout + caching + fallback for that tool
  |      |
  |      |-- No
  |           |
  |           |-- Is cost dominated by token usage / prompt size?
  |           |      |
  |           |      |-- Yes -> reduce context (summaries, retrieval limits, templates)
  |           |      |
  |           |      |-- No
  |           |           |
  |           |           |-- Is throughput limited by serial tool calls?
  |           |                 |
  |           |                 |-- Yes -> async with concurrency limits
  |           |                 |
  |           |                 |-- No -> scale replicas + load balancing
```

### Trade-off matrix: Caching vs correctness

| Technique | Benefit | Risk | Mitigation |
|---|---|---|---|
| TTL cache for retrieval | faster answers | stale results | short TTL + invalidate on updates |
| Cache tool responses | lower tool load | wrong scope | include tenant + auth scope in key |
| Cache summaries | smaller prompts | summary drift | store provenance + refresh on doc change |
| Batch embeddings | cheaper compute | latency spikes | background jobs + rate limits |

### Decision tree: Cache or not?

```
Start
  |
  |-- Is the data tenant-scoped and permission-scoped?
  |      |
  |      |-- No -> do not cache (high leakage risk)
  |      |
  |      |-- Yes
  |           |
  |           |-- Is the tool read-only and idempotent?
  |                 |
  |                 |-- No -> cache only with strong invalidation and idempotency
  |                 |
  |                 |-- Yes -> safe to cache with scoped keys + TTL
```

### Trade-off matrix: Async vs queue-based workflow

| Approach | Benefit | Risk | Recommended when |
|---|---|---|---|
| Async inside request | low latency | overload dependencies | few subtasks, strict limits |
| Job queue + workers | predictable | more components | long workflows, approvals, heavy tools |
| Hybrid (sync + async) | flexible | complexity | mixed workloads and careful SLO design |

### Trade-off matrix: Context compression strategies

| Strategy | Benefit | Risk | Best for |
|---|---|---|---|
| Summarize then reference | large token savings | summary omits details | long tool outputs and long docs |
| Extract structured fields | precise and testable | schema work | billing/invoices/tickets with known fields |
| Drop low-signal history | easy and cheap | loses context | long conversations with repetition |

### Scaling checklist by layer (practical)

Use this as a quick review when preparing a workflow for higher traffic.

LLM layer:

- routing rules defined (small vs large model)
- context budgets enforced (prompt size does not grow unbounded)
- retries bounded (provider timeouts do not trigger storms)

Retrieval layer:

- top_k capped and reranking used where needed
- cache keys include tenant_id and scope
- degraded mode exists when retrieval is down

Tool layer:

- timeouts and bounded retries per tool
- bulkheads per tool (slow tools cannot starve others)
- batching used for chatty calls where safe

Orchestrator layer:

- stop conditions enforced (max steps, max time, max tool calls)
- partial success handling defined (what can be returned safely)

Multi-tenant layer (if applicable):

- per-tenant quotas and budgets
- per-tenant dashboards (success rate, cost per success)

### Scaling review questions (architect-level)

Use these questions in a design review:

1. What is the cost per successful outcome and what is the top driver (tokens, tool calls, retrieval)?
2. What happens when the top dependency degrades (tool outage, provider latency spike)?
3. How do you prevent retry storms (timeouts, circuit breakers, backoff)?
4. How do you prevent cross-tenant leakage (cache keys, retrieval scope, log access)?
5. What is the maximum workload the system can handle before it degrades (and how is that measured)?
6. What is the rollback plan for performance changes (routing rules, cache configs, budgets)?
7. How do safety controls behave under load (approvals, guardrails, redaction)?

If the answer to any of these is "we will find out in production", treat the design as not ready.

One last scaling trap: teams improve latency and cost while quietly degrading correctness. Always pair scaling work with evaluation (golden set) and safety metrics (blocks by rule, redaction events). "Fast and wrong" is not a success.

In practice, keep a small baseline workload and run it after every scaling change. If success rate or citation quality drops, treat it as a regression even if latency improved.

Store baseline results with the release artifacts so performance and quality changes remain comparable over time.

If the team cannot reproduce baseline numbers within a small tolerance, treat scaling work as incomplete and fix measurement first.

Also document the measurement method (dataset, load shape, environment) so another engineer can reproduce the results without guesswork.

---

## 7) Case Studies (Production Scenarios)

Each case study is summarized here and expanded in `case_studies/`.

Case study links:

- `case_studies/04_multi_tenant_support_platform_scaling.md`
- `case_studies/05_cost_spike_post_rollout.md`

### Case Study 1: Multi-Tenant Support Platform Under Load

**Scenario:** A support agent serves many tenants. Some tenants spike traffic during incidents.  
**Goal:** Maintain fairness and SLOs.

Key design choices:

- per-tenant quotas and budgets
- caching for retrieval results (scoped by tenant)
- concurrency limits on slow tools
- fallback routing when vector store degrades

Failure mode to plan for:

- retry storms when a tool is slow -> use circuit breakers and backoff

Metrics to validate scaling improvements:

- per-tenant success rate and p95 latency
- cache hit rate for retrieval
- retry counts per tool
- cost per success by tenant (budget enforcement working)

### Case Study 2: Scaling a Tool-Heavy Workflow (Long Chains)

**Scenario:** An agent calls multiple internal tools per request (CRM, billing, analytics).  
**Goal:** Reduce tail latency.

Key design choices:

- parallelize independent tool calls (async)
- cap concurrency
- introduce a "workflow cache" for stable intermediate results
- restructure chain to do cheap checks first (fail fast)

Failure mode to plan for:

- parallel tool calls overload a shared dependency -> add bulkheads and per-tool limits

### Mini-case: Scaling the multi-agent system

Multi-agent systems can scale throughput by parallelism, but they also increase total work. The scaling levers are the same:

- stop conditions and budgets (max subtasks, max time)
- concurrency limits (bulkheads)
- caching for read-only tool results
- verifier stage to avoid repeated rework

---

## 8) Hands-on Exercises

1. Build a bottleneck scorecard for one workflow:
   - tokens (prompt and completion)
   - tool calls and retries
   - p95 step latency
2. Implement one safe cache:
   - choose a read-only tool or retrieval step
   - define a safe cache key (tenant + role + config version)
   - measure hit rate and correctness impact
3. Add backpressure:
   - cap concurrency for a slow tool
   - add timeouts and retries with backoff
   - verify behavior under simulated tool degradation

4. Add context compression:
   - pick one verbose tool output (logs, tickets, docs)
   - summarize and store a reference ID
   - measure prompt size reduction and success rate impact

5. Run one scaling validation:
   - load test with a realistic burst pattern
   - chaos test one dependency (timeouts) and verify degraded mode

Deliverable: update an ADR with "what we measured" and "what scaling lever we chose".

---

## 9) One-Page Takeaway (Summary)

### What to remember

- Scaling agents is about latency, cost per success, reliability, and policy compliance under load.
- Measure where time and tokens go before scaling replicas.
- Caching is powerful but must be scoped (tenant, role, config version) to be safe.
- Async helps when you add backpressure; otherwise it melts dependencies.
- Routing and quotas are required for multi-tenant fairness.

### Minimal production checklist (scaling)

- [ ] Step-level latency and cost breakdown exists
- [ ] Timeouts at request and tool levels
- [ ] Concurrency limits for fan-out tools
- [ ] Cache keys include tenant + auth scope
- [ ] Circuit breakers for degraded dependencies
- [ ] Fallback modes are explicit and observable

### Suggested next steps

- Pick one workflow and instrument it end-to-end.
- Add caching for a safe read-only tool and measure impact.
- Write an ADR documenting which scaling levers you chose and why.

### Evidence artifacts (what to produce)

- A bottleneck scorecard before/after (tokens, tool calls, p95 latency, cost per success).
- A load test summary (throughput, tail latency, error rates).
- A chaos test summary (dependency degraded) showing circuit breakers and degraded mode behavior.
- A short note on cache safety: keys, TTL, invalidation, and scope.

Optional but useful:

- A "budget policy" doc: max tokens, max tool calls, and the user-facing degraded mode message when budgets are hit.

Scaling evidence is most valuable when it is repeatable. Keep a small baseline workload (golden set or synthetic canaries) and re-run it after every scaling change so you can detect "performance improved but quality regressed" failures early.
