# Agent Core Design - Technical Review Report
## Initial Findings & Analysis

**Reviewer:** Technical Architect  
**Review Phase:** Layer 1 - Foundations Complete  
**Report Date:** January 25, 2026  
**Status:** IN PROGRESS

---

## Executive Summary

Initial review of Agent Core design foundations (01_principles.md, 02_system_overview.md, 03_public_api.md) reveals a **well-structured, coherent foundation** with clear design intent and production-grade thinking. The architecture balances flexibility (pluggable providers/engines) with safety (centralized tool enforcement, observability, determinism).

**Overall Assessment:** ✅ **STRONG FOUNDATION** - Design principles are clear, system architecture is layered and coherent, and public API is minimalist and extensible.

---

## 1. Layer 1: Foundations Review ✅ COMPLETE

### 1.1 Design Principles (01_principles.md)

**Strengths:**
- **I1: Centralized policy enforcement** - Single ToolExecutor point is correct. Prevents policy bypass.
- **I2: Always emit observability** - Structured events with correlation IDs enable deterministic replay and audit trails.
- **I3: Evaluation gates as code** - Gate primitive allows CI/CD gates for regression testing. Good.
- **I4: No hidden side effects** - Tools declare `read`/`write`/`admin` risk. Enables permission model.
- **I5: Determinism requirement** - Critical for testing and reproducibility. Properly emphasized.

**Coherence Assessment:** ✅ Principles are **internally consistent** and **framework-aware** (no hidden external dependencies).

**Design Constraints Validation:**
- ✅ C1: Minimal dependencies (pydantic, httpx, stdlib only) - appropriate for core lib
- ✅ C2: OpenAI support via httpx (no SDK coupling) - good architectural choice
- ✅ C3: Standardization over convenience - CLI/service reuse library; excellent

**Gaps Identified:**
- ⚠️ **MINOR**: No explicit mention of plugin isolation/sandboxing. Clarify: Can a buggy tool plugin crash the core runtime? Should add: "I6: Plugins cannot corrupt core state or memory."
- ⚠️ **MINOR**: Error handling strategy not defined at principle level. Should reference 19_error_taxonomy.md for how invariants are violated.

**Verdict:** ✅ **APPROVED** - Principles are solid. Suggest small clarification on plugin isolation.

---

### 1.2 System Overview (02_system_overview.md)

**Architecture Validation:**
- ✅ **Mermaid diagram clearly shows** layering: Config → Factories → ExecutionEngine → Model/Tool/Retrieval/Memory
- ✅ **Plugin registration pattern** (dotted lines to agent_lg, agent_lc) shows correct separation
- ✅ **No core coupling** to LangChain/LangGraph - both optional

**Core Responsibilities Mapping:**
1. ✅ **Deterministic execution & artifacts** - Clear specification. Implementation should follow.
2. ✅ **Tool boundary safety** - Lists enforcement points: allowlists, risk classification, timeouts, error taxonomy, audit events. Good.
3. ✅ **Multi-model roles and routing** - Config-driven provider selection per role. Extensible.
4. ✅ **Observability and redaction** - Structured events → exporters → redaction. Clear pipeline.
5. ✅ **Evaluation gates** - Goldens + scorecards + gate primitive. Matches principles.

**Coherence with Principles:** ✅ **STRONG**
- Principle I1 (centralized policy) → mapped to ToolExecutor
- Principle I2 (always emit) → mapped to Observability+Redaction subsystem
- Principle I3 (gates as code) → mapped to Evaluation Gate primitive
- Principle I4 (no hidden effects) → mapped to Tool Boundary Safety
- Principle I5 (determinism) → mapped to Artifact Bundles

**Gaps Identified:**
- ⚠️ **IMPORTANT**: System diagram shows Registries and Factories but their relationship is unclear. Should clarify:
  - What do registries contain? (model registry, tool registry, retrieval registry?)
  - What do factories construct? (providers? engines?)
  - Is there a dependency order?
  - **Recommend:** Add detailed subsection on Registries and Factories pattern.

- ⚠️ **IMPORTANT**: "Data flow (single run)" section cuts off. Cannot assess data flow coherence without full section. **Action Required:** Read full 02_system_overview.md and document data flow.

- ⚠️ **MINOR**: No mention of configuration precedence (env vars vs config file vs defaults). Should be defined in 04_configuration.md for clarity.

