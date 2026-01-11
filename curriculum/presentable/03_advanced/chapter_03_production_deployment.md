# Chapter 03: Production Deployment (Docker, Kubernetes, Cloud)

**Level:** 3 (Advanced)  
**Target audience:** Senior engineers, staff+ engineers, architects  
**Prerequisites:** You can run labs locally. You understand basic CI/CD concepts and containerization.  
**Primary internal references:** `Agents/11_self_managed_vs_agent_as_a_service.md`, `Agents/12_06_ops_troubleshooting_agent_architecture.md`

## Learning Objectives (3-5)

By the end of this chapter, you will be able to:

1. Choose an appropriate deployment model for an agent (single service, platform, or agent-as-a-service) using explicit trade-offs.
2. Package an agent service using Docker with config-driven providers (Ollama for local, hosted LLMs for prod).
3. Deploy and operate an agent service on Kubernetes with safe defaults (probes, HPA, resource limits, secret management).
4. Design a deployment pipeline with release gates for non-deterministic systems (tests + evals + safety checks).
5. Create a production deployment checklist that covers safety, observability, and rollback.

## Chapter Outline

1. What makes agent deployment different from "normal" services
2. Deployment models and runtime architecture
3. Container packaging patterns (Docker)
4. Kubernetes patterns (config, secrets, scaling, probes)
5. CI/CD and release gates (tests, evals, policy checks)
6. Decision trees and trade-off matrices
7. Case studies (production scenarios)
8. One-page takeaway

---

## 1) Why Agent Deployment Is Different

Traditional services mostly transform inputs into outputs deterministically. Agent services are different:

- **Non-determinism:** the same input may produce different outputs.
- **External dependencies:** LLM providers, vector stores, tool APIs.
- **Higher operational risk:** tool calls can cause side effects (writes).
- **Policy and safety as runtime concerns:** guardrails must be enforced consistently.
- **Cost sensitivity:** LLM calls can dominate cost, and "bad loops" are expensive.

This changes how you deploy:

- You must treat evals and safety tests as release gates, not optional QA.
- You must version and pin model/tool behavior, or you will see unexpected drift.
- You must have strong observability, or incidents become "mysterious model behavior".

### Operational invariants to enforce from day one

In production, you want a small set of invariants that are always true. These invariants are what make incidents debuggable and rollouts safe:

1. **Every request has a request_id** that flows through logs, traces, tools, and audit events.
2. **Every write is authorized, approved (if required), and audited.**
3. **Every dependency has timeouts** and degraded mode behavior.
4. **Every release is reproducible** (pinned deps, pinned prompt/tool config, pinned model routing rules).
5. **Every rollout is reversible** (rollback plan is documented and tested).

If you cannot enforce these invariants, you may still deploy, but you should treat the system as a prototype, not a production service.

---

## 2) Deployment Models and Runtime Architecture

### Model A: Single agent service (simplest)

One service exposes an API (HTTP) and internally uses:

- LLM provider
- tool registry/executor
- memory/retrieval components (optional)
- guardrails and policies
- logging/metrics/tracing

Good for:

- a single domain or workflow
- early production pilots

Risks:

- hard to scale across multiple agent types
- config complexity grows quickly

### Model B: Agent platform (shared runtime)

Multiple agents share a runtime:

- shared tool runtime with contracts and sandboxing
- shared observability and eval harness
- per-agent policies and configuration
- multi-tenant support

Good for:

- org-wide adoption
- many teams building agents with shared standards

Risks:

- higher upfront engineering investment
- governance becomes a product

### Model C: Agent-as-a-service (hosted)

You outsource the runtime. Good for speed. Risks include:

- vendor lock-in
- limited control over logs, policy, and data handling
- compliance complexity

The key is to match the deployment model to constraints: compliance, risk tolerance, scale, and team ownership.

### Model D: Job-based agent (queue + workers)

Some agent workflows are not interactive. They are long-running (minutes), expensive, or require approvals. In that case, deploy a job-based architecture:

