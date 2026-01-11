# Chapter 05: Monitoring and Alerting (Observability, SLOs, Incident Response)

**Level:** 3 (Advanced)  
**Target audience:** Senior engineers, staff+ engineers, architects  
**Prerequisites:** You know basic logging/metrics. You have built at least one agent workflow with tools.  
**Related lab:** `labs/06/` (Observability & Monitoring)  
**Primary internal references:** `Agents/05_06_observability_logging_metrics_tracing.md`, `labs/06/src/observable_agent.py`

## Learning Objectives (3-5)

By the end of this chapter, you will be able to:

1. Define a production observability model for agents: logs, metrics, traces, and audit events.
2. Design SLOs and alerting that reflect agent reality (success rate, safety blocks, tool health, cost per success).
3. Implement end-to-end tracing across agent turns, tool calls, and provider calls with stable correlation IDs.
4. Build incident response playbooks for agent-specific incidents (prompt injection, model outage, retry storms).
5. Use decision trees and trade-off matrices to balance observability depth vs privacy, cost, and performance.

## Chapter Outline

1. What to observe in an agent system
2. Logs, metrics, traces, and audit events (and how they differ)
3. SLOs and alerting for agents
4. Implementation patterns (with code) inspired by Lab 6
5. Incident response patterns and runbooks
6. Decision trees and trade-off matrices
7. Case studies (production scenarios)
8. One-page takeaway

---

## 1) What to Observe in an Agent System

Agent observability is not just "service health". You need to observe:

- **Behavior:** what the agent decided to do (plan, tool choices, refusals).
- **Performance:** latency by step, token usage, tool usage, retries.
- **Safety:** blocks, policy violations, redaction events, approval flows.
- **Correctness signals:** success/failure outcomes, user feedback, eval scores.
- **Cost:** cost per request, cost per success, cost by tool/provider/model.

Traditional service metrics (CPU, memory, HTTP latency) are necessary but insufficient. The most valuable signals are often domain-specific:

- "tool X error rate"
- "blocked_by_rule spikes"
- "human approval queue backlog"
- "cache hit rate for retrieval"

---

## 2) Logs vs Metrics vs Traces vs Audit Events

These are related but distinct.

### A) Structured logs (event stream)

Logs answer: "What happened?"

Best practice: emit structured JSON logs with:

- timestamp, level
- event name (stable string)
- request_id/session_id
- tenant_id (if applicable)
- data payload (sanitized)

Examples of agent events (from Lab 6 concepts):

- `agent_started`
- `turn_started`
- `llm_request_sent`
- `llm_response_received`
- `tool_call_initiated`
- `tool_call_completed`
- `guardrail_blocked`
- `agent_completed`

#### Log schema design rules (practical)

1. Keep `event` names stable. Renaming events breaks dashboards and alerts.
2. Log structured fields, not only human text:
   - request_id, tenant_id, tool_name, status, duration_ms
3. Do not log raw prompts or raw tool outputs by default.
   - store references (IDs) and use redacted previews
4. Prefer a small number of well-defined events over many ad-hoc logs.

If you are forced to choose, log fewer events with better structure.

### B) Metrics (aggregates)

Metrics answer: "How often and how long?"

Examples:

- `agent_requests_total{status=success|fail}`
- `agent_latency_ms_p95`
- `llm_tokens_total{model=...}`
- `tool_calls_total{tool=...}`
- `guardrail_blocks_total{rule=...}`
- `cost_usd_total{model=...}`

Metrics are used for dashboards and alerting.

#### Metric cardinality warning (agents make it worse)

Avoid putting high-cardinality values into metric labels:

- request_id (infinite)
- user_id (very high)
- raw query strings (infinite)

High-cardinality metrics overload your monitoring system and become expensive. Use:

- low-cardinality labels (workflow, tool, model, status)
- logs/traces for high-cardinality drilldowns
- sampling and exemplars (trace IDs linked from metrics)

### C) Traces (request path)

Traces answer: "Where did the time go, end-to-end?"

Trace structure for agents:

- root span: request
  - turn spans
    - llm span(s)
    - tool span(s)
    - retrieval span(s)

