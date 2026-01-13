# Chapter 04: Observability & Monitoring

[Prev](chapter_03_context_engineering.md) | [Up](README.md) | [Next](chapter_05_multi_turn_conversations.md)

---

## Learning Objectives

After completing this chapter, you will be able to:

1. **Implement Structured Logging** — Emit JSON-formatted logs with context fields for machine-readable analysis
2. **Build Execution Traces** — Capture complete request lifecycles with event sequences and timing
3. **Collect Performance Metrics** — Track counters (requests, errors) and latencies (LLM calls, tool execution)
4. **Debug Agent Behavior** — Use traces and logs to identify bottlenecks and unexpected decisions
5. **Export Telemetry** — Write traces and metrics to files, databases, or external observability platforms

---

## Introduction

When an agent makes an unexpected decision in production, you need to understand *why*. Observability is the ability to understand a system's internal state from its external outputs—logs, metrics, and traces.

This chapter covers the observability patterns implemented in Lab 6 and `src/agent_labs/observability/`. You'll learn to instrument agents so that every decision, every tool call, and every error is traceable.

**Key Insight:** Observability isn't optional for production agents. Without it, debugging is guesswork. With it, you can replay exactly what happened and why.

---

## 1. The Three Pillars of Observability

### 1.1 Logs, Metrics, and Traces

```
┌─────────────────────────────────────────────────────────────────────┐
│                   THREE PILLARS OF OBSERVABILITY                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                        LOGS                                 │     │
│  │  • Discrete events with timestamps                         │     │
│  │  • "What happened at this moment"                          │     │
│  │  • JSON format for machine parsing                         │     │
│  │  • Example: {"event": "tool_called", "tool": "calculator"} │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                       METRICS                               │     │
│  │  • Aggregated measurements over time                       │     │
│  │  • "How much / how fast / how often"                       │     │
│  │  • Counters, gauges, histograms                            │     │
│  │  • Example: llm_calls_total: 1523, avg_latency_ms: 245     │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                       TRACES                                │     │
│  │  • Request lifecycle across components                     │     │
│  │  • "How did this request flow through the system"          │     │
│  │  • Spans with parent-child relationships                   │     │
│  │  • Example: agent_run → llm_call → tool_execution          │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 When to Use Each

| Signal | Use Case | Query Type |
|--------|----------|------------|
| **Logs** | Debug specific request | "What happened to request X?" |
| **Metrics** | Monitor system health | "How many requests failed today?" |
| **Traces** | Analyze request flow | "Where did request X spend time?" |

---

## 2. Structured Logging

### 2.1 Why JSON Logs?

Plain text logs are human-readable but machine-hostile:

```
# Plain text (hard to parse)
2026-01-11 12:45:00 INFO Agent completed task in 245ms with 3 tool calls

# Structured JSON (easy to query)
{"timestamp": "2026-01-11T12:45:00Z", "level": "INFO", "event": "agent_completed", 
 "duration_ms": 245, "tool_calls": 3, "session_id": "abc123"}
```

With JSON logs, you can:
- Filter by field: `jq 'select(.tool_calls > 2)'`
- Aggregate: `GROUP BY event`
- Alert: `WHERE error_count > threshold`

### 2.2 Structured Logger Implementation

```python
from dataclasses import dataclass, field
from typing import Any, Dict
from datetime import datetime, timezone