```
Client -> API (enqueue job) -> queue -> workers (agent runtime) -> store results -> notify client
```

Benefits:

- avoids API timeouts
- isolates expensive workloads
- supports retries and idempotency at the job level
- supports human approvals as part of the workflow state machine

Risks:

- more system components (queue, storage, worker scaling)
- requires a user experience for job status (polling or callbacks)

### Runtime boundaries and ownership

Deployment is not only "where it runs". It is also "who owns what":

- Who is on call when the provider is down?
- Who can change guardrail configs in production?
- Who approves model upgrades and prompt changes?
- Who has access to logs and audit events?

For advanced deployments, define:

- ownership (service team, security team, domain team)
- escalation paths (on-call, incident commander)
- change management (PR approvals, gates, release notes)

### Service interface design (API contracts and UX)

Deployment is easier when the service interface is explicit. Decide early:

- Is this an interactive API (seconds) or a job-based workflow (minutes)?
- Do you stream partial responses, or return a single result?
- What is the schema of a request and response?

Conceptual interactive request:

```json
{
  "request_id": "req-123",
  "tenant_id": "t-9",
  "user_id": "u-7",
  "workflow": "support_ticket_summary",
  "input": {"text": "Summarize ticket 123 and propose next steps"}
}
```

Conceptual response:

```json
{
  "request_id": "req-123",
  "status": "success",
  "answer": "...",
  "evidence": [{"type": "tool", "tool": "ticket_read", "ref": "tool-55"}],
  "policy_version": "guardrails-prod-v3"
}
```

If the workflow is write-gated, the response may include:

- proposed change (diff)
- approval_required flag
- approval_request_id

Why this matters:

- it enables clients to build a UI that matches safety posture (approvals and audit)
- it enables downstream services to parse and store evidence
- it makes observability and auditing easier (structured fields)

### Streaming vs non-streaming responses

Streaming can improve perceived latency, but it has trade-offs:

- harder to enforce output policies (you must filter as you stream)
- more complex client handling
- can leak partial unsafe output if not carefully filtered

For Tier 2 workflows (high-stakes), many teams prefer non-streaming responses with strict validation before returning output.

### Cloud deployment options (vendor-neutral mapping)

Most organizations end up with one of these runtime options:

1. **Managed Kubernetes:** best for long-lived services with complex dependencies.
2. **Serverless containers:** good for bursty, stateless Tier 0 workloads, but watch cold starts and timeouts.
3. **Batch/queue workers:** best for long workflows, approvals, and heavy tool chains.

Key questions when selecting:

- Do you need long-lived connections and streaming?
- Are requests short enough for serverless timeouts?
- Do you need fine-grained network controls (egress restrictions)?
- Do you need stable warm caches (retrieval, embeddings)?

The selection is often driven by operational maturity: teams with strong platform support can run K8s reliably; teams without it may start with managed offerings but must still enforce the same safety and observability principles.

---

## 3) Container Packaging Patterns (Docker)

Even if you deploy to Kubernetes, start by making the service runnable locally in a container.

### A) Minimal Dockerfile pattern (Python service)

This repo is Python-first. A minimal Dockerfile often looks like:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy only dependency metadata first (better layer caching)
COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv && uv sync --frozen

# Copy the rest of the code
COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["python", "-m", "agent_labs.server"]
```

Notes:

- In production, pin dependencies using `uv.lock` (or equivalent).
- Prefer running with a non-root user if feasible.
- Consider multi-stage builds for smaller images.

### B) Config-driven provider selection (local vs prod)

Your container should not "hardcode" provider choice. It should read config:

- `USE_OLLAMA=true/false`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `OPENAI_API_KEY` or other provider credentials

This allows the same container image to run:

- on a dev laptop using local Ollama
- in prod using a managed LLM provider

### C) Local dev with Ollama (optional)

If you want local reproducibility, use docker compose:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
  agent:
    build: .
    environment:
      USE_OLLAMA: "true"
      OLLAMA_BASE_URL: "http://ollama:11434"
      OLLAMA_MODEL: "llama2"
    depends_on: [ollama]
    ports: ["8000:8000"]
```

