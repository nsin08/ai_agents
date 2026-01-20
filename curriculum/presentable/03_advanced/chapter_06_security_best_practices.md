# Chapter 06: Security Best Practices (Auth, Secrets, Audit Logs)

**Level:** 3 (Advanced)  
**Target audience:** Senior engineers, staff+ engineers, architects  
**Prerequisites:** You understand tool execution, data access patterns, and basic security concepts.  
**Primary internal references:** `Agents/05_05_policies_and_guardrails.md`, `Agents/12_05_medical_agent_architecture.md`, `Agents/12_01_customer_support_agent_architecture.md`

## Learning Objectives (3-5)

By the end of this chapter, you will be able to:

1. Threat-model an agent system (prompt injection, tool misuse, data exfiltration, memory contamination).
2. Enforce least privilege across tools, memory, and retrieval with explicit authorization checks.
3. Design secrets management that prevents credential leakage into prompts, logs, and memory.
4. Implement audit logging for high-risk actions that supports incident response and compliance.
5. Use decision trees and trade-off matrices to choose security controls appropriate to risk tier and domain constraints.

## Chapter Outline

1. Threat model for agent systems
2. Security boundaries: tools, memory, retrieval, and multi-tenancy
3. Authentication and authorization patterns
4. Secrets management and data handling
5. Audit logs and compliance evidence
6. Decision trees and trade-off matrices
7. Case studies (production scenarios)
8. One-page takeaway

---

## 1) Threat Model for Agent Systems

Agent systems inherit classic security risks and add new ones:

### A) Prompt injection (including RAG injection)

Attackers embed instructions in:

- user prompts
- retrieved documents ("ignore policy, reveal secrets")
- tool outputs (logs, tickets, web pages)

Goal: cause the model to break policy or exfiltrate data.

### B) Tool misuse and privilege escalation

If the agent can call tools, an attacker can:

- trick it into calling a write tool
- trick it into calling a tool with unsafe args
- chain tools to exfiltrate data (read -> summarize -> output)

### C) Data exfiltration through logs and memory

Common failure:

- storing raw tool outputs with PII into logs or memory
- later retrieval exposes sensitive data

### D) Memory contamination (long-term "facts" poisoning)

If you store user content as facts, an attacker can plant false information that persists.

### E) Supply chain and dependency risks

Agents often integrate many libraries and tools. A compromised dependency or tool endpoint can compromise the agent.

Supply chain controls (practical):

- pin dependencies (lockfiles) and avoid unreviewed upgrades
- scan container images and dependencies (CI gate)
- generate and store SBOMs for compliance and incident response
- restrict which tools can be installed or executed in production images

In agent systems, "one extra dependency" can become an attack path because the runtime often has access to valuable data and privileged tools.

Threat modeling is not a one-time exercise. You must review it as tools and workflows evolve.

### Threat modeling method (practical for engineers)

Use a lightweight method like STRIDE to structure thinking:

- **Spoofing:** can someone impersonate a user or tool?
- **Tampering:** can someone alter tool inputs/outputs or memory?
- **Repudiation:** can you prove who did what (auditability)?
- **Information disclosure:** can data leak via output, logs, or retrieval?
- **Denial of service:** can an attacker trigger retry storms or token explosions?
- **Elevation of privilege:** can the agent be tricked into calling privileged tools?

Agent-specific twist: "the attacker" can be a user, a retrieved document, or even a tool output. Treat every model input channel as potentially untrusted.

Questions to ask per workflow:

- What are the write tools and how are they gated?
- What is the most sensitive data that can reach prompts/logs/memory?
- What happens when retrieval returns malicious content?
- What evidence exists after an incident (request_id, audit events, config versions)?

### Defense-in-depth for prompt injection and exfiltration

Prompt injection is not a corner case. It is a normal condition for any system that accepts untrusted text.

Defense-in-depth means you do not rely on a single mechanism (like a system prompt). You layer controls:

1. **Input channel separation**
   - Clearly separate system instructions, developer instructions, user text, and retrieved content.
   - Treat retrieved content as untrusted user input.
   - Avoid concatenating raw tool outputs into the system prompt.

