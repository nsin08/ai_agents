# Case Study 06: Healthcare Triage Assistant (Security and Compliance)

**Related chapter(s):** `../chapter_06_security_best_practices.md`, `../chapter_01_safety_guardrails.md`  
**Primary internal references:** `Agents/12_05_medical_agent_architecture.md`

## Executive Summary

Healthcare workflows are regulated and high risk. The primary requirement is safety and compliance, not automation. This case study describes a triage assistant that:

- summarizes symptoms and history
- retrieves policy guidance
- escalates to clinicians

Key posture:

- no autonomous medical decisions
- no writes to patient record without human control
- strict audit logs and privacy controls

## Scenario

Users (patients or staff) ask questions. The assistant:

- provides general guidance based on approved policies
- refuses unsafe requests
- escalates to a clinician workflow for high-risk cases

## Security and Compliance Requirements

- strict access control (role-based, least privilege)
- audit logs for all access and escalations
- data minimization (retrieve only what is required)
- strong PII redaction in logs and outputs
- retention policies aligned with regulation

## Architecture Overview

```
User -> TriageAssistant API
  -> AuthN/AuthZ (role + patient scope)
  -> Retrieval (approved policy docs)
  -> Optional read-only patient context (scoped)
  -> Response policy:
      - safe language
      - refusal for diagnosis
      - escalation path
  -> Audit log (immutable)
```

## Threat Model Highlights

- prompt injection via user text or retrieved content
- data exfiltration through logs
- cross-patient leakage (scope failure)

Mitigations:

- strict allowlist for retrieval and read tools
- redaction before logging
- tenant/patient scoping enforced in code
- no autonomous write tools

## Decision Tree (Escalation)

```
If symptoms indicate emergency OR user requests diagnosis OR low confidence:
  -> escalate to clinician (human)
Else:
  -> provide general guidance + cite policy + advise next steps
```

## Lessons Learned

1. Compliance is a product requirement, not an afterthought.
2. The safest action is often escalation, not automation.
3. Audit logs and access controls must be designed early.

## Suggested Exercises

1. Write an ADR documenting why the system forbids autonomous writes.
2. Build an adversarial prompt set (injection attempts) and verify refusal/escalation behavior.
3. Define a logging policy that prevents PII leakage while preserving debuggability.

