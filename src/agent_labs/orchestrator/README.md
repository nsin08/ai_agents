# Orchestrator (Observe -> Plan -> Act -> Verify -> Refine)

Framework-agnostic orchestration loop for agents. The design is minimal, readable, and extensible with clear integration points for tools, memory, and observability.

## State Diagram (Text)

```
Observe -> Plan -> Act -> Verify -> Done
                     |
                     v
                  Refine -> Observe (loop)
```

## Key Concepts

- **AgentState**: Discrete loop phases including DONE and FAILED.
- **AgentContext**: Shared execution state (goal, inputs, turn count, history, metadata).
- **Agent**: Orchestrator that manages the loop and lifecycle hooks.

## Usage

```python
from agent_labs.orchestrator import Agent
from agent_labs.llm_providers import MockProvider

agent = Agent(provider=MockProvider())
result = await agent.run("What is 2+2?")
print(result)
```

## Integration Hooks

The `Agent` constructor supports hooks so tools, memory, and observability can be injected later:

- `verifier(context, result) -> VerificationResult`: custom verification logic
- `tool_executor(plan) -> str`: custom action execution
- `on_state_change(old_state, new_state)`: state transition callback

These hooks allow tests and labs to control loop behavior without framework coupling.
