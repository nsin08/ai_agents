"""
Report generation utilities.
"""

from __future__ import annotations

import json
from typing import Dict, List


def report_json(results: List[Dict[str, object]]) -> str:
    """Generate JSON report."""
    return json.dumps({"results": results}, indent=2)


def report_markdown(results: List[Dict[str, object]]) -> str:
    """Generate Markdown report."""
    lines = [
        "# Evaluation Report",
        "",
        "| Case | Score | Explanation |",
        "|------|-------|-------------|",
    ]
    for entry in results:
        case_id = entry.get("case_id", "")
        score = entry.get("score", 0.0)
        explanation = entry.get("explanation", "")
        lines.append(f"| {case_id} | {score} | {explanation} |")
    return "\n".join(lines)
