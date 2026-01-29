# ADR-0003: Plugin loading via registries + on-demand entry points

**Date:** 2026-01-25  
**Status:** Accepted

## Context

We want swappable implementations (engines, tool providers, vector stores) without importing optional dependencies or creating hard coupling.

## Decision

- Use registries (key -> constructor) for all swappable components.
- Use factories to construct implementations from config.
- Use entry points for optional plugin discovery:
  - entry point group: `ai_agents.agent_core.plugins`
- Plugins are loaded on-demand:
  - only when config selects a key that is not built-in.

## Consequences

### Positive
- `agent_core` stays dependency-light.
- Optional integrations do not load unless requested.
- Supports future plugins beyond LC/LG.

### Negative / trade-offs
- Entry points are not conditional on extras; plugin load may fail if deps are missing.
  - Mitigation: load only selected plugins and emit actionable error messages.

## Alternatives considered

1. Auto-import all plugins at startup  
   - Rejected: would cause import-time failures and unpredictable dependency behavior.
2. Manual plugin registration only (no discovery)  
   - Rejected: increases adoption friction and complicates hosted deployments.