In production, you typically do not run Ollama in the same pod. You run a managed model endpoint or a dedicated model service.

### D) Image hardening and reproducible builds

Agent services are attractive targets because they often have broad data access and many integrations. Harden your container build:

- run as a non-root user (where feasible)
- pin dependencies (lockfile) and avoid "latest" tags
- scan images for vulnerabilities (CI gate)
- generate an SBOM (software bill of materials) for compliance
- keep the runtime image small (multi-stage builds)

Conceptual non-root Docker pattern:

```dockerfile
RUN useradd -m appuser
USER appuser
```

### E) Configuration layering (dev/staging/prod)

Most production incidents are configuration incidents. Use explicit layers:

- defaults in code (safe)
- environment config (dev/staging/prod)
- tenant config (if multi-tenant)
- feature flags for risky changes (routing rules, new tools)

Rules:

- config changes are reviewed like code (PRs, approvals)
- config versions are attached to audit events and traces
- rollback includes config rollback, not only code rollback

---

## 4) Kubernetes Patterns (Config, Secrets, Scaling, Probes)

Kubernetes helps with:

- scaling
- health management
- configuration and secret distribution
- rollout and rollback

### A) Probes: readiness and liveness

Agent services should expose health endpoints:

- `/healthz` liveness: process is alive
- `/readyz` readiness: dependencies reachable (or degraded mode is enabled)

If your service depends on external LLMs, readiness should reflect:

- can you serve read-only responses?
- do you require LLM connectivity for core functions?

Design for degraded mode:

- if vector store is down, fall back to "no retrieval" and tell the user
- if LLM is down, return a helpful error and record an incident signal

### B) Resource limits and concurrency control

Agent services can be CPU and memory heavy. Add:

- CPU and memory requests/limits
- concurrency limits (in-process) to avoid overload
- request timeouts

Scaling without concurrency control causes queue collapse: more pods do not help if each pod is blocked on slow external calls.

### C) Configuration: ConfigMap + Secret

Use ConfigMaps for non-secret settings:

- model name
- budgets
- feature flags

Use Secrets for credentials:

- API keys
- database passwords

Never put secrets in prompts or logs.

### D) Rollouts and rollback

Use rolling updates and include:

- canary deployments (small % traffic)
- automatic rollback if SLOs degrade
- evaluation gates before full rollout

Agent changes can cause subtle regressions. Treat the rollout itself as an experiment with guardrails.

### E) Network policies and egress control (reduce blast radius)

Many agent tool failures are security failures in disguise:

- SSRF via URL fetch tools
- accidental access to internal metadata endpoints
- unbounded egress to unknown domains

In Kubernetes, consider:

- NetworkPolicy to restrict pod egress where feasible
- allowlisted domains for HTTP tools at the application layer
- separate namespaces for high-risk workloads

The rule is simple: do not allow "the agent can fetch anything on the internet" unless you are comfortable with the resulting attack surface.

### F) Autoscaling (HPA) and queue depth scaling

Autoscaling works best when your bottleneck is CPU/memory. Many agent services are bottlenecked on external calls. In that case:

- more replicas help only if the provider and tools can handle the increased concurrency
- concurrency caps per pod are often more important than replica count

For job-based systems, autoscale workers based on:

- queue depth
- queue age
- tool/provider error rates (stop scaling if dependencies are degraded)

### G) Graceful shutdown and disruption budgets

Agent requests can be long-running. Add:

- graceful shutdown handling (finish in-flight requests or checkpoint)
- PodDisruptionBudget to avoid dropping too many pods at once

If you cannot checkpoint, keep requests short and enforce timeouts to reduce disruption risk.

### H) Reference Kubernetes manifests (conceptual, minimal set)

Below is a conceptual "minimal set" of manifests. Treat it as a learning example, not a production-ready template.

1) ConfigMap (non-secrets)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-config
data:
  LOG_LEVEL: "INFO"
  USE_OLLAMA: "false"
  MODEL_NAME: "gpt-4o-mini"
  MAX_TOKENS_PER_REQUEST: "2000"
