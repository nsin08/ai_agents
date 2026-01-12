# Implementation Patterns Library (Level 3 - Advanced)

This library is a reusable set of implementation patterns used across the Level 3 curriculum.

**Chapters:**  
- Safety: `chapter_01_safety_guardrails.md`  
- Multi-agent: `chapter_02_multi_agent_systems.md`  
- Deployment: `chapter_03_production_deployment.md`  
- Scaling: `chapter_04_scaling_strategies.md`  
- Observability: `chapter_05_monitoring_alerting.md`  
- Security: `chapter_06_security_best_practices.md`

---

## Pattern 01: Guardrail Checkpoints (Pre-Request, Pre-Tool, Post-Output)

**Problem:** Prompt-only safety is not enforceable against injection and tool misuse.  
**Solution:** Enforce policy at lifecycle checkpoints.

```text
request -> validate_request -> plan -> validate_tool_call -> execute -> validate_output -> response
```

**Pitfalls:**

- putting enforcement logic in prompts only
- logging raw tool outputs without redaction

**Related:** Lab 7, ADR-001

---

## Pattern 02: Risk Tiers + Approval Gating for Writes

**Problem:** Writes have irreversible consequences; autonomous writes are risky.  
**Solution:** Classify workflows into tiers and gate writes with human approvals.

```text
Tier 0: read-only -> no approvals
Tier 1: low-risk writes -> confirm-before-write
Tier 2: high-stakes writes -> supervisor queue / dual approval + audit
```

**Pitfalls:**

- approvals without showing the exact change (diff)
- approvals without an audit trail

**Related:** `case_studies/01_invoice_approval_assistant.md`

---

## Pattern 03: Tool Contracts (Schema + AuthZ + Idempotency)

**Problem:** Tool calls are the highest-risk boundary (side effects, data access).  
**Solution:** Treat tools like privileged APIs with contracts.

Minimum contract requirements:

- name + description
- input schema (validate)
- output schema (validate)
- authn/authz (RBAC + tenant scope)
- idempotency keys for writes
- timeouts and retries at orchestrator layer

Pseudo-wrapper:

```python
def call_tool(tool, actor, args, *, idempotency_key=None):
    validate_schema(tool.input_schema, args)
    authorize(actor, tool.name, args)
    result = tool.execute(args, idempotency_key=idempotency_key)
    validate_schema(tool.output_schema, result)
    return result
```

**Pitfalls:**

- skipping output validation
- allowing tool calls based on "intent" without hard allowlists

**Related:** `chapter_06_security_best_practices.md`

---

## Pattern 04: Evidence-Carrying Results (Answer + Evidence + Assumptions)

**Problem:** Agents can produce convincing but unsupported outputs.  
**Solution:** Require structured results with evidence and explicit assumptions.

```json
{
  "answer": "....",
  "evidence": [{"type": "tool", "tool": "kb_search", "ref": "req-123"}],
  "assumptions": ["..."],
  "confidence": "medium"
}
```

**Pitfalls:**

- storing evidence without provenance (who produced it, when)

**Related:** `chapter_02_multi_agent_systems.md`

---

## Pattern 05: Stop Conditions and Budgets (Prevent Runaway Systems)

**Problem:** Retry loops and multi-step planning can explode cost and latency.  
**Solution:** Explicit budgets and stop conditions.

Examples:

- max turns
- max tool calls
- max total time
- max retries per step
- max tokens per session

**Pitfalls:**

- no degraded mode when budgets are hit (users get hard failures)

**Related:** `chapter_04_scaling_strategies.md`

---

## Pattern 06: Router + Decomposition (Entry-Level Multi-Agent)

**Problem:** One agent struggles with context or conflicting skills.  
**Solution:** Split tasks and route to specialists with clear boundaries.

```text
subtasks = decompose(task)
for subtask in subtasks:
  agent = route(subtask)
  result = delegate(agent, subtask)
return combine(results)
```

**Pitfalls:**

- LLM-driven routing without deterministic constraints
- missing traceability (cannot explain routing)

**Related:** Lab 8, ADR-002

---

## Pattern 07: Concurrency-Limited Async Tool Execution

**Problem:** Tool chains are slow; naive parallelism overloads dependencies.  
**Solution:** Use async + concurrency limits (backpressure).

```python
import asyncio

sem = asyncio.Semaphore(5)

async def run_step(step):
    async with sem:
        return await step()
```

**Pitfalls:**

- increasing concurrency without measuring tool saturation

**Related:** `chapter_04_scaling_strategies.md`

---

## Pattern 08: Safe Caching (Scoped Keys + Explicit Fallback)

**Problem:** Caching improves latency and cost, but can leak data across tenants or roles.  
**Solution:** Scope cache keys and keep fallbacks explicit.

Safe cache key components:

- tenant_id
- role / permission scope
- tool/config version
- data version (if available)

**Pitfalls:**

- shared caches without tenant keys
- caching write outcomes without idempotency and invalidation

**Related:** `case_studies/04_multi_tenant_support_platform_scaling.md`

---

## Pattern 09: Degraded Mode as a First-Class Feature

**Problem:** External dependencies fail (LLM, vector store, tools).  
**Solution:** Define explicit degraded modes with user messaging.

Examples:

- retrieval down -> "no retrieval" mode with disclaimers
- tool down -> partial response + next steps
- provider down -> safe failure + retry guidance

**Pitfalls:**

- silent fallbacks that hide correctness loss

**Related:** `chapter_03_production_deployment.md`

---

## Pattern 10: Canary Rollouts with Evals as Release Gates

**Problem:** Model and prompt changes can cause subtle regressions and cost spikes.  
**Solution:** Gate rollouts with evals and monitor canaries.

Release gates:

- golden set success rate must not drop beyond threshold
- cost per success must not exceed baseline beyond threshold
- safety blocks must not change unexpectedly (guardrail drift)

**Related:** `case_studies/05_cost_spike_post_rollout.md`

