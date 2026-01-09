# Lab 1: RAG Fundamentals

## Learning Objectives

- Understand the retrieve → generate flow in RAG systems.
- Build a simple retriever with mock embeddings.
- Observe how retrieved context changes responses.

## Overview

RAG combines retrieval with generation. We retrieve relevant documents
from a knowledge base and inject them into the prompt before generation.

## Lab Structure

```
labs/01/
  README.md
  data/documents.json
  src/
    documents.py
    rag_agent.py
  tests/
    test_rag_agent.py
  exercises/
    exercise_1.md
    exercise_2.md
    exercise_3.md
```

## Example Output

```
Retrieved Documents:
- RAG Overview
- Prompt Grounding
```

## Quick Start

```bash
python labs/01/src/rag_agent.py
pytest labs/01/tests/test_rag_agent.py -v
```

## Notes

- This lab uses mock embeddings for reproducibility.
- No external API calls are made in tests.
