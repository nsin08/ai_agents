"""Basic MCP tool provider stub."""

from __future__ import annotations

import os
from typing import Any, Mapping, Sequence

import httpx

from .contract import ExecutionStatus, ToolContract, ToolResult
from .exceptions import ToolProviderError
from .provider import ToolProvider


class McpToolProvider(ToolProvider):
    """HTTP-based MCP tool provider (basic)."""

    def __init__(
        self,
        base_url: str,
        timeout_s: float | None = 30.0,
        bearer_token_env: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_s = timeout_s
        self._bearer_token_env = bearer_token_env
        self._client = client or httpx.AsyncClient(timeout=self._timeout_s)
        self._tool_cache: dict[str, ToolContract] = {}

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._bearer_token_env:
            token = os.getenv(self._bearer_token_env, "").strip()
            if token:
                headers["Authorization"] = f"Bearer {token}"
        return headers

    async def list_tools(self) -> Sequence[ToolContract]:
        if self._tool_cache:
            return list(self._tool_cache.values())
        try:
            response = await self._client.get(
                f"{self._base_url}/tools",
                headers=self._headers(),
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:  # pragma: no cover - exercised via executor error mapping
            raise ToolProviderError(f"MCP list_tools failed: {exc}") from exc

        tools_payload = payload.get("tools") if isinstance(payload, dict) else payload
        if not isinstance(tools_payload, list):
            raise ToolProviderError("MCP list_tools returned invalid payload.")

        for tool_payload in tools_payload:
            contract = ToolContract.from_dict(tool_payload)
            self._tool_cache[contract.name] = contract
        return list(self._tool_cache.values())

    async def execute(self, tool_name: str, args: Mapping[str, Any]) -> ToolResult:
        payload = {"tool_name": tool_name, "arguments": dict(args)}
        try:
            response = await self._client.post(
                f"{self._base_url}/execute",
                json=payload,
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:  # pragma: no cover - exercised via executor error mapping
            raise ToolProviderError(f"MCP execute failed: {exc}") from exc

        if isinstance(data, dict) and "status" in data:
            status_raw = str(data.get("status", ExecutionStatus.SUCCESS.value))
            try:
                status = ExecutionStatus(status_raw)
            except ValueError:
                status = ExecutionStatus.FAILURE
            return ToolResult(
                status=status,
                output=data.get("output"),
                metadata={"provider": "mcp"},
            )

        return ToolResult(
            status=ExecutionStatus.SUCCESS,
            output=data,
            metadata={"provider": "mcp"},
        )

    async def aclose(self) -> None:
        await self._client.aclose()


__all__ = ["McpToolProvider"]
