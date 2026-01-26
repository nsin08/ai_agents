# Copilot Instructions: AI Agents

**Framework:** space_framework (SDLC Governance Control Plane)  
**Framework Repository:** https://github.com/nsin08/space_framework  
**Purpose:** Comprehensive AI agent learning platform with knowledge base, curriculum, and hands-on labs  
**Last Updated:** 2026-01-11

---

## Framework Integration

This project follows the **space_framework** governance model for AI-native SDLC enforcement.

**Load Framework Context:**
All governance rules are loaded from the framework repository. When working on this project, reference:

@workspace https://github.com/nsin08/space_framework

Or if using Copilot Spaces:

@space_framework

**Core Framework Principles:**
- **Enforcement-first:** Automation enforces policy, not documentation
- **State machine:** All work flows through: Idea → Approved → Ready → In Progress → In Review → Done → Released
- **Artifact linking:** Every PR links to Story, every Story links to Epic
- **Approval gates:** Only CODEOWNER can merge PRs
- **Evidence-based:** PRs require evidence (tests, screenshots, metrics)

---

## 1.1 Environment Awareness (Reduce Retries)

Agents MUST adapt to the user's environment and avoid guessing.

### Preflight (run once before GitHub/Git operations)

- Detect which shell you are in and output commands for that shell only.
- If the environment is unknown, ask the user: OS + shell (Windows PowerShell vs WSL bash vs macOS zsh).
- If the repo includes helper scripts, prefer running one preflight:
  - PowerShell: `scripts/env-preflight.ps1`
  - bash/zsh (Linux/macOS/WSL): `scripts/env-preflight.sh`
- Confirm `git` exists (`git --version`).
- Confirm `gh` exists (`gh --version`).
- If you will create/update Issues/PRs/labels: confirm auth (`gh auth status`).
  - If not authenticated: STOP and ask the user to authenticate. Do not attempt alternate methods.

### Command emission rule (must-follow)

- Emit exactly one command variant matching the detected shell (PowerShell OR bash). Do not mix syntaxes.
- If the user explicitly asks for both, provide both variants labeled clearly.

### GitHub tooling policy

- Prefer `gh` first for GitHub operations (issues/PRs/labels).
- Use GitHub MCP only if the user explicitly asks to use it (and only after checking it is available).
- Do not try multiple approaches for the same action; fail fast with the exact error and missing prerequisite.

### Branch safety

- Do not push directly to protected branches (`main`, `develop`, `release/*`) unless the user explicitly requests it.
- Use PR-based flow for merges; branch protection enforces policy server-side.

---

## Essential Framework Files

When you need governance context, load these from https://github.com/nsin08/space_framework:

**Roles (10-roles/):**
- `00-shared-context.md` — ALWAYS load first for base constraints
- `05-implementer.md` — AI agent implementing Stories
- `06-reviewer.md` — AI agent reviewing PRs
- `09-codeowner.md` — Human maintainer (merge authority)

**Rules (20-rules/):**
- `01-state-machine.md` — Mandatory workflow states and transitions
- `02-definition-of-ready.md` — Exit criteria for state:ready
- `03-definition-of-done.md` — Exit criteria for state:done
- `04-artifact-linking.md` — PR → Story → Epic traceability
- `10-ai-agent-boundaries.md` — What AI agents can/cannot do
- `11-file-organization.md` — Where to place files (tests, temp, context)
- `12-label-taxonomy.md` — Standard label set and meanings

**Templates (50-templates/):**
- `01-idea.md` — Initial business need
- `02-epic.md` — Large feature breakdown
- `03-story.md` — Implementable unit of work
- `05-pull-request.md` — PR structure with evidence
- `05-dor-checklist.md` — Definition of Ready checklist
- `06-dod-checklist.md` — Definition of Done checklist

**Enforcement (70-enforcement/):**
- GitHub Actions workflows validate state transitions, artifact linking, approval gates
- Copy workflows from framework to project `.github/workflows/` as needed

---

## Project-Specific Context

**Project Name:** AI Agents  
**Repository:** nsin08/ai_agents  
**Tech Stack:** Python 3.11+, pytest, LangChain, LangGraph, Pydantic

