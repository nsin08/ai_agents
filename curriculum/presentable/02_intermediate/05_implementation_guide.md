# Level 2 Implementation Guide (Intermediate)

This guide is the “what to run / what to edit” map for the Intermediate curriculum. It connects each chapter to the reusable core (`src/agent_labs/`) and to hands-on labs (`labs/03`–`labs/06`).

## Prerequisites

- Completed Level 1 (Beginner)
- Python 3.11
- Dependencies installed with `uv` (recommended)

## Setup (one-time)

From repo root:

```powershell
uv venv
uv pip install -e ".[dev]"
```

If you prefer not to install editable, set `PYTHONPATH` when running snippets:

```powershell
$env:PYTHONPATH = "src"
```

## How this repo maps to the curriculum

### Core modules (reusable)

- Orchestrator loop: `src/agent_labs/orchestrator/`
- LLM providers: `src/agent_labs/llm_providers/`
- Memory tiers + manager: `src/agent_labs/memory/`
- Context engineering utilities: `src/agent_labs/context/`
- Tools framework: `src/agent_labs/tools/`
- Observability utilities: `src/agent_labs/observability/`
- Safety guardrails: `src/agent_labs/safety/`

### Hands-on labs (learning-by-building)

- Lab 03: `labs/03/README.md` (orchestrator patterns)
- Lab 04: `labs/04/README.md` (memory management)
- Lab 05: `labs/05/README.md` (context engineering)
- Lab 06: `labs/06/README.md` (observability)

### Verified runnable examples (this curriculum)

- Snippets index: `curriculum/presentable/02_intermediate/snippets/README.md`
- Snippet tests: `tests/integration/test_intermediate_snippets.py`

## Chapter-by-chapter “what to do”

### Chapter 1 — Orchestrator Patterns

- Read: `curriculum/presentable/02_intermediate/chapter_01_orchestrator_patterns.md`
- Explore core:
  - `src/agent_labs/orchestrator/agent.py`
  - `src/agent_labs/orchestrator/states.py`
  - `src/agent_labs/orchestrator/context.py`
- Do the lab: `labs/03/README.md`
- Run a verified snippet:
  - `curriculum/presentable/02_intermediate/snippets/ch01_orchestrator_state_transitions.py`

### Chapter 2 — Advanced Memory

- Read: `curriculum/presentable/02_intermediate/chapter_02_advanced_memory.md`
- Explore core:
  - `src/agent_labs/memory/manager.py`
  - `src/agent_labs/memory/short_term.py`
  - `src/agent_labs/memory/long_term.py`
  - `src/agent_labs/memory/rag.py`
- Do the lab: `labs/04/README.md`
- Run a verified snippet:
  - `curriculum/presentable/02_intermediate/snippets/ch02_memory_manager_tiers.py`

### Chapter 3 — Context Engineering

- Read: `curriculum/presentable/02_intermediate/chapter_03_context_engineering.md`
- Explore core:
  - `src/agent_labs/context/templates.py`
  - `src/agent_labs/context/chunking.py`
  - `src/agent_labs/context/tokens.py`
  - `src/agent_labs/context/window.py`
- Do the lab: `labs/05/README.md`
- Run a verified snippet:
  - `curriculum/presentable/02_intermediate/snippets/ch03_prompt_template_token_count.py`

### Chapter 4 — Observability & Monitoring

- Read: `curriculum/presentable/02_intermediate/chapter_04_observability.md`
- Explore core:
  - `src/agent_labs/observability/logger.py`
  - `src/agent_labs/observability/tracer.py`
  - `src/agent_labs/observability/metrics.py`
- Do the lab: `labs/06/README.md`
- Run a verified snippet:
  - `curriculum/presentable/02_intermediate/snippets/ch04_tracing_and_metrics.py`

### Chapter 5 — Multi-Turn Conversations

- Read: `curriculum/presentable/02_intermediate/chapter_05_multi_turn_conversations.md`
- Explore core:
  - `src/agent_labs/orchestrator/context.py` (history format + metadata)
  - `src/agent_labs/context/window.py` (history windowing)
  - `src/agent_labs/memory/short_term.py` (bounded memory)
- Run a verified snippet:
  - `curriculum/presentable/02_intermediate/snippets/ch05_conversation_history_window.py`

### Chapter 6 — Integration Patterns

- Read: `curriculum/presentable/02_intermediate/chapter_06_integration_patterns.md`
- Explore core:
  - `src/agent_labs/tools/contract.py`
  - `src/agent_labs/tools/registry.py`
  - `src/agent_labs/tools/builtin.py`
- Run a verified snippet:
  - `curriculum/presentable/02_intermediate/snippets/ch06_tool_registry_batch.py`

## Running the snippets

From repo root:

```powershell
python curriculum/presentable/02_intermediate/snippets/ch01_orchestrator_state_transitions.py
```

## Running the snippet tests

```powershell
python -m pytest -q tests/integration/test_intermediate_snippets.py
```

