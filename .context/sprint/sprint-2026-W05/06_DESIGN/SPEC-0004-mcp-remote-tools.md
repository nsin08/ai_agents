# SPEC-0004: MCP Remote Tools (Production Profile)

Status: Draft
Date: 2026-01-28
Related ADRs:
- `.context/sprint/sprint-2026-W05/04_DECISIONS/ADR-0005-mcp-support-profile.md`

## Abstract
This spec defines a production remote-tool boundary inspired by MCP concepts. It explains what MCP-like tool servers are, what the system needs from them, how remote tools are discovered and invoked safely, and how to decide which transport/profile to support based on deployment scenarios.

## 1. Introduction
### 1.1 What is MCP (at a conceptual level)?
Model Context Protocol (MCP) is a pattern for tool servers: a standardized way for a model/agent runtime to discover tools and call them. Practically, MCP-like systems separate the agent runtime from tool execution so tools can be hosted, permissioned, audited, and updated independently.

### 1.2 Why remote tools matter
Remote tools are a security and reliability boundary:
- A tool can access networks, files, credentials, or internal systems.
- If calls are not policy-checked and audited, incidents are inevitable and untraceable.

### 1.3 What we have today
- `labs/09`: offline deterministic fake MCP server for teaching.
- `src/agent_core/tools/mcp.py`: an HTTP tool provider stub using `/tools` and `/execute`.

This is not production MCP yet.

## 2. Requirements
### 2.1 Functional
- Tool discovery: list tools and load ToolContracts.
- Tool execution: call a named tool with structured args.
- Contract validation: validate args and outputs.
- Correlation: propagate request/tool-call IDs.

### 2.2 Non-functional
- Security posture: deny-by-default policy, authZ, auditing.
- Resilience: timeouts, retries/backoff for idempotent tools.
- Compatibility: avoid building a private protocol accidentally.

## 3. Technical Design

### 3.1 Tool discovery contract
`list_tools()` must yield ToolContracts containing:
- name, version, description
- input_schema, output_schema
- risk classification fields (or safe defaults)

### 3.2 Execution contract
`execute(tool_name, args)` MUST:
- validate args against ToolContract schema BEFORE network call
- enforce allowlist/permissions BEFORE network call
- include correlation IDs in outbound headers
- emit audit events (allowed/blocked + timing)

### 3.3 Error taxonomy mapping
Remote errors must map into typed Tool errors:
- timeout
- unauthorized
- tool_not_found
- invalid_arguments
- provider_failure

### 3.4 Security expectations
Minimum:
- authentication for remote calls (token or mTLS)
- authorization enforced locally (tool boundary policies)
- logging and artifacts must apply redaction rules

### 3.5 Retries/backoff semantics
- idempotent tools may retry on transient failures.
- non-idempotent tools MUST NOT be retried automatically.

## 4. Decision Guidance (Transport/profile)

### Scenario A: Local dev and early Phase 2
Support a hardened HTTP profile.
- Why: lowest integration friction; works well with service mode later.

### Scenario B: Interop with existing MCP servers
Adopt the transport and semantics required by target MCP server(s) (often stdio/SSE).
- Why: avoids "fake MCP" drift.

### Scenario C: High-security environments
Prefer stronger transport security:
- mTLS, short-lived tokens, explicit allowlists, and strict auditing.

## 5. Validation (What "done" means)
- Offline conformance:
  - uses `labs/09` fake MCP server.
- Interop conformance:
  - runs against at least one real MCP-compatible server target.
- Audit:
  - every remote tool call is logged with correlation IDs and decision outcome.

## 6. References
```text
MCP (conceptual background / ecosystem entry point)
https://modelcontextprotocol.io/

Zero Trust (why authZ/audit matters)
https://www.nist.gov/cyberframework
```