"""Lab 09 demo: discover and invoke MCP tools through ToolRegistry."""

from __future__ import annotations

import asyncio

from src.agent_labs.mcp import McpToolAdapter
from src.agent_labs.tools import ToolRegistry

from fake_mcp import FakeMcpClient


def build_registry_from_mcp(*, allowlist: set[str]) -> ToolRegistry:
    client = FakeMcpClient()
    registry = ToolRegistry()

    for tool in client.list_tools():
        if tool.name not in allowlist:
            continue
        registry.register(McpToolAdapter(client, tool))

    return registry


async def main() -> None:
    registry = build_registry_from_mcp(allowlist={"echo", "add"})

    # Correlation metadata can be passed via reserved kwargs (prefixed with "__").
    result = await registry.execute("add", a=2, b=3, __request_id="req-1", __tool_call_id="tc-1")
    print(result.to_dict())


if __name__ == "__main__":
    asyncio.run(main())
