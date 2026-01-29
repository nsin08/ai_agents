# Consumption Surfaces (Library, CLI, Service, Web, VSCode)

This document defines how `agent_core` becomes a usable product without requiring token streaming in v1.

## Canonical layering

Single source of truth:
- **Library API** (`agent_core`) is canonical.

Standardization wrappers:
- **CLI** uses the library API and writes artifacts.
- **Service** uses the library API and writes the same artifacts.

Clients:
- Web UI and VSCode act as clients of the service (recommended).

## 1) Library (developers embedding as a dependency)

Use when:
- building an application that imports `agent_core`
- needing programmatic control and testing

Characteristics:
- async-first API with sync wrappers
- config from file/env/object
- returns `RunResult` and optional `RunArtifact`

## 2) CLI (standardized developer workflow)

Use when:
- you want reproducible runs and a standard debug/eval interface
- you want CI integration with gates

Key properties:
- single command to run and write artifacts
- deterministic mode as a hard correctness gate
- JSON output for automation

## 3) Hosted service (standardized product workflow)

Use when:
- you need a shared interface for devs and non-technical stakeholders
- you want web and VSCode integrations

v1 approach:
- polling-first (no streaming required)
- background execution with run_id
- cursor-based event polling
- artifact bundle download

Reference deployment topology:
- API server (HTTP)
- worker process(es)
- stores:
  - run metadata
  - event log
  - artifact store

## 4) Web UI (for managers/leaders and demos)

The web UI should:
- create runs
- show live progress via polled events
- show final output + evidence summary + policy blocks
- provide links to artifacts for auditability

Design principle:
- the UI does not need privileged access to tools; it calls the service only.

## 5) VSCode integration (for developers, high leverage)

Recommended architecture:
- VSCode extension talks to a **local** `agent_core` service by default.
  - avoids shipping Python runtime inside the extension
  - allows local access to the workspace when needed

Two modes:

### Local service mode (recommended default)
- VSCode -> localhost service
- service can read the workspace (if explicitly configured) or accept file context sent by the extension

### Remote service mode (optional later)
- VSCode -> remote service
- workspace context must be explicitly packaged and sent (to avoid remote file system access assumptions)

Security note:
- do not automatically upload full repos
- require explicit user selection for what context is shared