```

2) Secret (secrets)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: agent-secrets
type: Opaque
stringData:
  OPENAI_API_KEY: "REDACTED"
```

3) Deployment (replicas, probes, limits)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: agent
  template:
    metadata:
      labels:
        app: agent
    spec:
      containers:
        - name: agent
          image: your-registry/agent:0.1.0
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: agent-config
            - secretRef:
                name: agent-secrets
          readinessProbe:
            httpGet: { path: /readyz, port: 8000 }
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet: { path: /healthz, port: 8000 }
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests: { cpu: "250m", memory: "256Mi" }
            limits: { cpu: "1", memory: "1Gi" }
```

4) Service (stable endpoint)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: agent
spec:
  selector:
    app: agent
  ports:
    - port: 80
      targetPort: 8000
```

5) HPA (autoscaling by CPU as a starting point)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

Notes:

- CPU-based HPA is a starting point. For agent systems, concurrency and external dependencies often dominate. Use custom metrics (queue depth, in-flight requests) when you can.
- Keep secrets out of ConfigMaps and code.
- Pair scaling with concurrency caps to avoid overload.

Production hardening add-ons (what teams usually add next):

- **securityContext:** runAsNonRoot, drop Linux capabilities, readOnlyRootFilesystem (where feasible)
- **service accounts and RBAC:** the pod should have only the permissions it needs
- **NetworkPolicy:** restrict egress to required services/domains where possible
- **Ingress with TLS:** terminate TLS and add authentication/authorization at the edge
- **Config version labels:** label pods with config/policy versions for easier rollback

Even if you do not implement all of these in the first pilot, document them as the next steps. Production systems rarely fail because they lacked HPA. They fail because they lacked containment and governance.

---

## 5) CI/CD and Release Gates for Agents

For deterministic systems, unit tests are enough. For agents, you need layered gates:

1. **Deterministic tests**: tool contracts, guardrails, orchestrator state transitions.
2. **Integration tests**: external services (optional), or mocks with contract checks.
3. **Evaluation suite**: golden scenarios, adversarial prompts, policy compliance checks.
4. **Operational checks**: can the service start, export metrics, pass probes.

### Pinning and versioning

Treat these as versioned artifacts:

- model name and version (or checksum)
- prompt templates
- tool schemas
- guardrail config

If you do not pin, you cannot reproduce incidents.

### Evidence-driven PRs

Your PR should contain evidence:

- tests pass
- eval results (summary)
- rollout plan (if production)

This matches the governance model of this repo: evidence-based changes.

### Example CI pipeline (conceptual)

An agent pipeline usually needs both deterministic validation and probabilistic evaluation:

1. Lint/format/type checks (fast feedback)
2. Unit tests (tool contracts, guardrails)
3. Integration tests (mocked dependencies or contract tests)
4. Build container image (pinned deps)
5. Security scan + SBOM generation (gate)
6. Evaluation suite (golden set + adversarial prompts)
7. Publish artifacts (image + config versions + eval report)

Conceptual pipeline steps (pseudo YAML):

```yaml
jobs:
  test:
    steps:
      - lint_and_format
      - unit_tests
      - integration_tests
  build:
    steps:
      - docker_build
      - image_scan
      - sbom_generate
  eval:
    steps:
      - run_golden_set
      - run_adversarial_set
      - compare_to_baseline
```

The output of the pipeline should be human-readable evidence: "what changed" and "what risk changed".

### Environment promotion (dev -> staging -> prod)

For agent systems, environment promotion is not only a deployment concern. It is a behavior concern:

- prompts change behavior
- model routing changes behavior
- tool availability changes behavior
- guardrail config changes behavior

Practical promotion rules:

1. **Dev:** fast iteration, permissive budgets, verbose logs (redacted).
2. **Staging:** production-like configs, synthetic canaries, eval suite required.
3. **Prod:** strict budgets, restricted logs, canary rollouts, rollback readiness.

Treat "promotion" as a controlled increase in risk:

