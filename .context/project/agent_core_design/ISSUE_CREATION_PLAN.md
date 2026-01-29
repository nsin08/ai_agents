# Epic & Story Creation Plan - Phase 1 MVP

**Purpose:** Create GitHub issues for Agent Core Phase 1 MVP implementation with proper space_framework compliance  
**Date:** 2026-01-25  
**Total Issues:** 1 parent epic + 4 child epics + 16 stories = 21 issues

---

## PREREQUISITE: Framework Templates

Load templates from https://github.com/nsin08/space_framework:

```bash
# Load framework templates
gh repo clone nsin08/space_framework /tmp/space_framework
```

**Required Templates:**
- `50-templates/02-epic.md` - Epic template
- `50-templates/03-story.md` - Story template
- `12-rules/12-label-taxonomy.md` - Standard labels

---

## ISSUE CREATION SEQUENCE

### Phase 1: Parent Epic (Issue #85)
### Phase 2: Child Epics (Issues #86, #90, #94, #98)
### Phase 3: Stories - Foundation (Issues #87-#89)
### Phase 4: Stories - Core (Issues #91-#93)
### Phase 5: Stories - Orchestration (Issues #95-#97)
### Phase 6: Stories - Polish (Issues #99-#102)

---

## ISSUE #85: PARENT EPIC - Agent Core Phase 1 MVP

### Template: 02-epic.md

**Issue Title:**
```
Epic: Agent Core Phase 1 MVP Implementation
```

**Labels:**
```
type:epic, state:approved, priority:high, phase:phase-1
```

**Milestone:** `Phase 1 - Agent Core MVP`

**Body:**

