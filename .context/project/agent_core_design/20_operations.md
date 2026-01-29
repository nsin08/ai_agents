# Operations (Versioning, SLOs, Deployment, and Governance)

## Versioning and compatibility

Because `agent_core` is intended for external adopters:
- semver for public API
- document public interface boundaries
- version artifact schema changes explicitly

Recommended: include `schema_version` in:
- run events
- run artifact index

## Observability and SLOs

Minimum recommended SLOs/metrics:
- run success rate
- policy violation rate (by type)
- tool call error rate + latency p95
- model call error rate + latency p95
- cost per run (estimate)
- queue time (service)

Dashboards should be driven by the event schema, not ad-hoc logs.

## Deployment model (service)

For v1:
- single host can run API + worker + filesystem artifact store

For production:
- separate API and workers
- stores:
  - Postgres for run metadata and (optionally) events index
  - object storage (S3-like) for artifacts
  - Redis for job queue / session state (optional)

## Config management

Recommendations:
- environment-specific config profiles (local/staging/prod)
- secrets from env/secret stores only
- validate config at startup (`validate-config`)

## Security operations

Minimum:
- rotate API keys/tokens
- audit export mechanism (artifact + event logs)
- data retention policy for artifacts
- redaction reviews (ensure no secrets leak)

## Evaluation operations

Evaluation quality is a process:
- maintain golden suites
- review thresholds periodically
- track drift between baseline and candidate over time

