# Level 1 Use Cases — Foundations & Mental Models

Use this file to help learners practice “agent fit” analysis.

## Candidate Workflows (Pick 3–5)

1. **IT:** Triage incident tickets using logs + knowledge base, propose next actions
2. **HR:** Answer policy questions grounded in handbook + open HR requests (read-only)
3. **Finance:** Vendor invoice QA (extract → validate → flag anomalies)
4. **Sales Ops:** CRM enrichment (read-only), propose outreach plan, draft emails
5. **Support:** Classify ticket intent, route to correct queue, suggest response + links
6. **Engineering:** PR review assistant (read-only), suggest tests, highlight risk
7. **Security:** Alert triage (read-only), summarize, correlate, propose investigation steps
8. **Operations:** Runbook assistant (read-only), propose mitigations, open Jira tasks

## Agent Fit Checklist (Fast)

For each workflow, answer:

- Does it require **multiple steps** across systems?
- Is there **uncertainty** or variability in the steps?
- Do we need **fresh data** (tools/retrieval) to be correct?
- Are there meaningful **verification signals** (tool results, constraints, checks)?
- What is the **risk** if it makes a mistake? (read-only vs writes vs irreversible)

## Anti-Patterns (Avoid)

- Using an agent for simple deterministic logic (“if X then Y”)
- Using an agent where latency must be <100ms
- Allowing writes without confirmation/audit
- Treating “the prompt” as the architecture

## Mini-Case: Ticket Triage (Read-Only MVP)

**Goal:** Reduce time-to-triage without automating irreversible actions.

- Tools: ticket system (read), logs (read), runbook search (RAG)
- Outputs: classification, summary, proposed next steps, recommended escalation
- Guardrails: no writes, PII redaction, citations to retrieved sources

Next step after Level 1: evolve into Level 2 by adding tool contracts, memory policy, and observability.

