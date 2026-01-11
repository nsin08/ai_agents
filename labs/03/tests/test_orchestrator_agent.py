import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
LAB_SRC = ROOT / "labs" / "03" / "src"
if str(LAB_SRC) not in sys.path:
    sys.path.insert(0, str(LAB_SRC))

from orchestrator_agent import OrchestratorAgent  # noqa: E402


def test_simple_task_completion():
    agent = OrchestratorAgent(max_turns=5)
    result = agent.run("What's 2 + 2?")
    assert "4" in result
    assert agent.turn_count <= 2


def test_max_turns_enforced():
    agent = OrchestratorAgent(max_turns=1)
    result = agent.run("impossible task")
    assert "Max turns" in result
    assert agent.turn_count == 1


def test_state_trace_logged():
    agent = OrchestratorAgent(max_turns=2)
    agent.run("test query")
    history = agent.get_state_history()
    assert history, "state history should not be empty"
    assert all(entry.duration_ms < 1000 for entry in history)
    states = [entry.state for entry in history]
    # At least Observe, Plan, Act, Verify should appear once.
    for expected in ["Observe", "Plan", "Act", "Verify"]:
        assert expected in states


@pytest.mark.parametrize("threshold", [0.6, 0.8])
def test_confidence_threshold_exit(threshold):
    agent = OrchestratorAgent(max_turns=5, confidence_threshold=threshold)
    result = agent.run("What's 15% of $234.50 plus $12 shipping?")
    assert "shipping" in result.lower()
    assert agent.turn_count == 1