@dataclass
class StructuredLogger:
    """Structured logger that emits context-rich records."""

    name: str
    context: Dict[str, Any] = field(default_factory=dict)

    def with_context(self, **fields: Any) -> "StructuredLogger":
        """Create child logger with additional context fields."""
        merged = dict(self.context)
        merged.update(fields)
        return StructuredLogger(name=self.name, context=merged)

    def log(self, level: str, message: str, **fields: Any) -> Dict[str, Any]:
        """Emit a structured log record."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": level.upper(),
            "message": message,
            "logger": self.name,
        }
        record.update(self.context)
        record.update(fields)
        
        # Output as JSON
        import json
        print(json.dumps(record))
        
        return record

    def info(self, message: str, **fields: Any) -> Dict[str, Any]:
        return self.log("INFO", message, **fields)

    def warning(self, message: str, **fields: Any) -> Dict[str, Any]:
        return self.log("WARNING", message, **fields)

    def error(self, message: str, **fields: Any) -> Dict[str, Any]:
        return self.log("ERROR", message, **fields)
```

### 2.3 Context Propagation

Add context that flows through all child loggers:

```python
# Create base logger
logger = StructuredLogger(name="agent")

# Add session context
session_logger = logger.with_context(session_id="user_12345", user="alice")

# All subsequent logs include session context
session_logger.info("Agent started", goal="Book a flight")
# {"timestamp": "...", "session_id": "user_12345", "user": "alice", 
#  "message": "Agent started", "goal": "Book a flight"}

# Add turn context
turn_logger = session_logger.with_context(turn=1)
turn_logger.info("Planning action")
# {"session_id": "user_12345", "user": "alice", "turn": 1, 
#  "message": "Planning action"}
```

### 2.4 Log Levels Strategy

| Level | Use For | Example |
|-------|---------|---------|
| **DEBUG** | Developer details | "Token count: 1523" |
| **INFO** | Normal operations | "Agent completed successfully" |
| **WARNING** | Recoverable issues | "Rate limit approaching" |
| **ERROR** | Failures | "Tool execution failed" |

**Production Tip:** Set INFO level in production, DEBUG for troubleshooting specific sessions.

---

## 3. Execution Tracing

### 3.1 What is a Trace?

A trace captures the complete lifecycle of a request as it flows through your agent:

```
Trace: agent_run_12345
├── agent_started (0ms)
│   └── session_id: "user_12345"
├── turn_started (1ms)
│   ├── turn: 1
│   └── query: "What's the weather?"
├── llm_request_sent (2ms)
├── llm_response_received (245ms)
│   ├── duration_ms: 243
│   └── tokens: 45
├── tool_call_initiated (246ms)
│   └── tool: "weather"
├── tool_call_completed (298ms)
│   ├── duration_ms: 52
│   └── success: true
├── turn_completed (299ms)
└── agent_completed (300ms)
    └── total_duration_ms: 300
```

### 3.2 Observable Agent Implementation

```python
from dataclasses import dataclass
from typing import Any, Dict, List
import time
import json
from datetime import datetime, timezone

class ObservableAgent:
    """Agent instrumented with structured logs and metrics."""

    def __init__(
        self,
        max_turns: int = 5,
        session_id: str = "demo-session",
    ) -> None:
        self.max_turns = max_turns
        self.session_id = session_id
        self.trace: List[Dict[str, Any]] = []
        self.metrics = {
            "turns": 0,
            "llm_calls": 0,
            "tool_calls": 0,
            "total_time_ms": 0.0,
            "tokens_used": 0,
        }
        self._timers: Dict[str, float] = {}

    def _now(self) -> str:
        """ISO-8601 timestamp with milliseconds."""
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    def _start_timer(self, name: str) -> None:
        """Start a named timer."""
        self._timers[name] = time.perf_counter()

    def _end_timer(self, name: str) -> float:
        """End timer and return duration in milliseconds."""
        start = self._timers.get(name)
        if start is None:
            return 0.0
        return (time.perf_counter() - start) * 1000.0

    def log_event(self, event: str, **data: Any) -> None:
        """Log an event to the trace."""
        entry = {
            "timestamp": self._now(),
            "event": event,
            "session_id": self.session_id,
            "data": data,
        }
        self.trace.append(entry)
        print(json.dumps(entry))

    def get_trace(self) -> List[Dict[str, Any]]:
        """Return the complete execution trace."""
        return self.trace

    def get_metrics(self) -> Dict[str, Any]:
        """Return aggregated metrics."""
        return self.metrics
```

### 3.3 Instrumenting the Agent Loop

```python
class ObservableAgent:
    # ... (init from above)

    def run(self, query: str) -> str:
        """Run agent with full instrumentation."""
        self._start_timer("total")
        self.log_event("agent_started", query=query, max_turns=self.max_turns)

        result_text = ""
        
        for turn in range(1, self.max_turns + 1):
            self.metrics["turns"] += 1
            self.log_event("turn_started", turn=turn)

            # LLM call instrumentation
            self._start_timer("llm")
            self.log_event("llm_request_sent", turn=turn, query=query)
            
            llm_response = self._call_llm(query)  # Your LLM call
            
            llm_time = self._end_timer("llm")
            self.metrics["llm_calls"] += 1
            self.metrics["tokens_used"] += llm_response.tokens
            self.log_event("llm_response_received",
                turn=turn,
                duration_ms=llm_time,
                tokens=llm_response.tokens,
            )

            # Tool call instrumentation (if needed)
            if llm_response.requires_tool:
                self._start_timer("tool")
                self.log_event("tool_call_initiated",
                    turn=turn,
                    tool=llm_response.tool_name,
                )
                
                tool_result = self._execute_tool(llm_response)
                
                tool_time = self._end_timer("tool")
                self.metrics["tool_calls"] += 1
                self.log_event("tool_call_completed",
                    turn=turn,
                    tool=llm_response.tool_name,
                    duration_ms=tool_time,
                    success=tool_result.success,
                )
                result_text = tool_result.output
            else:
                result_text = llm_response.text

            self.log_event("turn_completed", turn=turn)

            if self._is_goal_achieved(result_text):
                break

        total_time = self._end_timer("total")
        self.metrics["total_time_ms"] = total_time
        self.log_event("agent_completed",
            total_time_ms=total_time,
            metrics=self.metrics,
        )
        
        return result_text
```

### 3.4 Trace Export

```python
from pathlib import Path

def export_trace(self, path: str) -> None:
    """Export trace and metrics to JSON file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    export_data = {
        "session_id": self.session_id,
        "trace": self.trace,
        "metrics": self.metrics,
        "exported_at": self._now(),
    }
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2)

