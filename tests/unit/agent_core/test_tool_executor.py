"""Tests for ToolExecutor policy enforcement."""

from __future__ import annotations

import asyncio

import pytest

from agent_core.config.models import BudgetsConfig, PoliciesConfig
from agent_core.tools import (
    ExecutionStatus,
    RiskLevel,
    ToolCall,
    ToolContract,
    ToolExecutor,
    ToolIdempotency,
    ToolConstraints,
    ToolPermissions,
    ToolResult,
)
from agent_core.tools.provider import ToolProvider


class DummyTool:
    def __init__(self, contract: ToolContract, result: ToolResult | None = None, delay: float = 0.0):
        self.contract = contract
        self._result = result
        self._delay = delay

    async def execute(self, **kwargs):  # type: ignore[override]
        if self._delay:
            await asyncio.sleep(self._delay)
        if self._result is not None:
            return self._result
        return ToolResult(status=ExecutionStatus.SUCCESS, output={"ok": True})


class DummyProvider(ToolProvider):
    def __init__(self, tools: dict[str, DummyTool]) -> None:
        self._tools = tools

    async def list_tools(self):
        return [tool.contract for tool in self._tools.values()]

    async def execute(self, tool_name: str, args):
        return await self._tools[tool_name].execute(**args)


@pytest.mark.asyncio
async def test_allowlist_blocks_tool() -> None:
    contract = ToolContract(name="calculator", description="calc")
    provider = DummyProvider({"calculator": DummyTool(contract)})
    executor = ToolExecutor([provider], allowlist=["calculator"])

    call = ToolCall(tool_name="other_tool", arguments={})
    result = await executor.execute(call)

    assert result.status == ExecutionStatus.FAILURE
    assert result.error is not None
    assert result.error.type == "PolicyViolation"


@pytest.mark.asyncio
async def test_write_path_enforced(tmp_path) -> None:
    contract = ToolContract(
        name="file_write",
        description="file write",
        constraints=ToolConstraints(requires_write=True),
        permissions=ToolPermissions(write_paths=[str(tmp_path)]),
    )
    provider = DummyProvider({"file_write": DummyTool(contract)})
    executor = ToolExecutor([provider], allowlist=["file_write"])

    other_path = tmp_path.parent / "not_allowed.txt"
    call = ToolCall(tool_name="file_write", arguments={"write_path": str(other_path)})
    result = await executor.execute(call)

    assert result.status == ExecutionStatus.FAILURE
    assert result.error is not None
    assert result.error.type == "PolicyViolation"


@pytest.mark.asyncio
async def test_input_validation_fails() -> None:
    contract = ToolContract(
        name="calculator",
        description="calc",
        input_schema={
            "type": "object",
            "properties": {"a": {"type": "number"}},
            "required": ["a"],
        },
    )
    provider = DummyProvider({"calculator": DummyTool(contract)})
    executor = ToolExecutor([provider], allowlist=["calculator"])

    call = ToolCall(tool_name="calculator", arguments={})
    result = await executor.execute(call)

    assert result.status == ExecutionStatus.INVALID_INPUT


@pytest.mark.asyncio
async def test_read_only_blocks_write_tool() -> None:
    contract = ToolContract(
        name="write_tool",
        description="write",
        risk=RiskLevel.WRITE,
        idempotency=ToolIdempotency(required=True),
    )
    provider = DummyProvider({"write_tool": DummyTool(contract)})
    policies = PoliciesConfig(read_only=True)
    executor = ToolExecutor([provider], allowlist=["write_tool"], policies=policies)

    call = ToolCall(tool_name="write_tool", arguments={})
    result = await executor.execute(call)

    assert result.status == ExecutionStatus.FAILURE
    assert result.error is not None
    assert result.error.type == "PolicyViolation"


@pytest.mark.asyncio
async def test_timeout_is_enforced() -> None:
    contract = ToolContract(name="slow_tool", description="slow")
    provider = DummyProvider({"slow_tool": DummyTool(contract, delay=0.05)})
    executor = ToolExecutor([provider], allowlist=["slow_tool"])

    call = ToolCall(tool_name="slow_tool", arguments={}, timeout_ms=1)
    result = await executor.execute(call)

    assert result.status == ExecutionStatus.TIMEOUT


@pytest.mark.asyncio
async def test_output_schema_validation() -> None:
    contract = ToolContract(
        name="tool",
        description="output test",
        output_schema={
            "type": "object",
            "properties": {"value": {"type": "number"}},
            "required": ["value"],
        },
    )
    bad_result = ToolResult(status=ExecutionStatus.SUCCESS, output={"nope": 1})
    provider = DummyProvider({"tool": DummyTool(contract, result=bad_result)})
    executor = ToolExecutor([provider], allowlist=["tool"])

    call = ToolCall(tool_name="tool", arguments={})
    result = await executor.execute(call)

    assert result.status == ExecutionStatus.FAILURE
    assert result.error is not None
    assert result.error.type == "ToolResultInvalid"


@pytest.mark.asyncio
async def test_budget_enforced_per_run() -> None:
    contract = ToolContract(name="tool", description="budget")
    provider = DummyProvider({"tool": DummyTool(contract)})
    policies = PoliciesConfig(budgets=BudgetsConfig(max_tool_calls=1))
    executor = ToolExecutor([provider], allowlist=["tool"], policies=policies)

    call = ToolCall(tool_name="tool", arguments={}, run_id="run-1")
    first = await executor.execute(call)
    second = await executor.execute(call)

    assert first.status == ExecutionStatus.SUCCESS
    assert second.status == ExecutionStatus.FAILURE
    assert second.error is not None
    assert second.error.type == "BudgetExceeded"


@pytest.mark.asyncio
async def test_scopes_required() -> None:
    contract = ToolContract(
        name="scoped_tool",
        description="scoped",
        required_scopes=["scope:read"],
    )
    provider = DummyProvider({"scoped_tool": DummyTool(contract)})
    executor = ToolExecutor([provider], allowlist=["scoped_tool"])

    call = ToolCall(tool_name="scoped_tool", arguments={}, scopes=["scope:write"])
    result = await executor.execute(call)

    assert result.status == ExecutionStatus.FAILURE
    assert result.error is not None
    assert result.error.type == "PolicyViolation"


@pytest.mark.asyncio
async def test_read_path_enforced(tmp_path) -> None:
    contract = ToolContract(
        name="file_read",
        description="file read",
        permissions=ToolPermissions(read_paths=[str(tmp_path)]),
    )
    provider = DummyProvider({"file_read": DummyTool(contract)})
    executor = ToolExecutor([provider], allowlist=["file_read"])

    other_path = tmp_path.parent / "not_allowed.txt"
    call = ToolCall(tool_name="file_read", arguments={"path": str(other_path)})
    result = await executor.execute(call)

    assert result.status == ExecutionStatus.FAILURE
    assert result.error is not None
    assert result.error.type == "PolicyViolation"
