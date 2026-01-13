from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SNIPPETS_DIR = REPO_ROOT / "curriculum" / "presentable" / "02_intermediate" / "snippets"


@pytest.mark.parametrize(
    "script_name, expected_substrings",
    [
        ("ch01_orchestrator_state_transitions.py", ["OK: start_state=", "OK: agent_result_prefix=Executed"]),
        ("ch02_memory_manager_tiers.py", ["OK: short_term_count=", "OK: long_term_count=", "OK: rag_count="]),
        ("ch03_prompt_template_token_count.py", ["OK: estimated_tokens=", "OK: fits_128="]),
        ("ch04_tracing_and_metrics.py", ["OK: latencies_keys="]),
        ("ch05_conversation_history_window.py", ["OK: history_last_3="]),
        ("ch06_tool_registry_batch.py", ["OK: discovered_tools=", "OK: batch_statuses=", "OK: calc_output="]),
    ],
)
def test_intermediate_snippet_runs(script_name: str, expected_substrings: list[str]) -> None:
    script_path = SNIPPETS_DIR / script_name
    assert script_path.exists(), f"missing snippet: {script_path}"

    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env.pop("USE_OLLAMA", None)
    env.pop("OLLAMA_MODEL", None)
    env.pop("OLLAMA_BASE_URL", None)

    completed = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    assert completed.returncode == 0, f"script failed: {script_name}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
    for expected in expected_substrings:
        assert expected in stdout, f"expected '{expected}' in stdout for {script_name}\nSTDOUT:\n{stdout}"

