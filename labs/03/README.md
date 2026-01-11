# Lab 3: Orchestrator Patterns (Observe → Plan → Act → Verify → Refine)

## Learning Objectives
- Trace the Observe → Plan → Act → Verify → Refine loop with timing.
- Implement an orchestrator that enforces max_turns and exit conditions.
- Capture structured logs for debugging (state, timestamp, duration, data).
- Practice success, refinement, and graceful failure paths.
- Tune execution flow via `max_turns` and `confidence_threshold`.

## Architecture Overview
```
Turn N:
  Observe → Plan → Act → Verify → (Refine?) → next turn
Exit when: confidence met OR value available OR max_turns reached
```

### Logging Contract
- Timestamp: ISO-8601 UTC with milliseconds.
- Turn number: e.g., `Turn 1/5`.
- State: Observe, Plan, Act, Verify, Refine.
- Duration: `+<ms>` since previous state.
- Data: observation/plan/result/verify context.

## Files
- `src/orchestrator_agent.py` — Core orchestrator with logging and demo.
- `src/reasoning_chain.py` — Human-readable reasoning chain sample.
- `tests/test_orchestrator_agent.py` — Unit tests.
- `exercises/exercise_1.md` — Trace and annotate runs.
- `exercises/exercise_2.md` — Vary `max_turns` and compare outcomes.
- `exercises/exercise_3.md` — Add confidence-based exit and log it.

## Setup & Quick Start
```bash
# From repo root
$env:PYTHONPATH='.'; python labs/03/src/orchestrator_agent.py
pytest labs/03/tests/test_orchestrator_agent.py -v --capture=tee-sys
```

## Example Execution Traces

### Simple Task (Weather)
```
Result: Weather in Seattle: 20C and clear.
Turn 1 Observe @ 2026-01-10T00:00:00.000Z (+0.6ms) {'query': "What's the weather in Seattle?", 'context': {'confidence': 0.0}}
Turn 1 Plan    @ ... (+0.4ms) {'action': 'weather_lookup', 'city': 'Seattle', 'expect': 'weather'}
Turn 1 Act     @ ... (+0.3ms) {'status': 'success', 'response': 'Weather in Seattle: 20C and clear.', 'confidence': 0.7}
Turn 1 Verify  @ ... (+0.2ms) {'reason': 'confidence_met', 'confidence': 0.7}
```

### Multi-Step Math (Refine Flow)
```
Result: Subtotal 35.18, total with shipping 47.18
Turn 1 Observe ... {'query': "What's 15% of $234.50 plus $12 shipping?", ...}
Turn 1 Plan    ... {'action': 'multi_step_math', 'steps': ['percentage', 'addition']}
Turn 1 Act     ... {'status': 'success', 'response': 'Subtotal 35.18, total with shipping 47.18', 'confidence': 0.8, 'value': 47.18}
Turn 1 Verify  ... {'reason': 'value_available', 'confidence': 0.8}
```

### Error Recovery (Missing Tool)
```
Result: Provide a helpful message; unable to use the requested tool.
Turn 1 Observe ... {'query': 'Send email to user@example.com', ...}
Turn 1 Plan    ... {'action': 'respond', 'message': 'I cannot find a suitable tool.'}
Turn 1 Act     ... {'status': 'failure', 'response': 'I cannot find a suitable tool.', 'confidence': 0.2}
Turn 1 Verify  ... {'reason': 'action_failed', 'error': 'I cannot find a suitable tool.'}
Turn 1 Refine  ... {'query': 'Provide a helpful message; unable to use the requested tool.', 'reason': 'action_failed', 'error': 'I cannot find a suitable tool.'}
```

## Exercises
1. **Exercise 1**: Run 3 tasks (weather, math, missing tool). Annotate turns, states, durations, exit condition.
2. **Exercise 2**: Set `max_turns` to 1 vs 10, compare completion vs early stop; produce a table.
3. **Exercise 3**: Add/adjust `confidence_threshold` to exit early when high confidence; log confidence progression.

## Acceptance Criteria Alignment
- State transitions logged with timestamps and durations.
- Step-by-step reasoning traceable; success and failure paths demonstrated.
- Execution completes quickly (<5 seconds in examples).
- Tests in `tests/test_orchestrator_agent.py` cover success, max_turns, trace logging, confidence exit.