- first: validate deterministic correctness (tests)
- next: validate behavior on fixed scenarios (evals)
- finally: validate under real dependency conditions (canary traffic)

If you skip staging-like validation, you will discover behavior regressions in production.

### Common deployment anti-patterns (and how to avoid them)

1. **Deploying prompts without versioning**
   - Fix: version prompt templates and attach versions to traces and audit events.
2. **No rollback plan**
   - Fix: practice rollback in staging; include config rollback, not only code rollback.
3. **Treating provider outages as "rare"**
   - Fix: implement timeouts, circuit breakers, and degraded mode from day one.
4. **Scaling replicas without concurrency limits**
   - Fix: cap in-flight requests per pod and add bulkheads per tool.
5. **Shipping without eval evidence**
   - Fix: run a golden set and adversarial set and store the report with the release.

Deployment maturity is mostly about avoiding these traps. The technology (Docker, Kubernetes) is the easy part.

A common success pattern is to deploy Tier 0 read-only workflows first, then progressively add higher-risk capabilities (Tier 1, Tier 2) only after observability and rollback are proven. This matches how you build trust with stakeholders: stable basics, then controlled expansion.

---

## 6) Decision Trees and Trade-off Matrices

### Decision tree: Self-managed vs hosted

```
Start
  |
  |-- Are you in a regulated environment with strict audit/log controls?
  |      |
  |      |-- Yes -> Prefer self-managed (or a provider with strong compliance)
  |      |
  |      |-- No
  |           |
  |           |-- Do you need deep control over tools, policies, and custom runtime?
  |           |      |
  |           |      |-- Yes -> Self-managed / platform
  |           |      |
  |           |      |-- No -> Consider hosted for speed
```

### Trade-off matrix: Docker-only vs Kubernetes

| Dimension | Docker (single host) | Kubernetes | Notes |
|---|---|---|---|
| Operational overhead | low | medium-high | K8s pays off with scale |
| Scaling | limited | strong | HPA and replicas |
| Rollout safety | basic | strong | canary, rollback, health probes |
| Multi-tenancy | harder | easier | namespaces, policies |
| Cost | lower at small scale | can be higher | depends on baseline load |

### Decision tree: Interactive API vs job-based workflow

```
Start
  |
  |-- Does the user need an answer within a few seconds?
  |      |
  |      |-- Yes -> interactive API
  |      |
  |      |-- No
  |           |
  |           |-- Does the workflow require approvals or long tool chains?
  |                 |
  |                 |-- Yes -> job queue + workers (status + callbacks)
  |                 |
  |                 |-- No -> interactive API with strict timeouts
```

### Trade-off matrix: Self-managed vs hosted vs hybrid

| Dimension | Self-managed | Hosted | Hybrid |
|---|---|---|---|
| Control over policies/tools | high | medium-low | high for tools, variable for model |
| Compliance/audit control | high | variable | high (if logs/audit stay internal) |
| Time to ship | slower | fastest | medium |
| Cost predictability | medium | variable | medium |
| Vendor lock-in | low | high | medium |

Hybrid often means: you own the tool runtime and policy enforcement, and you call a hosted model provider behind strict guardrails.

---

## 7) Case Studies (Production Scenarios)

Each case study is summarized here and expanded in `case_studies/`.

Case study links:

- `case_studies/03_rag_faq_kubernetes_deployment.md`
- `case_studies/01_invoice_approval_assistant.md`

### Case Study 1: Deploying a RAG FAQ Agent to Kubernetes

**Scenario:** You deploy a FAQ bot with retrieval and a tool runtime.  
**Constraints:** Must be reliable, cost-controlled, and observable.

Key design choices:

- containerize the service and run in K8s behind an ingress
- use ConfigMaps for model selection and budgets
- use Secrets for provider keys
- add readiness/liveness probes
- enforce request timeouts and concurrency limits
- run eval suite as part of the release gate

Operational details that matter in practice:

- define "citation required" behavior and test it in the golden set
- cache retrieval results where safe (tenant-scoped keys)
- use canary rollout and monitor success rate, citation rate, and cost per success
- define a degraded mode response when retrieval is unavailable

