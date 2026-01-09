"""
Unit tests for observability utilities.
"""

import json
import pytest

from src.agent_labs.observability import (
    StructuredLogger,
    JsonFormatter,
    TextFormatter,
    MemoryExporter,
    Tracer,
    MetricsCollector,
    timeit,
)


def test_json_formatter_outputs_json():
    formatter = JsonFormatter()
    record = {"level": "INFO", "message": "hello"}
    payload = formatter.format(record)
    parsed = json.loads(payload)
    assert parsed["message"] == "hello"
    assert parsed["level"] == "INFO"
    assert "timestamp" in parsed


def test_text_formatter_outputs_text():
    formatter = TextFormatter()
    record = {"level": "INFO", "message": "hello", "step": "plan"}
    payload = formatter.format(record)
    assert "hello" in payload
    assert "plan" in payload


def test_structured_logger_with_context():
    exporter = MemoryExporter()
    logger = StructuredLogger(
        name="test",
        exporter=exporter,
        formatter=JsonFormatter(),
    ).with_context(turn=1)
    logger.info("test message", step="plan")

    assert len(exporter.records) == 1
    record = exporter.records[0]
    assert record["turn"] == 1
    assert record["step"] == "plan"
    assert record["message"] == "test message"


def test_tracer_records_latency():
    exporter = MemoryExporter()
    logger = StructuredLogger(
        name="trace",
        exporter=exporter,
        formatter=JsonFormatter(),
    )
    tracer = Tracer(logger=logger)
    with tracer.span("plan", turn=2):
        pass

    snapshot = tracer.metrics.snapshot()
    assert "plan" in snapshot["latencies"]
    assert snapshot["latencies"]["plan"]["count"] == 1.0


def test_metrics_collector_counts():
    metrics = MetricsCollector()
    metrics.increment("calls")
    metrics.increment("calls", value=2)
    metrics.record_latency("plan", 10.0)
    snapshot = metrics.snapshot()
    assert snapshot["counters"]["calls"] == 3
    assert snapshot["latencies"]["plan"]["count"] == 1.0


def test_timeit_decorator_sync():
    metrics = MetricsCollector()

    @timeit("work", metrics=metrics)
    def work():
        return "ok"

    assert work() == "ok"
    snapshot = metrics.snapshot()
    assert snapshot["latencies"]["work"]["count"] == 1.0


@pytest.mark.asyncio
async def test_timeit_decorator_async():
    metrics = MetricsCollector()

    @timeit("async_work", metrics=metrics)
    async def work():
        return "ok"

    assert await work() == "ok"
    snapshot = metrics.snapshot()
    assert snapshot["latencies"]["async_work"]["count"] == 1.0
