# Phase 2+ Roadmap Plan (Sprint 2026-W05)

## Purpose
Plan the remaining work after Phase 1 completion, aligned to the phased delivery plan and Phase 2 preview.

## Sources
- .context/project/agent_core_design/17_phased_delivery_plan.md
- .context/project/agent_core_design/TECHNICAL_REVIEW_REPORT.md
- Issues: #89 (Phase 1 Polish/Release), #82 (not found in local context; pending link)

## Assumptions
- Phase 1 is complete and released (issue #89 closed).
- Artifact bundles and event schemas are stable inputs for Phase 2+.
- Two-week sprint cadence (see .context/sprint/README.md).

## Phase 2 (Planned) - Retrieval, Memory, Evaluation Foundations
Deliverables (from Phase 2 preview + phased plan):
- Retrieval abstractions + evidence manifest.
- Vector store registry/factory.
- Deterministic in-memory vector store.
- Optional chroma_persist backend (if dependency allowed).
- Long-term memory persistence + write/retrieval policies.
- Evaluation gate primitives + golden suites scaffolding (calibration in Phase 2/3).

Acceptance criteria:
- Evidence manifest included in artifacts and RunResult.
- Retrieval determinism holds under fixtures.
- Config swapping of vector store backend works.
- Long-term memory policies enforced in deterministic tests.

## Phase 3 (Planned) - CLI v1 Standardization
Deliverables:
- agent-core CLI commands: run, validate-config, eval, gate, serve.
- JSON output for automation.

Acceptance criteria:
- CLI produces artifact bundles identical to library runs.
- validate-config catches missing env keys and missing plugins.
- eval produces scorecards; gate can fail builds.

## Phase 4 (Planned) - Service v1 (Polling-First)
Deliverables:
- HTTP API per 15_service_spec.md.
- Background worker execution.
- Persistent event logs + artifact downloads.

Acceptance criteria:
- Create run -> poll status -> poll events -> download artifacts.
- Service output matches CLI/library artifact formats.

## Phase 5 (Planned) - Optional Plugins (LangGraph / LangChain)
Deliverables:
- agent_lg provides langgraph engine plugin.
- agent_lc provides langchain integration plugin (tools/retrieval).
- Plugin loader works on-demand.

Acceptance criteria:
- Base install does not require LC/LG.
- Selecting engine=langgraph fails clearly if deps missing.
- Conformance tests preserve policies/events.

## Phase 6 (Optional) - Streaming
Deliverables:
- SSE endpoint for events.
- Optional token streaming events.

Acceptance criteria:
- Streamed events match polled event schema.
- Cancellation works and emits terminal events.

## Phase 2+ Risks and Deferred Gaps (Carry-Forward)
- Plugin isolation/sandboxing (Phase 2 priority).
- Config precedence edge cases (multi-file loading) (Phase 2).
- Streaming API shape not finalized (Phase 2).
- Long-term memory policies underspecified (Phase 2).
- Multi-model routing policy algorithm undefined (Phase 2).
- Evaluation gate thresholds calibration (Phase 2/3).
- Multi-tenancy enforcement (Phase 2).
- Service API auth (Phase 2).

## Roadmap Sequencing (2-week sprints)
Phase 2 (8-12 weeks = 4-6 sprints):
- Sprint 1: Retrieval interfaces + evidence manifest schema + deterministic vector store.
- Sprint 2: Vector store registry + config swapping + chroma_persist (optional).
- Sprint 3: Long-term memory persistence + write/retrieval policies + tests.
- Sprint 4: Evaluation gate primitives + golden suite scaffolding.
- Sprint 5: Stabilization, docs, and phase gate review (go/no-go for Phase 3).

Phase 3 (2-4 sprints):
- Sprint 1: CLI run + validate-config with JSON output parity.
- Sprint 2: CLI eval + gate commands + test automation.

Phase 4 (2-3 sprints):
- Sprint 1: Service API skeleton + worker model.
- Sprint 2: Events + artifact downloads + parity tests.

Phase 5 (1-2 sprints):
- Sprint 1: Optional plugin packaging + loader + conformance tests.

Phase 6 (1-2 sprints, optional):
- Sprint 1: SSE events + cancellation semantics.

## Virtual Planning Meeting (PO/PM/Architect)
Participants: PO, PM, Architect
Agenda:
- Confirm Phase 2 scope and sequencing.
- Align on Phase 3 CLI priorities and gating.
- Identify dependencies for Phase 4 service design.

Decisions:
- Phase 2 scope locked to retrieval + memory + eval foundations.
- Phase 3 scope locked to CLI v1 with eval/gate support.
- Phase 4 service delayed until CLI parity complete.

Action Items:
- Link or create issue #82 for Phase 2+ roadmap scope.
- Create Phase 2 epics and milestones (8-12 week window).
- Update dependency map for retrieval, memory, and evaluation.

## Open Items
- Provide the exact GitHub links or titles for issues #82 and #89 to cross-reference.
- Confirm whether chroma_persist is an approved dependency.
- Confirm target release window for Phase 2.