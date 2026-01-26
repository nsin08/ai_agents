"""Fixture-based tool provider adapter."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..providers import FixtureToolProvider, ToolFixture
from .contract import ExecutionStatus, ToolContract, ToolResult
from .exceptions import ToolNotFound
from .provider import ToolProvider


class FixtureToolProviderAdapter(ToolProvider):
    """Adapter to expose FixtureToolProvider as a ToolProvider."""

    def __init__(self, path: str) -> None:
        self._provider = FixtureToolProvider(path)
        self._contracts = self._build_contracts(self._provider)

    async def list_tools(self) -> Sequence[ToolContract]:
        return list(self._contracts.values())

    async def execute(self, tool_name: str, args: Mapping[str, Any]) -> ToolResult:
        contract = self._contracts.get(tool_name)
        if contract is None:
            raise ToolNotFound(f"Tool '{tool_name}' not available in fixtures.")
        output = await self._provider.execute(tool_name, args, tool_version=contract.version)
        return ToolResult(
            status=ExecutionStatus.SUCCESS,
            output=output,
            metadata={"tool_version": contract.version, "fixture": True},
        )

    @staticmethod
    def _build_contracts(provider: FixtureToolProvider) -> dict[str, ToolContract]:
        contracts: dict[str, ToolContract] = {}
        for fixture in provider.list_fixtures():
            if fixture.tool_name in contracts:
                continue
            contracts[fixture.tool_name] = ToolContract(
                name=fixture.tool_name,
                description=f"Fixture tool for {fixture.tool_name}.",
                version=fixture.tool_version or "1.0.0",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
            )
        return contracts


__all__ = ["FixtureToolProviderAdapter"]
