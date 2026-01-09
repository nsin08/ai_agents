"""
Decorators for performance timing.
"""

from __future__ import annotations

from functools import wraps
from time import perf_counter
from typing import Any, Awaitable, Callable, Optional, TypeVar, Union

from .logger import StructuredLogger
from .metrics import MetricsCollector

F = TypeVar("F", bound=Callable[..., Any])


def timeit(
    metric_name: str,
    metrics: Optional[MetricsCollector] = None,
    logger: Optional[StructuredLogger] = None,
    step: Optional[str] = None,
) -> Callable[[F], F]:
    """Measure execution time and emit metrics/logs."""
    metrics = metrics or MetricsCollector()

    def decorator(func: F) -> F:
        if callable(getattr(func, "__call__", None)) and hasattr(func, "__await__"):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                start = perf_counter()
                result = await func(*args, **kwargs)
                latency_ms = (perf_counter() - start) * 1000
                metrics.record_latency(metric_name, latency_ms)
                if logger:
                    logger.info(
                        "Timed async function",
                        step=step or func.__name__,
                        latency_ms=round(latency_ms, 3),
                    )
                return result

            return async_wrapper  # type: ignore[return-value]

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = perf_counter()
            result = func(*args, **kwargs)
            latency_ms = (perf_counter() - start) * 1000
            metrics.record_latency(metric_name, latency_ms)
            if logger:
                logger.info(
                    "Timed function",
                    step=step or func.__name__,
                    latency_ms=round(latency_ms, 3),
                )
            return result

        return wrapper  # type: ignore[return-value]

    return decorator