# Usage
agent = ObservableAgent(session_id="user_12345")
result = agent.run("What's the weather in Seattle?")
agent.export_trace("traces/user_12345.json")
```

---

## 4. Metrics Collection

### 4.1 Counter and Latency Metrics

```python
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class MetricsCollector:
    """Collect counters and latency metrics."""

    counters: Dict[str, int] = field(default_factory=dict)
    latencies_ms: Dict[str, List[float]] = field(default_factory=dict)

    def increment(self, name: str, value: int = 1) -> None:
        """Increment a counter."""
        self.counters[name] = self.counters.get(name, 0) + value

    def record_latency(self, name: str, latency_ms: float) -> None:
        """Record a latency measurement."""
        self.latencies_ms.setdefault(name, []).append(latency_ms)

    def snapshot(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        summary = {}
        
        for name, values in self.latencies_ms.items():
            if not values:
                continue
            summary[name] = {
                "count": len(values),
                "avg_ms": sum(values) / len(values),
                "min_ms": min(values),
                "max_ms": max(values),
                "p50_ms": sorted(values)[len(values) // 2],
            }
        
        return {
            "counters": dict(self.counters),
            "latencies": summary,
        }
```

### 4.2 Using Metrics in Agent

```python
class MetricAgent:
    def __init__(self):
        self.metrics = MetricsCollector()
    
    async def run(self, query: str) -> str:
        self.metrics.increment("requests_total")
        
        start = time.perf_counter()
        try:
            result = await self._process(query)
            self.metrics.increment("requests_success")
            return result
        except Exception as e:
            self.metrics.increment("requests_failed")
            self.metrics.increment(f"errors_{type(e).__name__}")
            raise
        finally:
            latency = (time.perf_counter() - start) * 1000
            self.metrics.record_latency("request_latency", latency)

# Check metrics
print(agent.metrics.snapshot())
# {
#     "counters": {"requests_total": 100, "requests_success": 95, "requests_failed": 5},
#     "latencies": {
#         "request_latency": {"count": 100, "avg_ms": 245.3, "p50_ms": 220.0}
#     }
# }
```

### 4.3 Key Metrics to Track

| Metric | Type | Purpose |
|--------|------|---------|
| `requests_total` | Counter | Total request volume |
| `requests_success` | Counter | Successful completions |
| `requests_failed` | Counter | Errors |
| `llm_calls_total` | Counter | LLM API calls |
| `tokens_used_total` | Counter | Token consumption (cost) |
| `tool_calls_total` | Counter | Tool executions |
| `request_latency_ms` | Histogram | End-to-end latency |
| `llm_latency_ms` | Histogram | LLM response time |
| `tool_latency_ms` | Histogram | Tool execution time |
| `turns_per_request` | Histogram | Loop iterations |

---

## 5. Log Levels and Verbosity

### 5.1 Configurable Log Levels

```python
import logging

class ObservableAgent:
    def __init__(self, log_level: str = "INFO"):
        self.logger = self._setup_logger(log_level)

    def _setup_logger(self, level: str) -> logging.Logger:
        """Configure logger with specified level."""
        logger = logging.getLogger(f"agent.{self.session_id}")
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        logger.propagate = False

        # JSON formatter for structured output
        formatter = logging.Formatter(
            '{"timestamp":"%(asctime)s","level":"%(levelname)s",'
            '"message":"%(message)s"}'
        )

        if not logger.handlers:
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            logger.addHandler(console)

        return logger
```

### 5.2 Level Comparison

Running the same query with different log levels:

**DEBUG Level (verbose):**
```json
{"level": "DEBUG", "event": "token_count", "tokens": 1523}
{"level": "DEBUG", "event": "context_packed", "items": 5}
{"level": "INFO", "event": "llm_request_sent"}
{"level": "DEBUG", "event": "llm_raw_response", "text": "..."}
{"level": "INFO", "event": "llm_response_received", "tokens": 45}
{"level": "DEBUG", "event": "tool_args_parsed", "args": {...}}
{"level": "INFO", "event": "tool_call_initiated"}
{"level": "INFO", "event": "tool_call_completed"}
```

**INFO Level (production):**
```json
{"level": "INFO", "event": "llm_request_sent"}
{"level": "INFO", "event": "llm_response_received", "tokens": 45}
{"level": "INFO", "event": "tool_call_initiated"}
{"level": "INFO", "event": "tool_call_completed"}
```

### 5.3 Dynamic Level Switching

```python
def set_log_level(self, level: str) -> None:
    """Change log level at runtime."""
    self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))

