"""
Visualization utilities for evaluation results.
"""

from __future__ import annotations

from typing import Dict, List


def score_distribution(results: List[Dict[str, object]]) -> Dict[str, int]:
    """Bucket scores into simple bins."""
    buckets = {"0-0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, "0.8-1.0": 0}
    for entry in results:
        score = float(entry.get("score", 0.0))
        if score < 0.2:
            buckets["0-0.2"] += 1
        elif score < 0.4:
            buckets["0.2-0.4"] += 1
        elif score < 0.6:
            buckets["0.4-0.6"] += 1
        elif score < 0.8:
            buckets["0.6-0.8"] += 1
        else:
            buckets["0.8-1.0"] += 1
    return buckets


def comparison_chart(scores: Dict[str, float]) -> str:
    """Render a simple ASCII comparison chart."""
    lines = ["Model Comparison"]
    for label, score in scores.items():
        bars = "#" * int(score * 20)
        lines.append(f"{label:20} | {bars} {score:.2f}")
    return "\n".join(lines)
