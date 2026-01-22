import pytest

from src.agent_labs.mcp import (
    McpInvalidArgumentsError,
    McpTool,
    McpToolAdapter,
    McpToolCallResult,
    McpToolNotFoundError,
)
from src.agent_labs.tools import ExecutionStatus, ToolRegistry


class FakeMcpClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []
        self._tools = [
            McpTool(
                name="echo",
                description="Echo back the input.",
                input_schema={
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                },
                output_schema={"type": "string"},
            )
        ]

    def list_tools(self):
        return list(self._tools)

    def call_tool(self, name: str, arguments: dict, *, timeout_s=None):
        self.calls.append({"name": name, "arguments": arguments, "timeout_s": timeout_s})
        if name != "echo":
            raise McpToolNotFoundError(f"Tool not found: {name}")
        if "text" not in arguments:
            raise McpInvalidArgumentsError("Missing required field: text")
        return McpToolCallResult(content=arguments["text"], metadata={"from": "fake"})


@pytest.mark.asyncio
async def test_mcp_tool_adapter_executes_via_tool_registry():
    client = FakeMcpClient()
    tool = client.list_tools()[0]
    adapter = McpToolAdapter(client, tool)

    registry = ToolRegistry()
    registry.register(adapter)

    result = await registry.execute("echo", text="hello", __request_id="req-1")
    assert result.status == ExecutionStatus.SUCCESS
    assert result.output == "hello"
    assert result.metadata["tool_name"] == "echo"
    assert result.metadata["from"] == "fake"
    assert result.metadata["request_id"] == "req-1"
    assert client.calls[-1]["arguments"] == {"text": "hello"}


@pytest.mark.asyncio
async def test_mcp_tool_adapter_maps_invalid_args():
    client = FakeMcpClient()
    tool = client.list_tools()[0]
    adapter = McpToolAdapter(client, tool)

    registry = ToolRegistry()
    registry.register(adapter)

    result = await registry.execute("echo")
    assert result.status == ExecutionStatus.INVALID_INPUT

