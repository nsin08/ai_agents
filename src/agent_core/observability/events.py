"""RunEvent schema and trace context for observability."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class TraceContext:
    trace_id: str
    span_id: str
    parent_span_id: str | None = None

    @classmethod
    def new(cls) -> "TraceContext":
        return cls(trace_id=uuid4().hex, span_id=uuid4().hex)

    def child(self) -> "TraceContext":
        return TraceContext(
            trace_id=self.trace_id,
            span_id=uuid4().hex,
            parent_span_id=self.span_id,
        )

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
        }
        if self.parent_span_id:
            payload["parent_span_id"] = self.parent_span_id
        return payload


@dataclass(frozen=True)
class RunEvent:
    run_id: str
    event_type: str
    severity: str = "info"
    time: str = field(default_factory=utc_now)
    trace: TraceContext | None = None
    actor: str | None = None
    attrs: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "time": self.time,
            "run_id": self.run_id,
            "event_type": self.event_type,
            "severity": self.severity,
        }
        if self.trace is not None:
            payload["trace"] = self.trace.to_dict()
        if self.actor is not None:
            payload["actor"] = self.actor
        if self.attrs:
            payload["attrs"] = dict(self.attrs)
        return payload


__all__ = ["RunEvent", "TraceContext", "utc_now"]