Traces are essential for debugging tail latency and complex failures.

### D) Audit events (security and compliance)

Audit logs answer: "Who did what, and what changed?"

Audit events must be:

- immutable (append-only)
- access-controlled
- retention-managed

Examples:

- "user requested write action"
- "approver approved change"
- "tool executed write with idempotency key"
- "policy config version applied"

Do not treat audit logs as normal application logs.

#### Observability for approvals (HITL workflows)

If your workflow includes approvals, observability must cover the human queue:

- approval_requested_total / approval_approved_total / approval_denied_total
- approval_queue_depth
- approval_time_to_decision_ms (p50/p95)

These are product health metrics. If approvals are too slow or too frequent, users will bypass the system or the system will be blocked from doing useful work.

---

## 3) SLOs and Alerting for Agents

### Choose SLOs that match agent outcomes

Agent SLOs are not just HTTP 200 rate.

Recommended SLO categories:

1. **Availability:** % requests that get a valid response (including safe fallbacks)
2. **Latency:** p95 end-to-end latency for interactive flows
3. **Success rate:** % tasks that meet acceptance criteria (golden set)
4. **Safety:** % unsafe actions blocked, refusal correctness, PII redaction effectiveness
5. **Cost:** cost per success, tokens per success

### Example SLOs

- p95 latency < 2.5s for Tier 0 (read-only) requests
- success rate >= 92% on golden set for release candidate
- guardrail blocks do not exceed baseline by +20% after a rollout (guardrail drift signal)
- cost per success <= $0.03 for a specific workflow

### Alerting pitfalls

1. **Alerting on raw error rate only**  
   Many agent failures are "soft failures" (refusals, degraded mode). Alert on outcomes.

2. **Noisy alerts during model/provider incidents**  
   Provider outages can cause cascades. Add circuit breakers and "provider health" alerts.

3. **No alerts for safety regression**  
   If safety blocks drop to zero unexpectedly, that can be a bug.

### Alert tuning (reduce noise, increase trust)

Alerting for agents can become noisy because external dependencies are noisy and agent behavior is variable. Practical tuning rules:

- alert on sustained signals (time windows), not single spikes
- alert on outcome metrics first (success rate, p95 latency), then on causes (tool error rate)
- separate alerts for user impact vs internal risk:
  - user impact: success rate down, latency up
  - internal risk: safety blocks drift, audit failures
- use different thresholds per workflow tier (Tier 0 vs Tier 2)

When an alert fires, the on-call engineer should have:

- a clear hypothesis of likely causes (top failing tool, provider outage)
- links to traces and logs via request_id exemplars
- a safe containment action (disable tool, tighten allowlist, enable degraded mode)

### Dashboard blueprint (minimum viable)

If you only build one dashboard, make it answer these questions quickly:

1. Are users getting successful outcomes?
2. Are we safe (guardrails and approvals working)?
3. Are we within latency and cost budgets?
4. Which dependency is failing?

Recommended panels:

- success rate (overall + by workflow)
- p95 latency (overall + by workflow)
- tool error rate (top tools)
- guardrail blocks by rule (drift signal)
- cost per success (by model and workflow)
- queue backlog (if approvals or jobs exist)

### Error budgets and release velocity (advanced but practical)

Error budgets connect reliability to change management:

- If you are meeting SLOs, you can ship faster.
- If you are burning the error budget, you slow down and stabilize.

For agent systems, define budgets not only for "service errors", but also for:

- cost overruns (budget burn)
- safety regressions (unexpected drop or spike in blocks)
- quality regressions (golden set success rate)

This is how you avoid the "ship prompt changes on Friday and hope" anti-pattern. You treat releases as controlled experiments with measurable guardrails.

### Bridging offline evals and online monitoring (advanced practice)

Agent quality is not fully observable from production traffic alone:

- user intent distribution changes over time
- users do not always provide clear feedback
- failures can be rare but high impact

Advanced teams connect two feedback loops:

1. **Offline evaluation** (golden + adversarial sets)
2. **Online monitoring** (real traffic + synthetic canaries)

#### Offline evaluation (what it gives you)

