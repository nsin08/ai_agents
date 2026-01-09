[Previous](05_02_llms_and_reasoning_modes.md) | [Next](05_04_0_memory_and_rag.md)

# Tools and APIs for Agents  

## Table of Contents

- [**5.3 Tools & APIs — The Action Layer of an AI Agent**](#53-tools-apis-the-action-layer-of-an-ai-agent)
- [1. What are tools in an agentic system?](#1-what-are-tools-in-an-agentic-system)
- [2. Why tools are essential](#2-why-tools-are-essential)
- [3. Categories of tools in modern agents](#3-categories-of-tools-in-modern-agents)
  - [3.1 Information retrieval tools](#31-information-retrieval-tools)
  - [3.2 System access tools](#32-system-access-tools)
  - [3.3 Engineering & DevOps tools](#33-engineering-devops-tools)
  - [3.4 Document processing tools](#34-document-processing-tools)
  - [3.5 Computational tools](#35-computational-tools)
  - [3.6 Workflow / action tools](#36-workflow-action-tools)
- [4. Designing tools for agents](#4-designing-tools-for-agents)
  - [4.1 Deterministic outputs](#41-deterministic-outputs)
  - [4.2 Fail gracefully](#42-fail-gracefully)
  - [4.3 Avoid hidden state](#43-avoid-hidden-state)
  - [4.4 Clear permission boundaries](#44-clear-permission-boundaries)
- [5. How the LLM uses tools](#5-how-the-llm-uses-tools)
- [6. Tool output interpretation](#6-tool-output-interpretation)
- [7. Safety considerations](#7-safety-considerations)
  - [Hard limits](#hard-limits)
  - [Authorization](#authorization)
  - [Sandboxing](#sandboxing)
  - [Human approval](#human-approval)
- [8. Best practices](#8-best-practices)
- [9. End-to-end tool interaction flow](#9-end-to-end-tool-interaction-flow)
- [10. Summary](#10-summary)


## **5.3 Tools & APIs — The Action Layer of an AI Agent**

Tools are the **hands** of an AI Agent.
If the LLM is the “brain” and the orchestrator is the “nervous system,” then tools are the **mechanisms through which the agent interacts with the real world**.

Tools allow agents to *do* rather than *describe* — bridging reasoning with execution. This is foundational for real workflows, automation, and enterprise integration.

---

## 1. What are tools in an agentic system?

A **tool** is any callable external capability that an agent can invoke to:

- retrieve structured or unstructured data
- perform computations deterministically
- read/write documents
- call REST/GraphQL APIs
- query databases
- trigger workflows
- modify state in an external system

A well-defined tool has:

- **name**
- **description** (so the model knows when to use it)
- **input schema** (strict)
- **output schema** (strict)
- **side effects** (read vs write)
- **permissions / constraints**

Example tool contract:

```json
{
  "name": "get_order_status",
  "description": "Fetch authoritative order status from the order service.",
  "input_schema": { "order_id": "string" },
  "output_schema": {
    "status": "string",
    "eta": "string",
    "last_updated": "string"
  }
}
```

**Separation of responsibilities:**
- **LLM**: proposes *which tool* to use and *what args* to pass.
- **Orchestrator**: validates, checks permissions, executes.
- **Tool**: performs deterministic work and returns structured output.

---

## 2. Why tools are essential

LLMs cannot reliably:

- fetch live data
- modify records safely
- run strict logic or math
- operate on files (PDF, images, spreadsheets)
- execute multi-step workflows end-to-end

Without tools, an LLM is a text generator.
With tools, an agent becomes a **capability engine** that can:

- ground answers in real data (reduce hallucinations)
- automate operational workflows
- integrate across enterprise systems
- validate outcomes using authoritative sources

---

## 3. Categories of tools in modern agents

### 3.1 Information retrieval tools
Used to ground planning and answers:

- Vector DB / RAG queries
- Knowledge base lookups
- Web search
- Document retrieval APIs

### 3.2 System access tools
Used for structured enterprise connectivity:

- CRM / ERP connectors
- Ticketing systems (ServiceNow, Zendesk, JIRA)
- SQL / NoSQL database connectors
- User profile & authorization
- Inventory or billing APIs

### 3.3 Engineering & DevOps tools
Used for ops automation:

- CI/CD triggers
- Kubernetes interactions (via secure proxy)
- Log retrieval tools
- Monitoring APIs (Prometheus, Datadog, Grafana)
- Code execution sandboxes

### 3.4 Document processing tools
Used for knowledge workflows:

- PDF parsing
- OCR
- Spreadsheet analyzers
- Email/calendar integrations

### 3.5 Computational tools
Used to avoid LLM math failures:

- Python execution
- math solvers
- statistical engines

### 3.6 Workflow / action tools
Tools that modify real-world state:

- create/update tickets
- initiate refunds
- provision accounts
- send notifications
- approve/deny requests

These provide the highest business value — and also the highest risk.

---

## 4. Designing tools for agents

### 4.1 Deterministic outputs
Tools should return consistent results and validate response shapes.

### 4.2 Fail gracefully
Return structured errors so the orchestrator can retry/refine safely:

```json
{
  "error": true,
  "type": "NotFound",
  "message": "Order ID 123 not found"
}
```

### 4.3 Avoid hidden state
Keep state in the orchestrator workflow state or external storage, not inside tools.

### 4.4 Clear permission boundaries
Enforce:
- read vs write separation
- RBAC checks
- tenant isolation
- workflow-level approval gates

---

## 5. How the LLM uses tools

LLMs should output **structured tool call intents**:

```json
{
  "tool_call": {
    "name": "create_support_ticket",
    "arguments": {
      "user_id": "45982",
      "issue_summary": "App crashes on login"
    }
  }
}
```

The orchestrator then:
1. validates schema
2. checks permissions
3. executes tool
4. records outputs in state
5. decides next step (verify/refine/respond)

---

## 6. Tool output interpretation

After execution, the agent must:

- parse tool results
- validate schema and invariants
- detect errors and decide recovery steps
- determine whether more tool calls are required

Some systems use a dedicated **executor model** to interpret large/complex tool outputs.

---

## 7. Safety considerations

### Hard limits
- max tool calls per request
- max retries per tool
- timeouts
- blast-radius limits (e.g., max records affected)

### Authorization
- prevent privilege escalation
- enforce tenant/user isolation
- redact sensitive fields

### Sandboxing
- code execution must run in a sandbox
- restrict network/file access if needed

### Human approval
Require explicit human confirmation for destructive or high-impact operations.

---

## 8. Best practices

- Keep tool APIs small and predictable
- Use strict input/output schemas
- Provide high-quality tool descriptions
- Return consistent error shapes
- Version tools to avoid breaking changes
- Separate read tools from write tools
- Log tool usage for auditability

---

## 9. End-to-end tool interaction flow

```text
LLM → proposes plan
   ↓
LLM → selects tool + arguments
   ↓
Orchestrator → validates + executes tool
   ↓
Tool → returns structured output
   ↓
Orchestrator → verifies correctness
   ↓
LLM → interprets results, plans next step
   ↓
Final output or next tool call
```

---

## 10. Summary

Tools convert reasoning into real actions.
A strong tool layer makes an agent:

- actionable
- grounded
- reliable
- safe
- enterprise-ready

Next: **05_04_0_memory_and_rag.md**

[Previous](05_02_llms_and_reasoning_modes.md) | [Next](05_04_0_memory_and_rag.md)
