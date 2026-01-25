# ADR-0005: Centralized tool boundary enforcement

**Date:** 2026-01-25  
**Status:** Accepted

## Context

Tools are where side effects happen.
Without a centralized enforcement boundary, production risks include:
- unauthorized tool use
- unintended writes
- missing auditability
- inconsistent timeouts and retries

## Decision

- All tool calls go through a single component: `ToolExecutor`.
- Tools must declare:
  - risk classification (`read|write|admin`)
  - schemas
  - required scopes
  - idempotency rules for write/admin
  - data-handling constraints for logging/redaction
- Deny-by-default allowlist is enforced by `ToolExecutor`.
- Policy violations are recorded as events and surfaced in results/artifacts.

## Consequences

### Positive
- Consistent safety posture and audit trail.
- Enables strict read-only mode (safe-by-default recipes and deployments).
- Supports deterministic tool replay for CI gates.

### Negative / trade-offs
- Requires discipline: tool authors must provide correct metadata.
- Some integrations may need adapter work to fit the contract (e.g., LangChain tools).

## Alternatives considered

1. Let engines or model providers call tools directly  
   - Rejected: cannot guarantee policy enforcement and auditability.

