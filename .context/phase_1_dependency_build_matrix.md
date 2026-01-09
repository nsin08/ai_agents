# Phase 1 Story Dependency & Build Matrix

## Quick Reference: Which Stories Block Which?

### SHARED CORE (Stories 1.1-1.8)
**Timeline**: Weeks 1-2 (sequential + parallel)
**Owner**: Architect
**Status**: Foundation Layer

| Story | Title | Depends On | Blocks (Labs) | Start | Duration | Status |
|-------|-------|-----------|---------------|-------|----------|--------|
| 1.1 | LLM Providers | NONE | All labs + core 1.2-1.8 | Week 1, Day 1 | 2 days | CRITICAL PATH |
| 1.2 | Orchestrator | 1.1 | Labs 3,6,8 | Week 1, Day 3 | 2 days | CRITICAL PATH |
| 1.3 | Tool Contracts | 1.1 | Labs 2,7,8 | Week 2, Day 5 | 2 days | Sequential start |
| 1.4 | Memory Systems | 1.1 | Labs 1,4,8 | Week 2, Day 5 | 3 days | Parallel start |
| 1.5 | Context Eng | 1.1 | Labs 3,5 | Week 2, Day 5 | 2 days | Parallel start |
| 1.6 | Observability | 1.1, 1.2 | Lab 6 | Week 2, Day 5 | 2 days | Parallel start |
| 1.7 | Evaluation | 1.1, 1.2 | Lab testing | Week 2, Day 6 | 2 days | Nice-to-have |
| 1.8 | Safety | 1.1, 1.3 | Lab 7 | Week 2, Day 6 | 2 days | Parallel start |

---

## LABS (Stories 2.0-2.8)
**Timeline**: Weeks 2-8 (staggered parallel after core complete)
**Owner**: Dev 1 (Labs 0-3), Dev 2 (Labs 4-8)
**Status**: Implementation Layer

### Lab 0: Environment Setup (CRITICAL BLOCKER)
| Story | Depends On | Can Start | Duration | Blocks All Labs |
|-------|-----------|-----------|----------|-----------------|
| 2.0 | 1.1-1.8 complete | Week 2, Day 5 | 3 days | YES - Labs 1-8 blocked |

**EXIT WEEK 2**: Lab 0 MUST be merged before any other lab starts Week 3.

### Labs 1-3 (Dev 1 - First Batch)
| Story | Depends On | Can Start | Duration | Independent? | Owner |
|-------|-----------|-----------|----------|-------------|-------|
| 2.1 | 1.1, 1.4, 2.0 | Week 3, Day 1 | 3 days | YES | Dev 1 |
| 2.2 | 1.1, 1.3, 2.0 | Week 3, Day 1 | 3 days | YES (parallel 2.1) | Dev 1 |
| 2.3 | 1.1, 1.2, 1.5, 2.0 | Week 3, Day 1 | 3 days | YES (parallel 2.1-2.2) | Dev 1 |

**PARALLEL**: Labs 1-3 have NO interdependencies. Can all start Day 1 Week 3. Dev 1 juggles 3 labs = 9 days / 3 weeks (Weeks 3-5).

### Labs 4-8 (Dev 2 - Second Batch, Staggered)
| Story | Depends On | Can Start | Duration | Complexity | Owner |
|-------|-----------|-----------|----------|-----------|-------|
| 2.4 | 1.1, 1.4, 2.0 | Week 3, Day 1 | 3 days | Medium | Dev 2 |
| 2.5 | 1.1, 1.5, 2.0 | Week 3, Day 1 | 3 days | Medium | Dev 2 |
| 2.6 | 1.1, 1.2, 1.6, 2.0 | Week 3, Day 3 | 3 days | Medium | Dev 2 |
| 2.7 | 1.1, 1.3, 1.8, 2.0 | Week 3, Day 3 | 3 days | Medium | Dev 2 |
| 2.8 | 1.1, 1.2, 1.4, 1.6, 2.0 | Week 4, Day 1 | 4 days | HIGH (most complex) | Dev 2 |

**STAGGERED**: Dev 2 starts Labs 4-5 Week 3, adds 6-7 Week 3/4, finishes with 8 Week 4-5. Parallelizable at 2-3 labs/week. Estimated completion: Week 8, Day 1.

---

## CURRICULUM (Stories 3.1-3.5)
**Timeline**: Weeks 8-12 (parallel write, sequential collation)
**Owner**: Curriculum Team (2-3 people)
**Status**: Learning Materials Layer