Offline evals provide repeatable measurements:

- success rate on golden scenarios
- safety compliance (blocks/refusals where expected)
- citation rate (for RAG workflows)
- cost and latency on a fixed workload

Offline evals are best for:

- comparing candidates to a baseline
- gating releases (block if regression beyond threshold)

#### Online monitoring (what it gives you)

Online monitoring shows:

- real dependency health (providers, tools)
- real performance under load
- real safety signals (injection attempts, weird user behavior)

Online monitoring is best for:

- detecting incidents and drift
- measuring user experience (latency, success outcomes)

#### Synthetic canaries (the bridge)

To bridge the two, run synthetic canaries in production:

- select a small set of safe prompts (no PII) that represent key intents
- run them periodically (every 5-15 minutes)
- treat failures as early warnings for provider or tool degradation

Example canary set:

- Tier 0: "summarize policy X" (read-only)
- Tier 1: "draft response to ticket Y" (no write)
- Tier 2: "propose invoice approval change" (write-gated, should request approval)

Synthetic canaries should be:

- deterministic in expected policy behavior (block vs allow)
- safe to run (no side effects, no writes)

#### Mapping eval metrics to monitoring metrics

| Quality dimension | Offline eval metric | Online monitoring metric |
|---|---|---|
| Task success | golden set pass rate | user outcome success rate |
| Safety | adversarial block rate | blocks by rule (drift) |
| Cost | tokens/cost per scenario | cost per success (by workflow/model) |
| Latency | p95 latency on eval set | p95 latency in production |

The goal is consistency: use the same definitions across evals and monitoring so you can compare apples to apples.

---

## 4) Implementation Patterns (with Code) Inspired by Lab 6

Lab 6 demonstrates a simple pattern: structured logs + trace buffer + metrics snapshot.

### Pattern 1: Stable event names and schemas

Define an event contract (even informally) so dashboards do not break.

Example log payload shape:

```json
{
  "timestamp": "2026-01-11T12:45:00.123Z",
  "level": "INFO",
  "event": "tool_call_completed",
  "request_id": "req-123",
  "data": {
    "tool": "weather_lookup",
    "duration_ms": 12.5,
    "status": "ok"
  }
}
```

Minimal structured logger (conceptual):

```python
import json
import time


def log_event(event: str, *, request_id: str, level: str = "INFO", **data):
    payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": level,
        "event": event,
        "request_id": request_id,
        "data": data,
    }
    print(json.dumps(payload, sort_keys=True))
```

In production, integrate with your logging system and ensure redaction happens before emitting.

### Pattern 2: Correlation IDs everywhere

Every request must have a stable ID that is passed to:

- logs
- traces
- tool calls (as metadata)
- audit events

Without correlation IDs, debugging becomes guesswork.

### Pattern 3: Metric snapshots per request (for debugging)

In addition to global metrics, capture per-request snapshots:

- turns, tool calls, tokens
- total_time_ms
- safety blocks

This can be exported for a single problematic request without enabling debug logs globally.

### Pattern 4: Sampling for cost control

Full tracing and full logs can be expensive and risky (privacy).

Use sampling:

- 100% sampling for failures and guardrail blocks
- low sampling for successes (e.g., 1-5%)
- separate sampling for high-risk workflows (higher sampling)

Sampling must be deterministic by request_id for reproducibility.

### Pattern 5: Trace spans as context managers (simple and effective)

You do not need a full tracing stack to teach the concept. A minimal trace span can be implemented with a context manager:

```python
import time
from contextlib import contextmanager


@contextmanager
def span(trace: list[dict], name: str, **attrs):
    start = time.perf_counter()
    try:
        yield
        status = "ok"
    except Exception as e:
        status = "error"
        attrs["error"] = str(e)
        raise
    finally:
        trace.append(
            {
                "span": name,
                "status": status,
                "duration_ms": (time.perf_counter() - start) * 1000,
                "attrs": attrs,
            }
        )
```

This pattern produces structured spans you can export as JSON. In production, you can map this concept to OpenTelemetry or your tracing system.

### Pattern 6: Redaction at the logging boundary

