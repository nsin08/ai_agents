# ADR-006: Security Boundaries (Tool AuthZ, Secrets Hygiene, Audit Logs)

**Status:** Accepted (curriculum reference)  
**Date:** 2026-01-11  
**Related chapter:** `../chapter_06_security_best_practices.md`

## Context

Agent systems are exposed to:

- prompt injection (user and retrieved content)
- tool misuse and privilege escalation
- data exfiltration through output, logs, and memory
- multi-tenant isolation failures

Security must be enforceable and auditable, not prompt-based.

## Decision

Adopt a security posture that:

- enforces authn/authz at tool boundaries (RBAC + tenant scope)
- uses strict tool allowlists by risk tier
- prevents secrets from entering prompts/logs/memory
- emits audit logs for high-risk actions and privileged reads
- scopes caches and storage by tenant and role

## Alternatives Considered

1. "Trust the model" for policy compliance
   - Rejected: not enforceable; fails under injection.
2. Secrets in environment printed in debug logs
   - Rejected: common leak vector.
3. Shared caches without tenant keys
   - Rejected: high risk of cross-tenant leakage.

## Consequences

### Positive

- Reduced blast radius of injection attempts
- Stronger compliance and forensic capabilities
- Safer multi-tenant deployments

### Negative / Costs

- Requires policy enforcement code and testing
- More operational complexity (audit log retention and access control)

## Links

- Case study: `../case_studies/06_healthcare_triage_security.md`

