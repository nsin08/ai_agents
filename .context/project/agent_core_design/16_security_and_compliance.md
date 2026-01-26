# Security and Compliance (Production Posture)

## Security goals

- Prevent unauthorized or unintended side effects (tool boundary).
- Prevent data leakage (logs/artifacts/memory).
- Maintain auditability (who/what/when/why).
- Make safe defaults easy and unsafe configs explicit.

## Threat model (practical)

### S1. Prompt injection
Attack:
- retrieved content or user content attempts to override system instructions

Controls:
- mark retrieved text as untrusted in context packing
- keep tool instructions separate from data
- apply retrieval gating for high-risk requests
- policy can block tool calls when injection signals exist

### S2. Tool privilege escalation
Attack:
- model attempts to call a write/admin tool or craft dangerous args

Controls:
- deny-by-default allowlist
- scope checks (`required_scopes`)
- read-only policy enforcement
- approvals for risky operations
- schema validation and argument sanitization

### S3. Data exfiltration via telemetry/artifacts
Attack:
- secrets/PII leak into event logs or artifacts

Controls:
- redaction at export time
- tool contracts declare data-handling constraints
- do not store raw prompts/model outputs by default
- separate "debug artifacts" behind explicit opt-in

### S4. Cross-tenant leakage
Attack:
- memory/retrieval mixes data between tenants

Controls:
- tenant_id in context and persistent keys
- enforce tenant filters at store boundaries
- tests for isolation invariants

### S5. Supply chain coupling to external frameworks
Attack/Failure mode:
- dependency churn breaks core semantics or introduces vulnerabilities

Controls:
- keep optional ecosystems out of core dependency graph
- load plugins only when requested

## Secrets handling

Rules:
- secrets must only come from environment or secret stores (never config files committed to repo)
- do not log secrets
- do not store secrets in artifacts

## Audit requirements

Every tool call attempt should be auditable:
- who (tenant/user)
- what tool/version
- whether allowed/blocked and why
- minimal redacted args hash
- result status and latency

## Compliance considerations (baseline)

If targeting regulated domains later:
- provide hooks for:
  - consent tracking
  - right-to-delete
  - data retention policies
  - audit export

Do not overbuild in v1, but design interfaces to allow it.