The safest approach is to apply redaction before logs/traces are emitted:

- redact tool outputs
- redact user inputs
- avoid logging full prompts

Treat "logging redaction" as a guardrail: it should be deterministic and tested.

### Pattern 7: Cost accounting as a first-class metric

If your LLM provider returns token usage, record it:

- prompt tokens
- completion tokens
- total tokens
- estimated cost

Then aggregate "cost per success" by workflow and model. Cost is not an afterthought; it is an SLO.

### Pattern 8: Tool spans and safe payload previews

Tool calls are the most common root cause of production incidents. When you trace tools, capture attributes that help triage:

- tool name
- duration_ms
- status (ok/error/timeout)
- retry_count
- dependency name (if tool wraps multiple calls)

Avoid capturing raw inputs/outputs. Use safe previews:

- structured IDs (ticket_id, invoice_id) if not sensitive
- redacted text previews (first N chars after redaction)

If you need full payloads for debugging, store them in a restricted store and log a reference ID.

---

## 5) Incident Response Patterns and Runbooks

Agent incidents are not only "service down". Common incident classes:

### A) LLM provider outage or latency spike

Symptoms:

- latency spikes across all workflows
- increased timeouts

Mitigations:

- circuit breaker opens for provider
- route to fallback model/provider (if available)
- degrade to safe response ("cannot answer now, try later") with incident banner

### B) Tool dependency degradation

Symptoms:

- tool_call_completed errors spike for one tool
- retry storms increase load

Mitigations:

- circuit breaker for the tool
- fallback mode (cached results, read-only summary)
- temporarily disable the tool (policy change) with audit log

### C) Prompt injection or data exfil attempts

Symptoms:

- guardrail blocks spike for "allowed_tools" or "block_pii"
- suspicious tool calls attempted

Mitigations:

- tighten allowlists for the workflow
- enable stricter redaction and output limits
- isolate and investigate affected tenants/users

### D) Guardrail drift after rollout

Symptoms:

- sudden increase in blocks for benign inputs
- user complaints: "agent refuses everything"

Mitigations:

- rollback config version
- compare eval results to baseline
- re-tune policy with evidence (false positives)

### E) Suspected data leakage (privacy incident)

Symptoms:

- user reports seeing another tenant's data
- logs contain unredacted PII
- suspicious retrieval results (wrong tenant scope)

Immediate containment:

- disable affected workflows or tools (policy change with audit)
- restrict access to logs and traces (limit blast radius)
- preserve evidence: request_ids, trace samples, and config versions

Longer-term fixes:

- enforce tenant scoping in retrieval and cache keys
- add regression tests for tenant isolation
- tighten redaction and logging policies

### Runbook drill (how to make this real)

Runbooks are only useful if you test them. A practical drill:

1. Simulate a provider outage (force timeouts) and verify circuit breakers and alerts.
2. Simulate a tool degradation (return 5xx) and verify fallback modes.
3. Simulate guardrail drift (tighten a rule) and verify dashboards show the spike.
4. Simulate an injection attempt and verify blocks are visible and actionable.

### Runbook template (minimum)

For each incident type, document:

- detection signals (metrics + logs)
- immediate containment actions
- rollback steps
- data collection steps (trace IDs, sample requests)
- communication plan (status page, internal updates)
- postmortem questions (what changed, what guardrail failed)

### Example runbook: Tool degradation (step-by-step)

**Scenario:** `tool_call_completed` errors spike for `kb_search`.

1. Confirm user impact:
   - success rate down?
   - p95 latency up?
2. Confirm dependency impact:
   - tool error rate and timeout rate
   - retry counts (is a retry storm happening?)
3. Contain:
   - open circuit breaker for `kb_search`
   - enable degraded mode: "no retrieval" with clear messaging
   - cap concurrency for the tool (bulkhead)
4. Communicate:
   - update internal status channel
   - document workaround (manual KB access)
5. Recover:
   - validate dependency health
   - gradually close circuit breaker (canary)
6. Postmortem questions:
   - did alerts fire early enough?
   - did degraded mode preserve safety and user trust?
   - did retries amplify the incident?

Deliverable:

