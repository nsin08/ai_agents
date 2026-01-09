"""
Metrics collection utilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MetricsCollector:
    """Collect counters and latency metrics."""

    counters: Dict[str, int] = field(default_factory=dict)
    latencies_ms: Dict[str, List[float]] = field(default_factory=dict)

    def increment(self, name: str, value: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + value

    def record_latency(self, name: str, latency_ms: float) -> None:
        self.latencies_ms.setdefault(name, []).append(latency_ms)

    def snapshot(self) -> Dict[str, Dict[str, float]]:
        summary: Dict[str, Dict[str, float]] = {}
        for name, values in self.latencies_ms.items():
            if not values:
                continue
            summary[name] = {
                "count": float(len(values)),
                "avg_ms": sum(values) / len(values),
                "max_ms": max(values),
            }
        return {
            "counters": dict(self.counters),
            "latencies": summary,
        }