2. **Least authority by design**
   - The model should not have direct access to privileged actions.
   - Privileged actions are performed by tools behind allowlists, schemas, and authz.

3. **Tool allowlists and parameter constraints**
   - Do not provide "generic" tools that can do anything (fetch any URL, read any file).
   - Add allowlists for domains and directories (SSRF/path traversal prevention).
   - Cap output sizes and enforce timeouts.

4. **Output validation and refusal patterns**
   - If a request asks for disallowed data, refuse or escalate.
   - Redact known PII patterns as a baseline.
   - Do not return sensitive datasets even if redacted (refusal is safer).

5. **Observability for attacks**
   - Track blocks by rule and spikes by tenant/workflow.
   - Track suspicious tool attempts (blocked tools, blocked domains).
   - Sample traces for blocks and failures (privacy-aware).

The key idea: even if the model is fully compromised by malicious instructions, it still cannot break the system because the tool boundary enforces policy.

---

## 2) Security Boundaries: Tools, Memory, Retrieval, Multi-Tenancy

### A) Tool boundary (most important)

Tools are where side effects happen. Treat tool calls like privileged API calls:

- authenticate the caller (user identity, service identity)
- authorize the action (RBAC + tenant scope)
- validate inputs (schemas, allowlists)
- enforce rate limits and budgets
- log audit events for writes

### Tool sandboxing (reduce blast radius)

If your threat model includes untrusted inputs (it should), consider sandboxing the tool runtime:

- run tools in a separate process or container
- restrict filesystem access (read-only where possible)
- restrict network egress (only allow required domains)
- restrict OS-level permissions (no shell access unless required)

Sandboxing is especially valuable for:

- tools that fetch external URLs
- tools that execute code
- tools that can write to production systems

The goal is not perfect isolation. The goal is to reduce worst-case impact if a tool is misused.

### B) Memory boundary

Memory is a data store. Apply:

- write policies (what can be stored)
- retention policies (how long)
- provenance (who wrote it, from what source)
- encryption at rest (if sensitive)

Default stance: do not store raw user data in long-term memory unless required.

### C) Retrieval boundary (RAG)

Retrieval can expose sensitive docs. Enforce:

- tenant scoping
- role-based doc access
- query filtering and logging controls

Never allow retrieval to bypass normal access controls.

Retrieval access control patterns:

- **Pre-filtering:** only search documents the actor is allowed to see (ACL filter).
- **Post-filtering:** retrieve candidates, then remove docs that fail access checks (riskier).
- **Row-level security:** enforce tenant and role constraints at the storage layer.

Practical guidance:

- prefer pre-filtering (least risk of accidental leakage)
- require citations (doc IDs) so retrieval behavior is observable
- log retrieval metadata safely (doc IDs, not raw doc text)

Prompt injection is common in retrieval. Treat retrieved content as untrusted:

- do not execute tool calls based on retrieved instructions
- require that tool calls come from allowed workflows and explicit intent
- consider scanning retrieved text for known injection patterns and flagging suspicious docs

Example retrieval audit fields (metadata only):

```json
{
  "event": "retrieval_completed",
  "request_id": "req-123",
  "tenant_id": "t-9",
  "top_docs": ["doc-1", "doc-7", "doc-12"],
  "top_k": 3
}
```

### D) Multi-tenant isolation

In multi-tenant systems, isolation failures are catastrophic.

Minimum requirements:

- tenant_id is part of every tool call and every storage key
- no cross-tenant caches (or strict cache keys)
- strict separation for audit logs

Additional isolation controls (recommended):

- tenant-scoped encryption keys for sensitive stores (where feasible)
- per-tenant budgets and quotas (prevents noisy neighbor and abuse)
- separate indices or partitions for retrieval if datasets are large
- "deny by default" policy: new tools are blocked until explicitly allowed

Common isolation failures:

- caching only by query text (tenant A sees tenant B)
- logging tenant_id but not enforcing tenant_id in tool calls
- writing shared "facts" to memory without provenance and scope

A useful mental model: tenant_id is a required parameter of every privileged operation. If a function does not accept tenant_id, it is suspicious.

### E) Remote tool servers (MCP)