### Build/Test Commands
```bash
# Installation (editable for development)
python -m pip install -e .

# Test suite (all tests use pytest with asyncio auto-mode)
pytest tests/                                    # Run all tests
pytest tests/unit/                               # Fast tests only (no Ollama/network)
pytest tests/integration/                        # Slow tests (e.g., with Ollama)
pytest tests/ -m "not ollama"                    # Skip tests requiring Ollama instance
pytest tests/ -k "test_agent" -v                 # Run specific tests with output
pytest tests/ --cov=src --cov-report=term-missing  # Coverage report

# Code quality
ruff check src/ tests/                           # Lint (fast Python linter)
ruff check --fix src/ tests/                     # Auto-fix lint issues
black --check src/ tests/                        # Code formatting check
black src/ tests/                                # Auto-format code
mypy src/                                        # Type checking (strict mode)

# Interactive exploration (require running environment)
python scripts/quick_test.py "Your prompt"      # Single-prompt test (uses mock by default)
python scripts/quick_test.py "Prompt" --ollama  # With real Ollama (requires ollama serve)
python scripts/interactive_agent.py              # Full REPL with tools and conversation
python scripts/advanced_interactive_agent.py    # REPL + observability, context, safety
python scripts/explore.py quickstart            # Predefined learning scenarios

# Makefile shortcuts (in scripts/)
cd scripts && make test                         # Run tests from scripts directory
cd scripts && make lint
cd scripts && make format
```

**Key Testing Patterns:**
- **Async-first**: All agent/tool/memory tests use `pytest-asyncio` (async functions marked with `async def test_*()`)
- **Provider-agnostic**: Tests configure `LLM_PROVIDER=mock` by default; use `MockProvider` for deterministic outputs
- **Markers**: Use `@pytest.mark.ollama` for tests requiring live Ollama; use `@pytest.mark.integration` for slow tests
- **Test file locations**: `tests/unit/` for isolated tests (no network/Ollama), `tests/integration/` for real provider tests
- **Mock vs Real**: All labs use mock LLM by default (fast, CI-friendly); configure `LLM_PROVIDER=ollama` for hands-on learning with real model

### Architecture Overview
Monorepo with three integrated layers: (1) production-oriented reference knowledge base (Agents/), (2) modular learning curriculum for multiple skill levels (curriculum/), and (3) framework-agnostic shared core with progressive lab modules (src/agent_labs/ + labs/00-08/). All labs support both mock mode (deterministic, CI-friendly) and real LLM mode (Ollama/cloud) for practical learning.

**Key Architectural Principles:**
- **Framework-agnostic first**: Core teaches fundamentals (control loop, tool contracts, memory, safety) independent of LangChain/LangGraph
- **Pluggable LLM providers**: SingleProvider interface with MockProvider (for tests), OllamaProvider (local), and CloudProvider adapters (OpenAI, Anthropic, Google, Azure)
- **Async-first**: All tools, orchestrator, and memory systems use async/await (pytest-asyncio required)
- **Contract-driven tools**: Tools define input/output schemas via Pydantic, validated before execution; registry manages execution, timing, and error handling
- **State machine orchestrator**: Agent flows through Observe → Plan → Act → Verify states with configurable max turns and timeout enforcement

**Key Components:**
- **Shared Core (src/agent_labs/)**:
  - `llm_providers/`: Provider base class + implementations (MockProvider, OllamaProvider, CloudProvider); env var configured via `LLMProvider` and `ProviderConfig`
  - `orchestrator/`: `Agent` class (control loop), `AgentState` enum (Observe/Plan/Act/Verify), `AgentContext` (conversation history + metadata)
  - `tools/`: `Tool` base class, `ToolContract` (input/output schemas), `ToolRegistry` (async execution + validation), built-in tools (Calculator, WebSearch, FileRead)
  - `memory/`: ConversationMemory (short-term), RAG memory interfaces (long-term retrieval)
  - `safety/`: Guardrails, permission validators, injection detection
  - `observability/`: Structured logging, metrics events, cost attribution
  - `evaluation/`: Golden test runner, regression comparison, reporting
  - `config.py`: Centralized configuration (LLM_PROVIDER, LLM_MODEL, timeouts, defaults)
- **Labs (labs/00-08/)**: Progressive hands-on exercises; each with README (overview), exercise.md (tasks), src/ (runnable code), tests/ (deterministic tests)
- **Curriculum (curriculum/)**: Multi-level learning materials (beginner → intermediate → advanced → pro)

### File Organization (per Rule 11)
- **Application code:** `src/`, `lib/`, `app/` (standard project structure)
- **Tests:** `tests/unit/`, `tests/integration/`, `tests/e2e/`
- **Context docs:** `.context/` (project-level documentation)
- **Task working files:** `.context/tasks-{id}-{slug}__gh/` (temp files, gitignored)
- **CI/CD:** `.github/workflows/`

### Dependencies
**Core:**
- Python >= 3.11
- setuptools >= 65.0

