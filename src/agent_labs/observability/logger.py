"""
Structured logger with context fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .exporters import LogExporter, StdoutExporter
from .formatters import JsonFormatter


@dataclass
class StructuredLogger:
    """Structured logger that emits context-rich records."""

    name: str
    exporter: LogExporter = field(default_factory=StdoutExporter)
    formatter: JsonFormatter = field(default_factory=JsonFormatter)
    context: Dict[str, Any] = field(default_factory=dict)

    def with_context(self, **fields: Any) -> "StructuredLogger":
        merged = dict(self.context)
        merged.update(fields)
        return StructuredLogger(
            name=self.name,
            exporter=self.exporter,
            formatter=self.formatter,
            context=merged,
        )

    def log(self, level: str, message: str, **fields: Any) -> Dict[str, Any]:
        record = {
            "level": level.upper(),
            "message": message,
            "logger": self.name,
        }
        record.update(self.context)
        record.update(fields)
        formatted = self.formatter.format(record)
        self.exporter.emit(record, formatted)
        return record

    def info(self, message: str, **fields: Any) -> Dict[str, Any]:
        return self.log("INFO", message, **fields)

    def warning(self, message: str, **fields: Any) -> Dict[str, Any]:
        return self.log("WARNING", message, **fields)

    def error(self, message: str, **fields: Any) -> Dict[str, Any]:
        return self.log("ERROR", message, **fields)
