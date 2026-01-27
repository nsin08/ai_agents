"""Helpers for constructing the observability emitter from config."""

from __future__ import annotations

from typing import Any, Mapping, TYPE_CHECKING

from ..config.models import ObservabilityConfig
from .emitter import ObservabilityEmitter
from .redaction import Redactor

if TYPE_CHECKING:  # pragma: no cover - typing only
    from ..registry import ExporterRegistry


def build_emitter(
    config: ObservabilityConfig,
    registry: "ExporterRegistry",
) -> ObservabilityEmitter:
    exporter_key, exporter_config = _normalize_exporter(config.exporter)
    constructor = registry.get(exporter_key)
    exporter = _construct_exporter(constructor, exporter_config)
    redactor = Redactor(config.redact)
    return ObservabilityEmitter([exporter], redactor=redactor)


def _normalize_exporter(exporter: str) -> tuple[str, Mapping[str, Any]]:
    if not exporter:
        return "stdout", {}
    normalized = exporter.strip().lower()
    if normalized in {"stdout_json", "stdout"}:
        return "stdout", {}
    if normalized.startswith("file:"):
        return "file", {"path": normalized.split("file:", 1)[1].strip() or "run_events.jsonl"}
    return normalized, {}


def _construct_exporter(constructor: Any, config: Mapping[str, Any]) -> Any:
    if not config:
        return constructor()
    try:
        return constructor(**dict(config))
    except TypeError:
        return constructor()


__all__ = ["build_emitter"]
