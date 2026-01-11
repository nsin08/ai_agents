"""
Lab-specific tool implementations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from src.agent_labs.tools import Tool, ToolContract, ToolResult, ExecutionStatus


@dataclass
class CalculatorTool(Tool):
    """Calculator tool for Lab 2."""

    name: str = "calculator"
    description: str = "Perform arithmetic operations"

    def __post_init__(self) -> None:
        self.contract = ToolContract(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                    },
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["operation", "a", "b"],
            },
            output_schema={"type": "number"},
            tags=["math", "lab"],
        )

    async def execute(self, **kwargs) -> ToolResult:
        op = kwargs.get("operation")
        a = kwargs.get("a")
        b = kwargs.get("b")
        if op not in {"add", "subtract", "multiply", "divide"}:
            return ToolResult(status=ExecutionStatus.FAILURE, error="Invalid operation")
        if op == "divide" and b == 0:
            return ToolResult(status=ExecutionStatus.FAILURE, error="Division by zero")
        if op == "add":
            result = a + b
        elif op == "subtract":
            result = a - b
        elif op == "multiply":
            result = a * b
        else:
            result = a / b
        return ToolResult(status=ExecutionStatus.SUCCESS, output=result)

    def get_schema(self) -> Dict[str, Any]:
        return self.contract.to_dict()


@dataclass
class WeatherLookupTool(Tool):
    """Mock weather lookup tool."""

    name: str = "weather_lookup"
    description: str = "Return mock weather data for a city"

    def __post_init__(self) -> None:
        self.contract = ToolContract(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                },
                "required": ["city"],
            },
            output_schema={"type": "object"},
            tags=["weather", "lab"],
        )

    async def execute(self, **kwargs) -> ToolResult:
        city = kwargs.get("city", "")
        data = {"city": city, "temp_c": 25, "condition": "sunny"}
        return ToolResult(status=ExecutionStatus.SUCCESS, output=data)

    def get_schema(self) -> Dict[str, Any]:
        return self.contract.to_dict()


@dataclass
class FileOpsTool(Tool):
    """Mock file operations tool."""

    name: str = "file_ops"
    description: str = "Mock file operations (list files)"

    def __post_init__(self) -> None:
        self.contract = ToolContract(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
            output_schema={"type": "object"},
            tags=["file", "lab"],
        )

    async def execute(self, **kwargs) -> ToolResult:
        path = kwargs.get("path", ".")
        output = {"path": path, "files": ["README.md", "data.txt"]}
        return ToolResult(status=ExecutionStatus.SUCCESS, output=output)

    def get_schema(self) -> Dict[str, Any]:
        return self.contract.to_dict()
