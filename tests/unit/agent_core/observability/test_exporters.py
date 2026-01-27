"""Tests for observability exporters."""

from __future__ import annotations

import json
from io import StringIO

from agent_core.observability import FileExporter, MemoryExporter, StdoutExporter


def test_memory_exporter_collects_events() -> None:
    exporter = MemoryExporter()
    exporter.export({"run_id": "r1", "event_type": "run.started"})

    assert exporter.events[0]["run_id"] == "r1"


def test_stdout_exporter_writes_json() -> None:
    buffer = StringIO()
    exporter = StdoutExporter(stream=buffer)
    exporter.export({"run_id": "r1", "event_type": "run.started"})

    payload = json.loads(buffer.getvalue().strip())
    assert payload["event_type"] == "run.started"


def test_file_exporter_appends_json(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    exporter = FileExporter(str(path))
    exporter.export({"run_id": "r1", "event_type": "run.started"})

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert json.loads(lines[0])["run_id"] == "r1"