Failure mode to plan for:

- vector store degraded -> fallback to "no retrieval" mode with clear user messaging

### Case Study 2: Deploying a Guardrail-Constrained Support Agent

**Scenario:** Customer support agent with PII redaction and controlled writes.  
**Constraints:** Logs must be safe; writes require approval.

Key design choices:

- guardrail config is versioned and deployed like code
- audit logs stored with restricted access
- canary rollout with monitoring of "blocked_by_rule" spikes

Operational details that matter in practice:

- separate draft generation (low risk) from record updates (write-gated)
- require idempotency keys for writes to avoid duplicate updates during retries
- sample traces for failures and guardrail blocks (privacy-aware)
- ensure logs are redacted before export to shared systems

### Mini-case: Provider outage during rollout

If the model provider degrades during a rollout:

- circuit breaker opens to stop retry storms
- traffic remains on the previous stable version (or routes to fallback)
- incident is declared with a clear on-call owner

The lesson: rollouts must include failure containment, not only "deploy the new version".

---

## 8) Hands-on Exercises

1. Pick one lab-based agent and write a deployment plan:
   - target environment (dev/staging/prod)
   - dependency inventory (LLM, tools, retrieval)
   - degraded modes (what happens if dependencies fail)
2. Draft a minimal Kubernetes manifest set (conceptual):
   - Deployment (replicas, limits)
   - Service + Ingress
   - ConfigMap + Secret usage
3. Define release gates:
   - which tests run in CI
   - what eval suite is required before rollout
   - what metrics must remain within thresholds during canary

Deliverable: attach your plan to an ADR (see `adrs/`) and link the relevant case study in `case_studies/`.

---

## 9) One-Page Takeaway (Summary)

### What to remember

- Agent deployment is different: non-determinism, external dependencies, and safety constraints require layered release gates.
- Use config-driven provider selection so the same service can run locally (Ollama) and in production (hosted LLMs).
- Kubernetes helps with scaling and rollouts, but only if you implement probes, limits, and rollback plans.
- Pin and version models, prompts, tools, and guardrails or you will not be able to reproduce incidents.

### Minimal production checklist (deployment)

- [ ] Container image builds reproducibly with pinned deps
- [ ] Health endpoints exist and probes are configured
- [ ] Secrets are managed via Secret store (not in env files committed to git)
- [ ] Concurrency limits and request timeouts exist
- [ ] Eval suite is part of release gates
- [ ] Rollback plan exists (and is tested)

### Suggested next steps

- Write an ADR selecting the deployment model for your org (self-managed vs hosted).
- Create a canary release process and an eval gating workflow.
- Use the production deployment checklist in `production_deployment_checklist.md`.

### Evidence artifacts (what to produce)

- A "minimal manifests" bundle (or helm values) and a short explanation of probes, limits, and rollouts.
- A release gate report: tests + eval summary + baseline comparison.
- A rollback runbook: code rollback and config rollback steps.
- A dashboard snapshot showing success rate, p95 latency, tool error rate, and cost per success during canary.

Optional but useful:

- A dependency map showing which workflows require which tools/providers and what the degraded mode is for each.

If you can hand these artifacts to a peer team and they can operate the service safely, your deployment design is solid.

In other words: production deployment is not a build step. It is a transfer of responsibility to operators. If the operators cannot answer "what changed", "what risk changed", and "how do we rollback", the system is not ready regardless of how clean the Dockerfile looks.

Treat deployment as part of curriculum, not an afterthought: learners should practice probes, rollbacks, and degraded modes the same way they practice prompts and tools. This is how you get from a demo to a service.

Use `production_deployment_checklist.md` as the final review gate. If you cannot answer the checklist items with evidence (tests, traces, rollback steps), delay the release and fix the gaps.

The checklist is not bureaucracy; it is how you turn operational risk into explicit, testable requirements.

In advanced teams, deployment reviews include safety, security, and SRE concerns in a single evidence-driven pass before merge.
