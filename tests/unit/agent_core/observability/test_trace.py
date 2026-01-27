"""Tests for TraceContext propagation."""

from __future__ import annotations

from agent_core.observability import TraceContext


def test_trace_child_propagation() -> None:
    root = TraceContext.new()
    child = root.child()

    assert child.trace_id == root.trace_id
    assert child.parent_span_id == root.span_id
    assert child.span_id != root.span_id