# Usage: Enable debug for specific session
agent.set_log_level("DEBUG")
result = agent.run("problematic query")
agent.set_log_level("INFO")  # Reset
```

---

## 6. Debugging Patterns

### 6.1 Identifying Bottlenecks

Use trace data to find slow components:

```python
def analyze_trace(trace: List[Dict]) -> Dict[str, float]:
    """Analyze trace to identify bottlenecks."""
    component_times = {}
    
    for i, event in enumerate(trace):
        if event["event"].endswith("_completed"):
            component = event["event"].replace("_completed", "")
            duration = event["data"].get("duration_ms", 0)
            component_times[component] = component_times.get(component, 0) + duration
    
    total = sum(component_times.values())
    
    return {
        name: {"ms": ms, "pct": (ms / total * 100) if total else 0}
        for name, ms in component_times.items()
    }

# Usage
analysis = analyze_trace(agent.get_trace())
# {
#     "llm": {"ms": 243, "pct": 81.0},
#     "tool_call": {"ms": 52, "pct": 17.3},
#     "turn": {"ms": 5, "pct": 1.7}
# }
# -> LLM is the bottleneck (81% of time)
```

### 6.2 Error Investigation

When something fails, use logs to reconstruct the event sequence:

```python
def investigate_failure(trace: List[Dict], session_id: str) -> Dict:
    """Reconstruct events leading to failure."""
    
    # Find error events
    errors = [e for e in trace if e.get("level") == "ERROR"]
    
    if not errors:
        return {"status": "no_errors_found"}
    
    last_error = errors[-1]
    error_time = last_error["timestamp"]
    
    # Get events before error
    preceding = [e for e in trace 
                 if e["timestamp"] < error_time][-5:]
    
    return {
        "error": last_error,
        "preceding_events": preceding,
        "session_id": session_id,
    }
```

### 6.3 Replay from Trace

Traces enable request replay for debugging:

```python
def replay_from_trace(trace_path: str) -> None:
    """Replay a request from saved trace."""
    with open(trace_path) as f:
        data = json.load(f)
    
    # Extract original query
    start_event = next(e for e in data["trace"] 
                       if e["event"] == "agent_started")
    original_query = start_event["data"]["query"]
    
    # Replay with DEBUG logging
    agent = ObservableAgent(
        session_id=f"replay_{data['session_id']}",
        log_level="DEBUG"
    )
    result = agent.run(original_query)
    
    print(f"Original result: {data.get('result')}")
    print(f"Replay result: {result}")
