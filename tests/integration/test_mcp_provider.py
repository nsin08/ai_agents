"""Integration tests for MCP tool provider (mocked transport)."""

from __future__ import annotations

import json

import httpx
import pytest

from agent_core.tools import ExecutionStatus, McpToolProvider


@pytest.mark.asyncio
async def test_mcp_provider_list_and_execute() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/tools":
            return httpx.Response(
                200,
                json=[
                    {
                        "name": "calculator",
                        "description": "mock calculator",
                        "version": "1.0.0",
                        "risk": "read",
                        "input_schema": {"type": "object"},
                        "output_schema": {"type": "object"},
                    }
                ],
            )
        if request.url.path == "/execute":
            payload = json.loads(request.content.decode("utf-8"))
            return httpx.Response(
                200,
                json={
                    "status": "success",
                    "output": {"echo": payload["arguments"]},
                },
            )
        return httpx.Response(404, json={"error": "not found"})

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport, base_url="http://mcp.test")

    provider = McpToolProvider(base_url="http://mcp.test", client=client)
    tools = await provider.list_tools()

    assert tools[0].name == "calculator"

    result = await provider.execute("calculator", {"a": 1})
    assert result.status == ExecutionStatus.SUCCESS
    assert result.output == {"echo": {"a": 1}}

    await provider.aclose()
