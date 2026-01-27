"""Event exporters for observability."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import IO, Any, Mapping, Protocol


class EventExporter(Protocol):
    def export(self, event: Mapping[str, Any]) -> None:
        ...


class StdoutExporter:
    def __init__(self, stream: IO[str] | None = None) -> None:
        self._stream = stream or sys.stdout

    def export(self, event: Mapping[str, Any]) -> None:
        self._stream.write(json.dumps(event, default=str) + "\n")
        self._stream.flush()


class FileExporter:
    def __init__(self, path: str = "run_events.jsonl") -> None:
        self._path = Path(path)

    def export(self, event: Mapping[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, default=str) + "\n")


class MemoryExporter:
    def __init__(self) -> None:
        self.events: list[Mapping[str, Any]] = []

    def export(self, event: Mapping[str, Any]) -> None:
        self.events.append(dict(event))


__all__ = ["EventExporter", "StdoutExporter", "FileExporter", "MemoryExporter"]