**Development:**
- pytest >= 7.0 (testing framework)
- pytest-asyncio >= 0.21 (async test support)
- pytest-cov >= 4.0 (coverage reporting)
- mypy >= 1.0 (type checking)
- black >= 23.0 (code formatting)
- ruff >= 0.1 (linting)

**Runtime (installed per lab):**
- LangChain (agent orchestration)
- LangGraph (agent state machines)
- Pydantic (data validation)
- Various lab-specific dependencies

### Environment Variables
**LLM Provider Configuration:**
- `LLM_PROVIDER`: Provider type (mock, ollama, openai, anthropic, etc.)
- `LLM_MODEL`: Model name to use (e.g., "llama3.2", "gpt-4", etc.)
- `LLM_BASE_URL`: Base URL for LLM API (e.g., "http://localhost:11434" for Ollama)

**API Keys (when using cloud providers):**
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- Other provider-specific keys as needed

**Testing:**
- Use `LLM_PROVIDER=mock` for deterministic testing (default in CI)
- Use `LLM_PROVIDER=ollama` for local development with real LLM

---

## Codebase-Specific Patterns & Conventions

### LLM Provider Abstraction
All agent code accesses LLMs through the `Provider` interface, never directly. Configuration flows through `ProviderConfig` env vars:

```python
from agent_labs.config import LLMProvider, ProviderConfig
from agent_labs.llm_providers import MockProvider, OllamaProvider

# Configuration from env vars (LLM_PROVIDER, LLM_MODEL, OPENAI_API_KEY, etc.)
config = ProviderConfig(LLMProvider.OLLAMA)
provider = OllamaProvider(model=config.model, base_url=config.base_url)

# In tests, always use MockProvider for deterministic behavior
provider = MockProvider(responses=["answer1", "answer2"])
```

### Tool Design Pattern (Async-First, Contract-Driven)
Tools inherit from `Tool` base class and define Pydantic schemas for inputs/outputs. `ToolRegistry` handles validation, execution, and error handling:

```python
from agent_labs.tools import Tool, ToolContract, ExecutionStatus, ToolResult
from pydantic import BaseModel

class MyToolInput(BaseModel):
    query: str

class MyTool(Tool):
    async def execute(self, **kwargs) -> ToolResult:
        # Always async; ToolRegistry validates against schema
        return ToolResult(
            output="result",
            status=ExecutionStatus.SUCCESS,
            duration=0.5
        )

# Registry execution (async, validated, with timing)
registry = ToolRegistry()
registry.register(MyTool(), "my_tool")
result = await registry.execute("my_tool", query="test")
```

### Agent Orchestrator (State Machine)
The `Agent` class implements Observe → Plan → Act → Verify loop with configurable stop conditions:

```python
from agent_labs.orchestrator import Agent, AgentState, AgentContext

context = AgentContext(user_message="your prompt", max_turns=5, timeout_seconds=30)
agent = Agent(llm_provider=provider, tool_registry=registry)
result = await agent.run(context)  # Returns AgentState.DONE or raises error

# States: Observe (perceive) → Plan (reason) → Act (execute) → Verify (check success)
# Stop on: max_turns exceeded, timeout, explicit done signal, or error
```

### Memory Systems (Conversation + Long-Term)
Short-term memory stores conversation history; long-term memory supports RAG retrieval with write/retrieval policies:

```python
from agent_labs.memory import ConversationMemory

memory = ConversationMemory(max_turns=20)
memory.add_user_message("What is Python?")
memory.add_assistant_message("Python is a programming language...")
context = memory.get_context()  # Returns formatted history for LLM
```

### Configuration Loading
All runtime config flows through `src/agent_labs/config.py`:
- `LLM_PROVIDER`: Which provider to use (mock, ollama, openai, anthropic, google, azure-openai)
- `LLM_MODEL`: Model name (e.g., "mistral:7b", "gpt-4", "claude-3-opus")
- `LLM_BASE_URL`: API endpoint (e.g., "http://localhost:11434" for Ollama)
- Provider-specific keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.
- Agent settings: `AGENT_MAX_TURNS`, `AGENT_TIMEOUT`

### Error Handling Pattern
Providers raise typed exceptions; agents catch and decide recovery:

```python
from agent_labs.llm_providers import ProviderConnectionError, ProviderTimeoutError

try:
    response = await provider.query("prompt")
except ProviderConnectionError:
    # Retry or fallback
except ProviderTimeoutError:
    # Longer timeout or skip
```

### Observability Conventions
Use structured logging for traces; emit events for cost/metrics:

```python
from agent_labs.observability import emit_event

emit_event("agent_turn", {
    "turn": 1,
    "state": "Plan",
    "tokens_used": 150,
    "cost": 0.001
})
```

---