- attach sample request_ids and traces to the incident ticket
- record config/policy versions active during the incident

---

## 6) Decision Trees and Trade-off Matrices

### Decision tree: How much tracing to enable

```
Start
  |
  |-- Is this a high-risk workflow (writes, regulated data)?
  |      |
  |      |-- Yes -> capture 100% audit events + higher trace sampling for failures
  |      |
  |      |-- No
  |           |
  |           |-- Are you in active incident investigation?
  |                 |
  |                 |-- Yes -> temporarily increase sampling (timeboxed)
  |                 |
  |                 |-- No -> keep low sampling for success, high for failures
```

### Trade-off matrix: Observability depth vs privacy and cost

| Choice | Benefit | Cost/Risk | Mitigation |
|---|---|---|---|
| Full logs | best debugging | PII risk, storage cost | redaction, access control, retention limits |
| Full traces | latency breakdown | overhead and cost | sampling, compress spans |
| Per-request snapshots | targeted debugging | engineering effort | build once, reuse everywhere |
| Audit everything | compliance | storage, review burden | scope to high-risk actions |

### Decision tree: What is safe to log?

```
Start
  |
  |-- Does the field contain secrets or PII?
  |      |
  |      |-- Yes -> do not log raw value (redact or drop)
  |      |
  |      |-- No
  |           |
  |           |-- Is the field needed for debugging or auditing?
  |                 |
  |                 |-- Yes -> log structured field (low cardinality)
  |                 |
  |                 |-- No -> drop it (reduce noise and risk)
```

This decision tree is intentionally conservative. If you are unsure, assume the data is sensitive and log only references (IDs) and redacted previews.

### Retention and access control (privacy meets operability)

Observability data is a dataset. Treat it like one:

- define retention per data class (logs vs traces vs audit)
- restrict access by role (developers do not always need raw audit logs)
- avoid exporting sensitive logs to widely accessible systems

Practical compromise:

- keep short retention for high-volume logs
- keep longer retention for audit events (high value, lower volume)
- keep sampled traces for failures and guardrail blocks

If you cannot enforce access control, reduce what you collect. Over-collection without governance is a common source of privacy incidents.

### Example alert definitions (conceptual)

Use alert definitions that are actionable and tied to outcomes.

Outcome alerts (user impact):

```text
ALERT: success_rate_drop
IF success_rate(workflow="support") < 0.85 for 10m
THEN page on-call and link dashboard + recent request_id exemplars
```

Cause alerts (dependency):

```text
ALERT: tool_timeouts_spike
IF tool_timeout_rate(tool="kb_search") > 0.20 for 5m
THEN open incident and enable degraded mode playbook
```

Safety drift alerts:

```text
ALERT: safety_blocks_drift
IF guardrail_blocks_total(rule="allowed_tools") increases > 30% after rollout
THEN rollback policy config or investigate false positives
```

Cost drift alerts:

```text
ALERT: cost_per_success_drift
IF cost_per_success(workflow="faq") increases > 25% compared to baseline
THEN block rollout and investigate routing/context changes
```

The exact thresholds are domain-specific. The key is that every alert has a clear containment action.

Alert hygiene matters:

- test alerts in staging (force conditions) so you know they fire and routes work
- review alerts periodically and delete noisy ones
- track alert fatigue signals (repeated pages with no user impact)

If alerts are not trusted, teams will ignore them, and observability becomes a dashboard that no one looks at.

A useful pattern is to separate alerts into:

- pages: immediate user impact or security risk
- tickets: slower drift signals that require investigation

This keeps on-call focused and still preserves longer-term learning from metrics.

Make alert ownership explicit: every alert should have an owner, a runbook link, and a "disable/contain" action that can be executed safely. Alerts without owners become noise over time.

Over time, the best teams treat alert catalogs like code: reviewed, versioned, and pruned when they stop providing value.

As a simple practice, add a short "why this alert exists" note in the runbook so future maintainers do not reintroduce noisy pages.

This preserves institutional knowledge and keeps alerting aligned with real user impact instead of historical accidents.

It also speeds up onboarding for new on-call engineers.

---

