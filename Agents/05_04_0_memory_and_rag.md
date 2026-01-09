[Previous](05_03_tools_and_apis_agent.md) | [Next](05_04_1_context_engineering.md)

# Memory and Retrieval-Augmented Generation  

## Table of Contents

- [**5.4 Memory & Retrieval-Augmented Generation (RAG)**](#54-memory-retrieval-augmented-generation-rag)
- [1. Why memory matters](#1-why-memory-matters)
- [2. Types of memory in agent systems](#2-types-of-memory-in-agent-systems)
  - [2.1 Short-term memory (working memory)](#21-short-term-memory-working-memory)
  - [2.2 Long-term memory (persistent memory)](#22-long-term-memory-persistent-memory)
  - [2.3 Knowledge memory (RAG)](#23-knowledge-memory-rag)
- [3. The RAG pipeline](#3-the-rag-pipeline)
  - [3.1 Chunking](#31-chunking)
  - [3.2 Embeddings](#32-embeddings)
  - [3.3 Retrieval & reranking](#33-retrieval-reranking)
  - [3.4 Context assembly](#34-context-assembly)
- [4. Memory management patterns](#4-memory-management-patterns)
  - [4.1 Summarization](#41-summarization)
  - [4.2 Episodic storage](#42-episodic-storage)
  - [4.3 Selective exposure](#43-selective-exposure)
- [5. Memory in the agent loop](#5-memory-in-the-agent-loop)
- [6. Memory safety considerations](#6-memory-safety-considerations)
  - [6.1 Over-retention](#61-over-retention)
  - [6.2 Contamination](#62-contamination)
  - [6.3 Sensitive data handling](#63-sensitive-data-handling)
  - [6.4 Integrity](#64-integrity)
- [7. RAG vs long context](#7-rag-vs-long-context)
  - [Use RAG when:](#use-rag-when)
  - [Use long context when:](#use-long-context-when)
  - [Best practice: hybrid](#best-practice-hybrid)
- [8. Designing memory for scalable agents](#8-designing-memory-for-scalable-agents)
- [9. Summary](#9-summary)


## **5.4 Memory & Retrieval-Augmented Generation (RAG)**

Memory is what transforms an agent from a stateless “respond-once” model into a **context-aware, persistent, and grounded system**. Real workflows require continuity, historical awareness, and the ability to pull relevant knowledge from large corpora — capabilities that pure LLM calls do not provide alone.

This section covers three pillars of memory in agentic systems:

1. **Short-term memory** (working memory)
2. **Long-term memory** (persistent user/system memory)
3. **Knowledge memory (RAG)** (document grounding)

---

## 1. Why memory matters

LLMs are stateless between calls. Agents, however, must:

- track multi-step workflows
- remember tool outputs
- preserve constraints and user preferences
- reason over large documents (policies, manuals, runbooks)
- maintain continuity across long conversations

Memory makes agents reliable, personalized, and less hallucination-prone.

---

## 2. Types of memory in agent systems

### 2.1 Short-term memory (working memory)

**Purpose:** maintain context for the active request/session.

Typically includes:
- recent conversation history
- current plan state (step index, intermediate variables)
- tool outputs and errors
- scratch summaries to stay within context limits

Implementation patterns:
- in-memory state (per request)
- external state store (Redis) for multi-worker systems
- rolling summaries (token-budget management)

Short-term memory is usually **ephemeral** unless explicitly persisted.

---

### 2.2 Long-term memory (persistent memory)

**Purpose:** retain stable, user- or org-specific information across sessions.

Examples:
- user preferences (language, tone, defaults)
- prior resolved tickets / outcomes
- stable environment metadata (tenants, regions, namespaces)
- learned workflows and recurring tasks

Storage options:
- relational DB (Postgres)
- NoSQL store
- “memory events” table (append-only)
- vector memory store (for semantic recall of snippets)

**Rule:** long-term memory should be **intentional, sparse, and sanitized**.

---

### 2.3 Knowledge memory (RAG)

RAG is how agents access large document collections when the model context window is limited.

Common sources:
- policy manuals
- runbooks
- product docs
- internal wikis
- PDFs (technical manuals, compliance docs)
- incident postmortems

RAG reduces hallucinations by grounding outputs in retrieved evidence.

---

## 3. The RAG pipeline

A typical RAG system has these stages:

1. **Ingest** documents
2. **Chunk** into smaller passages
3. **Embed** chunks into vectors
4. **Index** vectors in a vector database
5. **Retrieve** relevant chunks at runtime
6. **Assemble context** into the prompt
7. **Generate** grounded response

### 3.1 Chunking
Good chunks are:
- small enough to be specific
- large enough to contain meaning

Common approaches:
- fixed-size chunking (simple)
- heading/section-based chunking (better)
- semantic chunking (best, more complex)

### 3.2 Embeddings
Embeddings map text to a vector space so “similar meaning” is “close distance”.

Key choices:
- embedding model
- dimensionality
- normalization

### 3.3 Retrieval & reranking
Typical retrieval:
- top-k similarity search

Better retrieval:
- top-k + **reranker** (cross-encoder) for relevance

### 3.4 Context assembly
The orchestrator decides:
- how many chunks to include
- ordering
- whether to include citations or metadata
- what to omit to fit token budget

---

## 4. Memory management patterns

### 4.1 Summarization
Compress long conversations into:
- a rolling summary
- topic summaries
- task-state snapshots

### 4.2 Episodic storage
Persist only key events:
- decisions made
- tool outputs that matter
- final outcomes

### 4.3 Selective exposure
The orchestrator controls what memory enters each prompt.

**Do not** blindly inject all memory into every call.

---

## 5. Memory in the agent loop

```text
User Input
  ↓
Orchestrator loads:
  - short-term state (session)
  - long-term memory (user/system)
  - RAG context (retrieved docs)
  ↓
LLM planning / tool selection
  ↓
Tool calls (outputs written into short-term state)
  ↓
Verification + refinement
  ↓
Final response + optional memory updates
```

Memory supports every stage of **Plan → Act → Verify → Refine**.

---

## 6. Memory safety considerations

### 6.1 Over-retention
Storing too much increases:
- privacy risk
- compliance burden
- noisy prompts

### 6.2 Contamination
Do not store hallucinations or unverified claims as memory.

### 6.3 Sensitive data handling
- minimize PII
- encrypt at rest
- redact logs
- apply retention policies

### 6.4 Integrity
Prevent:
- cross-user memory mixing
- stale knowledge reuse without validation
- silent corruption of long-term memory

---

## 7. RAG vs long context

### Use RAG when:
- knowledge base is large
- documents change frequently
- grounding and citations matter
- cost control is important

### Use long context when:
- the task context is large but temporary
- you need sequential reasoning over the full input

### Best practice: hybrid
Use:
- long context for **workflow state**
- RAG for **knowledge grounding**

---

## 8. Designing memory for scalable agents

Guiding principles:

- store meaning, not raw transcripts
- summarize aggressively
- tag and version memory entries
- separate “preference memory” vs “knowledge memory”
- keep ingestion pipelines observable (what changed, when?)
- make memory writes explicit and reviewable

---

## 9. Summary

Memory is the backbone of reliable agents.
With short-term, long-term, and RAG working together, an agent becomes:

- persistent
- grounded
- context-aware
- capable of multi-step real workflows

Next: **05_05_policies_and_guardrails.md**

[Previous](05_03_tools_and_apis_agent.md) | [Next](05_04_1_context_engineering.md)
