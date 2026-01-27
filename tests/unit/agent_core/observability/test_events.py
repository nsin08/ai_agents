"""Tests for RunEvent schema."""

from __future__ import annotations

from agent_core.observability import RunEvent, TraceContext


def test_run_event_to_dict_includes_required_fields() -> None:
    trace = TraceContext.new()
    event = RunEvent(
        run_id="run-1",
        event_type="run.started",
        trace=trace,
        actor="engine",
        attrs={"state": "init"},
    )

    payload = event.to_dict()

    assert payload["run_id"] == "run-1"
    assert payload["event_type"] == "run.started"
    assert payload["severity"] == "info"
    assert "time" in payload
    assert payload["trace"]["trace_id"] == trace.trace_id
