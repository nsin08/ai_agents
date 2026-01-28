# SPEC-0006: Rancher/Kubernetes Environment (Phase 4+)

Status: Draft
Date: 2026-01-28
Related ADRs:
- `.context/sprint/sprint-2026-W05/04_DECISIONS/ADR-0002-rancher-k8s-phasing.md`

## Abstract
This spec defines the production deployment environment for the service mode (Phase 4+) using Kubernetes with Rancher as a management plane. It explains why Kubernetes is deferred until Phase 4, what must be present for stateful services, and how to decide between in-cluster and managed backing services.

## 1. Introduction
### 1.1 What is Rancher used for?
Rancher is used to manage Kubernetes clusters and workloads across environments.
- RBAC and access control
- cluster and namespace management
- workload visibility and governance

### 1.2 Why not Phase 2?
Phase 2 is about building correctness: retrieval, memory, evaluation, and CLI. Kubernetes introduces operational work that does not reduce core product risk at this stage.

## 2. Requirements
### 2.1 Functional
- Deploy the service mode with a stable API surface.
- Manage configuration and secrets.
- Provide environment separation (dev/staging/prod).

### 2.2 Non-functional
- Security posture: least privilege RBAC, secret handling.
- Reliability: health probes, rollouts, restart behavior.
- Stateful safety: PVCs and backup/restore strategy.

## 3. Technical Design

### 3.1 Phased rollout
- Phase 2-3: Docker Compose (fast iteration)
- Phase 4+: Kubernetes (service mode)
- Rancher: management plane once K8s is adopted

### 3.2 Workload expectations
- Namespaces: dev/staging/prod
- RBAC roles: read-only vs deploy
- Deployment manifests: Helm or Kustomize
- Ingress + TLS

### 3.3 Stateful services posture
If running stateful services in-cluster:
- Postgres + pgvector:
  - PVCs
  - backups/snapshots
  - restore runbook

- MinIO:
  - PVCs
  - bucket lifecycle

If using managed services:
- prefer managed Postgres in production to reduce ops burden
- keep vector store interface unchanged

### 3.4 Observability baseline
Minimum expectations:
- logs aggregation
- metrics
- tracing (OTel later if adopted)

## 4. Decision Guidance (Scenarios)

### Scenario A: small team / early service rollout
Use managed Postgres + object store; keep K8s workload small.

### Scenario B: regulated environment
In-cluster stateful services may be required; ensure backups and access controls are designed first.

### Scenario C: multi-team platform
Rancher becomes valuable for consistent RBAC and cluster governance.

## 5. Validation (What "done" means)
- service deploys with readiness/liveness probes
- secrets are not stored in plain text
- rollback works
- backup/restore plan exists and is tested in staging

## 6. References
```text
Rancher
https://www.rancher.com/

Kubernetes docs
https://kubernetes.io/docs/

Kubernetes probes
https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
```