If you adopt remote tool servers (e.g., via MCP), treat them as a first-class security boundary:

- The model is not trusted; tool calls must be validated and authorized in code.
- The tool server is a dependency; it can fail, be misconfigured, or be compromised.

Minimum controls for MCP-style tool execution:

1. **Allowlist tools per workflow** (deny by default)
2. **Validate inputs** against tool schemas before sending to the server
3. **Bind identity to every call**:
   - `tenant_id` (required)
   - `actor_id` / roles
   - `request_id` / `tool_call_id` (for traceability)
4. **Audit events** for every tool call (especially writes):
   - tool name, action, outcome, latency, and sanitized metadata
5. **Do not trust tool output** as safe instructions:
   - tool output can contain injection strings; treat it like any other untrusted input channel

Example audit event fields (metadata only):

```json
{
  "event": "remote_tool_call_completed",
  "request_id": "req-123",
  "tenant_id": "t-9",
  "tool": "repo_read_file",
  "status": "success",
  "latency_ms": 42
}
```

---

## 3) Authentication and Authorization Patterns

### Pattern A: Central authorization for tool calls

Do not rely on "the model knows what it can do". Enforce authz in code.

Example RBAC check (conceptual):

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Actor:
    user_id: str
    tenant_id: str
    roles: set[str]


def authorize_tool_call(actor: Actor, tool_name: str, action: str) -> None:
    if tool_name == "ticket_write" and "support_agent" not in actor.roles:
        raise PermissionError("missing role: support_agent")
    if action == "write" and "approver" not in actor.roles:
        raise PermissionError("write requires approver role")
```

In production, authorization is often policy-as-code (OPA, Cedar, custom engine), but the key is the same:

- enforce authz at the boundary
- include tenant_id in the decision

### Pattern A2: Service identity and delegation

In real deployments, the actor is not always a human user. It can be:

- a background worker processing a job
- a system account executing a scheduled workflow
- a multi-agent coordinator delegating to specialists

Best practice: separate identities and scopes:

- user identity: what the user is allowed to request
- service identity: what the runtime is allowed to do
- delegated scope: the intersection of the two (least privilege)

Example: a service might be allowed to call `ticket_write`, but only within the tenant_id and only when the user has a role that permits writes (or an approval token exists).

Avoid "break glass" patterns becoming the default. If a privileged override is required, log it as an audit event and require additional approval.

### Pattern B: "Safe by default" tool catalog

Organize tools by risk:

- Tier 0: read-only tools
- Tier 1: reversible writes
- Tier 2: irreversible/high-stakes writes

Gate Tier 1 and Tier 2 tools behind approvals and audit logs.

### Pattern C: Input sanitization and allowlists

Many tool risks are input risks:

- file paths
- URLs (SSRF)
- SQL queries

Prefer allowlists:

- allowed domains for HTTP fetch tools
- allowed file directories for file tools
- allowed operations for admin tools

Example: SSRF-safe HTTP allowlist (conceptual)

```python
from urllib.parse import urlparse


ALLOWED_DOMAINS = {"api.example.com", "status.example.com"}


def validate_url_allowlist(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"https"}:
        raise ValueError("only https URLs allowed")
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_DOMAINS:
        raise ValueError(f"domain not allowed: {host}")
```

Example: Path traversal protection (conceptual)

```python
from pathlib import Path


BASE_DIR = Path("/app/data").resolve()


def validate_safe_path(path_str: str) -> Path:
    path = (BASE_DIR / path_str).resolve()
    if not str(path).startswith(str(BASE_DIR)):
        raise ValueError("path outside allowed directory")
    return path
