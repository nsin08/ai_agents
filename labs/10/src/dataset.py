"""Small deterministic dataset for Lab 10."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Doc:
    doc_id: str
    source: str
    tenant_id: str
    text: str


@dataclass(frozen=True)
class GoldenCase:
    case_id: str
    tenant_id: str
    question: str
    reference_answer: str


def sample_docs() -> List[Doc]:
    return [
        Doc(
            doc_id="runbook-1",
            source="runbook",
            tenant_id="t1",
            text="Reset password steps. Step 1: verify identity. Step 2: rotate token.",
        ),
        Doc(
            doc_id="kb-1",
            source="kb",
            tenant_id="t1",
            text="MCP is a tool server protocol. It supports tool discovery and invocation.",
        ),
        Doc(
            doc_id="kb-2",
            source="kb",
            tenant_id="t2",
            text="Tenant t2 only: refund policy. Refunds require approval.",
        ),
    ]


def golden_set() -> List[GoldenCase]:
    return [
        GoldenCase(
            case_id="c1",
            tenant_id="t1",
            question="What is MCP?",
            reference_answer="MCP is a tool server protocol.",
        ),
        GoldenCase(
            case_id="c2",
            tenant_id="t1",
            question="How do I reset password?",
            reference_answer="Reset password steps.",
        ),
    ]

