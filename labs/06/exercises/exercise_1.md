# Exercise 1: Run Agent and Interpret Logs

**Objective:** Read structured logs to understand execution flow.

## Steps
1. Run three queries:
   - `"What's the weather in Seattle?"`
   - `"Use a tool to add 2 and 3"`
   - `"Multi-step tool workflow"`
2. Export trace and metrics:
   - `$env:PYTHONPATH='.'; python labs/06/src/observable_agent.py`
   - `agent.export_trace("labs/06/visualizations/run_trace.json")` (if editing code) or parse console output.
3. Identify in logs:
   - `turn_started`, `llm_request_sent`, `llm_response_received`
   - `tool_call_initiated`, `tool_call_completed` (if applicable)
   - `turn_completed`, `agent_completed`
4. Compute time per component from `duration_ms` fields.

## Deliverable
- Annotated log/trace showing event flow and timing for each query.
