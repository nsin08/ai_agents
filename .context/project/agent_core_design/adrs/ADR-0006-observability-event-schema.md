# ADR-0006: Internal event schema with trace context and redaction

**Date:** 2026-01-25  
**Status:** Accepted

## Context

Agents are hard to debug without consistent telemetry.
We need an internal event model that:
- works across different engines and providers
- can be polled or streamed
- is safe to store and export (redaction)

## Decision

- Define a stable `RunEvent` schema and `TraceContext` model in core.
- Emit events for run lifecycle, model calls, tool calls, retrieval, policy decisions, and evaluation.
- Apply redaction at export time (PII/secrets, tool-specific data constraints).
- Implement exporters (stdout/file/memory) in core; OTel exporter later as optional.

## Consequences

### Positive
- Standard debugging and monitoring across CLI and service.
- Enables hosted product without token streaming (poll events).
- Makes it possible to add streaming later without redesign.

### Negative / trade-offs
- Requires schema versioning discipline.
- Some users may want raw prompts; must be explicit opt-in due to risk.

