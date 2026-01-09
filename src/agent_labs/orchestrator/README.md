# Orchestrator Agent - Agent Controller

The Orchestrator is a stateful agent controller that implements a goal-directed reasoning loop using Large Language Models (LLMs). It manages agent execution through a well-defined state machine, ensuring reliable and traceable agent behavior.

## Architecture

### State Machine

The orchestrator follows a strict state machine pattern to ensure predictable agent behavior:

```
┌─────────────┐
│  OBSERVING  │◄──────────────────────┐
└─────┬───────┘                       │
      │                               │
      ▼                               │
┌─────────────┐                       │
│  PLANNING   │                       │
└─────┬───────┘                       │
      │                               │
      ▼                               │
┌─────────────┐                       │
│   ACTING    │                       │
└─────┬───────┘                       │
      │                               │
      ▼                               │
┌─────────────┐                       │
│  VERIFYING  │                       │
└─────┬───────┘                       │
      │                               │
      ├─────────────┬─────────────────┤
      │             │                 │
      ▼             ▼                 ▼
┌─────────────┐ ┌──────────┐  ┌──────────┐
│  REFINING   │ │   DONE   │  │  FAILED  │
└─────┬───────┘ └──────────┘  └──────────┘
      │
      └──────────────────────────────┘
```

**State Descriptions:**

- **OBSERVING**: Initial state where the agent receives its goal and observes the environment/inputs
- **PLANNING**: Agent generates a plan to achieve the goal
- **ACTING**: Agent executes the plan, potentially using tools or APIs
- **VERIFYING**: Agent checks if the goal has been achieved
- **REFINING**: Agent adjusts its approach based on feedback (if verification failed)
- **DONE**: Terminal state - goal successfully achieved
- **FAILED**: Terminal state - max iterations reached without achieving goal

### Valid State Transitions

The orchestrator enforces strict transition rules:

| From State | To States                    |
|-----------|------------------------------|
| OBSERVING | PLANNING, FAILED             |
| PLANNING  | ACTING, FAILED               |
| ACTING    | VERIFYING, FAILED            |
| VERIFYING | DONE, REFINING, FAILED       |
| REFINING  | OBSERVING, FAILED            |
| DONE      | *(terminal)*                 |
| FAILED    | *(terminal)*                 |

Invalid transitions raise `StateTransitionError`.

## Core Components

### AgentContext

The `AgentContext` dataclass holds all runtime state:

```python
from src.agent_labs.orchestrator import AgentContext, AgentState

context = AgentContext(
    goal="Generate a weather report for Seattle",
    inputs={"location": "Seattle", "days": 7},
    current_state=AgentState.OBSERVING,
    metadata={"user_id": "12345"}
)

# Add to conversation history
context.add_history("user", "What's the weather in Seattle?")
context.add_history("assistant", "Fetching weather data...")

# Get recent history for prompts
recent = context.get_recent_history(n=3)

# Format for LLM prompt
history_str = context.format_history()
```

### VerificationResult

Verification returns rich results for decision-making:

```python
from src.agent_labs.orchestrator import VerificationResult

result = VerificationResult(
    is_complete=True,
    confidence=0.95,
    reason="Weather data includes 7-day forecast with temperatures and conditions",
    feedback=""  # Optional feedback for refinement if not complete
)
```

### Exceptions

Custom exceptions for different failure modes:

- `OrchestratorError` - Base exception for all orchestrator errors
- `MaxTurnsExceededError` - Agent reached max iterations without completing goal
- `VerificationError` - Verification process failed
- `PlanningError` - Failed to generate valid plan
- `ActionExecutionError` - Failed to execute action
- `StateTransitionError` - Attempted invalid state transition

## Usage

### Basic Usage

```python
from src.agent_labs.providers import MockProvider
from src.agent_labs.orchestrator import Agent, AgentContext

# Create agent with LLM provider
provider = MockProvider()
agent = Agent(provider=provider, model="mock")

# Run agent with goal
context = AgentContext(goal="Calculate the sum of 42 and 58")
result = await agent.run(context, max_turns=5)

print(f"Result: {result}")
print(f"Final state: {context.current_state}")
print(f"Turns used: {context.turn_count}")
```

### Custom Verification

Inject custom verification logic for domain-specific goal checking:

```python
from src.agent_labs.orchestrator import Agent, AgentContext, VerificationResult

def weather_verifier(context: AgentContext, result: str) -> VerificationResult:
    """Verify weather report contains required data."""
    has_temp = "temperature" in result.lower()
    has_forecast = "forecast" in result.lower()
    
    if has_temp and has_forecast:
        return VerificationResult(
            is_complete=True,
            confidence=1.0,
            reason="Report contains temperature and forecast data"
        )
    else:
        missing = []
        if not has_temp:
            missing.append("temperature")
        if not has_forecast:
            missing.append("forecast")
        
        return VerificationResult(
            is_complete=False,
            confidence=0.3,
            reason=f"Missing data: {', '.join(missing)}",
            feedback=f"Please include {', '.join(missing)} in the report"
        )

# Use custom verifier
agent = Agent(provider=provider, verifier=weather_verifier)
context = AgentContext(goal="Generate a weather report")
result = await agent.run(context)
```

