"""Built-in calculator tool."""

from __future__ import annotations

from typing import Any

from ..contract import ExecutionStatus, RiskLevel, ToolContract, ToolResult


class CalculatorTool:
    """Perform basic arithmetic operations."""

    def __init__(self) -> None:
        self.contract = ToolContract(
            name="calculator",
            description="Perform basic arithmetic operations.",
            version="1.0.0",
            risk=RiskLevel.READ,
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
            output_schema={
                "type": "object",
                "properties": {"value": {"type": "number"}},
                "required": ["value"],
            },
            metadata={"category": "math"},
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        operation = kwargs.get("operation")
        a = kwargs.get("a")
        b = kwargs.get("b")

        try:
            if operation == "add":
                value = a + b
            elif operation == "subtract":
                value = a - b
            elif operation == "multiply":
                value = a * b
            elif operation == "divide":
                if b == 0:
                    raise ZeroDivisionError("Division by zero.")
                value = a / b
            else:
                raise ValueError(f"Unsupported operation '{operation}'.")
        except Exception as exc:  # pragma: no cover - exercised via executor error mapping
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                error=None,
                output=None,
                metadata={"error": str(exc)},
            )

        return ToolResult(
            status=ExecutionStatus.SUCCESS,
            output={"value": value},
            metadata={"tool_version": self.contract.version},
        )


__all__ = ["CalculatorTool"]
