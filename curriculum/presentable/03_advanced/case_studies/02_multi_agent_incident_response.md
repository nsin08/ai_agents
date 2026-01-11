# Case Study 02: Multi-Agent Incident Response (Operations)

**Related chapter(s):** `../chapter_02_multi_agent_systems.md`, `../chapter_05_monitoring_alerting.md`  
**Primary internal references:** `Agents/12_06_ops_troubleshooting_agent_architecture.md`, `labs/08/src/multi_agent_system.py`

## Executive Summary

An incident response assistant can accelerate diagnosis and communication during outages. This is a high-risk domain: unsafe actions can worsen incidents. Multi-agent designs help by separating roles and permissions:

- Investigator: read-only data gathering
- Mitigator: proposes actions but requires approval for writes
- Communicator: drafts human-facing updates with strict output constraints

This case study shows how to design a multi-agent incident assistant that is safe and operable.

## Scenario

During an outage, on-call engineers ask:

- "What changed recently?"
- "What is the most likely root cause?"
- "What mitigations are safe to try?"
- "Draft a status update for customers."

The system must work under time pressure and partial dependency failures (metrics/logs tools may degrade).

## Architecture Overview

```
User -> IncidentAssistant API
  -> Orchestrator (multi-agent coordinator)
      -> decompose(task)
      -> route subtasks
  -> Agents:
      - Investigator (read-only tools)
      - Mitigator (write-gated tools)
      - Communicator (no tools, output-limited)
  -> Combined response + evidence + suggested next actions
```

## Role Design and Boundaries

### Investigator (read-only)

Responsibilities:

- query logs and metrics
- fetch runbooks
- summarize recent deploys

Constraints:

- strict allowlist: logs_read, metrics_read, runbook_search
- no writes

### Mitigator (write-gated)

Responsibilities:

- propose mitigations (feature flag rollback, scaling changes)
- produce a "proposed change" payload

Constraints:

- can propose but cannot execute writes without approval
- timeouts and bounded retries

### Communicator (output-limited)

Responsibilities:

- draft a status update based on investigator findings and mitigator proposals

Constraints:

- no tools
- strict length limit
- avoid speculation; use evidence and uncertainty statements

## Decision Tree (Action Safety)

```
If action is irreversible OR affects many users:
  -> require supervisor approval
Else if action is reversible (feature flag rollback):
  -> propose + require single approval
Else:
  -> provide read-only recommendation only
```

## Observability Requirements

Minimum traceability:

- request_id for the incident session
- subtask -> agent routing decisions
- tool call durations and error rates
- approvals and outcomes for any write actions

Alerting:

- retry storms (tool calls spike)
- tool degradation (timeouts)
- increased guardrail blocks (injection attempts or policy drift)

## Failure Modes and Mitigations

1. Tool degradation: logs tool is slow or down.
   - fallback: cached incident summary + manual links to dashboards
2. Wrong routing: mitigator tries to act when investigator is needed.
   - deterministic routing rules for high-risk actions
3. Hallucinated mitigation: proposes unsafe steps not backed by evidence.
   - require evidence-carrying results and a verifier stage

## Lessons Learned

1. Multi-agent helps most when roles have different permissions and output constraints.
2. Action gating and approvals must be enforced in code, not prompts.
3. Incident workflows require low-latency, clear traceability, and explicit fallback modes.

## Suggested Exercises

1. Extend Lab 8: add an approval gate for write actions in a "mitigator" agent.
2. Define an incident golden set (5-10 scenarios) and measure response quality and safety.
3. Write an ADR for multi-agent incident response: why roles are separated and how boundaries are enforced.