### Custom Tool Execution

Override tool execution for custom integrations:

```python
import httpx

async def api_tool_executor(plan: str) -> str:
    """Execute tools by calling real APIs."""
    if "weather" in plan.lower():
        # Call real weather API
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.weather.com/...")
            return response.json()
    else:
        return f"Executed: {plan}"

agent = Agent(provider=provider, tool_executor=api_tool_executor)
```

### State Change Callbacks

Monitor agent execution with state change callbacks:

```python
from src.agent_labs.orchestrator import AgentState

def log_state_changes(from_state: AgentState, to_state: AgentState):
    """Log all state transitions for observability."""
    logger.info(f"State transition: {from_state.value} -> {to_state.value}")

agent = Agent(
    provider=provider,
    on_state_change=log_state_changes
)
```

### Error Handling

```python
from src.agent_labs.orchestrator import (
    Agent, AgentContext,
    MaxTurnsExceededError,
    StateTransitionError,
    VerificationError
)

try:
    context = AgentContext(goal="Complex task")
    result = await agent.run(context, max_turns=3)
    
    if context.current_state == AgentState.FAILED:
        print(f"Agent failed after {context.turn_count} turns")
    else:
        print(f"Success: {result}")
        
except MaxTurnsExceededError as e:
    print(f"Exceeded {e.turns} turns trying to achieve: {e.goal}")
    
except StateTransitionError as e:
    print(f"Invalid transition: {e.from_state} -> {e.to_state}")
    
except VerificationError as e:
    print(f"Verification failed: {e}")
```

## Integration Points

### LLM Provider

The orchestrator is provider-agnostic and works with any provider implementing the `Provider` interface:

```python
from src.agent_labs.providers import OllamaProvider

# Use Ollama locally
provider = OllamaProvider(base_url="http://localhost:11434")
agent = Agent(provider=provider, model="llama3.2")
```

### Memory Integration

Future integration with memory systems (RAG, context management):

```python
# Coming in Story 1.4
context = AgentContext(
    goal="Answer question about project history",
    memory_refs=["doc_1234", "meeting_notes_5678"]  # References to memory systems
)
```

### Tool Integration

Future integration with tool orchestration (Story 1.3):

```python
# Coming in Story 1.3
from src.agent_labs.tools import ToolRegistry

registry = ToolRegistry()
registry.register_tool("weather", weather_api)
registry.register_tool("calculator", calculate)

agent = Agent(provider=provider, tool_executor=registry.execute)
```

## Development

### Running Tests

```bash
# Run all orchestrator tests
pytest tests/unit/orchestrator/ -v

# Run with coverage
pytest tests/unit/orchestrator/ --cov=src.agent_labs.orchestrator

# Run specific test class
pytest tests/unit/orchestrator/test_agent.py::TestAgentVerificationAndStateTransitions -v
```

### Test Coverage Areas

- ✅ Basic agent execution (run, plan, act, verify, refine)
- ✅ State machine transitions (valid and invalid)
- ✅ Custom verification logic
- ✅ Custom tool execution
- ✅ Max turns behavior
- ✅ Context operations (history, metadata)
- ✅ Error handling and exceptions

## Design Decisions

### Why Injectable Verification?

The original implementation had a critical bug: verification checked `len(result) > 0`, which always returned `True` since actions never return empty strings. This made the agent always exit on the first turn, preventing refinement and multi-turn reasoning.

**Solution**: Make verification injectable with two modes:
1. **Custom verifier** (for testing/domain-specific logic): Users provide their own verification function
2. **LLM-based verifier** (default): Ask the LLM if the goal has been achieved

This makes verification testable and properly goal-directed.

### Why VerificationResult Instead of Bool?

A boolean is insufficient for complex verification scenarios. `VerificationResult` provides:
- `is_complete`: Goal achieved (yes/no)
- `confidence`: How certain is the verification (0.0-1.0)
- `reason`: Why was this conclusion reached
- `feedback`: What should be improved (for refinement)

This enables better debugging, logging, and refinement loops.

### Why Explicit State Machine?

The state machine pattern provides:
- **Predictability**: Only valid transitions are allowed
- **Debuggability**: Current state is always explicit
- **Observability**: State changes can be logged/monitored
- **Documentation**: State diagram is self-documenting

The `STATE_TRANSITIONS` dict makes valid transitions explicit and enforceable.

## References

- **Issue #4**: [Story 1.2: Orchestrator Controller](https://github.com/nsin08/ai_agents/issues/4)
- **Framework**: space_framework SDLC governance
- **Parent**: Epic 1 - Agentic Framework Core
