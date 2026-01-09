# Level 4 Workbook — Domain Specialization & Scale (P1–P6)

**Goal:** Apply patterns to real domains, choose deployment models, and design for platform-scale operation.  
**Estimated time:** 6–8 weeks (or 8–12 sessions instructor-led).  
**Prereqs:** Level 3 outcomes (testing/eval, security, HITL, scalability fundamentals).

## Level Outcomes

By the end of Level 4, learners can:

- Analyze reference architectures and extract reusable patterns
- Design domain-specialized agents with correct safety posture
- Choose an appropriate deployment model (self-managed vs agent-as-a-service)
- Plan operations: versioning, rollbacks, SLOs, monitoring, cost controls
- Design multi-agent and platform patterns where they add real value

## Deliverables (Evidence)

- Architecture review doc for a chosen domain (components + data flows + risks)
- Deployment decision record (ADR-style): self-managed vs hosted, with tradeoffs
- Operations plan: telemetry, SLOs, incident response, model/tool versioning, rollback
- Capstone demo plan (choose a project from `projects/`)

---

## P1 — Case Study Deep Dive: Customer Support

**Primary sources:** `../../../Agents/12_01_customer_support_agent_architecture.md`, `../../../Agents/09_04_case_study_customer_support_agent.md`  
**Timebox:** 90–120 minutes

### Objectives

- Identify components needed for a production support agent (triage, retrieval, tools, safety)
- Understand escalation paths and HITL integration

### Exercises

- Map the reference architecture to your organization’s support stack.
- Define what “read-only MVP” looks like vs “assisted write” vs “autonomous resolution.”

---

## P2 — Case Study Deep Dive: Coding Agent

**Primary source:** `../../../Agents/12_04_coding_agent_architecture.md`  
**Timebox:** 90–120 minutes

### Objectives

- Understand developer-tool integrations, safety boundaries, and evaluation signals
- Recognize why coding agents need strong verification (tests, lint, type checks)

### Exercises

- List the toolchain you would integrate (repo read, tests, formatter, PR creation).
- Define “allowed writes” and required approvals for code changes.

---

## P3 — Case Study Deep Dive: Medical Agent

**Primary source:** `../../../Agents/12_05_medical_agent_architecture.md`  
**Timebox:** 90–120 minutes

### Objectives

- Understand compliance and safety constraints in regulated domains
- Design for auditability, privacy, and conservative behavior

### Exercises

- Define data-access boundaries and logging constraints.
- Write a “safe response policy” (what the agent must refuse or escalate).

---

## P4 — Case Study Deep Dive: DevOps Troubleshooting

**Primary source:** `../../../Agents/12_06_ops_troubleshooting_agent_architecture.md`  
**Timebox:** 90–120 minutes

### Objectives

- Understand operational troubleshooting workflows and tool-heavy reasoning
- Design for partial success and safe mitigations

### Exercises

- Define safe mitigation tiers (read-only diagnosis → suggested actions → approved writes).
- Identify failure modes that could worsen incidents and how to prevent them.

---

## P5 — Deployment Models & Operations

**Primary source:** `../../../Agents/11_self_managed_vs_agent_as_a_service.md`  
**Timebox:** 120–150 minutes

### Objectives

- Choose between self-managed and agent-as-a-service models
- Understand operational responsibilities (SLOs, cost, governance, security)

### Exercises

- Write a deployment decision record (ADR-style) with:
  - constraints, risks, compliance needs
  - cost and latency expectations
  - ownership model (who is on call, who approves changes)

---

## P6 — Future Directions & Emerging Patterns

**Primary sources:** `../../../Agents/10_conclusion_future_directions.md`, `../../../Agents/09_03_retrieval_tools_planning_modern_stack.md`, `../../../Agents/09_01_agent_frameworks_and_multi_agent_systems.md`  
**Timebox:** 60–90 minutes

### Objectives

- Recognize emerging patterns (better tool runtimes, eval platforms, multi-agent collaboration)
- Decide what to adopt now vs monitor

### Exercises

- Pick one emerging pattern and write:
  - what problem it solves,
  - what risks it introduces,
  - what “minimum adoption bar” you would require (tests, safety, telemetry).

---

## Level 4 Capstone Options

Choose one:

- `projects/P08_multi_tenant_platform.md`
- `projects/P09_domain_production_agent.md`
- `projects/P10_evaluation_platform.md`
- `projects/P12_multi_agent_system.md`

