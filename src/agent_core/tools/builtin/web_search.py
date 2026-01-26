"""Built-in web search tool (mock)."""

from __future__ import annotations

from typing import Any

from ..contract import ExecutionStatus, RiskLevel, ToolContract, ToolConstraints, ToolResult


class WebSearchTool:
    """Mock web search returning deterministic results."""

    def __init__(self) -> None:
        self.contract = ToolContract(
            name="web_search",
            description="Search the web (mocked results).",
            version="1.0.0",
            risk=RiskLevel.READ,
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "minimum": 1, "maximum": 10},
                },
                "required": ["query"],
            },
            output_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "url": {"type": "string"},
                                "snippet": {"type": "string"},
                            },
                            "required": ["title", "url", "snippet"],
                        },
                    },
                },
                "required": ["query", "results"],
            },
            constraints=ToolConstraints(requires_network=True),
            metadata={"category": "web"},
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        query = str(kwargs.get("query", "")).strip()
        top_k = int(kwargs.get("top_k") or 5)

        results = [
            {
                "title": f"Result {idx + 1} for '{query}'",
                "url": f"https://example.com/search/{idx + 1}",
                "snippet": f"Mock snippet for '{query}' (item {idx + 1}).",
            }
            for idx in range(top_k)
        ]

        return ToolResult(
            status=ExecutionStatus.SUCCESS,
            output={"query": query, "results": results},
            metadata={"tool_version": self.contract.version},
        )


__all__ = ["WebSearchTool"]
