"""Built-in file read tool."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..contract import ExecutionStatus, RiskLevel, ToolContract, ToolConstraints, ToolResult


class FileReadTool:
    """Read text files from disk."""

    def __init__(self, max_lines: int = 200) -> None:
        self._max_lines = max_lines
        self.contract = ToolContract(
            name="file_read",
            description="Read a text file from disk.",
            version="1.0.0",
            risk=RiskLevel.READ,
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "start_line": {"type": "integer", "minimum": 1},
                    "end_line": {"type": "integer", "minimum": 1},
                },
                "required": ["path"],
            },
            output_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                    "start_line": {"type": "integer"},
                    "end_line": {"type": "integer"},
                },
                "required": ["path", "content", "start_line", "end_line"],
            },
            constraints=ToolConstraints(requires_file_access=True),
            metadata={"category": "filesystem"},
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        path_value = kwargs.get("path")
        if not path_value:
            return ToolResult(status=ExecutionStatus.FAILURE, output=None)

        path = Path(str(path_value))
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as exc:  # pragma: no cover - error mapping in executor
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                output=None,
                metadata={"error": str(exc)},
            )

        lines = content.splitlines()
        start_line = int(kwargs.get("start_line") or 1)
        end_line = int(kwargs.get("end_line") or min(len(lines), start_line + self._max_lines - 1))
        end_line = min(end_line, start_line + self._max_lines - 1, len(lines))
        if start_line > len(lines):
            start_line = len(lines)
        if end_line < start_line:
            end_line = start_line

        sliced = lines[start_line - 1 : end_line]
        return ToolResult(
            status=ExecutionStatus.SUCCESS,
            output={
                "path": str(path),
                "content": "\n".join(sliced),
                "start_line": start_line,
                "end_line": end_line,
            },
            metadata={"tool_version": self.contract.version},
        )


__all__ = ["FileReadTool"]
