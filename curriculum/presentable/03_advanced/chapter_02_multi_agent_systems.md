# Chapter 02: Multi-Agent Systems (Lab 8 Walkthrough)

**Level:** 3 (Advanced)  
**Target audience:** Senior engineers, staff+ engineers, architects  
**Prerequisites:** You can build a single-agent system with tools, basic memory, and guardrails.  
**Related lab:** `labs/08/` (Multi-Agent Systems)  
**Primary internal references:** `Agents/09_01_agent_frameworks_and_multi_agent_systems.md`, `labs/08/src/multi_agent_system.py`, `labs/08/src/specialist_agents.py`

## Learning Objectives (3-5)

By the end of this chapter, you will be able to:

1. Decide when multi-agent is worth the added complexity (and when it is not).
2. Explain and implement core coordination patterns: router, decomposition, hierarchical manager, and swarm/peer collaboration.
3. Design safe multi-agent boundaries (capabilities, tool access, memory isolation, and approvals).
4. Extend a simple router into a production-ready orchestrator (timeouts, retries, load balancing, traceability).
5. Validate multi-agent behavior with deterministic tests and scenario-based evaluations.

## Chapter Outline

1. Why multi-agent systems exist (and common failure modes)
2. Coordination and communication models
3. Multi-agent orchestration patterns
4. Lab 8 walkthrough: router + decomposition
5. Production hardening patterns (reliability, safety, observability)
6. Decision trees and trade-off matrices
7. Case studies (production scenarios)
8. One-page takeaway

---

## 1) Why Multi-Agent Systems Exist (and Where They Fail)

Multi-agent systems appear when a single agent starts to hit one of these ceilings:

- **Context ceiling:** The agent must reason over too much information at once (docs, logs, code, policies).
- **Skill ceiling:** The task requires different "modes" that conflict (creative writing vs strict verification).
- **Tool ceiling:** The task spans different tool permissions (read-only research vs privileged actions).
- **Throughput ceiling:** You want parallelism (research while drafting while validating).

### Multi-agent does not guarantee better results

The most common anti-pattern is "more agents = more intelligence". In practice, more agents often means:

- more failure modes (routing errors, inconsistent outputs, loops)
- harder debugging (who decided what and why?)
- higher cost (more LLM calls, more tool calls)

If you cannot clearly explain why a second agent is necessary, start with a single agent and add structure (tool contracts, state machine, context budgeting) first.

### Common failure modes in multi-agent systems

1. **Routing failure:** the wrong agent is selected; output is irrelevant or unsafe.
2. **Decomposition drift:** tasks split into subtasks that do not match user intent.
3. **Inconsistent policies:** one agent follows guardrails, another bypasses them.
4. **Coordination loops:** agents ask each other for help indefinitely.
5. **Traceability loss:** you cannot reconstruct the decision path after an incident.

The rest of this chapter is about gaining the benefits of multi-agent designs without losing safety and operability.

---

## 2) Coordination and Communication Models

Multi-agent coordination is mostly about two things:

1) **How tasks move** between agents  
2) **How information moves** between agents

### A) Message passing (explicit communication)

Agents send messages to each other through a coordinator. Benefits:

- auditable (messages can be logged)
- supports permissions (coordinator can enforce policy at boundaries)
- easier to test (messages are data)

In Lab 8, `Message` records `from_agent`, `to_agent`, and `content`, and the system stores a `message_log`.

### B) Shared memory / blackboard (implicit communication)

All agents read and write to a shared store (short-term memory, long-term memory, vector store). Benefits:

- efficient sharing
- supports swarm behavior

Risks:

