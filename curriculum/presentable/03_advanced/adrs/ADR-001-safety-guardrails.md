# ADR-001: Safety Guardrails as Code (Checkpoint Model)

**Status:** Accepted (curriculum reference)  
**Date:** 2026-01-11  
**Related chapter:** `../chapter_01_safety_guardrails.md`

## Context

Production agent systems are exposed to:

- prompt injection and adversarial inputs
- non-deterministic model behavior
- privileged tool execution (writes)
- privacy and compliance constraints

Prompt-only safety is insufficient because it does not enforce boundaries at the tool and output layers.

## Decision

Adopt a checkpoint-based guardrail architecture where policy is enforced at three boundaries:

1. Pre-request validation (budgets, sanity checks)
2. Pre-tool validation (allowlists/blocklists, authz, schema)
3. Post-output filtering (PII redaction, length limits, policy)

Guardrails are configuration-driven ("policy as data") and versioned.

## Alternatives Considered

1. Prompt-only safety guidelines
   - Rejected: not enforceable against injection and tool misuse.
2. Tool-only safety (validate tools but not outputs)
   - Rejected: does not prevent PII leakage through responses and logs.
3. Model-side safety only (provider safety filters)
   - Rejected: cannot express domain policies and cannot audit decisions.

## Consequences

### Positive

- Deterministic enforcement that is testable and observable
- Clear audit trail for policy decisions
- Policies can be tuned via config without rewriting tools

### Negative / Costs

- Engineering effort to build and maintain policy config and validation
- Requires careful redaction and logging controls to avoid privacy leaks

## Implementation Notes

- Use explicit exception types for guardrail violations (machine-readable rule ID).
- Emit telemetry for blocks and redaction events.
- Start with strict allowlists and expand with evidence.

## Links

- Lab 7: `../../../labs/07/README.md`
- Safety validator: `../../../labs/07/src/safety_validator.py`
- Case study: `../case_studies/01_invoice_approval_assistant.md`

