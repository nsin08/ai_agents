# Observability & Run Events

This document describes the `RunEvent` schema, event types, and exporters.

## RunEvent schema (v1)

Fields:
- `time`: ISO timestamp
- `run_id`: run identifier
- `event_type`: event name
- `severity`: debug | info | warn | error
- `trace`: { trace_id, span_id, parent_span_id? }
- `actor`: engine | model | tool | policy | retrieval | evaluation
- `attrs`: structured attributes (redacted as needed)

Example:
```json
{
  "time": "2026-01-27T05:00:00Z",
  "run_id": "abc123",
  "event_type": "model.call.finished",
  "severity": "info",
  "trace": {
    "trace_id": "trace-1",
    "span_id": "span-2",
    "parent_span_id": "span-1"
  },
  "actor": "model",
  "attrs": {
    "role": "actor",
    "latency_s": 0.12,
    "usage": { "total_tokens": 120 }
  }
}
```

## Event types (v1)

Run lifecycle:
- `run.started`
- `run.finished`
- `run.failed`
- `run.canceled`

Model:
- `model.call.started`
- `model.call.finished`

Tool:
- `tool.call.started`
- `tool.call.finished`
- `tool.call.blocked`

Policy:
- `policy.violation`

Engine state (debug):
- `engine.state` (state transitions for LocalEngine)

## Exporters

- `stdout`: JSON lines to stdout
- `file`: JSON lines appended to a file
- `memory`: in-memory buffer (tests)
- `disabled`/`none`: disable event emission

## Redaction

Redaction is applied at export time based on `ObservabilityConfig.RedactConfig`.
Secrets are always redacted; PII is redacted when enabled.
