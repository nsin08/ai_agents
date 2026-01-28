# ADR-0005: MCP Support Profile (Phase 2+)

Status: Proposed
Date: 2026-01-28
Owners: Architect/PM

## Context
We have MCP foundations:
- `labs/09` and `src/agent_labs/mcp/*` provide an offline, minimal interface.
- `src/agent_core/tools/mcp.py` is a basic HTTP tool provider using `/tools` and `/execute` endpoints.

This is not production MCP. Before we implement more, we must decide what MCP "profile" we support.

## Decision
Phase 2 will support a minimal, production-usable remote tool boundary with:
- an HTTP-based remote tool provider (current stub) upgraded with hardening
- conformance tests against at least one real MCP server (to prevent drifting into a private protocol)

Phase 3+ will add spec-aligned transports (stdio/SSE) if required by target MCP servers.

## Options Considered

1) HTTP-only remote tool boundary (chosen for Phase 2)
- Pros: easiest to operationalize; works in service deployments; good stepping stone.
- Cons: may not be interoperable with canonical MCP servers; risk of "fake MCP".

2) Full MCP spec transports immediately
- Pros: better interoperability.
- Cons: higher complexity; blocks Phase 2 retrieval/memory delivery; requires more security and lifecycle work.

## Required Hardening for Phase 2
- authN/authZ integration (bearer token is not enough; must integrate with tool policy)
- retries/backoff and timeouts
- request correlation IDs propagated in headers
- strict ToolContract schema validation and versioning
- audit events on remote calls

## Acceptance Criteria
- Can list tools and execute tool calls against a real MCP-compatible server.
- Tool results are normalized into ToolResult with correct status mapping.
- Policy decisions are logged (allowed/blocked) with correlation IDs.

## Open Questions
- Which MCP server(s) are in scope for interoperability testing?
- Do we require streaming tool results/events in Phase 3?