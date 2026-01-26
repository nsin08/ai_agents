# ADR-0001: Single `agent_core` framework with optional LC/LG packages

**Date:** 2026-01-25  
**Status:** Accepted

## Context

We need one production-ready framework that developers can install and use directly.
At the same time, we want the ability to use external ecosystems (LangChain) and external runtimes (LangGraph) without coupling the core to them or making them mandatory dependencies.

## Decision

- `agent_core` is the only required production framework package.
- Optional packages:
  - `agent_lc` provides LangChain-based integration plugins.
  - `agent_lg` provides LangGraph-based engine plugins.
- `agent_core` must not depend on or import `agent_lc`/`agent_lg` on the default import path.
- Optional packages depend on `agent_core` and register plugins when requested by configuration.

## Consequences

### Positive
- Base install stays stable and dependency-light.
- External adopters can use `agent_core` without adopting LangChain/LangGraph.
- LC/LG (or alternatives) can be swapped as plugins without changing core semantics.

### Negative / trade-offs
- Plugin mechanism must be designed carefully to avoid "dependency missing" import-time failures.
- Requires conformance tests to ensure plugins do not bypass core policies and observability.

## Alternatives considered

1. Make LC/LG mandatory dependencies of `agent_core`  
   - Rejected: increases churn and breaks the "works out of the box" core requirement for adopters that do not want LC/LG.
2. Ship two separate cores (one standalone, one LC/LG-based)  
   - Rejected: creates two mental models, increases maintenance, and fragments documentation and APIs.

