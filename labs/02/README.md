# Lab 2: Tool Integration

## Learning Objectives

- Understand tool contracts (name, description, schemas).
- Discover tools via registry and validate inputs.
- Execute tools and interpret results.
- Handle tool errors and missing tools safely.
- Chain multiple tool calls to complete tasks.

## Overview

This lab demonstrates how agents can discover and call tools. We use a tool
registry to execute a calculator, weather lookup, and file operations tool.

## Tool Integration Architecture

```
Agent → discover → validate → execute → handle error
```

## Tool Schema Specification

Every tool exposes a contract with:

- `name`: unique tool identifier
- `description`: human-readable purpose
- `input_schema`: JSON schema for inputs
- `output_schema`: JSON schema for outputs

## Prerequisites

- Lab 0 environment setup complete
- Lab 1 familiarity with agent workflows
- Basic understanding of function signatures

## Setup Instructions

1. Ensure core tools module exists: `src/agent_labs/tools/`
2. Create a venv and install dependencies (Lab 0 workflow)
3. Run the quick start below

## Lab Structure

```
labs/02/
  README.md
  src/
    custom_tools.py
    tool_agent.py
  tests/
    test_tool_agent.py
  exercises/
    exercise_1.md
    exercise_2.md
    exercise_3.md
```

## Example Trace (Tool Calls)

```
Discovered tools: ['calculator', 'weather_lookup', 'file_ops']
Tool call: calculator(operation=add, a=2, b=3)
Tool result: 5
Tool call: weather_lookup(city=Berlin)
Tool result: {'city': 'Berlin', 'temp_c': 25, 'condition': 'sunny'}
Tool call: file_ops(path=labs/02)
Tool result: {'path': 'labs/02', 'files': ['README.md', 'data.txt']}
Final response: {'calculator': 5, 'weather': {'city': 'Berlin', 'temp_c': 25, 'condition': 'sunny'}, 'files': {'path': 'labs/02', 'files': ['README.md', 'data.txt']}}
```

## Quick Start (under 5 minutes)

```bash
$env:PYTHONPATH='.'; python labs/02/src/tool_agent.py
pytest labs/02/tests/test_tool_agent.py -v
```

## Example Execution Trace

```
Discovered tools: ['calculator', 'weather_lookup', 'file_ops']
Tool call: calculator(operation=add, a=2, b=3)
Tool result: 5
Tool call: weather_lookup(city=Berlin)
Tool result: {'city': 'Berlin', 'temp_c': 25, 'condition': 'sunny'}
Tool call: file_ops(path=labs/02)
Tool result: {'path': 'labs/02', 'files': ['README.md', 'data.txt']}
Final response: {'calculator': 5, 'weather': {'city': 'Berlin', 'temp_c': 25, 'condition': 'sunny'}, 'files': {'path': 'labs/02', 'files': ['README.md', 'data.txt']}}
```

## Tool Contract Specification

A valid tool must:

- Implement `execute(**kwargs)` and return `ToolResult`
- Provide `get_schema()` with `name`, `description`, `input_schema`, `output_schema`
- Validate inputs before execution (directly or via registry)

## Error Handling Patterns

- Tool failure: return `ToolResult` with `status=FAILURE` and `error`
- Missing tool: registry returns `NOT_FOUND`
- Validation error: registry returns `INVALID_INPUT`

### Error Handling Example (simulated failure)

If a tool fails (e.g., divide by zero), the runner surfaces the error instead of crashing:

```
Tool call: calculator(operation=divide, a=1, b=0)
Tool result: Division by zero
Final response: {'calculator': {'error': 'Division by zero'}, 'weather': {'city': 'Berlin', 'temp_c': 25, 'condition': 'sunny'}, 'files': {'path': 'labs/02', 'files': ['README.md', 'data.txt']}}
```

## Notes

- Uses mock tools only (no external APIs).
- Error handling is part of the exercises.

## Exercises

1. **Exercise 1**: Run the agent and observe tool outputs.
   - See `labs/02/src/tool_agent.py` and run it from repo root.
2. **Exercise 2**: Add a new custom tool and register it.
   - Implement a new Tool class in `labs/02/src/custom_tools.py`.
   - Register it in `build_registry()` in `labs/02/src/tool_agent.py`.
3. **Exercise 3**: Handle tool execution errors without crashing.
   - Update `run_tool_sequence()` to check `result.success` and `result.error`.
