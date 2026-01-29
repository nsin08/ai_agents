# Observability (Events, Trace Context, Exporters)

## Goals

- A stable internal event schema that all runtimes/providers map into.
- Correlation IDs across the whole run: run_id, trace_id, span_id, tool_call_id.
- Redaction applied before export (PII/secrets).
- Exporters are swappable (stdout/file/memory; OTel later).

## Event model (core)

### RunEvent (high-level)

Every event includes:
- `time`: ISO timestamp
- `run_id`
- `event_type` (stable enum)
- `severity` (debug/info/warn/error)
- `trace`:
  - `trace_id`
  - `span_id`
  - `parent_span_id` (optional)
- `actor` (optional): `engine` | `model` | `tool` | `retrieval` | `policy` | `evaluation`
- `attrs`: structured attributes (redacted as needed)

### Required event types (v1)

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
- `tool.call.blocked` (policy violation)

Retrieval:
- `retrieval.started`
- `retrieval.finished`

Policy:
- `policy.violation`
- `policy.budget_exceeded`

Evaluation:
- `eval.suite.started`
- `eval.suite.finished`
- `eval.gate.decision`

## Trace context propagation

Design:
- `RunContext` contains a `TraceContext`.
- Every model/tool/retrieval call receives a child span context.
- Providers do not invent IDs; they use contexts passed in.

This is what enables:
- consistent debugging across engines
- optional later mapping to OpenTelemetry spans

## Redaction policy

Redaction should be applied at export time:
- never log secrets (API keys, tokens)
- redact PII by policy (configurable)
- do not log raw prompts or raw tool outputs by default
- store sensitive artifacts separately if needed

## Exporters

v1 exporters:
- stdout JSON (default)
- file JSON (append-only run event log)
- memory exporter (tests)

Later:
- OTel exporter (OTLP) as optional dependency

## Metrics

At minimum, emit metrics as fields on events:
- latency per step/tool/model call
- tokens and cost best effort
- tool call counts
- retrieval counts and chunk counts

This avoids a premature metrics subsystem while preserving observability.