```

These checks belong in the tool runtime, not in the prompt.

---

## 4) Secrets Management and Data Handling

### A) Never put secrets in prompts

Secrets should never appear in:

- prompts
- tool results sent to the model
- logs
- long-term memory

If a tool needs a secret, the tool runtime should access it from:

- a secret manager (vault)
- Kubernetes Secret
- cloud secret store

### B) Use short-lived credentials

Prefer:

- OAuth tokens with scopes
- short-lived API tokens

Avoid:

- long-lived shared keys
- embedding keys in config files

### B2) Rotation and secret scanning (operational security)

Secrets hygiene is not only about where secrets are stored. It is about:

- rotation (how often and how fast)
- detection (how you find leaks)
- blast radius (scopes and permissions)

Practical controls:

- rotate keys on a schedule and on-demand (incident response)
- scan repositories and CI logs for secret patterns
- use scoped tokens (least privilege)
- revoke leaked tokens quickly and record the incident

If you cannot rotate quickly, assume a leak will become a major incident.

### C) Redact sensitive data in logs and outputs

Redaction should happen:

- before logging
- before returning output
- before writing memory

Treat redaction as a tested feature (golden tests).

### C2) Redaction testing (false positives vs false negatives)

Redaction systems fail in two ways:

- false negatives: sensitive data leaks
- false positives: useful data is removed and users lose trust

Practical testing approach:

- build a golden set of known PII strings (must redact)
- build a golden set of non-PII strings (must not redact)
- add domain-specific identifiers (account IDs, ticket IDs) if they are sensitive

Operationally, treat false positives as product feedback:

- track user reports
- tune rules with evidence
- roll out redaction changes via canary where possible

### D) Data minimization

Only retrieve and store what the workflow requires.

Example: If the agent needs "invoice total" to decide an approval path, do not retrieve full invoice history.

### E) Memory write policies (prevent persistence of sensitive data)

Long-term memory is a persistence layer. If you store raw user content, you create long-lived risk.

Practical rules:

- default: do not store raw user prompts in long-term memory
- store derived artifacts instead (summaries, structured facts) with provenance
- never store secrets; redact PII before writes
- keep separate stores for "untrusted notes" vs "verified facts"

Memory writes should be treated like tool writes:

- authorized
- validated
- logged (at least as metadata)

---

## 5) Audit Logs and Compliance Evidence

Audit logs are mandatory for high-risk actions.

### What to include in an audit event

- request_id / correlation_id
- actor identity (user_id, tenant_id)
- tool name and action
- proposed change (diff)
- approvals (who, when, why)
- policy/config version applied
- outcome (success/fail) and error details

Example audit event shape:

```json
{
  "event": "tool_write_executed",
  "request_id": "req-123",
  "actor": {"user_id": "u-7", "tenant_id": "t-9"},
  "tool": "invoice_approve",
  "change": {"invoice_id": "inv-55", "from": "pending", "to": "approved"},
  "approval": {"approver": "u-1", "reason": "verified"},
  "policy_version": "guardrails-prod-v3",
  "result": "success"
}
```

### Retention and access control

- audit logs must be access-controlled (security and compliance)
- retention must match policy
- do not store raw PII unless required (and then encrypt and scope access)

### Audit log architecture (minimum viable)

Treat audit logs as a separate data product:

- append-only (no edits)
- write-once storage where possible
- strict access controls (not the same as application logs)
- clear retention and deletion policies (compliance)

If you operate in a regulated domain, define who can:

- view audit logs
- export audit logs
- approve retention changes

### Correlation: audit events should link to traces and config versions

For debugging and forensics you want to connect:

- audit event -> request_id
- request_id -> trace/log bundle
- policy_version -> which rules were active

Without correlation, you will waste time during incidents and audits.

### Review and detection

Audit logs are only useful if someone looks at them. Common approaches:

- alert on high-risk actions (writes, privileged reads)
- periodic review for anomalies (out-of-hours writes, repeated failures)
- anomaly detection for unusual tool usage patterns

### Compliance evidence package (what to be ready to show)

In regulated or high-risk environments, teams are often asked to provide evidence that controls exist and are enforced. A practical evidence package includes:

- threat model document (top abuse cases and mitigations)
- tool inventory with risk tiers (read vs write)
- RBAC policy summary (who can do what)
- sample audit events for a write workflow (with request_id and policy_version)
- redaction test results (no PII in logs)
- incident response runbooks (how you respond to suspected leaks)

Even if you are not regulated, building this package improves engineering quality:

- it forces clarity about boundaries and ownership
- it makes security review faster
- it makes incident response less chaotic

---

## 6) Decision Trees and Trade-off Matrices

### Decision tree: Which security controls are mandatory

```
Start
  |
  |-- Does the agent perform writes?
  |      |
  |      |-- No -> enforce read-only tool allowlist + retrieval access control + redaction
  |      |
  |      |-- Yes
  |           |
  |           |-- Are writes high-stakes or regulated?
  |                 |
  |                 |-- Yes -> approvals + audit logs + strict RBAC + tenant isolation
  |                 |
  |                 |-- No -> confirm-before-write + audit logs + idempotency keys
