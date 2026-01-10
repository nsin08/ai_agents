"""
Sample knowledge base for Lab 1.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Document:
    """Represents a knowledge base document."""

    doc_id: str
    title: str
    content: str
    tags: List[str]


def load_documents(path: str | Path) -> List[Document]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    docs = []
    for entry in data:
        docs.append(
            Document(
                doc_id=entry["id"],
                title=entry["title"],
                content=entry["content"],
                tags=entry.get("tags", []),
            )
        )
    return docs