| Story | Depends On | Can Start | Duration | Parallelizable? | Blocks |
|-------|-----------|-----------|----------|-----------------|--------|
| 3.1 | Labs 0-2 + Reference | Week 8 | 4 days | With 3.2-3.4 | Story 3.5 |
| 3.2 | Labs 1-4 + Reference | Week 8 | 4 days | With 3.1,3.3,3.4 | Story 3.5 |
| 3.3 | Labs 5-8 + Reference | Week 8 | 4 days | With 3.1-3.2,3.4 | Story 3.5 |
| 3.4 | Labs 0-8 + Case Studies | Week 8 | 5 days | With 3.1-3.3 | Story 3.5 |
| 3.5 | 3.1-3.4 complete | Week 11 | 3 days | NO - sequential | Epic exit |

**PARALLEL WRITE**: Stories 3.1-3.4 can write in parallel (separate authors). Story 3.5 requires all 4 completed (collation task).

**Early Start Opportunity**: Can START week 8 (end of Lab phase) and FINISH week 12 with 5 days buffer.

---

## CRITICAL PATH TIMELINE

```
WEEK 1    WEEK 2    WEEK 3    WEEK 4    WEEK 5    WEEK 6    WEEK 7    WEEK 8
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤

SHARED CORE PHASE (Architect)
├─ 1.1 ────┤
├─ 1.2 ────────┤
├─ 1.3-1.8 ────────────────────┤
└─ [GATE: All merged + tested] ─┘

LAB 0 PHASE (Dev 1, Critical Blocker)
                ├─ 2.0 (Lab 0 Setup) ────┤
                                         └─ [GATE: Lab 0 ready]

LABS 1-3 PHASE (Dev 1, Parallel)
                                ├─ 2.1 (Lab 1) ──┤
                                ├─ 2.2 (Lab 2) ──┤
                                ├─ 2.3 (Lab 3) ──┤
                                                   (Week 5) (Week 6) [Review]

LABS 4-8 PHASE (Dev 2, Staggered)
                                ├─ 2.4 (Lab 4) ──┤
                                ├─ 2.5 (Lab 5) ──┤
                                             ├─ 2.6 (Lab 6) ──┤
                                             ├─ 2.7 (Lab 7) ──┤
                                                          ├─ 2.8 (Lab 8) ──┤
                                                                          [GATE: Labs done]

CURRICULUM PHASE (Team, Parallel + Sequential)
                                                        ├─ 3.1-3.4 (parallel) ────┤
                                                                                   ├─ 3.5 ──┤
                                                                                           [GATE: Curriculum done]
```

---

## DEPENDENCY RESOLUTION GUIDE

### "Can I start Story X?"

#### Story 1.1 (LLM Providers)
- ✅ START: Week 1, Day 1 (NO dependencies)
- GATES: None (foundation)

#### Story 1.2 (Orchestrator)
- ✅ START: Week 1, Day 3 (after 1.1 code review, ~2 days)
- GATES: 1.1 interface reviewed + approved by architect

#### Stories 1.3-1.8
- ✅ START: Week 2, Day 5 (after 1.1-1.2 GATES pass)
- CAN PARALLEL: All 6 stories (6 tasks / 2 weeks = 3/week doable)

#### Story 2.0 (Lab 0 Setup)
- ⏸️ START: Week 2, Day 5 (after 1.1-1.8 code review begins)
- ✅ START PARALLEL WORK: Week 2, Day 5 (structure setup)
- ❌ MERGE: Cannot merge until Week 2, Day 10 (needs 1.1-1.8 final)
- GATES: All core modules 1.1-1.8 must be merged before Lab 0 ships

#### Stories 2.1-2.3 (Labs 1-3)
- ⏸️ START: Week 2, Day 5 (can prep structure)
- ✅ START IMPLEMENTATION: Week 3, Day 1 (Lab 0 merged, core 1.x deps met)
- CAN PARALLEL: All 3 labs independently
- GATES: Lab 0 + required core modules (1.1, 1.3, 1.4, 1.5)

#### Stories 2.4-2.8 (Labs 4-8)
- ⏸️ START: Week 2, Day 10 (can prep structure)
- ✅ START IMPLEMENTATION: Week 3, Day 1 (Labs 4-5) or Week 3, Day 3+ (Labs 6-8)
- CAN PARALLEL: All 5 labs independently (staggered start)
- GATES: Lab 0 + required core modules (1.1-1.8 coverage)

