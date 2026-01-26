# Tools

This document describes tool contracts, the ToolExecutor policy boundary, and built-in tools.

## ToolContract schema

Tool contracts describe a tool's interface and governance requirements.

Required fields:
- `name`
- `version`
- `description`
- `risk` (`read`, `write`, `admin`)
- `input_schema` (JSON Schema)
- `output_schema` (JSON Schema)
- `required_scopes`
- `idempotency` (required for write/admin)
- `data_handling` (PII/secrets logging constraints)

Example:

```python
from agent_core.tools import ToolContract, ToolIdempotency, ToolDataHandling, RiskLevel

contract = ToolContract(
    name="calculator",
    description="Perform basic arithmetic operations.",
    version="1.0.0",
    risk=RiskLevel.READ,
    input_schema={
        "type": "object",
        "properties": {
            "operation": {"type": "string"},
            "a": {"type": "number"},
            "b": {"type": "number"},
        },
        "required": ["operation", "a", "b"],
    },
    output_schema={
        "type": "object",
        "properties": {"value": {"type": "number"}},
        "required": ["value"],
    },
    required_scopes=[],
    idempotency=ToolIdempotency(required=False),
    data_handling=ToolDataHandling(pii=False, secrets=False),
)
```

## ToolExecutor policy enforcement

All tool calls flow through `ToolExecutor`, which enforces:
- Allowlist (deny-by-default)
- Input validation (JSON Schema)
- Read-only policy (blocks write/admin)
- Timeouts (per call or per contract)
- Error normalization
- Audit events (`tool.call.started`, `tool.call.finished`, `tool.call.blocked`)

## Minimal usage

```python
from agent_core import AgentCoreConfig
from agent_core.config.models import ToolsConfig
from agent_core.factories import EngineFactory, ToolExecutorFactory
from agent_core.registry import get_global_registry

registry = get_global_registry()
config = AgentCoreConfig(
    tools=ToolsConfig(allowlist=["calculator"]),
)

tool_factory = ToolExecutorFactory(registry.tool_providers)
engine_factory = EngineFactory(registry.engines)
engine = engine_factory.build_with_config(config, tool_executor_factory=tool_factory)
```

## Add a custom tool

1. Create a tool class with a `ToolContract`.
2. Implement `async execute(**kwargs) -> ToolResult`.
3. Register it in a `ToolProvider`.

Example:

```python
from agent_core.tools import ToolContract, ToolResult, ExecutionStatus, RiskLevel

class MyTool:
    def __init__(self) -> None:
        self.contract = ToolContract(
            name="my_tool",
            description="Custom tool.",
            version="1.0.0",
            risk=RiskLevel.READ,
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"result": {"type": "string"}}},
        )

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            status=ExecutionStatus.SUCCESS,
            output={"result": "ok"},
        )
```

## Built-in tools

- `calculator`: basic arithmetic operations.
- `web_search`: mock search provider (deterministic results).
- `file_read`: read text files from disk (read-only).
