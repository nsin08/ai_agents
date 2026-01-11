"""
Lightweight reasoning chain examples for Lab 3.
"""

from __future__ import annotations

from typing import List


def simple_reasoning_chain(question: str) -> List[str]:
    """
    Produce a short, human-readable reasoning chain.
    Used for demonstrating how the orchestrator logs intermediate steps.
    """
    steps = [
        f"Observe question: {question}",
        "Plan: identify if math or lookup is needed",
        "Act: execute chosen step",
        "Verify: check if goal met",
        "Refine: adjust if still incomplete",
    ]
    return steps
