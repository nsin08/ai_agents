"""
Trace/span management for orchestrator steps.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from time import perf_counter
from typing import Dict, Iterator, Optional

from .logger import StructuredLogger
from .metrics import MetricsCollector


@dataclass
class Span:
    """Represents a timed span."""

    name: str
    start: float
    end: Optional[float] = None

    @property
    def duration_ms(self) -> float:
        end = self.end if self.end is not None else perf_counter()
        return (end - self.start) * 1000


class Tracer:
    """Tracer that emits spans and metrics."""

    def __init__(
        self,
        logger: StructuredLogger,
        metrics: Optional[MetricsCollector] = None,
    ) -> None:
        self._logger = logger
        self._metrics = metrics or MetricsCollector()

    @property
    def metrics(self) -> MetricsCollector:
        return self._metrics

    @contextmanager
    def span(self, name: str, **fields: str) -> Iterator[Span]:
        span = Span(name=name, start=perf_counter())
        try:
            yield span
        finally:
            span.end = perf_counter()
            latency_ms = span.duration_ms
            self._metrics.record_latency(name, latency_ms)
            self._logger.info(
                "Span completed",
                step=name,
                latency_ms=round(latency_ms, 3),
                **fields,
            )
