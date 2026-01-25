# ADR-0008: OpenAI provider included in base install via `httpx` (no SDK)

**Date:** 2026-01-25  
**Status:** Accepted

## Context

We want cloud model support in `agent_core` while keeping base dependencies minimal and stable.
Provider SDKs can increase dependency churn and transitive dependency weight.

## Decision

- Include an OpenAI provider in base `agent_core`.
- Implement OpenAI API calls using `httpx` (no OpenAI SDK dependency).
- Reference secrets via environment variables (`OPENAI_API_KEY`).
- Keep the provider behind the `ModelClient` interface so:
  - other providers (Anthropic/Azure OpenAI/etc.) can be added later without changing the core API.

## Consequences

### Positive
- Cloud support available immediately after install.
- Minimal dependencies and predictable upgrade path.
- Works consistently across library/CLI/service.

### Negative / trade-offs
- Must maintain the HTTP integration as APIs evolve.
- Some provider-specific features may require extra work to expose cleanly via a stable interface.

## Alternatives considered

1. Use provider SDKs  
   - Rejected for base install due to dependency churn; may be acceptable as optional extras later if needed.

