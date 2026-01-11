# Lab 6: Observability & Monitoring

## Learning Objectives
- Produce structured JSON logs and human-readable traces.
- Trace execution start-to-finish with key events (turns, LLM, tools).
- Collect performance metrics (latency, tokens, tool counts).
- Spot bottlenecks and debug unexpected behavior.
- Control verbosity via log levels.

## Architecture Overview
```
ObservableAgent
  ├─ Structured logging (JSON + console)
  ├─ Trace buffer (in-memory list of events)
  ├─ Metrics (turns, llm_calls, tool_calls, total_time_ms, tokens_used)
  └─ Export (trace + metrics to JSON file)
```

Key events: `agent_started`, `turn_started`, `llm_request_sent`, `llm_response_received`,
`tool_call_initiated`, `tool_call_completed`, `turn_completed`, `agent_completed`, `agent_failed`.

## Setup & Quick Start
```bash
# From repo root
$env:PYTHONPATH='.'; python labs/06/src/observable_agent.py
$env:PYTHONPATH='.'; pytest labs/06/tests/test_observable_agent.py -v --capture=tee-sys
```

## Example Structured Log (JSON)
```json
{
  "timestamp": "2026-01-11T12:45:00.123Z",
  "level": "INFO",
  "event": "llm_response_received",
  "session_id": "demo-session",
  "data": {
    "turn": 1,
    "duration_ms": 12.5,
    "tokens": 45,
    "text_preview": "Here is the answer."
  }
}
```

## Example Execution Trace (Human-Readable)
```
=== Agent Execution Trace ===
Session: demo-session
Query: "What's the weather in Seattle?"

[Turn 1/5]
  Observe → LLM: llm_request_sent
  LLM response: tokens=45, +12ms
  Tool: calculator (add) +4ms
  Turn complete

Total time: 22ms | Tokens: 45 | Tools: 1 | Result: {"status": "success", "result": 5, "tool": "calculator"}
```

## Metrics Snapshot (aggregated)
```json
{
  "turns": 1,
  "llm_calls": 1,
  "tool_calls": 1,
  "total_time_ms": 22.1,
  "tokens_used": 45
}
```

## Exercises
1. **Exercise 1**: Run 3 queries, export logs to JSON, annotate key events and timings.
2. **Exercise 2**: Toggle log levels (DEBUG/INFO/WARNING/ERROR); compare output size vs usefulness.
3. **Exercise 3**: Run a complex query (multi-turn/tool); compute % time per component, identify bottleneck, propose optimizations.

## Files
- `src/observable_agent.py` — Instrumented agent with logs, metrics, trace export.
- `tests/test_observable_agent.py` — Tests for events, metrics, export.
- `exercises/exercise_1.md` — Log interpretation.
- `exercises/exercise_2.md` — Log level comparison.
- `exercises/exercise_3.md` — Bottleneck analysis.
- `visualizations/example_trace.json` — Sample trace.
- `visualizations/example_metrics.json` — Sample metrics snapshot.
