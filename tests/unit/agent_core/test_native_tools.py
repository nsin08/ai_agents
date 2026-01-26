"""Tests for native built-in tools."""

from __future__ import annotations

import pytest

from agent_core.tools import ExecutionStatus
from agent_core.tools.builtin import CalculatorTool, FileReadTool, WebSearchTool
from agent_core.tools.native import NativeToolProvider


@pytest.mark.asyncio
async def test_native_provider_lists_tools() -> None:
    provider = NativeToolProvider()
    contracts = await provider.list_tools()
    names = {contract.name for contract in contracts}

    assert {"calculator", "web_search", "file_read"} <= names


@pytest.mark.asyncio
async def test_calculator_tool_executes() -> None:
    tool = CalculatorTool()
    result = await tool.execute(operation="add", a=2, b=3)

    assert result.status == ExecutionStatus.SUCCESS
    assert result.output == {"value": 5}


@pytest.mark.asyncio
async def test_web_search_tool_executes() -> None:
    tool = WebSearchTool()
    result = await tool.execute(query="agents", top_k=2)

    assert result.status == ExecutionStatus.SUCCESS
    assert len(result.output["results"]) == 2


@pytest.mark.asyncio
async def test_file_read_tool_executes(tmp_path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("line1\nline2\nline3", encoding="utf-8")

    tool = FileReadTool(max_lines=5)
    result = await tool.execute(path=str(path), start_line=1, end_line=2)

    assert result.status == ExecutionStatus.SUCCESS
    assert "line1" in result.output["content"]