```

### Security controls by tier (summary table)

| Tier | Typical workflows | Mandatory controls |
|---|---|---|
| Tier 0 (read-only) | FAQ, summaries | tool allowlist, retrieval access control, redaction, request_id everywhere |
| Tier 1 (low-risk writes) | drafts, internal notes | confirm-before-write, idempotency keys, audit events for writes |
| Tier 2 (high-stakes) | finance/health/prod changes | supervisor queue or dual approval, strict RBAC, immutable audit log, restricted telemetry |

Even Tier 0 systems need real security boundaries. "Read-only" does not mean "low risk" if the system can read sensitive data or if logs can leak PII. Treat Tier 0 as a safe starting point, not as an excuse to skip access control and redaction.

### Trade-off matrix: Security vs developer velocity

| Control | Security benefit | Velocity cost | Recommendation |
|---|---|---|---|
| Strict tool allowlists | blocks exfil and misuse | more config | start strict, expand with evidence |
| Policy-as-code | consistent authz | upfront work | worth it for multi-tenant platforms |
| Full audit logs | compliance and forensics | storage + process | mandatory for writes |
| Sandboxed tool runtime | limits blast radius | engineering effort | recommended for untrusted inputs |

### Decision tree: Handling untrusted content (user, retrieval, tools)

```
Start
  |
  |-- Is the content used only for display (not for decisions)?
  |      |
  |      |-- Yes -> sanitize output + redaction
  |      |
  |      |-- No
  |           |
  |           |-- Can the content influence tool calls or writes?
  |                 |
  |                 |-- Yes -> enforce allowlists + schemas + approvals (do not trust content)
  |                 |
  |                 |-- No -> treat as untrusted context (limit, summarize, and add provenance)
