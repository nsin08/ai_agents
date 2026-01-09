"""
Log exporters for routing output.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class LogExporter(ABC):
    """Base class for log exporters."""

    @abstractmethod
    def emit(self, record: Dict[str, Any], formatted: str) -> None:
        raise NotImplementedError


class StdoutExporter(LogExporter):
    """Exporter that writes to stdout."""

    def emit(self, record: Dict[str, Any], formatted: str) -> None:
        print(formatted)


class FileExporter(LogExporter):
    """Exporter that writes to a file."""

    def __init__(self, path: str) -> None:
        self._path = path

    def emit(self, record: Dict[str, Any], formatted: str) -> None:
        with open(self._path, "a", encoding="utf-8") as handle:
            handle.write(formatted + "\n")


class MemoryExporter(LogExporter):
    """Exporter that stores logs in memory (for tests)."""

    def __init__(self) -> None:
        self.records: List[Dict[str, Any]] = []
        self.formatted: List[str] = []

    def emit(self, record: Dict[str, Any], formatted: str) -> None:
        self.records.append(dict(record))
        self.formatted.append(formatted)
