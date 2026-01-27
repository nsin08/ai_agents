"""Tests for ObservabilityEmitter."""

from __future__ import annotations

from agent_core.config.models import RedactConfig
from agent_core.observability import MemoryExporter, ObservabilityEmitter, Redactor, RunEvent


def test_emitter_adds_defaults_and_redacts() -> None:
    exporter = MemoryExporter()
    emitter = ObservabilityEmitter([exporter], redactor=Redactor(RedactConfig(pii=True, secrets=True)))

    emitter.emit(
        {
            "run_id": "run-1",
            "event_type": "run.started",
            "attrs": {"api_key": "secret"},
        }
    )

    event = exporter.events[0]
    assert event["severity"] == "info"
    assert "time" in event
    assert event["attrs"]["api_key"] == "<redacted>"


def test_emitter_accepts_run_event() -> None:
    exporter = MemoryExporter()
    emitter = ObservabilityEmitter([exporter])
    event = RunEvent(run_id="run-1", event_type="run.started")

    emitter.emit(event)

    assert exporter.events[0]["run_id"] == "run-1"