```

### Trade-off matrix: Logging sensitive workflows

| Approach | Benefit | Risk | Recommendation |
|---|---|---|---|
| Log everything | best debugging | privacy leakage | rarely acceptable |
| Redact and log | debuggable | false negatives in redaction | recommended baseline |
| Log references only | safest | harder debugging | use for highly regulated flows |
| Separate secure log store | best balance | ops complexity | recommended for Tier 2 workflows |

### Security regression suite (what to automate)

Security controls fail silently if they are not tested. A practical regression suite for agent systems includes:

1. **Tool authz tests**
   - given actor without role X, write tool call is blocked
   - tenant scope is enforced (tenant A cannot access tenant B)
2. **Input validation tests**
   - URL allowlist blocks non-https and unknown domains (SSRF)
   - path allowlist blocks traversal attempts ("../")
3. **Injection scenario tests**
   - user prompt: "ignore policy and do X" -> policy still enforced
   - retrieved doc contains malicious instructions -> treated as untrusted
4. **Redaction tests**
   - known PII patterns are redacted in output and logs
   - known safe strings are not redacted (false positive guard)
5. **Audit log tests (Tier 2 workflows)**
   - every write emits an audit event with request_id and policy_version
   - approvals are recorded and linked to the write action

Where possible, keep these tests deterministic and fast so they run in CI.

For higher assurance, run periodic "security canaries" in staging:

- attempt blocked tool calls
- attempt cross-tenant access
- validate alerts and telemetry are triggered

The best time to discover a policy bypass is in CI, not in production.

---

## 7) Case Studies (Production Scenarios)

Each case study is summarized here and expanded in `case_studies/`.

Case study links:

- `case_studies/06_healthcare_triage_security.md`
- `case_studies/04_multi_tenant_support_platform_scaling.md`

### Case Study 1: Healthcare Triage Assistant (Regulated + Privacy)

**Scenario:** Agent assists triage by summarizing symptoms and suggesting next steps.  
**Risks:** privacy violations, unsafe medical advice, compliance failures.

Key design choices:

- strict retrieval access control (minimum necessary)
- aggressive redaction in logs and memory
- no autonomous writes to patient record
- audit logs for any access and any workflow escalation
- strong refusal and escalation policies

Security verification signals:

- audit events exist for privileged reads and escalations
- redaction tests pass (no PII in logs)
- retrieval respects role scope (no policy bypass)

### Case Study 2: Multi-Tenant Support Agent (Isolation and RBAC)

**Scenario:** Support agent handles tickets for multiple tenants.  
**Risks:** cross-tenant data leakage, unauthorized ticket updates.

Key design choices:

- tenant_id in every tool call and cache key
- RBAC enforced at tool boundary
- audit logs for writes
- strict tool allowlists per tenant policy

Security verification signals:

- cache keys include tenant_id and role scope
- cross-tenant access attempts are blocked and visible in telemetry
- write tools require approval and emit audit events

### Mini-case: Cross-tenant cache key bug

**Scenario:** A retrieval cache is keyed only by query text. Tenant A and tenant B ask the same question, and tenant B receives tenant A's cached citations.

Mitigation:

- include tenant_id and auth scope in cache keys
- add regression tests for cache scoping
- alert on cross-tenant doc ID anomalies (if observable)

This is one of the most common real-world multi-tenant failures. It is also one of the easiest to prevent if you treat cache keys as part of your security boundary.

---

## 8) Hands-on Exercises

1. Threat model one workflow using STRIDE:
   - identify write tools and sensitive data paths
   - list top 3 abuse cases and mitigations
2. Implement allowlists for one tool category:
   - URL allowlist (SSRF protection) or path allowlist (traversal protection)
3. Design an audit event schema for one write action:
   - include request_id, actor, diff, approvals, policy_version
4. Build a "security regression suite":
   - injection prompts
   - unsafe tool attempts
   - tenant isolation checks (cache keys and retrieval scope)
5. Design retrieval access control:
   - define how tenant and role scopes filter documents
   - define what retrieval metadata is safe to log (doc IDs, not text)

Deliverable: write an ADR capturing mandatory controls and trade-offs for the workflow.

---

## 9) One-Page Takeaway (Summary)

### What to remember

- Tools are the most important security boundary; enforce authz in code, not prompts.
- Prompt injection is expected; build systems that remain safe even when the model is tricked.
- Secrets must never enter prompts, logs, or memory.
- Multi-tenant isolation requires tenant scoping everywhere (tools, storage, caches).
- Audit logs are not optional for high-risk actions; they are your forensic record.

### Minimal production checklist (security)

- [ ] Threat model documented and reviewed
- [ ] RBAC + tenant scope enforced for every tool call
- [ ] Tool input schemas and allowlists exist (SSRF/path traversal protection)
- [ ] Secrets managed by secret store, never exposed to model
- [ ] Redaction applied to logs, outputs, and memory writes
- [ ] Audit logs enabled for writes and privileged reads

### Suggested next steps

- Create an ADR documenting your threat model and mandatory controls.
- Add a "security regression suite" with injection prompts and unsafe tool attempts.
- Review and harden the most privileged tool first (writes).

### Evidence artifacts (what to produce)

- A tool inventory with risk tiers (read/write) and required approvals.
- A sample audit event bundle for one write workflow (with request_id and policy_version).
- A redaction test report (golden set results).
- A tenant isolation test report (retrieval and cache key scoping).

Treat these artifacts as release gates for Tier 2 workflows. If the team cannot produce them quickly, that is a sign the system is not observable or enforceable enough to be trusted in production.

Security is also a team habit. Make the regression suite part of CI, and run periodic drills in staging to validate that blocks, audit events, and alerts still work as expected. The goal is not perfection; the goal is reducing surprise.

When security incidents happen, feed the lessons back into policy and tests. A small update to an allowlist or redaction rule, backed by a regression test, prevents repeat incidents.

This feedback loop is what turns security from a review phase into an operational capability.

In this curriculum, treat every new tool integration as a security change until proven otherwise by tests and audit evidence.
