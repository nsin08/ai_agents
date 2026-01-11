# ADR-003: Production Deployment Model (Config-Driven, K8s-Ready)

**Status:** Accepted (curriculum reference)  
**Date:** 2026-01-11  
**Related chapter:** `../chapter_03_production_deployment.md`

## Context

Agent systems depend on:

- external model providers
- vector stores and retrieval systems
- tool integrations with side effects

Deployment must support:

- safe rollouts and rollback
- secret management
- observability and audit events
- multiple environments (dev/staging/prod)

## Decision

Adopt a deployment approach that:

- packages the agent service as a container
- uses config-driven provider selection (local dev vs hosted prod)
- deploys on Kubernetes for production scale (probes, limits, rollouts)
- gates releases with layered checks (tests + evals + policy checks)

## Alternatives Considered

1. Docker-only deployment (single VM)
   - Rejected for production: limited rollout controls and scaling.
2. Hosted agent runtime only
   - Rejected: insufficient control for policy, audit, and compliance needs in many orgs.
3. Hardcoded provider settings per environment
   - Rejected: increases drift and reduces reproducibility.

## Consequences

### Positive

- Reproducible builds and consistent behavior across environments
- K8s supports safe rollouts, scaling, and health management
- Config versioning improves auditability

### Negative / Costs

- Additional ops overhead (cluster management)
- Requires careful secret handling and logging controls

## Implementation Notes

- Add readiness/liveness probes and degraded-mode behavior.
- Pin model and prompt versions to reproduce incidents.
- Use canary rollouts with cost and safety monitoring.

## Links

- Case study: `../case_studies/03_rag_faq_kubernetes_deployment.md`