```

---

## 7. Human-Readable Trace Output

### 7.1 Trace Formatter

```python
def format_trace_human(trace: List[Dict], metrics: Dict) -> str:
    """Format trace for human-readable display."""
    lines = [
        "=== Agent Execution Trace ===",
        f"Session: {trace[0]['session_id'] if trace else 'unknown'}",
    ]
    
    for event in trace:
        timestamp = event["timestamp"].split("T")[1][:12]
        event_name = event["event"]
        data = event.get("data", {})
        
        # Format based on event type
        if event_name == "agent_started":
            lines.append(f"\n[{timestamp}] Started: {data.get('query', '')}")
        
        elif event_name == "turn_started":
            lines.append(f"\n[Turn {data.get('turn', '?')}]")
        
        elif event_name == "llm_response_received":
            lines.append(f"  LLM: {data.get('tokens', 0)} tokens, "
                        f"+{data.get('duration_ms', 0):.1f}ms")
        
        elif event_name == "tool_call_completed":
            success = "✓" if data.get("success") else "✗"
            lines.append(f"  Tool {data.get('tool', '?')}: {success} "
                        f"+{data.get('duration_ms', 0):.1f}ms")
        
        elif event_name == "agent_completed":
            lines.append(f"\n[{timestamp}] Completed")
    
    # Add metrics summary
    lines.append(f"\n--- Metrics ---")
    lines.append(f"Total time: {metrics.get('total_time_ms', 0):.1f}ms")
    lines.append(f"LLM calls: {metrics.get('llm_calls', 0)}")
    lines.append(f"Tool calls: {metrics.get('tool_calls', 0)}")
    lines.append(f"Tokens used: {metrics.get('tokens_used', 0)}")
    
    return "\n".join(lines)

# Usage
print(format_trace_human(agent.get_trace(), agent.get_metrics()))
```

### 7.2 Example Output

```
=== Agent Execution Trace ===
Session: user_12345

[12:45:00.123] Started: What's the weather in Seattle?

[Turn 1]
  LLM: 45 tokens, +243.2ms
  Tool weather: ✓ +52.1ms

[12:45:00.423] Completed