#### Stories 3.1-3.4 (Curriculum Levels)
- ⏸️ START: Week 8, Day 1 (can plan + gather examples)
- ✅ START WRITING: Week 8, Day 1 (after final labs available)
- CAN PARALLEL: All 4 stories (4 authors, no blocking)
- GATES: Reference to Lab code + examples (not blocked)

#### Story 3.5 (Supporting Materials)
- ⏸️ START: Week 11, Day 1 (can prepare template)
- ✅ START COLLATION: Week 11, Day 1 (after 3.1-3.4 drafted)
- GATES: 3.1-3.4 must be complete + reviewed

---

## TEAM WORKLOAD DISTRIBUTION

### Architect (100% on core)
```
Week 1: Stories 1.1-1.2 (4 days) = 32 hours
Week 2: Stories 1.3-1.8 (8 days) = 64 hours
       Code review, integration, CI setup (4 days) = 32 hours
Total: 128 hours over 2 weeks = 64 hours/week
```

### Dev 1 (Labs 0-3)
```
Week 2: Lab 0 setup (3 days) = 24 hours
Week 3-5: Labs 1-3 (9 days, staggered) = 72 hours
Week 6-7: Polish, review, fixes (5 days) = 40 hours
Total: 136 hours over 6 weeks = 23 hours/week
```

### Dev 2 (Labs 4-8)
```
Week 2: Lab structure prep (2 days) = 16 hours
Week 3-8: Labs 4-8 (17 days, staggered) = 136 hours
         Code review, integration (3 days) = 24 hours
Total: 176 hours over 7 weeks = 25 hours/week
```

### Curriculum (2-3 people, parallel)
```
Week 8-10: Stories 3.1-3.4 (16 days / 2-3 people) = 64-96 hours per person
Week 11-12: Story 3.5 + review (5 days) = 40 hours per person
Total: 104-136 hours per person over 5 weeks = 21-27 hours/week
```

---

## GO/NO-GO GATES

### Gate 1: Week 2, EOD (Shared Core Ready)
- ✅ Story 1.1: Code complete + merged
- ✅ Story 1.2: Code complete + merged
- ✅ Story 1.3-1.8: Code complete + merged
- ✅ All 8 modules have >95% test coverage
- ✅ All modules have working examples
- ✅ Zero critical bugs found in review
- ✅ Lab 0 code complete (ready to merge)

**GO/NO-GO DECISION**: Lab 0 can merge Monday Week 3. If blocker exists, DELAY all labs until blocker fixed.

### Gate 2: Week 5, EOD (Labs 1-3 Ready)
- ✅ Labs 1-3: Code complete + merged
- ✅ All labs >95% test pass
- ✅ Exercises documented + solutions ready
- ✅ No critical bugs in integration tests

**GO/NO-GO DECISION**: Continue with Labs 4-8. If issues found, pause Dev 2 to support Lab fixes.

### Gate 3: Week 8, EOD (All Labs Ready)
- ✅ Labs 4-8: Code complete + merged
- ✅ All 9 labs (0-8) >95% test pass
- ✅ Full integration test suite passing
- ✅ Both mock + real LLM modes working

**GO/NO-GO DECISION**: Release labs to alpha users. Curriculum team finalizes materials.

### Gate 4: Week 12, EOD (Epic Ready for Release)
- ✅ All 21 stories: state:done
- ✅ All PRs: reviewed + merged
- ✅ Curriculum: approved by PO + Architect
- ✅ All tests: passing in CI
- ✅ Documentation: >90% complete

**GO/NO-GO DECISION**: Release to production. Close Epic. Plan Phase 2.

---

## Summary Table

| Component | Owner | Start | End | Duration | Parallelizable | Blocker For |
|-----------|-------|-------|-----|----------|---|---|
| Shared Core | Architect | W1D1 | W2D12 | 2 weeks | Partial (1.1-1.2 sequential, 1.3-1.8 parallel) | All labs + core itself |
| Lab 0 | Dev 1 | W2D5 | W2D12 | 1 week | NO | Labs 1-8 |
| Labs 1-3 | Dev 1 | W3D1 | W5D12 | 3 weeks | YES (all 3 parallel) | Story 3.1 (Curriculum) |
| Labs 4-8 | Dev 2 | W3D1 | W8D5 | 5.5 weeks | YES (staggered 2-3 parallel) | Stories 3.2-3.4 (Curriculum) |
| Curriculum | Team | W8D1 | W12D5 | 5 weeks | YES (3.1-3.4 parallel, 3.5 sequential) | Release |

---

**Last Updated**: 2026-01-09  
**Version**: 1.0  
**Status**: APPROVED FOR EXECUTION
