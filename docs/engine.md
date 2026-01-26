# Execution Engines

This document describes the `ExecutionEngine` interface and the built-in `LocalEngine`
state machine used by `agent_core`.

## Interface

Engines are responsible for coordinating models, tools, memory, and policies for a run.

```python
from agent_core.engine import EngineComponents, RunRequest, RunResult

class ExecutionEngine:
    async def execute(self, request: RunRequest, components: EngineComponents) -> RunResult:
        ...
```

### Core data structures

- `RunRequest`: input text, run_id, budgets (turns/time), metadata, cancellation event.
- `RunResult`: status, output_text, turns, reason, metadata.
- `EngineComponents`: role-based models, ToolExecutor, session memory, policies, event emitter.

## LocalEngine state machine

State order (v1):

```
Initialize -> Observe -> Plan -> Act -> Verify -> Done
```

Notes:
- Initialize: validate request, start budgets, add user message to memory.
- Observe: load current memory context for model calls.
- Plan: call `planner` role (fallback to `actor`) to outline next step.
- Act: call `actor` role to respond or propose tool calls.
- Verify: call `critic` role (if configured) to decide completion.
- Done: return `RunResult` with status and output text.

## Termination conditions

LocalEngine stops early if any of these fire:
- `max_turns` reached -> `status=failed` (`reason="max_turns"`)
- timeout exceeded -> `status=timeout` (`reason="timeout"`)
- token budget exceeded -> `status=budget_exceeded` (`reason="token_budget"`)
- cancellation event set -> `status=cancelled` (`reason="cancelled"`)

## Tool boundary (required)

All tool calls **must** flow through `ToolExecutor`.
LocalEngine never executes tools directly; it only submits ToolCall requests and
stores the ToolResult in memory for follow-up model calls.

## Observability

If an event emitter is provided, LocalEngine emits state transitions:

```
{
  "event_type": "engine.state",
  "run_id": "...",
  "state": "plan",
  "turn": 1,
  "status": "success"
}
```

## Minimal example

```python
from agent_core.engine import EngineComponents, LocalEngine, RunRequest
from agent_core.memory import InMemorySessionStore
from agent_core.providers import MockProvider

engine = LocalEngine()
components = EngineComponents(
    models={
        "planner": MockProvider(),
        "actor": MockProvider(),
    },
    memory=InMemorySessionStore(),
)

result = await engine.execute(RunRequest(input="Hello"), components)
print(result.status, result.output_text)
```
