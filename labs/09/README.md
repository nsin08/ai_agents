# Lab 9: MCP Tool Servers (Offline Foundations)

## Overview
This lab introduces **Model Context Protocol (MCP)** concepts using an offline, deterministic "fake MCP server".

Goals:
- Discover tools from an MCP-like server
- Allowlist which tools are exposed to the agent
- Invoke remote tools through the existing `agent_labs.tools.ToolRegistry`
- Capture basic correlation metadata (`request_id`, `tool_call_id`)

## Quick Start

```powershell
# From repo root
$env:PYTHONPATH='.'; python labs/09/src/mcp_client_agent.py
$env:PYTHONPATH='.'; pytest labs/09/tests/test_mcp_lab.py -v --capture=tee-sys
```

## Exercises
- `exercises/exercise_1.md` - Tool discovery
- `exercises/exercise_2.md` - Allowlist + schema validation
- `exercises/exercise_3.md` - Correlation IDs + observability fields

## Files
- `src/mcp_client_agent.py` - Example agent that discovers + calls MCP tools
- `src/fake_mcp.py` - Deterministic fake MCP client/server
- `tests/test_mcp_lab.py` - Offline tests

