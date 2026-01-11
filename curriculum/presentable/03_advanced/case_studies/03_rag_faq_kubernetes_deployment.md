# Case Study 03: RAG FAQ Agent Deployed on Kubernetes

**Related chapter(s):** `../chapter_03_production_deployment.md`, `../chapter_04_scaling_strategies.md`  
**Primary internal references:** `Agents/09_03_retrieval_tools_planning_modern_stack.md`, `projects/P01_faq_bot_with_rag.md`

## Executive Summary

A RAG FAQ agent is a common first production agent: it answers questions grounded in a controlled knowledge base. The major risks are:

- incorrect answers presented with false confidence
- leakage of sensitive internal documentation
- reliability issues due to external dependencies (vector store, model provider)

This case study describes a Kubernetes deployment with safe defaults:

- config-driven model provider (local for dev, hosted for prod)
- strict retrieval access control and tenant scoping
- degraded mode when retrieval is unavailable
- evaluation gates for releases (golden set + regression)

## Scenario

The organization has internal FAQs, policy docs, and product docs. The agent must:

- answer user questions with citations to retrieved sources
- avoid answering when evidence is missing (safe fallback)
- support multiple environments (dev/staging/prod)

## Architecture Overview

```
Client -> FAQ Agent API (K8s)
  -> Retrieval:
      - embed query
      - vector search (tenant-scoped)
      - optional rerank
  -> Prompt template (citations required)
  -> LLM provider (config-driven)
  -> Output policy (redaction + length limits)
  -> Observability (logs, traces, metrics)
```

## Deployment Model

### Containerization

- Build a single image for the agent service.
- Inject environment-specific config via ConfigMap.
- Inject provider credentials via Secret.

### Kubernetes basics

- Deployment with replicas (HPA if needed)
- Service + Ingress
- Readiness/liveness probes
- Resource requests/limits

## Key Production Concerns

### 1) Retrieval failure and degraded mode

If the vector store is slow or down:

- do not hang the request
- return a response that clearly states: "retrieval unavailable"
- provide next steps (try later, manual links)

This avoids silent hallucinations when evidence is missing.

### 2) Citation enforcement

Policy: if no citations, do not answer as if certain.

Implementation options:

- prompt constraint ("must cite sources")
- output validator that checks for citations and downgrades response if missing

### 3) Multi-tenancy and data access

Tenant scoping must be enforced in:

- vector store queries
- cache keys
- logs (avoid cross-tenant correlation)

### 4) Release gates for quality

Before rollout:

- run deterministic unit tests
- run retrieval integration tests (can be mocked for CI)
- run golden set evaluation (behavioral)

During rollout:

- canary traffic
- monitor success rate, cost per success, and citation rate

## Failure Modes and Mitigations

1. Vector store degraded -> fallback mode + alert.
2. Model provider degraded -> circuit breaker + alternate model (if available).
3. Prompt injection in docs -> retrieval sanitization + strict tool allowlists + output policy.

## Lessons Learned

1. Degraded mode is a feature, not a failure.
2. Citation enforcement is essential for trust in RAG systems.
3. Rollouts must be gated by evals, not only unit tests.

## Suggested Exercises

1. Define a golden set of 25 FAQ questions with expected citations.
2. Add a "citation rate" metric and alert when it drops after rollout.
3. Write an ADR selecting the deployment model and documenting rollback strategy.

