# Hosted Service Specification (Polling-First, Streaming Later)

## Goal

Provide a hosted production surface without requiring token streaming.

The service standardizes:
- run creation and status
- event access (polling with cursors)
- artifact access (downloadable bundles)
- evaluation execution and gate decisions (optional)

## Core design

- The service is a thin wrapper over the library API (`AgentCore`).
- It uses the same config model.
- It produces the same artifact bundle format.

## Execution model

### Asynchronous runs (recommended)

1. Client submits a run request.
2. Service returns `run_id` immediately.
3. Run executes in a background worker.
4. Client polls:
   - status
   - events (cursor-based)
   - final result and artifacts

This supports:
- web UX with progress (by polling events)
- VSCode integration (polling events)
- later streaming (SSE/WebSocket) using the same event schema

## API surface (v1)

Base path:
- `/v1`

### Create run

- `POST /v1/runs`
  - body: `RunRequest`
  - response: `{ run_id, status_url, events_url, artifact_url }`

### Get run status/result

- `GET /v1/runs/{run_id}`
  - response includes:
    - status (`queued|running|finished|failed|canceled`)
    - timestamps
    - result (when finished)
    - artifact metadata

### Get events (polling)

- `GET /v1/runs/{run_id}/events?cursor=<opaque>&limit=<n>`
  - response:
    - `events: [RunEvent...]`
    - `next_cursor`
    - `complete: bool`

### Get artifact bundle

- `GET /v1/runs/{run_id}/artifact`
  - options:
    - download as zip
    - or list files and fetch individually

### Evaluate (optional v1)

- `POST /v1/eval`
  - body: `{ suite_ref, run_id | config_ref }`
  - response: `{ scorecard, gate_decision }`

## Streaming (v2)

Streaming is not required for production v1.
When needed, add:
- `GET /v1/runs/{run_id}/events/stream` (SSE)

The event payload must be identical to the polling endpoint.

## Auth and multi-tenancy (phase-able)

v1 options:
- `auth=none` (local/dev)
- `auth=static_token` (simple header token)

Tenant scoping:
- accept `X-Tenant-Id` header (optional early)
- run artifacts and stores should be tenant-scoped when enabled

## Storage model (v1)

Minimum required stores:
- Run metadata store (status, timestamps)
- Event log store (append-only JSONL)
- Artifact store (filesystem)

These can all start as filesystem-backed to ship v1 quickly.
A production deployment can later replace stores with Postgres/object storage.

## Deployment notes

The service should be separable:
- `agent_core` stays dependency-light and importable.
- `agent_core_service` (or a `serve` module) can add web framework deps via extras.

Avoid making web framework dependencies part of `agent_core` base install.

