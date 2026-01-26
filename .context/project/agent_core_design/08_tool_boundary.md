# Tool Boundary (Contracts, Enforcement, MCP)

## Why this is the production boundary

Models propose actions; tools perform actions.
Therefore, correctness and safety depend on a strict tool boundary with:
- schema validation
- allowlists and permissions
- idempotency discipline
- timeouts and cancellation
- audit trails
- normalized error taxonomy

## ToolContract (required metadata)

Each tool must declare:
- `name` (stable identifier)
- `version` (semver)
- `description` (for prompting and explainability)
- `risk`: `read` | `write` | `admin`
- `input_schema` and `output_schema`
- `required_scopes` (permission model for tenant/user)
- `idempotency`: required for `write`/`admin`
- `data_handling`: PII/secrets constraints (what can be logged)

## ToolExecutor (single enforcement point)

All tool calls must flow through ToolExecutor.

Responsibilities:
1. Validate input against schema.
2. Enforce allowlist (deny by default):
   - allowlist is part of config and can be environment-scoped.
3. Enforce policies:
   - read-only blocks write/admin tools
   - budget policy blocks excessive tool calls/time
   - approval policy can require human approval for certain risks
4. Execute via ToolProvider:
   - apply per-tool/provider timeouts
   - propagate cancellation
5. Audit and observe:
   - emit tool_call_started / tool_call_finished events
   - record tool_call_id, run_id, trace context
   - redact sensitive arguments/results
6. Normalize errors:
   - map provider errors to a small, stable taxonomy

## ToolProvider (discovery + invocation)

Tool providers supply tools and execute them.

Types:
- Native (in-process) tools
- MCP tools (remote tool servers)
- Optional LangChain-wrapped tools (via `agent_lc`)

## MCP provider (built into core)

Treat MCP as a network boundary:
- discovery: list tools with schemas
- invocation: structured args/results
- policy enforcement remains in ToolExecutor

Production requirements:
- per-server allowlists
- auth strategy (bearer token env, mTLS, etc.)
- correlation IDs and audit events
- timeouts and retries (bounded)

## Deterministic tool providers

To support deterministic mode:
- provide a "fixture" tool provider:
  - tool call results are replayed from files or deterministic functions
- record/replay should preserve:
  - tool name/version
  - arguments hash (redacted/normalized)
  - result payload

## Risk model (recommended)

Keep risk classification simple and enforceable:
- `read`: external reads only (no state changes)
- `write`: state changes that are reversible or bounded
- `admin`: high-risk irreversible or privileged actions

Read-only mode:
- allows only `read`
- blocks `write`/`admin` with an explicit policy violation event