```markdown
# Epic: Agent Core Phase 1 MVP Implementation

## Overview

**Epic ID:** #85  
**Parent:** None (top-level)  
**Status:** Approved (following Story #84 GO decision)  
**Duration:** 6-8 weeks  
**Team:** 1-2 engineers  

## Business Context

Implement minimal production-grade AI agent framework enabling developers to:
- Run AI agents with OpenAI/Ollama providers
- Execute tools with deny-by-default policy enforcement
- Reproduce runs deterministically for CI/CD correctness gates
- Observe agent behavior via structured event streams

**Market Need:** Current frameworks lack deterministic testing and production-grade policy enforcement.

**Success Metric:** Enable 10+ internal teams to build reliable agents with 90% test coverage.

## Scope

### In Scope (Phase 1)
- Configuration system (env vars, YAML, precedence)
- Plugin architecture (entry points for providers/tools)
- Model abstraction (OpenAI, Ollama, Mock providers)
- Tool executor with schema validation & policies
- Short-term memory (in-process session storage)
- LocalEngine (Observe → Plan → Act → Verify loop)
- AgentCore public API (library interface)
- Observability (structured events, stdout/file export)
- Artifacts & deterministic mode (reproducible runs)
- Basic CLI (run, validate-config, version)
- Integration tests (real OpenAI/Ollama)
- Documentation & examples

### Out of Scope (Phase 2+)
- Long-term memory (RAG, vector stores)
- Distributed engine (multi-node execution)
- Service mode (HTTP API)
- Advanced CLI (interactive REPL, debugging)
- Complex multi-agent workflows
- Production observability (CloudWatch, DataDog)

## Child Epics

- [ ] Epic #86: Foundation Layer (Week 1-2)
- [ ] Epic #90: Core Capabilities (Week 3-4)
- [ ] Epic #94: Orchestration Layer (Week 5-6)
- [ ] Epic #98: Polish & Release (Week 7-8)

## Success Criteria

### Functional
- [ ] Agent runs successfully with OpenAI provider (real API call)
- [ ] Agent executes tools with allowlist enforcement
- [ ] Deterministic mode: Same input → same output (100% reproducible)
- [ ] Configuration loads from env vars, YAML files, explicit params
- [ ] Plugins register via entry points (no hardcoded imports)

### Quality Gates
- [ ] Test coverage ≥ 85% (unit + integration)
- [ ] Zero critical/high security findings
- [ ] Performance: Agent turn latency < 5s (p95)
- [ ] Documentation complete (README, guides, examples)
- [ ] All 16 stories merged to `release/0.1.0`

### Release Criteria
- [ ] Version tagged: `v0.1.0-alpha`
- [ ] PyPI package published (test.pypi.org)
- [ ] 5+ example agents runnable
- [ ] Migration guide from competitors (LangChain, Haystack)

## Dependencies

### Prerequisites
- [x] Story #84: Technical Review (COMPLETE) - GO decision made
- [ ] Repository structure created
- [ ] CI/CD pipeline configured (.github/workflows/)

### Blockers
None (all prerequisites met)

## Timeline

```
Week 1-2: Foundation (Epic #86)
Week 3-4: Core Capabilities (Epic #90)
Week 5-6: Orchestration (Epic #94)
Week 7-8: Polish & Release (Epic #98)
```

**Target Completion:** 2026-03-15 (8 weeks from 2026-01-25)

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| OpenAI API rate limits hit during testing | Medium | High | Use mock provider for 80% of tests, real provider for 20% |
| Schema validation complexity (tools) | Medium | Medium | Start with simple JSON Schema, iterate in Phase 2 |
| State machine not extensible | High | Low | Document limitation, plan Strategy pattern for Phase 2 |
| Performance regression (latency) | Medium | Medium | Continuous benchmarking in CI (pytest-benchmark) |

## Resources

### Design Documents
- [Technical Review Report](.context/project/agent_core_design/TECHNICAL_REVIEW_REPORT.md)
- [Implementation Plan](.context/project/agent_core_design/IMPLEMENTATION_PLAN.md)
- [Design Pattern Evidence](.context/project/agent_core_design/DESIGN_PATTERN_EVIDENCE.md)
- Design Docs: `.context/project/agent_core_design/design_docs/` (20 docs)
- ADRs: `.context/project/agent_core_design/design_docs/adrs/` (10 ADRs)

### Team
- **Implementer:** AI Agent (Story execution)
- **Reviewer:** Human Developer (PR reviews)
- **CODEOWNER:** Maintainer (Merge authority)

## Acceptance Criteria

- [ ] All 4 child epics complete (Epic #86, #90, #94, #98)
- [ ] All 16 stories merged (Story #87-#102)
- [ ] Release branch ready: `release/0.1.0`
- [ ] Tag created: `v0.1.0-alpha`
- [ ] Documentation published
- [ ] 5+ runnable examples

## Related Issues

- Resolves Technical Review (Story #84) action items
- Blocks: Phase 2 (Long-term memory, Distributed engine)

---

**Created:** 2026-01-25  
**Updated:** 2026-01-25  
**State:** approved
```

**Assignees:** None (Epic-level, assigned at Story level)

**Projects:** Phase 1 - Agent Core MVP

---

## ISSUE #86: EPIC - Foundation Layer

### Template: 02-epic.md

**Issue Title:**
```
Epic: Foundation Layer (Week 1-2)
```

**Labels:**
```
type:epic, state:ready, priority:high, phase:phase-1, layer:foundation
```

**Parent:** #85

**Milestone:** `Week 1-2: Foundation`

**Body:**

```markdown
# Epic: Foundation Layer (Week 1-2)

## Overview

**Epic ID:** #86  
**Parent:** Epic #85 (Agent Core Phase 1 MVP)  
**Status:** Ready  
**Duration:** 2 weeks  
**Team:** 1 engineer  

## Purpose

Establish foundational infrastructure for Agent Core: configuration system, plugin architecture, and test infrastructure. This layer provides the base upon which all other components depend.

## Scope

### Stories
- [ ] Story #87: Configuration System (2 days)
- [ ] Story #88: Plugin Registry & Entry Points (1.5 days)
- [ ] Story #89: Test Infrastructure & Mock Providers (1.5 days)

### Deliverables
- Configuration loading (env vars, YAML, explicit params with precedence)
- Plugin registry (entry points for providers, tools, exporters)
- Test infrastructure (pytest, fixtures, mock providers)
- Example configs (local.yaml, staging.yaml, production.yaml)

## Dependencies

### Prerequisites
- [x] Story #84: Technical Review complete (GO decision)
- [ ] Repository structure initialized
- [ ] pyproject.toml created

### Dependent Components
- All stories in Epic #90, #94, #98 depend on Foundation Layer

## Success Criteria

- [ ] Configuration loads from 3 sources (env, file, explicit) with correct precedence
- [ ] Plugins register via entry points (test with mock provider)
- [ ] pytest runs successfully with async support (pytest-asyncio)
- [ ] Mock providers produce deterministic outputs
- [ ] All 3 foundation stories merged to `release/0.1.0`

## Technical Details

### Configuration System (Story #87)
**Key Design Decisions:**
- Precedence: Explicit > Env Vars > File > Defaults
- Pydantic for validation (runtime + IDE autocomplete)
- JSON Schema for docs/external validation
- No sensitive defaults (API keys must be explicit)

**Reference:** Design Doc 04_configuration.md, ADR-0001

### Plugin Registry (Story #88)
**Key Design Decisions:**
- Entry points for discovery (setuptools)
- Generic Registry base class (reused for models, tools, engines, exporters)
- Lazy loading (load plugin only when requested)

**Reference:** Design Doc 05_plugin_architecture.md, ADR-0003

### Test Infrastructure (Story #89)
**Key Design Decisions:**
- pytest + pytest-asyncio (all agent code is async)
- Fixture factory pattern (avoid duplication)
- Mock providers for deterministic tests (no network calls)
- Real provider markers (@pytest.mark.ollama, @pytest.mark.openai)

**Reference:** Implementation Plan Section 2.3, Story #89

## Timeline

```
Days 1-2:   Story #87 (Config)
Days 3-4:   Story #88 (Plugins) - parallel with #87
Days 4-5:   Story #89 (Test Infra)
```

**Milestone:** End of Week 1

## Risks

| Risk | Mitigation |
|------|------------|
| Config precedence bugs | Comprehensive unit tests (14 scenarios) |
| Plugin discovery fails | Fallback to direct import if entry point missing |
| Async test complexity | Use pytest-asyncio auto mode (auto-detect async tests) |

## Resources

### Design Documents
- Design Doc 04: Configuration (30 pages)
- Design Doc 05: Plugin Architecture (25 pages)
- ADR-0001: Config Precedence
- ADR-0003: Plugin Entry Points

### Code References
- Example: labs/00/src/quick_config_test.py (config loading patterns)
- Example: src/agent_labs/llm_providers/ (provider plugin structure)

## Acceptance Criteria

- [ ] All 3 stories complete (Story #87, #88, #89)
- [ ] Milestone 1 deliverable validated (runnable demo scripts)
- [ ] No blockers for Epic #90 (Core Capabilities)
- [ ] Code reviewed and merged to `release/0.1.0`

---

**Created:** 2026-01-25  
**Parent:** #85  
**State:** ready
```

---

## ISSUE #87: STORY - Configuration System

### Template: 03-story.md

**Issue Title:**
```
Story: Configuration System
```

**Labels:**
```
type:story, state:ready, priority:high, phase:phase-1, layer:foundation, component:config
```

**Parent:** #86

**Milestone:** `Week 1-2: Foundation`

**Estimate:** 2 days

**Body:**

```markdown
# Story: Configuration System

## Story ID
**Number:** #87  
**Epic:** #86 (Foundation Layer)  
**Priority:** High  
**Estimate:** 2 days  

## User Story

**As a** developer integrating Agent Core  
**I want** to configure agents via env vars, YAML files, or explicit params  
**So that** I can deploy agents across local/staging/prod with different settings without code changes

## Context

**Problem:**
Current agent implementations hardcode config (API keys, model names, timeouts), making deployment across environments error-prone and insecure.

**Solution:**
Implement precedence-based config system: Explicit params > Env vars > YAML file > Defaults

**Business Value:**
- Secure: No API keys in code
- Flexible: Same code, different environments
- Developer-friendly: IDE autocomplete via Pydantic

## Acceptance Criteria

### Functional Requirements

1. **Config Loading (Precedence)**
   - [ ] Load from explicit params: `AgentCoreConfig(app=AppConfig(name="custom"))`
   - [ ] Load from env vars: `APP_NAME=custom python script.py`
   - [ ] Load from YAML file: `AgentCoreConfig.from_file("config.yaml")`
   - [ ] Load from defaults: `AgentCoreConfig()` uses sensible defaults
   - [ ] Precedence enforced: Explicit > Env > File > Default
   - [ ] Test: `explicit=X, env=Y, file=Z → result=X` (explicit wins)

2. **Config Validation**
   - [ ] Invalid config raises `ConfigError` with clear message
   - [ ] Missing required fields (e.g., API key for OpenAI) caught at load time
   - [ ] Type mismatches caught: `timeout_s="not-a-number"` raises error
   - [ ] Pydantic validation integrated (runtime validation)
   - [ ] JSON Schema exported for docs: `config.schema.json`

3. **Config Sections**
   - [ ] `app`: name, environment, log_level
   - [ ] `mode`: "deterministic" or "default"
   - [ ] `models`: roles (actor, critic), provider configs
   - [ ] `tools`: allowlist, read_only_mode, providers
   - [ ] `memory`: max_turns, session_store config
   - [ ] `engine`: max_turns, timeout_s, budget
   - [ ] `observability`: exporters (stdout, file, network)

4. **Environment Variable Mapping**
   - [ ] `APP_NAME` → `config.app.name`
   - [ ] `MODEL_PROVIDER` → `config.models.roles.actor.provider`
   - [ ] `OPENAI_API_KEY` → `config.models.providers.openai.api_key`
   - [ ] `TOOL_ALLOWLIST` → `config.tools.allowlist` (comma-separated)
   - [ ] All env vars documented in README

5. **Example Configs**
   - [ ] `examples/configs/local.yaml` (Ollama, no API key)
   - [ ] `examples/configs/staging.yaml` (OpenAI gpt-3.5-turbo)
   - [ ] `examples/configs/production.yaml` (OpenAI gpt-4, restricted tools)
   - [ ] Configs use env var placeholders: `api_key: ${OPENAI_API_KEY}`

### Quality Requirements

6. **Security**
   - [ ] No API keys in default config or example files
   - [ ] Secrets must come from env vars or explicit params (never files)
   - [ ] Validation: Raise error if API key in file (anti-pattern detection)

7. **Testing**
   - [ ] Unit tests: 14 scenarios (precedence, validation, env vars)
   - [ ] Test: Load from file, override with env var
   - [ ] Test: Invalid YAML raises clear error
   - [ ] Test: Missing required field raises error with field name
   - [ ] Coverage: 100% for config loading logic

8. **Documentation**
   - [ ] `docs/configuration.md`: Full config reference
   - [ ] Config schema published: `schemas/agent_core_config.schema.json`
   - [ ] Example usage in README
   - [ ] Env var reference table (20+ variables)

### Technical Constraints

9. **Implementation**
   - [ ] Use Pydantic v2 for validation (not v1)
   - [ ] Config classes dataclass-compatible: `@dataclass` + Pydantic
   - [ ] Precedence via merge utility: `merge_config_value(explicit, env, file, default)`
   - [ ] No global config state (always explicit dependency injection)

10. **Dependencies**
    - [ ] Pydantic >= 2.0
    - [ ] PyYAML >= 6.0
    - [ ] Python-dotenv >= 1.0 (for .env file support)

### Integration Requirements

11. **API Design**
    ```python
    # Usage patterns
    config = AgentCoreConfig.from_file("config.yaml")
    config = AgentCoreConfig.from_env()
    config = AgentCoreConfig(app=AppConfig(name="custom"))
    
    # Merge explicit overrides with file
    config = AgentCoreConfig.from_file("config.yaml", overrides={"mode": "deterministic"})
    ```

12. **Error Handling**
    - [ ] `ConfigError` raised for validation failures
    - [ ] Clear error messages: "Missing API key for provider 'openai' (set OPENAI_API_KEY)"
    - [ ] File not found: "Config file not found: config.yaml"

13. **Performance**
    - [ ] Config load time < 100ms (including file I/O)
    - [ ] No network calls during config load (fail fast)

14. **Observability**
    - [ ] Log config source on load: "Config loaded from: config.yaml + env vars"
    - [ ] Redact secrets in logs: "OPENAI_API_KEY=***"

## Implementation Notes

### File Structure
```
src/agent_core/
  config/
    __init__.py          # Exports AgentCoreConfig
    core.py              # AgentCoreConfig, AppConfig, ModelsConfig
    loader.py            # from_file, from_env, merge logic
    validation.py        # Pydantic validators
    errors.py            # ConfigError, ConfigValidationError
examples/
  configs/
    local.yaml           # Local dev (Ollama)
    staging.yaml         # Staging (OpenAI gpt-3.5)
    production.yaml      # Production (OpenAI gpt-4)
schemas/
  agent_core_config.schema.json  # JSON Schema export
```

### Key Implementation Details

**Precedence Logic:**
```python
def merge_config_value(explicit, env, file, default):
    """Precedence: Explicit > Env > File > Default"""
    return explicit or env or file or default
```

**Validation Strategy:**
Use Pydantic for Python-side validation + JSON Schema for documentation/external validation.

## Definition of Done

- [ ] All 14 acceptance criteria met
- [ ] Code reviewed and approved
- [ ] Tests pass (100% coverage for config loading)
- [ ] Documentation complete
- [ ] Merged to `release/0.1.0` (base branch for Phase 1)

## Linked Issues

### Resolves
- Technical Review Gap C-002: Config precedence ambiguity

### Blocks
- Story #88: Plugin Registry (depends on config system)
- Story #91: Model Abstraction (loads provider configs)
- Story #92: Tool Executor (loads tool allowlist from config)

### Related
- ADR-0001: Config Precedence Decision
- Design Doc 04: Configuration (30 pages)

## Resources

### Design Documents
- [Design Doc 04: Configuration](.context/project/agent_core_design/design_docs/04_configuration.md)
- [ADR-0001: Config Precedence](.context/project/agent_core_design/design_docs/adrs/adr-0001-config-precedence.md)

### Code References
- Example: `labs/00/src/quick_config_test.py` (config loading patterns)
- Example: `src/agent_labs/config.py` (LLMProvider config)

### External References
- Pydantic docs: https://docs.pydantic.dev/latest/
- 12-Factor App (Config): https://12factor.net/config

## Testing Strategy

### Unit Tests (pytest)
```python
# tests/unit/test_config.py
def test_precedence_explicit_wins():
    """Explicit param overrides env var"""
    os.environ["APP_NAME"] = "from-env"
    config = AgentCoreConfig(app=AppConfig(name="explicit"))
    assert config.app.name == "explicit"

def test_env_overrides_file():
    """Env var overrides YAML file"""
    os.environ["MODEL_PROVIDER"] = "openai"
    config = AgentCoreConfig.from_file("tests/fixtures/config_with_ollama.yaml")
    assert config.models.roles["actor"].provider == "openai"

def test_invalid_yaml_raises_error():
    """Malformed YAML raises clear error"""
    with pytest.raises(ConfigError, match="Invalid YAML"):
        AgentCoreConfig.from_file("tests/fixtures/invalid.yaml")
```

### Integration Tests
```python
# tests/integration/test_config_loading.py
@pytest.mark.integration
def test_load_production_config():
    """Production config loads successfully"""
    config = AgentCoreConfig.from_file("examples/configs/production.yaml")
    assert config.models.roles["actor"].provider == "openai"
    assert config.models.roles["actor"].model == "gpt-4"
```

### Coverage Target
- Unit tests: 100% (config is critical)
- Integration tests: 3 scenarios (local, staging, production configs)

## Evidence Requirements

### For PR Review
- [ ] Screenshot: Config loaded from YAML + env override
- [ ] Screenshot: Validation error with clear message
- [ ] Test output: All 14 unit tests pass
- [ ] Coverage report: 100% for `src/agent_core/config/`
- [ ] JSON Schema: `schemas/agent_core_config.schema.json` exported

---

**Created:** 2026-01-25  
**Epic:** #86  
**State:** ready  
**Estimate:** 2 days
```

---

## SUMMARY: All 21 Issues

### Issue Structure

| Issue # | Type | Title | Parent | Milestone | Estimate | Labels |
|---------|------|-------|--------|-----------|----------|--------|
| #85 | Epic | Agent Core Phase 1 MVP | None | Phase 1 | 8 weeks | type:epic, state:approved, priority:high |
| #86 | Epic | Foundation Layer | #85 | Week 1-2 | 2 weeks | type:epic, state:ready, layer:foundation |
| #87 | Story | Configuration System | #86 | Week 1-2 | 2 days | type:story, state:ready, component:config |
| #88 | Story | Plugin Registry | #86 | Week 1-2 | 1.5 days | type:story, state:ready, component:plugin |
| #89 | Story | Test Infrastructure | #86 | Week 1-2 | 1.5 days | type:story, state:ready, component:testing |
| #90 | Epic | Core Capabilities | #85 | Week 3-4 | 2 weeks | type:epic, state:approved, layer:core |
| #91 | Story | Model Abstraction | #90 | Week 3-4 | 3 days | type:story, state:approved, component:model |
| #92 | Story | Tool Executor | #90 | Week 3-4 | 2.5 days | type:story, state:approved, component:tools |
| #93 | Story | Short-Term Memory | #90 | Week 3-4 | 1.5 days | type:story, state:approved, component:memory |
| #94 | Epic | Orchestration Layer | #85 | Week 5-6 | 2 weeks | type:epic, state:approved, layer:orchestration |
| #95 | Story | LocalEngine & State Machine | #94 | Week 5-6 | 3 days | type:story, state:approved, component:engine |
| #96 | Story | AgentCore Public API | #94 | Week 5-6 | 2 days | type:story, state:approved, component:api |
| #97 | Story | Observability | #94 | Week 5-6 | 2 days | type:story, state:approved, component:observability |
| #98 | Epic | Polish & Release | #85 | Week 7-8 | 2 weeks | type:epic, state:approved, layer:polish |
| #99 | Story | Artifacts & Deterministic | #98 | Week 7-8 | 2 days | type:story, state:approved, component:artifacts |
| #100 | Story | Basic CLI | #98 | Week 7-8 | 1.5 days | type:story, state:approved, component:cli |
| #101 | Story | Integration Tests | #98 | Week 7-8 | 2 days | type:story, state:approved, component:testing |
| #102 | Story | Documentation | #98 | Week 7-8 | 1.5 days | type:story, state:approved, component:docs |

---

## ISSUE CREATION COMMANDS

### Prerequisite: Authenticate GitHub CLI

```bash
# Verify authentication
gh auth status

# If not authenticated
gh auth login
```

### Step 1: Create Parent Epic (#85)

```bash
# Create Issue #85 (Epic)
gh issue create \
  --title "Epic: Agent Core Phase 1 MVP Implementation" \
  --label "type:epic,state:approved,priority:high,phase:phase-1" \
  --milestone "Phase 1 - Agent Core MVP" \
  --body-file .context/project/agent_core_design/issues/epic-85-body.md
```

**Note:** Save the body content above to `.context/project/agent_core_design/issues/epic-85-body.md`

### Step 2: Create Child Epics (#86, #90, #94, #98)

```bash
# Epic #86: Foundation Layer
gh issue create \
  --title "Epic: Foundation Layer (Week 1-2)" \
  --label "type:epic,state:ready,priority:high,phase:phase-1,layer:foundation" \
  --milestone "Week 1-2: Foundation" \
  --body-file .context/project/agent_core_design/issues/epic-86-body.md

# Epic #90: Core Capabilities
gh issue create \
  --title "Epic: Core Capabilities (Week 3-4)" \
  --label "type:epic,state:approved,priority:high,phase:phase-1,layer:core" \
  --milestone "Week 3-4: Core" \
  --body-file .context/project/agent_core_design/issues/epic-90-body.md

# Epic #94: Orchestration Layer
gh issue create \
  --title "Epic: Orchestration Layer (Week 5-6)" \
  --label "type:epic,state:approved,priority:high,phase:phase-1,layer:orchestration" \
  --milestone "Week 5-6: Orchestration" \
  --body-file .context/project/agent_core_design/issues/epic-94-body.md

# Epic #98: Polish & Release
gh issue create \
  --title "Epic: Polish & Release (Week 7-8)" \
  --label "type:epic,state:approved,priority:high,phase:phase-1,layer:polish" \
  --milestone "Week 7-8: Polish" \
  --body-file .context/project/agent_core_design/issues/epic-98-body.md
```

### Step 3: Create Stories - Foundation (#87-#89)

```bash
# Story #87: Configuration System
gh issue create \
  --title "Story: Configuration System" \
  --label "type:story,state:ready,priority:high,phase:phase-1,layer:foundation,component:config" \
  --milestone "Week 1-2: Foundation" \
  --body-file .context/project/agent_core_design/issues/story-87-body.md

# Story #88: Plugin Registry
gh issue create \
  --title "Story: Plugin Registry & Entry Points" \
  --label "type:story,state:ready,priority:high,phase:phase-1,layer:foundation,component:plugin" \
  --milestone "Week 1-2: Foundation" \
  --body-file .context/project/agent_core_design/issues/story-88-body.md

# Story #89: Test Infrastructure
gh issue create \
  --title "Story: Test Infrastructure & Mock Providers" \
  --label "type:story,state:ready,priority:high,phase:phase-1,layer:foundation,component:testing" \
  --milestone "Week 1-2: Foundation" \
  --body-file .context/project/agent_core_design/issues/story-89-body.md
```

### Step 4: Create Stories - Core (#91-#93)

```bash
# Story #91: Model Abstraction
gh issue create \
  --title "Story: Model Abstraction & Providers" \
  --label "type:story,state:approved,priority:high,phase:phase-1,layer:core,component:model" \
  --milestone "Week 3-4: Core" \
  --body-file .context/project/agent_core_design/issues/story-91-body.md

# Story #92: Tool Executor
gh issue create \
  --title "Story: Tool Executor & Contracts" \
  --label "type:story,state:approved,priority:high,phase:phase-1,layer:core,component:tools" \
  --milestone "Week 3-4: Core" \
  --body-file .context/project/agent_core_design/issues/story-92-body.md

# Story #93: Short-Term Memory
gh issue create \
  --title "Story: Short-Term Memory" \
  --label "type:story,state:approved,priority:high,phase:phase-1,layer:core,component:memory" \
  --milestone "Week 3-4: Core" \
  --body-file .context/project/agent_core_design/issues/story-93-body.md
```

### Step 5: Create Stories - Orchestration (#95-#97)

```bash
# Story #95: LocalEngine
gh issue create \
  --title "Story: LocalEngine & State Machine" \
  --label "type:story,state:approved,priority:critical,phase:phase-1,layer:orchestration,component:engine" \
  --milestone "Week 5-6: Orchestration" \
  --body-file .context/project/agent_core_design/issues/story-95-body.md

# Story #96: AgentCore API
gh issue create \
  --title "Story: AgentCore Public API" \
  --label "type:story,state:approved,priority:critical,phase:phase-1,layer:orchestration,component:api" \
  --milestone "Week 5-6: Orchestration" \
  --body-file .context/project/agent_core_design/issues/story-96-body.md

# Story #97: Observability
gh issue create \
  --title "Story: Observability & Event System" \
  --label "type:story,state:approved,priority:high,phase:phase-1,layer:orchestration,component:observability" \
  --milestone "Week 5-6: Orchestration" \
  --body-file .context/project/agent_core_design/issues/story-97-body.md
```

### Step 6: Create Stories - Polish (#99-#102)

```bash
# Story #99: Artifacts
gh issue create \
  --title "Story: RunArtifact & Deterministic Mode" \
  --label "type:story,state:approved,priority:high,phase:phase-1,layer:polish,component:artifacts" \
  --milestone "Week 7-8: Polish" \
  --body-file .context/project/agent_core_design/issues/story-99-body.md

# Story #100: CLI
gh issue create \
  --title "Story: Basic CLI" \
  --label "type:story,state:approved,priority:medium,phase:phase-1,layer:polish,component:cli" \
  --milestone "Week 7-8: Polish" \
  --body-file .context/project/agent_core_design/issues/story-100-body.md

# Story #101: Integration Tests
gh issue create \
  --title "Story: Integration Tests & Performance" \
  --label "type:story,state:approved,priority:high,phase:phase-1,layer:polish,component:testing" \
  --milestone "Week 7-8: Polish" \
  --body-file .context/project/agent_core_design/issues/story-101-body.md

# Story #102: Documentation
gh issue create \
  --title "Story: Documentation & Examples" \
  --label "type:story,state:approved,priority:medium,phase:phase-1,layer:polish,component:docs" \
  --milestone "Week 7-8: Polish" \
  --body-file .context/project/agent_core_design/issues/story-102-body.md
```

---

## POST-CREATION: Link Issues

### Update Epic #85 with Child Epic Links

```bash
# After creating child epics, update #85 body with actual issue numbers
gh issue edit 85 --body-file .context/project/agent_core_design/issues/epic-85-body-updated.md
```

**Update body to include:**
```markdown
## Child Epics

- [ ] Epic #86: Foundation Layer (Week 1-2)
- [ ] Epic #90: Core Capabilities (Week 3-4)
- [ ] Epic #94: Orchestration Layer (Week 5-6)
- [ ] Epic #98: Polish & Release (Week 7-8)
```

### Update Epic #86 with Story Links

```bash
gh issue edit 86 --body-file .context/project/agent_core_design/issues/epic-86-body-updated.md
```

**Update body to include:**
```markdown
## Stories

- [ ] Story #87: Configuration System (2 days)
- [ ] Story #88: Plugin Registry & Entry Points (1.5 days)
- [ ] Story #89: Test Infrastructure & Mock Providers (1.5 days)
```

**Repeat for Epics #90, #94, #98 with their respective story links.**

---

## VERIFICATION CHECKLIST

### After Creation

- [ ] All 21 issues created successfully
- [ ] Parent-child relationships documented in issue bodies
- [ ] Labels applied correctly (type, state, priority, phase, layer, component)
- [ ] Milestones assigned (Week 1-2, Week 3-4, Week 5-6, Week 7-8)
- [ ] Issue bodies contain all required sections:
  - [ ] Overview
  - [ ] Context
  - [ ] Acceptance Criteria (numbered, checkboxes)
  - [ ] Implementation Notes
  - [ ] Definition of Done
  - [ ] Linked Issues (Resolves, Blocks, Related)
  - [ ] Resources (Design Docs, ADRs, Code References)
  - [ ] Testing Strategy
  - [ ] Evidence Requirements

### Quality Checks

- [ ] Issue titles follow convention: "Type: Description"
- [ ] Acceptance criteria are testable (not vague)
- [ ] Dependencies explicitly documented (Blocks/Resolves)
- [ ] Design doc references included (with file paths)
- [ ] Test coverage targets specified
- [ ] Evidence requirements defined (screenshots, logs, metrics)

---

## LABEL TAXONOMY

### Standard Labels (from space_framework)

**Type:**
- `type:epic` - Large feature spanning multiple stories
- `type:story` - Implementable unit of work

**State:**
- `state:approved` - Ready to plan implementation
- `state:ready` - Implementable (acceptance criteria defined)
- `state:in-progress` - Currently being implemented
- `state:in-review` - PR open, awaiting approval
- `state:done` - Merged and validated

**Priority:**
- `priority:critical` - Blocks other work
- `priority:high` - Important for release
- `priority:medium` - Nice to have
- `priority:low` - Future enhancement

**Phase:**
- `phase:phase-1` - MVP (this implementation)
- `phase:phase-2` - Future enhancements

**Layer:**
- `layer:foundation` - Config, plugins, testing
- `layer:core` - Model, tools, memory
- `layer:orchestration` - Engine, API, observability
- `layer:polish` - CLI, docs, release

**Component:**
- `component:config` - Configuration system
- `component:plugin` - Plugin registry
- `component:testing` - Test infrastructure
- `component:model` - Model abstraction
- `component:tools` - Tool executor
- `component:memory` - Memory systems
- `component:engine` - Execution engine
- `component:api` - Public API
- `component:observability` - Events, logging
- `component:artifacts` - Artifact generation
- `component:cli` - Command-line interface
- `component:docs` - Documentation

---

## NEXT STEPS

1. **Create Milestones:**
   ```bash
   gh api repos/nsin08/ai_agents_review/milestones -X POST -f title="Week 1-2: Foundation" -f due_on="2026-02-08T23:59:59Z"
   gh api repos/nsin08/ai_agents_review/milestones -X POST -f title="Week 3-4: Core" -f due_on="2026-02-22T23:59:59Z"
   gh api repos/nsin08/ai_agents_review/milestones -X POST -f title="Week 5-6: Orchestration" -f due_on="2026-03-08T23:59:59Z"
   gh api repos/nsin08/ai_agents_review/milestones -X POST -f title="Week 7-8: Polish" -f due_on="2026-03-22T23:59:59Z"
   gh api repos/nsin08/ai_agents_review/milestones -X POST -f title="Phase 1 - Agent Core MVP" -f due_on="2026-03-22T23:59:59Z"
   ```

2. **Create Release Branch:**
   ```bash
   git checkout -b release/0.1.0
   git push origin release/0.1.0
   ```

3. **Configure Branch Protection:**
   ```bash
   # Protect release/0.1.0 branch (require PR, reviews, CI pass)
   gh api repos/nsin08/ai_agents_review/branches/release/0.1.0/protection -X PUT \
     -f required_pull_request_reviews[required_approving_review_count]=1 \
     -f required_status_checks[strict]=true \
     -f required_status_checks[contexts][]=test \
     -f enforce_admins=false
   ```

4. **Create Issue Body Files:**
   ```bash
   mkdir -p .context/project/agent_core_design/issues
   # Copy issue body content from this document to individual files
   # epic-85-body.md, epic-86-body.md, ..., story-102-body.md
   ```

5. **Execute Creation Commands:**
   ```bash
   # Run Step 1-6 commands sequentially
   # Verify each issue created before proceeding
   ```

6. **Update Cross-References:**
   ```bash
   # After all issues created, update bodies with actual issue numbers
   # Use `gh issue edit {#} --body-file {file}` to update
   ```

---

**Plan Status:** ✅ READY FOR EXECUTION  
**Created:** 2026-01-25  
**Total Issues:** 21 (1 parent epic + 4 child epics + 16 stories)  
**Estimated Time to Create:** 2-3 hours (with verification)

