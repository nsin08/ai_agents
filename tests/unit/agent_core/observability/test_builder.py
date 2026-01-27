"""Tests for observability emitter builder."""

from __future__ import annotations

from agent_core.config.models import ObservabilityConfig, RedactConfig
from agent_core.observability import FileExporter, MemoryExporter, ObservabilityEmitter
from agent_core.observability.builder import _normalize_exporter, build_emitter
from agent_core.registry import get_global_registry


def test_normalize_exporter_file_path() -> None:
    key, config = _normalize_exporter("file:logs/run.jsonl")
    assert key == "file"
    assert config["path"] == "logs/run.jsonl"


def test_build_emitter_memory_exporter() -> None:
    config = ObservabilityConfig(exporter="memory", redact=RedactConfig(pii=False, secrets=False))
    emitter = build_emitter(config, get_global_registry().exporters)

    assert isinstance(emitter, ObservabilityEmitter)
    assert isinstance(emitter._exporters[0], MemoryExporter)


def test_build_emitter_file_exporter_default() -> None:
    config = ObservabilityConfig(exporter="file", redact=RedactConfig())
    emitter = build_emitter(config, get_global_registry().exporters)

    assert isinstance(emitter._exporters[0], FileExporter)
