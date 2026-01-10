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
ToolRegistry: calculator(operation=add, a=2, b=3) -> 5
ToolRegistry: weather_lookup(city=Berlin) -> {temp_c: 25, condition: sunny}
ToolRegistry: file_ops(path=labs/02) -> {files: [...]}
```

## Quick Start (under 5 minutes)

```bash
python -m labs.02.src.tool_agent
pytest labs/02/tests/test_tool_agent.py -v
```

If you see `ModuleNotFoundError: No module named 'src'`, run with:

```bash
$env:PYTHONPATH='.'; python labs/02/src/tool_agent.py
```

## Example Execution Trace

```
{'calculator': 5, 'weather': {'city': 'Berlin', 'temp_c': 25, 'condition': 'sunny'}, 'files': {'path': 'labs/02', 'files': ['README.md', 'data.txt']}}
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
