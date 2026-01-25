"""MCP tool adapter.

Wraps MCP-discovered tools so they can run through the existing ToolRegistry.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from ..tools import ExecutionStatus, Tool, ToolContract, ToolResult
from .client import McpClient
from .errors import (
    McpConnectionError,
    McpInvalidArgumentsError,
    McpTimeoutError,
    McpToolNotFoundError,
)
from .types import McpTool


class McpToolAdapter(Tool):
    """Expose an MCP tool as a local Tool."""

    def __init__(
        self,
        client: McpClient,
        tool: McpTool,
        *,
        timeout_s: Optional[float] = None,
        tags: Optional[list[str]] = None,
    ) -> None:
        self.client = client
        self.name = tool.name
        self.description = tool.description
        self.timeout_s = timeout_s
        self.contract = ToolContract(
            name=tool.name,
            description=tool.description,
            input_schema=tool.input_schema,
            output_schema=tool.output_schema,
            tags=(tags or []) + ["mcp"],
        )

    def get_schema(self) -> Dict[str, Any]:
        return self.contract.to_dict()

    async def execute(self, **kwargs: Any) -> ToolResult:
        start = time.perf_counter()

        # Reserve keys that are metadata, not tool arguments.
        reserved: Dict[str, Any] = {}
        arguments: Dict[str, Any] = {}
        for key, value in kwargs.items():
            if key.startswith("__"):
                reserved[key.lstrip("_")] = value
            else:
                arguments[key] = value

        try:
            result = self.client.call_tool(
                self.name,
                arguments,
                timeout_s=self.timeout_s,
            )
        except McpToolNotFoundError as exc:
            return ToolResult(
                status=ExecutionStatus.NOT_FOUND,
                output=None,
                error=str(exc),
                metadata={"tool_name": self.name, **reserved},
                latency_ms=(time.perf_counter() - start) * 1000,
            )
        except McpInvalidArgumentsError as exc:
            return ToolResult(
                status=ExecutionStatus.INVALID_INPUT,
                output=None,
                error=str(exc),
                metadata={"tool_name": self.name, **reserved},
                latency_ms=(time.perf_counter() - start) * 1000,
            )
        except McpTimeoutError as exc:
            return ToolResult(
                status=ExecutionStatus.TIMEOUT,
                output=None,
                error=str(exc),
                metadata={"tool_name": self.name, **reserved},
                latency_ms=(time.perf_counter() - start) * 1000,
            )
        except McpConnectionError as exc:
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                output=None,
                error=str(exc),
                metadata={"tool_name": self.name, **reserved},
                latency_ms=(time.perf_counter() - start) * 1000,
            )
        except Exception as exc:
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                output=None,
                error=f"Unexpected MCP error: {exc}",
                metadata={"tool_name": self.name, **reserved},
                latency_ms=(time.perf_counter() - start) * 1000,
            )

        if not result.ok:
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                output=None,
                error=result.error,
                metadata={"tool_name": self.name, **result.metadata, **reserved},
                latency_ms=(time.perf_counter() - start) * 1000,
            )

        return ToolResult(
            status=ExecutionStatus.SUCCESS,
            output=result.content,
            error=None,
            metadata={"tool_name": self.name, **result.metadata, **reserved},
            latency_ms=(time.perf_counter() - start) * 1000,
        )