--- Metrics ---
Total time: 300.5ms
LLM calls: 1
Tool calls: 1
Tokens used: 45
```

---

## 8. Best Practices

### 8.1 Instrumentation Checklist

- [ ] Every external call (LLM, tools, APIs) has timing
- [ ] Session ID flows through all logs
- [ ] Errors include stack traces and context
- [ ] Metrics have consistent naming (`component_action_unit`)
- [ ] Traces are exported on completion and failure

### 8.2 Performance Impact

| Operation | Overhead | Notes |
|-----------|----------|-------|
| Log event | ~0.01ms | Negligible |
| JSON serialize | ~0.1ms | Per event |
| File export | ~1-5ms | Batch at end |
| Metrics snapshot | ~0.1ms | Lightweight |

### 8.3 Security Considerations

- **Never log sensitive data:** API keys, passwords, PII
- **Redact user content:** Summarize queries, don't log full text
- **Rotate logs:** Set retention policies
- **Access control:** Restrict who can view traces

---

## 4.4 Log Fields You Should Always Emit

If you only add one observability feature, make it structured logs. They are the fastest path to debugging.

A minimal event should include:

- `run_id` or `trace_id`
- `agent_state` (OBSERVING, PLANNING, ACTING, VERIFYING, REFINING)
- `latency_ms`
- `tokens_used` (estimate is fine)
- `tool_name` and `tool_status` (when tools are used)

This makes it possible to answer: "What happened, when, and why?"

---

## 4.5 Tracing: Make the Loop Visible

Tracing should map to the OPRV steps. Each span should capture duration and key inputs/outputs.

Practical guidance:

- Start a span per phase: observe, plan, act, verify, refine.
- Attach context fields (goal, turn, tool calls).
- Always close spans even on failure.

If you cannot see the slowest span, you cannot optimize the agent.

When you add spans, keep the names stable and low-cardinality. Spans like `tool.execute` are useful; spans like `tool.execute:weather_lookup` can create noisy dashboards if the values explode.

---

## 4.6 Metrics That Change Behavior

Metrics are not a dashboard decoration. They are decision inputs for scaling and safety.

Start with:

- Request count
- Error rate
- Latency (p50, p95, p99)
- Tool error rate
- Token usage per request

Then define alert thresholds (example: error rate > 5% for 5 minutes).

Also track baseline values during healthy runs so you can spot drift; without baselines, every spike looks the same.

---

## Implementation Guide (using core modules)

Use these repo assets to make the chapter actionable:

- Structured logging: `src/agent_labs/observability/logger.py`
- Tracing spans: `src/agent_labs/observability/tracer.py`
- Metrics collector: `src/agent_labs/observability/metrics.py`
- Lab: `labs/06/README.md`
- Runnable snippet: `curriculum/presentable/02_intermediate/snippets/ch04_tracing_and_metrics.py`

Suggested sequence:

1. Wrap each orchestration phase in a span.
2. Emit a structured log per phase.
3. Record latency and error metrics.

**Deliverable:** a debugging checklist + metrics thresholds.

---

## Common Pitfalls and How to Avoid Them

1. **Logs without context:** Without a run ID, you cannot correlate events.
2. **Tracing only on success:** You need traces for failures the most.
3. **No alert thresholds:** Metrics without thresholds do not protect systems.
4. **Over-logging:** Too many logs can become noise; focus on signals first.

---

## 4.7 Incident Workflow (What to Do When It Breaks)

Observability is only useful if it changes your response. Define a lightweight incident workflow:

1. **Triage**: Identify the failing run by `run_id` or `trace_id`.
2. **Scope**: Check error rate and latency charts to see if the issue is isolated or systemic.
3. **Diagnose**: Inspect the slowest span and recent tool failures.
4. **Mitigate**: Apply a safe fallback (disable a tool, reduce retries, switch to a smaller model).
5. **Learn**: Update thresholds or add missing log fields.

If you cannot complete these steps in under 10 minutes, your observability is not sufficient.

**Practical tip:** Add a "diagnostic snapshot" function that prints the last trace, key metrics, and recent tool errors in one place. This becomes your first responder toolkit during incidents.

---

## Summary

### Key Takeaways

1. **Structured JSON logs** enable machine-readable analysis and alerting.

2. **Execution traces** capture the complete request lifecycle with timing for every component.

3. **Metrics** provide aggregated views for monitoring system health and performance.

4. **Log levels** control verbosity—DEBUG for troubleshooting, INFO for production.

5. **Trace analysis** identifies bottlenecks and enables request replay for debugging.

### What's Next

In Chapter 05, you'll learn about **Multi-Turn Conversations**—how to design conversation flows, manage state across turns, and handle context preservation.

---

## References

- **Lab 6:** [labs/06/README.md](../../../labs/06/README.md) — Observability hands-on exercises
- **Source Code:** [labs/06/src/observable_agent.py](../../../labs/06/src/observable_agent.py)
- **Observability Module:** [src/agent_labs/observability/](../../../src/agent_labs/observability/)
- **OpenTelemetry:** [opentelemetry.io](https://opentelemetry.io/) — Industry-standard observability framework

---

## Exercises

Complete these exercises in the workbook to reinforce your learning:

1. **Trace Analysis:** Run Lab 6's agent with 3 different queries. Export traces and identify which query had the highest LLM latency.

2. **Log Level Comparison:** Run the same query with DEBUG, INFO, and WARNING levels. Count the log lines produced at each level.

3. **Bottleneck Detection:** Implement `analyze_trace()` and find the component consuming >50% of execution time.

4. **Custom Metrics:** Add a `memory_retrieval_latency` metric and track it across 10 requests.

5. **Alerting Prototype:** Write a function that triggers an alert when `error_rate > 5%` or `p99_latency > 1000ms`.

---

[Prev](chapter_03_context_engineering.md) | [Up](README.md) | [Next](chapter_05_multi_turn_conversations.md)
