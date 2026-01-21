# Labs Index (Lane A)

This folder contains runnable, testable labs that implement agent fundamentals using `src/agent_labs/`.

## Recommended order

Follow labs `00` -> `10` in order unless a curriculum chapter suggests otherwise.

## Lab map

| Lab | Topic | Curriculum (presentable) | Core modules |
|---|---|---|---|
| 00 | Environment setup | `../curriculum/presentable/01_beginner/chapter_01_environment_setup.md` | n/a |
| 01 | RAG fundamentals | `../curriculum/presentable/01_beginner/chapter_03_rag_fundamentals.md` | `../src/agent_labs/retrieval/`, `../src/agent_labs/context/` |
| 02 | Tool integration | `../curriculum/presentable/01_beginner/chapter_04_tool_integration.md` | `../src/agent_labs/tools/` |
| 03 | Orchestrator patterns | `../curriculum/presentable/02_intermediate/chapter_01_orchestrator_patterns.md` | `../src/agent_labs/orchestrator/`, `../src/agent_labs/tools/` |
| 04 | Memory management | `../curriculum/presentable/01_beginner/chapter_05_memory_and_context.md` | `../src/agent_labs/memory/`, `../src/agent_labs/context/` |
| 05 | Context engineering | `../curriculum/presentable/02_intermediate/chapter_03_context_engineering.md` | `../src/agent_labs/context/` |
| 06 | Observability | `../curriculum/presentable/02_intermediate/chapter_04_observability.md` | `../src/agent_labs/observability/` |
| 07 | Safety and guardrails | `../curriculum/presentable/03_advanced/chapter_01_safety_guardrails.md` | `../src/agent_labs/safety/` |
| 08 | Multi-agent systems | `../curriculum/presentable/03_advanced/chapter_02_multi_agent_systems.md` | `../src/agent_labs/orchestrator/`, `../src/agent_labs/tools/` |
| 09 | MCP tool servers | `../curriculum/presentable/02_intermediate/chapter_06_integration_patterns.md` | `../src/agent_labs/mcp/`, `../src/agent_labs/tools/` |
| 10 | Vector retrieval + context packing | `../curriculum/presentable/02_intermediate/chapter_02_advanced_memory.md` | `../src/agent_labs/retrieval/`, `../src/agent_labs/context/manifest.py` |

## Run tips

- Each lab has its own `README.md` with quick start and exercises.
- Tests are deterministic and runnable with `pytest`.