## 7) Case Studies (Production Scenarios)

Each case study is summarized here and expanded in `case_studies/`.

Case study links:

- `case_studies/02_multi_agent_incident_response.md`
- `case_studies/05_cost_spike_post_rollout.md`

### Case Study 1: Incident Mitigation Agent (Operational Risk)

**Scenario:** Agent assists on-call engineers during incidents.  
**Risk:** Actions can make the outage worse.

Key observability requirements:

- trace every tool call with durations (tail latency matters)
- record all proposed mitigations and approvals
- alert on retry storms and tool timeouts
- maintain an audit trail of write actions (feature flag changes, paging)

Operational alerts that reduce incident time:

- provider timeout spike (global)
- tool-specific timeout spike (top 3 tools)
- approval backlog spike (writes are blocked waiting on humans)

Post-incident artifact:

- a trace bundle (sample request_ids) attached to the incident ticket

Mini-case: Missing correlation IDs

If you cannot find a request_id in logs during an incident, every investigation becomes slower. This is why correlation IDs are a deployment gate:

- block release if request_id propagation is missing
- add a synthetic canary that verifies request_id appears in logs and traces

### Case Study 2: Cost Spike After Model Change

**Scenario:** A model routing change increases token usage by 30%.  
**Risk:** Budget overruns and degraded SLOs.

Key observability requirements:

- cost per success metric by model
- token usage histograms
- alert on cost drift after rollout
- gating: block full rollout if cost per success crosses threshold

Operational best practice:

- store baseline cost and latency for a golden set
- compare candidate vs baseline in CI
- require a human sign-off for cost increases above threshold

---

## 8) Hands-on Exercises

1. Define an event taxonomy for one agent workflow:
   - agent events (start, end, fail)
   - tool events (start, end, fail)
   - guardrail events (blocked, redacted)
2. Implement correlation IDs:
   - propagate request_id through logs and tool calls
   - ensure trace spans share the same request_id
3. Build a dashboard blueprint:
   - success rate, p95 latency, tool error rate, blocks by rule, cost per success
4. Run an incident drill:
   - simulate provider outage and verify alerts + containment
5. Define alerting rules for one workflow:
   - success rate drop threshold
   - p95 latency threshold
   - safety blocks drift threshold
6. Define retention and access control:
   - what logs are kept and for how long
   - who can access audit events vs application logs

Deliverable: publish a short runbook and attach sample trace output for a single request.

---

## 9) One-Page Takeaway (Summary)

### What to remember

- Observe behavior, safety, correctness signals, and cost - not only uptime.
- Separate structured logs, metrics, traces, and audit events (they have different purposes and constraints).
- Define SLOs based on agent outcomes: success rate, safety compliance, and cost per success.
- Build incident runbooks for agent-specific incidents: provider outages, tool degradation, injection attempts, guardrail drift.

### Minimal production checklist (observability)

- [ ] Stable event names and schemas
- [ ] Correlation IDs for every request and tool call
- [ ] Metrics: success rate, latency, tool health, safety blocks, cost per success
- [ ] Trace sampling strategy (100% for failures and blocks)
- [ ] Audit logs for high-risk actions with strict access control
- [ ] Incident runbooks exist and are tested

### Suggested next steps

- Complete Lab 6 and extend it to include safety events and cost metrics.
- Create a dashboard: success rate, blocks by rule, p95 latency, cost per success.
- Write an ADR documenting your observability design choices and privacy constraints.

### Evidence artifacts (what to produce)

- A sample trace export (one request_id) showing turns, tool calls, and durations.
- An alert list with thresholds and containment actions (runbook links).
- A retention/access policy summary for logs, traces, and audit events.
- A canary report: synthetic prompts run in staging/prod with expected outcomes.

Optional but useful:

- A baseline report for one golden set: success rate, p95 latency, tokens, and cost per success.

These artifacts make observability a shared language across engineering, product, and operations.

If you want a quick maturity test: ask two people (an engineer and an on-call peer) to debug the same request using your dashboards and traces. If they cannot reach the same conclusion in a few minutes, your observability is either missing key events or too noisy to use. Improve signal density before adding more data.
