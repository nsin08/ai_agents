[Previous](05_04_3_memory_retrieval_policy.md) | [Next](05_06_observability_logging_metrics_tracing.md)

# Policies and Guardrails  

## Table of Contents

- [**5.5 Policies & Guardrails — Safety, Control, and Governance**](#55-policies-guardrails-safety-control-and-governance)
- [1. Why guardrails are first-class components](#1-why-guardrails-are-first-class-components)
- [2. Safety layers (defense in depth)](#2-safety-layers-defense-in-depth)
- [3. Permissioning](#3-permissioning)
  - [3.1 User-level permissions (RBAC/ABAC)](#31-user-level-permissions-rbacabac)
  - [3.2 Workflow-level permissions (policy on the plan)](#32-workflow-level-permissions-policy-on-the-plan)
- [4. Tool gateway enforcement](#4-tool-gateway-enforcement)
  - [4.1 Read vs write separation](#41-read-vs-write-separation)
  - [4.2 Approval gates for high-risk actions](#42-approval-gates-for-high-risk-actions)
- [5. Schema enforcement](#5-schema-enforcement)
  - [5.1 Structured outputs are mandatory](#51-structured-outputs-are-mandatory)
  - [5.2 Output validation is not just “JSON-valid”](#52-output-validation-is-not-just-json-valid)
- [6. Hallucination prevention](#6-hallucination-prevention)
  - [6.1 Grounded answers](#61-grounded-answers)
  - [6.2 “Unknown” is a valid outcome](#62-unknown-is-a-valid-outcome)
  - [6.3 Verification loops (Plan → Act → Verify)](#63-verification-loops-plan-act-verify)
- [7. User-level constraints vs workflow-level constraints](#7-user-level-constraints-vs-workflow-level-constraints)
  - [User-level constraints](#user-level-constraints)
  - [Workflow-level constraints](#workflow-level-constraints)
- [8. Practical guardrail controls](#8-practical-guardrail-controls)
  - [8.1 Budgets and hard limits](#81-budgets-and-hard-limits)
  - [8.2 Rate limiting and backoff](#82-rate-limiting-and-backoff)
  - [8.3 Redaction and data minimization](#83-redaction-and-data-minimization)
  - [8.4 Environment isolation](#84-environment-isolation)
- [9. Compliance considerations](#9-compliance-considerations)
- [10. Example policy rule set (illustrative)](#10-example-policy-rule-set-illustrative)
- [11. Summary](#11-summary)


## **5.5 Policies & Guardrails — Safety, Control, and Governance**

Agents are powerful because they can **act** (via tools) and **persist** (via memory). That is also why they are risky. Policies and guardrails are the components that make agent behavior **bounded, auditable, and production-safe**.

This section covers:
- safety layers (defense-in-depth)
- permissioning (user + workflow)
- schema enforcement
- hallucination prevention
- user-level and workflow-level constraints
- compliance considerations

---

## 1. Why guardrails are first-class components

In an agentic system, the model is not “in charge.” The **orchestrator + policies** are.

Without guardrails, agents can:
- hallucinate actions (tool calls that should not happen)
- exceed access boundaries (cross-tenant / cross-user)
- leak sensitive data (PII/keys/logs)
- loop indefinitely (runaway cost)
- perform harmful changes (destructive operations)

Guardrails turn an LLM from a creative engine into a **reliable system participant**.

---

## 2. Safety layers (defense in depth)

Do not rely on a single safety mechanism. Use layers:

1. **Prompt-level rules** — what the model is allowed to attempt
2. **Schema-level rules** — what the model is allowed to output
3. **Tool gateway rules** — what can be executed (allow-list + validation)
4. **Authorization rules** — who can do what (RBAC/ABAC)
5. **Runtime policies** — limits, approvals, and environment constraints
6. **Observability & audit** — what actually happened

If one layer fails, another catches it.

---

## 3. Permissioning

### 3.1 User-level permissions (RBAC/ABAC)

Controls **who** can do **what**.

Common patterns:
- RBAC roles: `viewer`, `operator`, `admin`, `auditor`
- ABAC attributes: tenant, project, compartment, region, environment

Examples:
- Viewer: read-only tools
- Operator: read + limited write (non-destructive)
- Admin: broad write with approvals
- Auditor: read + export, no changes

**Principle:** least privilege by default.

### 3.2 Workflow-level permissions (policy on the plan)

Controls **what the workflow may do**, independent of the user.

Example: even an admin user may be blocked from destructive actions in a “read-only diagnostic” workflow.

Workflow policies may include:
- allowed tools list
- allowed operations list (`read`, `create`, `update`, `delete`)
- environment scopes (only `staging`)
- approval gates required
- maximum blast radius

---

## 4. Tool gateway enforcement

Never let the model call tools directly.

Use a tool gateway (inside the orchestrator or as a service) that enforces:
- explicit allow-list of tools
- strict argument validation
- permission checks (user + workflow)
- rate limits + timeouts
- dry-run / simulation (when available)

### 4.1 Read vs write separation

Split tools by side effects:
- `get_*` / `list_*` → read-only
- `create_*`, `update_*`, `delete_*` → write

This makes it simple to enforce “read-only mode.”

### 4.2 Approval gates for high-risk actions

Require explicit confirmation for:
- deletes
- bulk updates
- money movement
- permission changes
- production deployments

Typical mechanism:
- agent proposes an “action intent”
- system returns a confirmation prompt to the user
- only after confirmation does the orchestrator execute

---

## 5. Schema enforcement

### 5.1 Structured outputs are mandatory

For agent steps that drive execution (plans, tool calls, decisions), enforce:
- JSON schema / Pydantic
- strict parsing
- rejection on invalid shape

Example: tool-call schema

```json
{
  "type": "object",
  "properties": {
    "tool_call": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "arguments": {"type": "object"}
      },
      "required": ["name", "arguments"]
    }
  },
  "required": ["tool_call"]
}
```

If the model returns invalid JSON, the orchestrator should:
- ask for a corrected output (single retry)
- fall back to a safer mode
- or stop and request clarification

### 5.2 Output validation is not just “JSON-valid”

Validate:
- types
- required fields
- enumerations
- invariants (e.g., `count <= max_allowed`)
- scope constraints (tenant/project/region)

---

## 6. Hallucination prevention

Hallucinations become dangerous when they turn into actions.

### 6.1 Grounded answers
Prefer responses that are:
- tool-verified
- retrieved from RAG with citations (internal citations/links)
- derived from system-of-record data

### 6.2 “Unknown” is a valid outcome
Make it easy for the agent to say:
- “I don’t have enough information”
- “I cannot verify that”

Avoid prompts that force a confident answer.

### 6.3 Verification loops (Plan → Act → Verify)
Use a verifier step that checks:
- does tool output match expectations?
- are constraints satisfied?
- is the goal actually achieved?

If not, refine with new constraints or ask the user.

---

## 7. User-level constraints vs workflow-level constraints

### User-level constraints
Attach to the identity:
- role
- tenant/project scope
- data access (PII/financial)
- write permissions

### Workflow-level constraints
Attach to the execution context:
- read-only mode
- max tool calls
- max retries
- max cost budget
- allowed environments (`dev`, `staging`, `prod`)
- mandatory approvals

**Rule:** enforce both; the stricter one wins.

---

## 8. Practical guardrail controls

### 8.1 Budgets and hard limits

- max reasoning steps / loops
- max tool calls per request
- max tokens / time
- max cost per session

Stops runaway behavior.

### 8.2 Rate limiting and backoff

- per user
- per tenant
- per tool

Prevents cascading failures and cost spikes.

### 8.3 Redaction and data minimization

- redact secrets (keys, tokens)
- minimize PII in prompts and logs
- avoid storing sensitive data in long-term memory

### 8.4 Environment isolation

- separate tools by environment
- separate credentials by environment
- prevent accidental prod actions

---

## 9. Compliance considerations

Depending on domain, you may need:

- **audit trails**: who requested what, what executed, what changed
- **retention policies**: logs/memory retention duration
- **PII handling**: masking, consent, and minimization
- **access reviews**: role assignment governance
- **change approvals**: for sensitive workflows
- **incident response**: rollback and escalation paths

Treat prompts, tool calls, and retrieved data as part of your compliance surface.

---

## 10. Example policy rule set (illustrative)

```yaml
policy:
  mode: read_only
  allowed_tools:
    - list_instances
    - get_instance
    - query_logs
    - query_metrics
  denied_tools:
    - delete_instance
    - update_network
  constraints:
    max_tool_calls: 8
    max_retries_per_tool: 2
    allowed_environments: ["staging"]
  approvals:
    required_for:
      - tool: "update_*"
      - tool: "delete_*"
```

---

## 11. Summary

Policies and guardrails are what make agents safe and reliable.
They enforce:
- permissions (user + workflow)
- schemas and invariants
- grounding and verification
- budgets and limits
- compliance and auditability

Next: **05_06_observability_logging_metrics_tracing.md**

[Previous](05_04_3_memory_retrieval_policy.md) | [Next](05_06_observability_logging_metrics_tracing.md)