## Testing & Development Workflows

### Running a Single Test
```bash
pytest tests/unit/test_config.py::TestConfigDefaults::test_default_model -v
```

### Debugging an Agent
```bash
# Set log level to DEBUG to see orchestrator state transitions
export DEBUG=1
python scripts/quick_test.py "your prompt"

# Interactive REPL with breakpoint access
python scripts/interactive_agent.py
```

### Adding a New Tool
1. Create class inheriting from `Tool` in `src/agent_labs/tools/`
2. Define input/output Pydantic schemas
3. Implement async `execute()` method
4. Add tests in `tests/unit/test_tools.py`
5. Register in `ToolRegistry` before running agent
6. Document in tool's docstring (used by LLM)

### Adding a Lab
1. Create `labs/NN_topic/` directory
2. Add `README.md` (overview + prerequisites), `exercise.md` (tasks), `src/` (code), `tests/` (tests)
3. Use `LLM_PROVIDER=mock` by default; support `--ollama` flag
4. Ensure deterministic tests pass in CI

---

## AI Agent Responsibilities

When working as an AI agent on this project:

### ✅ What You CAN Do
- Read/create issues following framework templates
- Implement code within assigned Story scope
- Create branches from `develop`: `feature/{story-#}/*` or `fix/{issue-#}/*`
- Open PRs back to `develop` linking to Stories: "Resolves #{story-#}"
- Run tests and provide evidence in PRs
- Request reviews (never self-approve)
- Write files per Rule 11 (tests in `tests/`, context in `.context/`)

### ❌ What You CANNOT Do
- Merge PRs (CODEOWNER only)
- Approve PRs (human reviewers only)
- Skip workflow states (enforced by GitHub Actions)
- Change issue state without meeting exit criteria
- Access secrets/credentials
- Write temp files to project root (Rule 11 violation)

### 🎯 Critical Workflow
1. Load framework context: `@space_framework` or reference GitHub repo
2. Read Story in `state:ready`
3. Create branch from `develop`: `git checkout develop && git pull origin develop && git checkout -b feature/{story-#}/{descriptor}`
4. Implement within Story acceptance criteria
5. Push commits with "fixes #{story-#}" or "feat(story-#): description"
6. Open PR to `develop` (not main) with evidence (tests pass, screenshots, metrics)
7. Request reviewers
8. Wait for approval + CI pass
9. CODEOWNER merges to `develop`
10. Main is synced from develop when ready for release

**Never skip states. Never self-merge. Always provide evidence. All feature branches merge to develop.**

---

## Response Format (REQUIRED)

Every AI agent response MUST follow this structure for clarity and auditability:

```markdown
## 1. Understanding
[What was requested, in 2-3 bullets]

## 2. Actions
- [ ] Action 1
- [ ] Action 2

## 3. Artifacts
| Item | Template | Action |
|------|----------|--------|

## 4. Tool Plan
[Commands to execute]

## 5. Exit Criteria
[What defines done]
```

---

## When You're Stuck

**Missing information?** Explicitly list what's needed:
```markdown
## ⚠️ Cannot Proceed
- Missing: Assignment to Story (required to create branch)
- Missing: Acceptance criteria in Story (needed to scope work)

Please provide above, then re-run with [Role: Implementer].
```

**Invalid state transition?** Check framework `20-rules/01-state-machine.md`:
```markdown
## ⚠️ Transition Blocked
Story cannot move from `state:in-progress` → `state:done` directly.
Required path: In Progress → In Review (PR required) → Done

Next: Open PR linking to this Story.
```

---

## Git Workflow - Branch Strategy

### Branch Naming
- **Feature branches**: `feature/{story-#}/{descriptor}` (e.g., `feature/12-lab-1-rag-fundamentals`)
- **Fix branches**: `fix/{issue-#}/{descriptor}` (e.g., `fix/15-memory-leak`)
- **Release**: `release/{version}` (e.g., `release/0.1.0`)

### Merge Strategy
- **Feature branches** → `develop` (via PR, CODEOWNER merges)
- **Develop** → `main` (when ready for release, CODEOWNER merges)
- **Never merge** feature branches directly to `main`
- **Always use squash merge** for clean commit history

### Base Branch Rules
- **Create from**: Always branch from latest `develop` (`git checkout develop && git pull origin develop`)
- **Submit PR to**: `develop` (base branch in PR)
- **Develop** is release candidate after weekly gate approval
- **Main** is stable release version

---

## Framework Home

**Repository:** https://github.com/nsin08/space_framework  
**Issues/Support:** https://github.com/nsin08/space_framework/issues  
**Documentation:** See framework README and 90-guides/

---
