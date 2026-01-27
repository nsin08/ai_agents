"""Event emitter that dispatches to exporters."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .events import RunEvent, TraceContext, utc_now
from .exporters import EventExporter
from .redaction import Redactor


class ObservabilityEmitter:
    def __init__(
        self,
        exporters: Sequence[EventExporter],
        redactor: Redactor | None = None,
    ) -> None:
        self._exporters = list(exporters)
        self._redactor = redactor or Redactor()

    def emit(self, event: RunEvent | Mapping[str, Any]) -> None:
        payload = self._normalize(event)
        redacted = self._redactor.redact(payload)
        for exporter in self._exporters:
            exporter.export(redacted)

    @staticmethod
    def _normalize(event: RunEvent | Mapping[str, Any]) -> dict[str, Any]:
        if isinstance(event, RunEvent):
            return event.to_dict()
        payload = dict(event)
        payload.setdefault("time", utc_now())
        payload.setdefault("severity", "info")
        trace = payload.get("trace")
        if isinstance(trace, TraceContext):
            payload["trace"] = trace.to_dict()
        return payload


__all__ = ["ObservabilityEmitter"]
