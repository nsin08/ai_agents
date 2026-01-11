import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB_SRC = ROOT / "labs" / "06" / "src"
if str(LAB_SRC) not in sys.path:
    sys.path.insert(0, str(LAB_SRC))

from observable_agent import ObservableAgent  # noqa: E402


def test_logs_include_key_events():
    agent = ObservableAgent(max_turns=2, log_level="DEBUG")
    agent.run("Use a tool to add 2 and 3")
    events = [e["event"] for e in agent.get_trace()]
    for key in ["agent_started", "turn_started", "llm_request_sent", "llm_response_received", "turn_completed", "agent_completed"]:
        assert key in events
    assert "tool_call_initiated" in events
    assert "tool_call_completed" in events


def test_metrics_collected():
    agent = ObservableAgent(max_turns=1)
    agent.run("simple query")
    metrics = agent.get_metrics()
    assert metrics["turns"] == 1
    assert metrics["llm_calls"] == 1
    assert metrics["total_time_ms"] >= 0
    assert metrics["tokens_used"] > 0


def test_trace_export_writes_file():
    agent = ObservableAgent(max_turns=1)
    agent.run("simple query")
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        out_path = tmp.name
    agent.export_trace(out_path)
    with open(out_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "trace" in data and "metrics" in data
    assert len(data["trace"]) > 0
    assert data["metrics"]["turns"] == 1
