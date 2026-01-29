# ADR-0007: Canonical consumption surfaces (library + CLI + service)

**Date:** 2026-01-25  
**Status:** Accepted

## Context

We need standardization for developers and non-technical stakeholders.
Library-only usage makes it hard to standardize runs, evaluation, and debugging across teams and environments.

## Decision

- Library API is canonical and stable.
- CLI is a thin wrapper over the library API and is mandatory for standardization:
  - run
  - validate-config
  - eval / gate
  - serve
- Service is a thin wrapper over the library API:
  - polling-first API for hosted product
  - streaming can be added later using the same event schema

## Consequences

### Positive
- Standard, reproducible workflows for devs and stakeholders.
- Same artifact bundles across local and hosted runs.
- Supports web and VSCode integrations through the service.

### Negative / trade-offs
- Service introduces operational complexity; keep it as an optional extra to avoid bloating core dependencies.