**Verdict:** ✅ **APPROVED with clarifications** - Architecture is sound. Need details on registries/factories and complete data flow review.

---

### 1.3 Public API (03_public_api.md)

**API Design Assessment:**

**AgentCore Class:**
- ✅ Constructor options: `from_env()`, `from_file()`, `from_config()` - covers all use cases
- ✅ Core methods: `run()` (async), `run_with_artifacts()`, `run_and_evaluate()` - minimal and sufficient
- ✅ Future-friendly: `run_events()` for streaming (not v1 but designed for it)

**RunRequest:**
- ✅ Minimum viable fields: input, metadata, context, mode
- ⚠️ **AMBIGUOUS**: What does `input` accept? Text string only? Structured schema? Should specify.
- ⚠️ **MISSING**: No mention of `max_turns`, `timeout`, `budget` (cost limit). Are these in config only?

**RunResult:**
- ✅ Standard fields: status, output_text, citations, metrics, errors
- ⚠️ **INCOMPLETE**: What is `citations` format exactly? Structured references to retrieved documents?
- ⚠️ **MISSING**: No mention of run ID / correlation ID for tracing

**RunArtifact:**
- ✅ Idea is correct: reproducible, auditable bundle
- ⚠️ **VAGUE**: List of contents incomplete. Does it include:
  - Actual tool responses (or summaries only)?
  - Model prompts (or result only)?
  - Memory state snapshots?
  - Full event log redacted or truncated?
  - Config snapshot hash or full config?

**Coherence with System Overview:** ✅ **GOOD**
- Public API is thin wrapper around core (as required by C3)
- Async-first matches constraint C1 (minimal deps; httpx for async)
- Artifact bundle matches Deterministic execution responsibility

**Gaps Identified:**
- 🔴 **CRITICAL**: Run request and result types underspecified. Cannot implement without knowing:
  - What `input` accepts (should be RunInput type with options)
  - Where behavioral parameters live (max_turns, timeout, budget)
  - What RunArtifact actually contains (detailed spec missing)
  - What `citations` looks like (need schema)
  
- ⚠️ **IMPORTANT**: No cancellation/interrupt mechanism mentioned. Should add:
  - `async cancel(run_id)` method?
  - Timeout behavior - does agent gracefully shutdown or hard kill?

- ⚠️ **IMPORTANT**: Streaming shape (`run_events()`) references RunEvent but no event schema shown. Need link to 11_observability.md or embedded event types.

**Verdict:** ⚠️ **APPROVED with conditions**
- Core idea is sound (thin library API, everything flows through AgentCore)
- **Required before Phase 1:** Specify RunRequest input types, RunArtifact contents, and cancellation behavior
- **Recommend:** Link to detailed type schemas (prefer embedded or separate schema file)

---

## 2. Cross-Layer Observations

### High-Level Architecture Coherence
- ✅ Principles → System responsibilities → Public API is a **coherent chain**
- ✅ Optional plugins model (agent_lc, agent_lg) doesn't break core abstraction
- ✅ Configuration-driven provider selection enables the "swap without rewrites" goal

### Remaining Uncertainties (Not Blockers Yet)
1. How do Registries and Factories interact? (Need 04-06 for clarity)
2. What's in a RunArtifact exactly? (Need 13_artifacts_and_run_state.md)
3. How do evaluation gates work in practice? (Need 12_evaluation_gates.md)
4. What does deterministic mode enforcement look like? (Need 06_runtime_engines.md)

---

## 3. Recommendation for Phase 1

### Layer 1 Completeness for MVP
✅ **Foundations are ready for Phase 1**

**Why:**
- Principles are clear and implementable
- System responsibilities are well-mapped
- Public API is minimal and extensible

**What must be clarified before coding starts:**
1. ❌ RunRequest/RunResult/RunArtifact detailed type specs (read 13_artifacts_and_run_state.md)
2. ❌ Configuration schema details (read 04_configuration.md)
3. ❌ Plugin registration mechanism (read 05_plugin_architecture.md)
4. ❌ Determinism enforcement approach (read 06_runtime_engines.md)

