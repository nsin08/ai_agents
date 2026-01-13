# Advanced Workbook: Production Case Studies and Analysis

**Level**: Advanced
**Total Case Studies**: 6
**Estimated Time**: 12-16 hours
**Prerequisites**: Intermediate curriculum + Labs 03-06

---

## How to Use This Workbook

1. Read the case context.
2. Design the system architecture and guardrails.
3. Compare with the solution analysis.

---

## Case Study 1: Safety Guardrails for Financial Advice

**Context:** An agent summarizes financial reports and answers user questions.

**Key Constraints:** Compliance, data leakage, hallucination risk.

**Solution Analysis:**
- Use rule-based validation for disclosures.
- Require citations for every numeric claim.
- Block prompt injection attempts with safety filters.

---

## Case Study 2: Multi-Agent Incident Response

**Context:** A set of agents triage alerts, gather logs, and suggest mitigations.

**Key Constraints:** Latency, noisy data, escalation rules.

**Solution Analysis:**
- Separate roles (triage, retrieval, verifier).
- Use shared incident context with strict write policy.
- Escalate to human when confidence drops.

---

## Case Study 3: Production Deployment Pipeline

**Context:** A CI/CD pipeline deploys agent updates weekly.

**Key Constraints:** Regression risk, rollback speed, audit trails.

**Solution Analysis:**
- Use staged rollout and canary metrics.
- Track prompt version and model version in logs.
- Automatic rollback on error-rate spikes.

---

## Case Study 4: Scaling Strategy for a Support Platform

**Context:** An agent handles 10k+ daily support tickets.

**Key Constraints:** Cost, latency, concurrency.

**Solution Analysis:**
- Use model routing (cheap classifier + strong planner).
- Cache high-confidence answers.
- Batch tool calls where possible.

---

## Case Study 5: Monitoring and Alerting

**Context:** Operations team needs real-time visibility into agent health.

**Key Constraints:** Signal vs noise, alert fatigue.

**Solution Analysis:**
- Define golden signals: latency, error rate, saturation, cost.
- Alert only on sustained thresholds.
- Provide a diagnostic snapshot in runbooks.

---

## Case Study 6: Security Boundaries for Tool Use

**Context:** An agent can read and write to internal systems.

**Key Constraints:** Data loss prevention, role-based access.

**Solution Analysis:**
- Enforce tool contracts with RBAC.
- Require confirmation gates for write actions.
- Log all tool executions with user and request IDs.

---

## Document Checklist

- [ ] Accessibility review (WCAG AA)
- [ ] 6 case studies included
- [ ] Each case includes constraints and analysis
- [ ] Language is production-focused
- [ ] ASCII only