- memory contamination (bad facts spread)
- privacy leakage (one tenant's data visible to another)
- difficult debugging (who wrote the misleading memory?)

Production recommendation:

- Treat shared memory as an interface with strict write policies.
- Store provenance with every memory write (who wrote it, from what tool output, at what time).
- Prefer append-only logs over mutable shared state for traceability.

### C) Supervisor / manager model (hierarchical)

A manager agent decomposes work and delegates to specialists. Benefits:

- centralizes planning and policy
- supports staged decision making (plan -> execute -> verify)

Risks:

- manager becomes bottleneck
- manager prompt becomes complex

This is often the best step up from single-agent systems: one planner + one executor + one verifier.

### D) Communication contracts (why you need schemas)

As soon as you have more than one agent, "free text" becomes a reliability problem:

- One agent's output becomes another agent's input.
- If that interface is unstructured, errors compound.

Treat inter-agent communication like an internal API:

- define message types (request, response, critique, evidence)
- define required fields (request_id, from_agent, to_agent, timestamp)
- define payload contracts for tools and evidence

Minimal message schema (conceptual):

```json
{
  "request_id": "req-123",
  "type": "agent_result",
  "from": "investigator",
  "to": "system",
  "payload": {
    "answer": "...",
    "evidence": [{"type": "tool", "tool": "logs_read", "ref": "tool-789"}],
    "assumptions": ["..."],
    "confidence": "medium"
  }
}
```

Schemas are not only for correctness. They are for traceability: after an incident you want to reconstruct what was decided, by whom, and based on what evidence.

---

## 3) Multi-Agent Orchestration Patterns

### Pattern 1: Router (capability-based routing)

The simplest pattern: pick the best specialist for the task.

Lab 8 uses a keyword overlap score:

- extract `task_keywords`
- for each agent, compare keywords to `get_capabilities()`
- pick highest score, else default to first agent

This is intentionally simple. In production, routing typically evolves to include:

- intent classification (LLM or ML)
- rule-based constraints (some tasks must go to a safe agent)
- load-aware routing (avoid hot specialists)
- fallback routing (if agent fails, route to alternate)

### Pattern 2: Decomposition (split into subtasks)

Decomposition breaks a task into smaller tasks, then routes each.

Lab 8 uses a naive split by " and ". This is enough to teach the concept:

- it is deterministic and testable
- it highlights that decomposition rules are product logic

In production, decomposition can be:

- template-driven ("gather info" -> "decide" -> "execute" -> "verify")
- schema-driven (tasks are structured objects, not free text)
- LLM-assisted (but still validated)

### Pattern 3: Hierarchical manager + specialists

Manager responsibilities:

- create a plan with explicit constraints
- decide which specialist to invoke
- merge results and verify completion criteria

Specialist responsibilities:

- solve a scoped subtask
- provide evidence and artifacts (tool outputs, citations)

### Pattern 4: Swarm / peer collaboration

Peer agents propose candidate solutions and critique each other. This can improve quality, but:

- costs more
- increases complexity
- requires strong stopping conditions

Swarm systems are best when you can afford exploration and you can verify results with deterministic checks (tests, schemas, constraints).

### Pattern 5: Verifier / judge stage (quality gate)

The single most useful production multi-agent pattern is adding a verifier:

- Specialists generate candidate outputs.
- A verifier checks completion criteria, evidence, and safety constraints.
- If verification fails, the system re-routes or asks for clarification.

Verification can be deterministic:

- schema checks
- unit tests
- citations required
- policy checks ("no writes without approval")

Or verification can be probabilistic (LLM critique), but you still need deterministic constraints to avoid "opinions" being treated as truth.

---

## 4) Lab 8 Walkthrough: Router + Decomposition

Lab 8 provides a compact, readable implementation you can extend.

### Key interfaces

Lab 8 defines an `Agent` protocol:

```python
from typing import List, Protocol


class Agent(Protocol):
    def run(self, task: str) -> str:
        ...

    def get_capabilities(self) -> List[str]:
        ...
```

And the orchestrator:

- `register_agent(name, agent)`
- `decompose(task) -> List[str]`
- `route_task(task) -> agent_name`
- `delegate(task, agent_name) -> result`
- `combine(results) -> final`
- `run(task) -> final`

### Traceability in the lab

Even in a toy system, Lab 8 includes trace hooks:

- prints when `verbose=True`
- message logging via `_log_message(...)`

In production, you should replace print statements with structured logs and tracing spans, but the conceptual shape is correct:

- record every delegation decision (subtask -> agent)
- record the inputs (sanitized) and outputs (sanitized)
- correlate events with a request_id

---

## 5) Production Hardening Patterns (Reliability, Safety, Observability)

Multi-agent systems multiply both capabilities and risk. Hardening is not optional.

### Pattern A: Capability boundaries as safety boundaries

Do not treat capabilities as "labels". Treat them as permissions:

- each specialist has an allowlist of tools
- each specialist has its own guardrail config (budgets, output policy)
- the coordinator enforces these at the boundary

Example policy rules:

- "research agent: read-only tools only"
- "executor agent: write tools allowed but requires approvals"
- "summarizer agent: no tools, output length limit"

### Pattern B: Explicit stop conditions

Production multi-agent systems require explicit stop conditions:

- maximum subtasks
- maximum total tool calls
- maximum total time
- maximum retries per agent

Without stop conditions, you get runaway systems and high costs.

### Pattern C: Coordinator-enforced timeouts and retries

Each delegation should be wrapped with:

- timeout (per subtask)
- bounded retries (with backoff)
- fallback agent route (optional)

Do not hide retries inside agent prompts. Implement them at the orchestrator layer.

### Pattern D: Evidence-carrying results

A common multi-agent failure is "convincing but unsupported results". Require specialists to return structured evidence:

- citations (doc IDs, URLs, file paths)
- tool outputs (sanitized)
- assumptions (explicit)

In a production system, prefer structured results:

```json
{
  "answer": "...",
  "evidence": [{"type": "tool", "tool": "kb_search", "id": "req-123"}],
  "assumptions": ["..."],
  "confidence": "medium"
}
```

### Pattern E: Global trace and audit log

At minimum, trace:

- task -> subtasks
- subtasks -> agents
- agents -> tools
- tools -> results

This is essential for debugging and for explaining outcomes to users and auditors.

### Pattern F: Routing that is safe under ambiguity

Routing decisions should be conservative when intent is unclear:

- default to read-only specialists if risk is unknown
- ask clarifying questions before selecting a write-capable agent
- require explicit user intent for write flows ("approve", "change", "delete")

This reduces "accidental write" incidents caused by ambiguous language.

### Pattern G: Parallel execution (only when independence is real)

Multi-agent systems can run subtasks concurrently, but only if:

- subtasks are independent (no ordering constraints)
- tools and dependencies can tolerate concurrency
- you have backpressure (concurrency limits)

Conceptual pattern:

```python
import asyncio


async def run_subtask(system, subtask: str) -> str:
    agent_name = system.route_task(subtask)
    return system.delegate(subtask, agent_name)


async def run_all(system, subtasks: list[str]) -> list[str]:
    # Add concurrency limits in production.
    return await asyncio.gather(*[run_subtask(system, s) for s in subtasks])
```

Parallelism is a scaling tool, not a default. It increases load and can amplify outages if you do it without limits.

### Pattern H: Shared memory with provenance (avoid contamination)

If agents share memory, enforce a write policy:

- store provenance (who wrote it, from what tool output)
- prefer append-only logs to mutable "facts"
- separate "untrusted notes" from "verified facts"

Example memory record (conceptual):

```json
{
  "type": "note",
  "text": "Possible root cause: deploy X",
  "written_by": "investigator",
  "source": {"type": "tool", "tool": "deploy_history", "ref": "tool-55"},
  "timestamp": "2026-01-11T12:00:00Z"
}
```

Without provenance, memory becomes a rumor engine.

---

## 6) Implementation Walkthrough: From Lab 8 to a Production Router

This walkthrough shows how to evolve the Lab 8 toy orchestrator into something you can safely deploy for internal pilots.

The goal is not a fully featured framework. The goal is a system that:

- is explainable (why did it route to that agent?)
- is safe (write capabilities are gated)
- is testable (routing and stop conditions are deterministic)
- is observable (traceable end-to-end)

### Step 1: Define specialist roles and boundaries

Start by defining roles that map to real constraints:

- **research/investigation:** read-only, can retrieve and summarize
- **execution:** write-gated, requires approvals for side effects
- **communication:** no tools, output-limited, no speculation
- **verification:** runs deterministic checks (schemas, tests, policy checks)

The boundary must be enforceable in code. In practice that means per-agent tool allowlists and budgets.

### Step 2: Define structured messages (avoid free-text coupling)

Inter-agent messages should be structured. At minimum, require:

- request_id
- agent_name
- result type (answer, evidence, critique, proposal)
- evidence references

Even if your internal system passes these as Python dicts, the schema provides stability.

### Step 3: Improve routing (deterministic, explainable scoring)

Lab 8 uses keyword overlap. That is fine as a baseline, but you can improve routing while staying deterministic:

- normalize tokens (lowercase, strip punctuation)
- use synonym maps ("debug" ~= "investigate", "write" ~= "draft")
- add rule-based overrides for high-risk intents (writes -> executor)

Conceptual router:

```python
SYNONYMS = {
    "investigate": {"debug", "analyze", "root", "cause"},
    "write": {"draft", "compose", "document"},
    "code": {"implement", "fix", "refactor"},
}


def normalize(text: str) -> set[str]:
    return set(text.lower().replace(",", " ").replace(".", " ").split())


def route(task: str, agents: dict[str, set[str]]) -> str:
    tokens = normalize(task)
    best_name = None
    best_score = -1
    for name, caps in agents.items():
        score = 0
        for cap in caps:
            if cap in tokens:
                score += 2
            for syn in SYNONYMS.get(cap, set()):
                if syn in tokens:
                    score += 1
        if score > best_score:
            best_score = score
            best_name = name
    return best_name or list(agents.keys())[0]
```

This is explainable: you can log the scores and show why routing happened.

### Step 4: Add a verifier stage (quality gate)

In production, verification prevents expensive rework and unsafe outcomes. Examples of deterministic verification:

- output must include citations when retrieval is used
- tool results must match schemas
- write actions must include an approval token

Verifier responsibilities:

- check completion criteria
- reject unsupported claims (no evidence)
- request clarifying input if required

### Step 5: Add stop conditions, timeouts, and retries

Multi-agent systems can run away. Add explicit budgets:

- max subtasks
- max retries per subtask
- max time per request
- max tool calls per request

Treat budgets as config so you can tune without redeploying code.

### Step 6: Add observability (routing decisions are first-class events)

At minimum, log:

- task -> subtasks
- subtask -> agent routing decision (+ score)
- agent -> tool calls (+ duration)
- verifier pass/fail reasons

In practice, this looks like an event stream:

```text
event=subtask_routed request_id=req-123 subtask="..." agent=investigator score=7
event=tool_call_completed request_id=req-123 tool=logs_read duration_ms=120 status=ok
event=verifier_failed request_id=req-123 reason="missing citation"
```

### Step 7: Test multi-agent systems like product logic

Most multi-agent bugs are logic bugs, not "model issues". Build:

- unit tests for routing (task -> expected agent)
- unit tests for stop conditions (max subtasks, max retries)
- scenario tests for end-to-end flows (deterministic specialists or mocks)

Add at least one regression test for a routing drift incident (see mini-case in this chapter).

### Step 8: LLM-assisted routing (optional, constrained)

At some point, keyword routing becomes too limited. You can introduce LLM assistance safely if you keep the final decision constrained:

1. LLM proposes:
   - candidate agent name
   - short rationale (why this agent)
   - confidence
2. The orchestrator validates:
   - the candidate agent exists
   - the candidate is allowed for this risk tier
   - write-capable agents require explicit user intent or approval token
3. If validation fails:
   - fall back to deterministic routing
   - or ask a clarifying question

This preserves safety and testability while gaining better intent understanding.

Conceptual "proposal then validate" pattern:

```text
proposed_agent = llm_route(task)
if not allowed(proposed_agent, task, risk_tier):
  proposed_agent = deterministic_route(task)
```

The key is that the LLM is advisory. The policy engine is authoritative.

### Step 9: Decomposition beyond "and" (structured subtasks)

Lab 8 decomposition is intentionally simple. In production, decomposition becomes a contract:

- define a subtask schema (type, input, expected output)
- constrain which agents can receive which subtask types
- include completion criteria ("done when tests pass", "done when citations exist")

Conceptual subtask schema:

```json
{
  "type": "investigation",
  "description": "Find top error cause in logs",
  "completion_criteria": ["include 2 evidence references", "no write actions"],
  "risk_tier": 0
}
```

This makes it possible to:

- verify results deterministically (criteria checks)
- reroute failed subtasks without re-running everything
- prevent specialists from drifting outside scope

### Step 10: Multi-agent safety posture checklist

Before deploying a multi-agent workflow, confirm:

- each agent has an explicit tool allowlist and budget
- write tools are gated behind approvals and audit logs
- routing decisions are logged and explainable
- stop conditions are enforced (time, retries, subtasks)
- a verifier stage exists for correctness and evidence

### Step 11: Operational debugging workflow (request_id first)

When a multi-agent system fails in production, teams often argue about "model behavior". A better approach is to debug like an engineer:

1. Start with a request_id and reconstruct the path:
   - task -> subtasks -> routing -> tool calls -> results -> verifier decisions
2. Identify whether the failure is:
   - routing logic (wrong agent)
   - dependency failure (tool/provider)
   - verification failure (missing evidence)
3. Contain the blast radius:
   - route to a safe fallback agent (read-only)
   - disable a degraded tool via policy
4. Fix and prevent:
   - update routing rules or schemas
   - add a regression test that reproduces the incident

A simple rule: if you cannot explain the routing decision with logs and scores, you are not ready to run multi-agent in production.

---

## 7) Decision Trees and Trade-off Matrices

### Decision tree: When to use multi-agent

```
Start
  |
  |-- Is the task reliably solved by one agent with tools and good prompts?
  |       |
  |       |-- Yes -> Stay single-agent (reduce complexity)
  |       |
  |       |-- No
  |            |
  |            |-- Is the problem mostly "too much context"?
  |            |       |
  |            |       |-- Yes -> Add decomposition + retrieval first
  |            |       |
  |            |       |-- No
  |            |            |
  |            |            |-- Is the problem "conflicting skills" (creative vs strict)?
  |            |            |       |
  |            |            |       |-- Yes -> Add specialists (router pattern)
  |            |            |       |
  |            |            |       |-- No -> Consider state machine, better tools, evals
```

### Trade-off matrix: Multi-agent vs single-agent

| Dimension | Single agent | Multi-agent | Notes |
|---|---|---|---|
| Debuggability | simpler | harder | multi-agent needs traceability by design |
| Cost | lower | higher | more LLM calls and coordination overhead |
| Parallelism | limited | better | can run subtasks concurrently |
| Safety | simpler | riskier | more boundaries to enforce consistently |
| Quality | good with strong tools | can be better | only if routing and verification are strong |

The key lesson: multi-agent is a scaling tool for architecture, not a shortcut to correctness.

### Trade-off matrix: Message passing vs shared memory vs hierarchical manager

| Model | Benefits | Risks | Recommended when |
|---|---|---|---|
| Message passing | explicit traceability | coordination overhead | regulated or high-risk workflows |
| Shared memory | fast collaboration | contamination + privacy leakage | trusted internal workflows with strong write policy |
| Hierarchical manager | centralized policy | bottleneck | complex workflows with clear stages and verification |

---

## 8) Case Studies (Production Scenarios)

Each case study is summarized here and expanded in `case_studies/`.

### Case Study 1: Multi-Agent Incident Response (Operations)

**Scenario:** During an outage, you want an assistant that can:

- gather signals (metrics, logs)
- propose hypotheses
- suggest mitigations
- draft a status update

Why multi-agent helps:

- different roles require different constraints (read-only vs privileged actions)
- you can separate "analysis" from "execution" and enforce approvals for writes

Recommended agents:

- **investigator (read-only):** query logs/metrics/runbooks
- **mitigator (write-gated):** propose actions behind approvals
- **communicator (output-limited):** draft human-facing updates

Critical guardrails:

- never allow autonomous mitigation
- all write actions go through a supervisor queue
- strict timeouts and bounded retries (during incidents, latency matters)

Operational telemetry to require:

- subtask routing decisions (subtask -> agent_name)
- tool call durations and status
- approvals requested/approved/denied
- retry counts by tool and agent

### Case Study 2: Developer Workflow Assistant (Multi-Agent PR Bot)

**Scenario:** An internal coding assistant prepares a change:

- research codebase patterns
- implement code
- run tests and lint
- open a PR with evidence

Why multi-agent helps:

- separate creative coding from strict verification
- apply different tool permissions per role (read vs write)

Recommended agents:

- **planner:** break down tasks and define acceptance criteria
- **implementer:** generate code changes
- **verifier:** run tests, check formatting, summarize evidence

Critical guardrails:

- verifier must run deterministic checks (tests, type checks)
- implementer cannot merge; PR requires human approval

Recommended artifacts:

- execution trace attached to the PR (commands run, tests passed)
- policy config version used for the run (tools allowlist and budgets)
- "why" summary (trade-offs and assumptions)

### Mini-case: Routing correctness drift

**Scenario:** A router starts sending "verification" tasks to the writing agent because of keyword overlap ("summary").

Mitigation:

- add deterministic routing rules for critical task types
- add a verifier stage that checks outputs against completion criteria
- build unit tests for routing (given task X, route to agent Y)

The lesson: routing is product logic and must be tested like any other logic.

### Multi-agent failure mode checklist (quick review)

Use this checklist when a multi-agent system behaves unexpectedly:

1. **Wrong agent routed:** Does the routing score/explanation match the task?
2. **Subtasks too broad:** Did decomposition create subtasks that are not independently solvable?
3. **Policy mismatch:** Are per-agent tool allowlists and budgets consistent with the workflow tier?
4. **Missing verification:** Is there a verifier stage for evidence and completion criteria?
5. **Coordination loops:** Are stop conditions enforced (max subtasks, retries, time)?
6. **Evidence loss:** Are tool outputs and citations referenced (not just narrated)?
7. **Shared memory contamination:** Are notes vs facts separated with provenance?
8. **Dependency overload:** Did parallelism increase tool failures (bulkheads missing)?

Most production issues will map to one of these. Fixing them is usually architecture and policy work, not prompt tweaking.

---

## 9) One-Page Takeaway (Summary)

### What to remember

- Multi-agent systems exist to manage context, skills, permissions, and throughput ceilings.
- More agents increases both capability and risk; traceability and guardrails must scale with it.
- Start with router + decomposition; evolve to hierarchical designs as needed.
- Treat capabilities as permissions, not labels.
- Make stop conditions explicit, or multi-agent systems will run away in cost and complexity.

### Minimal production checklist (multi-agent)

- [ ] Clear reason multi-agent is required (documented)
- [ ] Specialist roles and boundaries defined (tools, budgets, policies)
- [ ] Orchestrator enforces guardrails at delegation boundaries
- [ ] Traceability: subtask routing decisions and tool calls are logged/traced
- [ ] Stop conditions: max subtasks, max tool calls, max time, bounded retries
- [ ] Verification stage exists (tests, schemas, constraints)

### Suggested next steps

- Run Lab 8 and extend routing to include load balancing and fallback routing.
- Add structured results (answer + evidence + assumptions) to each specialist.
- Write an ADR documenting the chosen multi-agent pattern and trade-offs.

### Evidence artifacts (what to produce)

- A routing test suite: task -> expected agent, including at least one "routing drift" regression.
- A trace example for one request_id showing subtask routing decisions and tool durations.
- A verifier report for one workflow (what checks ran, what failed, and why).
- A short "role boundary" doc listing each agent, its tool allowlist, and its budgets.

Optional but high value:

- A case study write-up describing one incident (real or simulated) and how traceability and stop conditions helped.

These artifacts are what make multi-agent systems teachable and operable. Without them, teams cannot debug coordination failures, and multi-agent turns into "it did something weird" folklore.

A useful practice is to run a short "multi-agent postmortem" even for successful demos:

- Did routing match your mental model?
- Did any agent exceed budgets or require retries?
- Was evidence preserved and linked (tool refs, doc IDs)?
- Could a reviewer reproduce the run from the trace?

This turns multi-agent from a novelty into an engineering discipline.

Finally, remember that multi-agent is not a destination. It is a tool. Many teams succeed with a small number of agents (often 2-4) plus strong verification. The simplest system that meets the objective is usually the most reliable system.

If you take only one operational lesson from this chapter, take this one: invest in traceability and verification before you invest in more agents. The quality ceiling for "multi-agent without traces" is low, and the incident cost is high.

When you can replay a request end-to-end from a single request_id, multi-agent becomes a system you can trust.

That is the Level 3 bar for multi-agent production readiness.