### Estimated Phase 1 Scope (Layer 1-2 only)
```
Phase 1 MVP = Foundations + Public Contracts

Layer 1: Principles ✅ done
Layer 2: Public API ⚠️ needs type specs
+ Basic orchestrator (minimal state machine from 06_runtime_engines.md)
+ Config loading (from 04_configuration.md)
+ Basic observability (event emission from 11_observability.md)
+ Tool executor with central enforcement (from 08_tool_boundary.md)

Out of scope for Phase 1:
- Advanced plugin loading (05_plugin_architecture.md) → Phase 2
- RAG/retrieval (09_retrieval_layer.md) → Phase 2
- Evaluation gates (12_evaluation_gates.md) → Phase 2/3
- Service API (15_service_spec.md) → Phase 2
- Security hardening (16_security_and_compliance.md) → Phase 2/3
```

---

## 4. Next Review Steps

### Immediate (Before Phase 1 coding)
- [ ] Read full 02_system_overview.md (data flow section)
- [ ] Read 03_public_api.md (full spec with examples)
- [ ] Read 04_configuration.md (schema details)
- [ ] Read 05_plugin_architecture.md (registration pattern)
- [ ] Read 06_runtime_engines.md (state machine details)
- [ ] Read 08_tool_boundary.md (tool executor contract)
- [ ] Read 13_artifacts_and_run_state.md (bundle schema)

### Critical Questions to Answer
1. **RunRequest/Result/Artifact types** - Are they in separate schema files or embedded in 13_artifacts_and_run_state.md?
2. **Plugin registration** - Is there an entry_points mechanism or programmatic registry?
3. **Configuration precedence** - How do env vars, config file, and defaults interact?
4. **Determinism guarantees** - What makes a run deterministic? Mock providers only? All retrieval mocked?
5. **Error handling** - How do tool errors, model errors, and system errors flow through?

### After Layer 2 Complete
- [ ] Create Phase 1 MVP technical design (scope boundaries, build order)
- [ ] Map 8 ADRs against MVP scope
- [ ] Identify any blockers for Phase 1 start

---

## 5. Quality Metrics

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Principles Clarity** | ✅ STRONG | 5 invariants + 3 constraints, all implementable |
| **System Architecture** | ✅ STRONG | Layered, diagram clear, responsibilities mapped |
| **Public API Completeness** | ⚠️ PARTIAL | Core idea sound; type specs need detail |
| **Coherence (L1↔L2)** | ✅ STRONG | Principles flow through system to API |
| **Phase 1 Readiness** | ⚠️ CONDITIONAL | Foundations ready; need Layer 2-4 clarity |
| **Implementation Feasibility** | ✅ GOOD | Minimal dependencies, clear contracts |

---

## 6. Gaps & Issues Log

### Critical (Must resolve before Phase 1 code start)
- **C-001** | RunRequest/RunResult/RunArtifact types underspecified | Impact: Cannot implement library API | Resolution: Read 13_artifacts_and_run_state.md, create type hierarchy
- **C-002** | System diagram: Registries/Factories relationship unclear | Impact: Cannot design factory pattern | Resolution: Add subsection in 02_system_overview.md

### Important (Should resolve before Phase 2)
- **I-001** | Plugin isolation/sandboxing not addressed | Impact: Buggy plugins could crash core | Resolution: Add invariant I6 or clarify in 05_plugin_architecture.md
- **I-002** | RunArtifact contents vague (partial vs full event log?) | Impact: Artifact bundles may not be reproducible | Resolution: Add detailed schema in 13_artifacts_and_run_state.md
- **I-003** | Configuration precedence order not specified | Impact: CLI/service may load config differently | Resolution: Clarify in 04_configuration.md or add config precedence ADR

### Nice-to-Have (Consider for future)
- **N-001** | Streaming API shape incomplete (no event types) | Impact: Cannot implement `run_events()` now | Resolution: Link to 11_observability.md RunEvent schema when ready

---

## 7. Reviewer Sign-Off

**Layer 1 Review Status:** ✅ **COMPLETE**

**Findings:**
- ✅ Principles are solid and implementable
- ✅ System architecture is coherent and well-layered
- ⚠️ Public API needs type specification details
- ⚠️ System diagram needs Registries/Factories clarification

**Recommended Action:**
- **Continue to Layer 2** (Configuration, Plugin Architecture, Runtime Engines)
- **Resolve critical gaps (C-001, C-002) in parallel** while reading Layer 2

**Go Decision:** ✅ **PROCEED with Layer 2 review**

---

**Next Report:** Layer 2-4 Review (Configuration, APIs, Plugin Architecture)  
**Review Timeline:** Continuing...

