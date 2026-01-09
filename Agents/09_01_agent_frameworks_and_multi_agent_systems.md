[Previous](09_00_current_trends_and_patterns.md) | [Next](09_02_tool_use_computer_control_autonomous_workflows.md)

# Agent Frameworks and Multi-Agent Systems  

## Table of Contents

- [**9.1 Agent Frameworks & Multi‑Agent Systems**](#91-agent-frameworks-multiagent-systems)
- [1. What is an “agent framework”?](#1-what-is-an-agent-framework)
  - [What frameworks should not do](#what-frameworks-should-not-do)
- [2. Why frameworks are trending now](#2-why-frameworks-are-trending-now)
- [3. Categories of agent frameworks (practical taxonomy)](#3-categories-of-agent-frameworks-practical-taxonomy)
  - [3.1 Chain / pipeline frameworks](#31-chain-pipeline-frameworks)
  - [3.2 Graph / workflow frameworks](#32-graph-workflow-frameworks)
  - [3.3 Multi-agent coordination frameworks](#33-multi-agent-coordination-frameworks)
  - [3.4 Tool-protocol ecosystems](#34-tool-protocol-ecosystems)
- [4. Multi-agent systems: what they really are](#4-multi-agent-systems-what-they-really-are)
  - [A simple mental model](#a-simple-mental-model)
- [5. When to use multi-agent systems](#5-when-to-use-multi-agent-systems)
  - [Use multi-agent when](#use-multi-agent-when)
  - [Avoid multi-agent when](#avoid-multi-agent-when)
- [6. Common multi-agent patterns](#6-common-multi-agent-patterns)
  - [6.1 Planner–Executor–Critic](#61-plannerexecutorcritic)
  - [6.2 Coordinator–Worker (hub-and-spoke)](#62-coordinatorworker-hub-and-spoke)
  - [6.3 Debate / consensus](#63-debate-consensus)
  - [6.4 Specialist tool agents](#64-specialist-tool-agents)
- [7. Coordination design: make it explicit](#7-coordination-design-make-it-explicit)
  - [7.1 Define interfaces (contracts)](#71-define-interfaces-contracts)
  - [7.2 Shared state vs isolated state](#72-shared-state-vs-isolated-state)
  - [7.3 Termination conditions](#73-termination-conditions)
- [8. Safety and governance in multi-agent systems](#8-safety-and-governance-in-multi-agent-systems)
- [9. Observability: the difference between “cool” and “operational”](#9-observability-the-difference-between-cool-and-operational)
- [10. Minimal reference architecture](#10-minimal-reference-architecture)
- [11. Practical adoption strategy](#11-practical-adoption-strategy)
- [12. Summary](#12-summary)


## **9.1 Agent Frameworks & Multi‑Agent Systems**

Agent frameworks are becoming the “application frameworks” of the agent era: they standardize **orchestration, tool calling, memory, and observability** so teams don’t rebuild the same infrastructure repeatedly. In parallel, multi‑agent systems are gaining adoption because they mirror how humans solve complex work: **specialize, coordinate, verify**.

This chapter explains:
- what agent frameworks do (and don’t),
- when multi‑agent systems are worth the complexity,
- and practical patterns to build them safely.

---

## 1. What is an “agent framework”?

An agent framework is typically a library/runtime that provides building blocks for:

- **Workflows**: chains, graphs, state machines
- **Tool interfaces**: schemas, routing, retries
- **Memory**: session state, long‑term stores, RAG integration
- **Policies**: allow/deny rules, approvals, safety tiers
- **Observability**: tracing, logs, cost accounting

### What frameworks should not do
A framework should not replace:
- your RBAC/ABAC model
- your tool gateway enforcement
- your audit/compliance requirements

In production, **your orchestrator and policy layer remains the source of truth** — frameworks accelerate implementation.

---

## 2. Why frameworks are trending now

As teams moved from “prompt demos” to “agent products,” the pain shifted to:
- workflow reliability
- tool safety
- versioning + rollouts
- tracing and replay
- evaluation and regression testing

Frameworks exist because most agent failures are **systems failures**, not “model failures.”

---

## 3. Categories of agent frameworks (practical taxonomy)

### 3.1 Chain / pipeline frameworks
Best for linear tasks:
- document QA
- summarization pipelines
- simple tool usage

Strengths:
- fast to build
- easy mental model

Limitations:
- branching and retries get messy

### 3.2 Graph / workflow frameworks
Best for real-world robustness:
- branching
- parallel tool calls
- fallbacks
- human approval gates

Strengths:
- production-friendly control
- explicit state transitions

Limitations:
- more design upfront

### 3.3 Multi-agent coordination frameworks
Best for complex tasks requiring specialization:
- research + synthesis
- incident response
- multi-system investigations

Strengths:
- specialization and verification
- composable roles

Limitations:
- cost and coordination overhead

### 3.4 Tool-protocol ecosystems
The modern trend is standardizing tool interoperability:
- consistent schemas
- discoverable tool catalogs
- shared gateway enforcement

This is where “tool ecosystems” become platform assets.

---

## 4. Multi-agent systems: what they really are

A multi-agent system is not “multiple chatbots.”

It is a coordinated set of specialized components (agents) with:
- defined roles
- a shared protocol
- handoff rules
- termination conditions

### A simple mental model

- **Coordinator**: decides who does what
- **Workers**: do specialized tasks (retrieve, execute tools, summarize)
- **Verifier**: checks correctness and policy compliance

---

## 5. When to use multi-agent systems

### Use multi-agent when
- the task decomposes naturally (research → execution → verification)
- you need independent checks (reduce hallucinations)
- tool-space is large and specialization improves accuracy
- tasks involve parallel work (multiple data sources)

### Avoid multi-agent when
- the task is mostly informational and single-pass
- tool actions are trivial
- you’re cost-sensitive and volume is high
- you can achieve reliability via **Plan → Verify → Refine** with one agent

**Rule of thumb:** Start single-agent + verifier. Add multi-agent only when the decomposition clearly improves outcomes.

---

## 6. Common multi-agent patterns

### 6.1 Planner–Executor–Critic
- **Planner**: produces structured plan
- **Executor**: runs tools, gathers evidence
- **Critic**: verifies claims, checks constraints

Benefits:
- separation of concerns
- strong reliability improvements

### 6.2 Coordinator–Worker (hub-and-spoke)
- Coordinator assigns subtasks to workers
- Workers return artifacts
- Coordinator composes final response

Benefits:
- scalable task decomposition
- supports parallelism

### 6.3 Debate / consensus
- multiple agents propose solutions
- a judge/verifier selects best

Use carefully:
- can increase cost without improving quality
- best used with strong evidence requirements

### 6.4 Specialist tool agents
Create agents specialized by tool domain:
- “Log Analyst Agent”
- “Metrics Agent”
- “Database Query Agent”
- “Policy/Compliance Agent”

This scales when tool ecosystems become large.

---

## 7. Coordination design: make it explicit

Multi-agent success depends on protocol design.

### 7.1 Define interfaces (contracts)
Each agent should accept/return structured objects:

- task request schema
- expected output schema
- evidence references
- confidence/unknown states

### 7.2 Shared state vs isolated state

- **Shared state**: faster coordination, but risk of contamination
- **Isolated state**: safer; coordinator merges results

Best practice:
- workers operate mostly isolated
- coordinator merges only validated artifacts

### 7.3 Termination conditions
Always define:
- max turns per agent
- max total tool calls
- stop reasons

Without this, multi-agent systems can loop indefinitely.

---

## 8. Safety and governance in multi-agent systems

Multi-agent increases blast radius because more components can attempt actions.

Key safeguards:

- **Central tool gateway** (single enforcement point)
- **Uniform policy engine** (same rules apply to all agents)
- **Role-based tool allow-lists** (workers often read-only)
- **Approval gates** for write actions
- **Budget controls** across the whole run (not per agent)

**Critical rule:** Policies must not be “per-agent prompts.” Policies must be enforced by the system.

---

## 9. Observability: the difference between “cool” and “operational”

For multi-agent systems, you need:
- trace_id across all agents
- spans per agent and per tool call
- per-agent cost and latency
- artifact logs (plans, evidence ids, decisions)

A useful view is a “run timeline”:
- who acted
- what tool they called
- what evidence they returned
- which verification passed/failed

---

## 10. Minimal reference architecture

```text
Client
  → Orchestrator/Coordinator
      → Worker Agent A (retrieval)
      → Worker Agent B (tools)
      → Worker Agent C (summarization)
      → Verifier/Critic
  → Tool Gateway (shared)
  → RAG Service (shared)
  → State Store (shared)
  → Observability (shared)
```

---

## 11. Practical adoption strategy

A safe adoption path:

1. **Single-agent + strong tool gateway**
2. Add **verifier step** (rules first, model critic optional)
3. Convert linear flows into **workflow graphs**
4. Add a **second specialized agent** only when needed
5. Expand into multi-agent roles with explicit contracts and budgets

---

## 12. Summary

Agent frameworks and multi-agent systems are trending because they address the real problems:
- workflow reliability
- tool safety
- cost control
- observability

Multi-agent architectures can improve robustness, but only when:
- roles are explicit,
- policies are centrally enforced,
- and execution is bounded and observable.

Next: **09_02_tool_use_computer_control_autonomous_workflows.md**

[Previous](09_00_current_trends_and_patterns.md) | [Next](09_02_tool_use_computer_control_autonomous_workflows.md)
