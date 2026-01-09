# Observability & Logging

Structured logging, tracing, and metrics for agent workflows.

## Components

- `StructuredLogger`: context-rich logger with JSON or text formatting.
- `Tracer`: spans for Observe→Plan→Act→Verify→Refine steps.
- `MetricsCollector`: counters and latency tracking.
- `Exporters`: stdout, file, in-memory (tests).
- `timeit`: decorator for timing sync/async functions.

## Logger Example

```python
from agent_labs.observability import StructuredLogger, JsonFormatter, StdoutExporter

logger = StructuredLogger(
    name="orchestrator",
    exporter=StdoutExporter(),
    formatter=JsonFormatter(),
)

logger.info("LLM plan generated", step="plan", turn=1, tokens_used=120)
```

## Tracing Example

```python
from agent_labs.observability import Tracer, StructuredLogger, MemoryExporter, JsonFormatter

exporter = MemoryExporter()
logger = StructuredLogger(name="agent", exporter=exporter, formatter=JsonFormatter())
tracer = Tracer(logger=logger)

with tracer.span("plan", turn=1):
    # do work
    pass
```

## Metrics Example

```python
from agent_labs.observability import MetricsCollector

metrics = MetricsCollector()
metrics.increment("tool_calls")
metrics.record_latency("plan", 12.3)
snapshot = metrics.snapshot()
```

## Integration Points

- Orchestrator: wrap each step in `Tracer.span`.
- Tools: log tool name, status, latency via `StructuredLogger`.

## Notes

- JSON formatting is machine-readable.
- Text formatting is human-readable.
- Exporters are pluggable for file/stdout/test capture.
