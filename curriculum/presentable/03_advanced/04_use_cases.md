# Level 3 Use Cases: Production Patterns, Safety, and Operations

Use these scenarios to practice production posture: failure handling, security, HITL, evaluation, deployment, and operations.

Each use case maps to a deeper case study in `case_studies/`.

---

## Use Case 1: Invoice Approval Assistant (High-Risk Writes)

**Case study:** `case_studies/01_invoice_approval_assistant.md`

- Tools: invoice retrieval, vendor DB, fraud scoring, approval workflow (write)
- Risks: fraud, incorrect approvals, compliance violations
- Required: HITL approvals, audit trail, regression suite, strict tool allowlists

Key focus: approvals + audit + Tier 2 guardrails.

---

## Use Case 2: Multi-Agent Incident Response Assistant (Operational Risk)

**Case study:** `case_studies/02_multi_agent_incident_response.md`

- Tools: logs, metrics, runbooks, feature flags (write-gated), paging (write-gated)
- Risks: making outage worse, noisy actions, retry storms
- Required: role separation, supervisor queue, circuit breakers, degraded mode, traceability

Key focus: multi-agent boundaries + incident-ready observability.

---

## Use Case 3: Healthcare Triage Assistant (Regulated + Privacy)

**Case study:** `case_studies/06_healthcare_triage_security.md`

- Tools: policy retrieval, scoped read-only patient context, escalation workflow
- Risks: privacy violations, unsafe advice, compliance failures
- Required: strict access control, redaction, audit logs, refusal/escalation policies

Key focus: security boundaries + compliance evidence.

---

## Use Case 4: Multi-Tenant Support Platform (Scale + Isolation)

**Case study:** `case_studies/04_multi_tenant_support_platform_scaling.md`

- Tools: tenant-scoped KB search, ticket read/write, analytics
- Risks: cross-tenant leakage, inconsistent policy enforcement, noisy neighbor
- Required: tenant scoping everywhere, per-tenant budgets, audit logs, per-tenant dashboards

Key focus: multi-tenant isolation + scaling fairness.

---

## Use Case 5: RAG FAQ Agent Deployed on Kubernetes

**Case study:** `case_studies/03_rag_faq_kubernetes_deployment.md`

- Tools: retrieval + optional reranking, model provider (local dev vs hosted prod)
- Risks: hallucinations when retrieval fails, data exposure from internal docs
- Required: citation enforcement, degraded mode, canary rollout, eval gates

Key focus: deployment readiness + quality gates.

---

## Use Case 6: Cost Regression After Rollout (Ops and Governance)

**Case study:** `case_studies/05_cost_spike_post_rollout.md`

- Tools: model routing rules, retrieval configuration, prompt templates
- Risks: cost per success spikes, latency regression, hidden drift
- Required: cost metrics, release gates, baseline comparisons, rollback strategy

Key focus: cost as an SLO + evidence-based rollout.

