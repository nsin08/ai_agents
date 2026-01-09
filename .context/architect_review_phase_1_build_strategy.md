# Architect's Review: Phase 1 Epic #2 - Build Strategy & Dependencies

**Review Date**: 2026-01-09  
**Reviewed By**: Lead Architect  
**Status**: READY FOR IMPLEMENTATION  

---

## 1. DEPENDENCY GRAPH

### Critical Path (Sequential Dependencies)

```
WEEK 1-2: SHARED CORE (Foundation Block)
├─ Story 1.1: LLM Providers (no deps)
│  └─ MUST COMPLETE before: All labs, All core modules
├─ Story 1.2: Orchestrator Controller (depends on 1.1)
│  └─ MUST COMPLETE before: All labs
├─ Story 1.3: Tool Contracts (depends on 1.1)
│  └─ MUST COMPLETE before: Labs 2, 3, 7, 8
├─ Story 1.4: Memory Systems (depends on 1.1)
│  └─ MUST COMPLETE before: Labs 1, 4, 8
├─ Story 1.5: Context Engineering (depends on 1.1)
│  └─ MUST COMPLETE before: Labs 3, 5
├─ Story 1.6: Observability (depends on 1.1, 1.2)
│  └─ MUST COMPLETE before: Labs 6
├─ Story 1.7: Evaluation (depends on 1.1, 1.2)
│  └─ NICE-TO-HAVE for: Labs testing
└─ Story 1.8: Safety (depends on 1.1, 1.3)
   └─ MUST COMPLETE before: Labs 7

WEEK 3-8: LABS (Parallel, Staggered)
├─ Story 2.0: Lab 0 (depends on all of 1.x)
│  └─ BLOCKER: All subsequent labs
├─ Story 2.1: Lab 1 (depends on 1.1, 1.4, 2.0)
│  ├─ Can start: Week 2, mid-day
│  └─ Blocks: Nothing (independent)
├─ Story 2.2: Lab 2 (depends on 1.1, 1.3, 2.0)
│  ├─ Can start: Week 2, end-of-day
│  └─ Blocks: Nothing (independent)
├─ Story 2.3: Lab 3 (depends on 1.1, 1.2, 1.5, 2.0)
│  ├─ Can start: Week 2, end-of-day
│  └─ Blocks: Nothing (independent)
├─ Story 2.4: Lab 4 (depends on 1.1, 1.4, 2.0)
│  ├─ Can start: Week 3, day 1
│  └─ Blocks: Nothing (independent)
├─ Story 2.5: Lab 5 (depends on 1.1, 1.5, 2.0)
│  ├─ Can start: Week 3, day 1
│  └─ Blocks: Nothing (independent)
├─ Story 2.6: Lab 6 (depends on 1.1, 1.2, 1.6, 2.0)
│  ├─ Can start: Week 3, day 2
│  └─ Blocks: Nothing (independent)
├─ Story 2.7: Lab 7 (depends on 1.1, 1.3, 1.8, 2.0)
│  ├─ Can start: Week 3, day 2
│  └─ Blocks: Nothing (independent)
└─ Story 2.8: Lab 8 (depends on 1.1, 1.2, 1.4, 1.6, 2.0)
   ├─ Can start: Week 4, day 1
   └─ Blocks: Nothing (independent)

WEEK 9-12: CURRICULUM (Parallel with Labs)
├─ Story 3.1: Beginner (depends on Labs 0-2)
│  ├─ Can start: Week 8, end (parallel with Lab 8)
│  └─ Blocks: Nothing
├─ Story 3.2: Intermediate (depends on Labs 1-4)
│  ├─ Can start: Week 8, mid (parallel with Labs 6-8)
│  └─ Blocks: Story 3.5
├─ Story 3.3: Advanced (depends on Labs 5-8, Reference docs)
│  ├─ Can start: Week 8, mid (parallel with Labs 6-8)
│  └─ Blocks: Story 3.5
├─ Story 3.4: Pro (depends on Labs all, Case studies)
│  ├─ Can start: Week 8, mid (parallel with Labs 6-8)
│  └─ Blocks: Story 3.5
└─ Story 3.5: Supporting Materials (depends on 3.1-3.4)
   ├─ MUST COMPLETE LAST
   └─ Unblocks: Epic exit criteria
```

---

## 2. TEAM ALLOCATION & WORKLOAD

### Allocation (Revised Based on Dependencies)

**Architect Role**: Story 1.1-1.8 (Shared Core)
- **Why**: Core decisions must be locked before labs start. Foundation work is sequential early.
- **Hours**: ~25-30 days (1 person, 6 weeks)
- **Delivery**: Weeks 1-6
- **Parallelizable**: Stories 1.4-1.8 can start mid-Week 1 after 1.1-1.2 review

**Dev 1**: Stories 2.0-2.3 (Labs 0-3)
- **Why**: Lab 0 is critical path blocker; Labs 1-3 have fewest dependencies
- **Hours**: ~15-18 days (1 person, 4 weeks)
- **Delivery**: Weeks 2-5
- **Parallelizable**: Labs 1-3 can run in parallel Week 3+

**Dev 2**: Stories 2.4-2.8 (Labs 4-8)
- **Why**: Labs 4-8 depend on more core modules; can start later
- **Hours**: ~20-24 days (1 person, 5 weeks)
- **Delivery**: Weeks 3-8
- **Parallelizable**: Labs 4-5 can run parallel Week 3+, Labs 6-8 Week 4+

**Curriculum Team**: Stories 3.1-3.5 (Separate)
- **Why**: Content work is independent; can start Week 8 (parallel)
- **Hours**: ~30-35 days (2-3 people, 3-4 weeks)
- **Delivery**: Weeks 8-12
- **Parallelizable**: Stories 3.1-3.4 fully parallel, then 3.5 collates

---

## 3. BUILD SEQUENCE (WEEK-BY-WEEK)

### WEEKS 1-2: Shared Core Foundation

#### Week 1
- **Day 1-2**: Architect: Story 1.1 (LLM Providers)
  - Parallel task: Architect defines interfaces
  - Blocker: NONE (foundation)
  - Dev 1: Prepare Lab 0 structure
  
- **Day 3-4**: Architect: Story 1.2 (Orchestrator)
  - Depends on: Story 1.1 (provider interface)
  - Dev 1: Implement Lab 0 boilerplate
  
- **Day 5**: Architect reviews 1.1 + 1.2, Dev 1 preps Lab 0 for integration
  - Start: Stories 1.4-1.8 in parallel (4 days each)

#### Week 2
- **Day 6-10**: Architect: Stories 1.3, 1.4, 1.5, 1.6, 1.8 (in parallel, ~2 days each)
  - Coord point: Daily standup to ensure no blocking issues
  - Dev 1: Finish Lab 0, integrate 1.1-1.2
  - Dev 2: Start prep on Lab module structure

- **Day 10 EOD**: All Stories 1.1-1.8 code-complete
- **Day 11-12**: Code review, integration testing, CI/CD setup

**Exit Criteria Week 2**:
- ✅ All 8 core modules in `src/agent_labs/`
- ✅ 100% test coverage in mock mode
- ✅ All stories merged to `develop`
- ✅ No critical bugs blocking labs
- ✅ Lab 0 ready for student use

---

### WEEKS 3-8: Labs (Staggered Parallel)

#### Week 3
**Start Dependencies Met**: 1.1-1.8 complete

- **Dev 1 (Labs 1-3)**:
  - Story 2.1: Lab 1 RAG (depends: 1.1, 1.4) - START
  - Story 2.2: Lab 2 Tools (depends: 1.1, 1.3) - START (parallel)
  - Story 2.3: Lab 3 Orchestrator (depends: 1.1, 1.2, 1.5) - START (parallel)
  
- **Dev 2 (Labs 4-8)**:
  - Story 2.4: Lab 4 Memory (depends: 1.1, 1.4) - START
  - Story 2.5: Lab 5 Context (depends: 1.1, 1.5) - START (parallel)

- **Curriculum Team (Early Start)**:
  - Start writing Story 3.1 (Beginner) with Lab 0 examples

#### Week 4-5
- **Dev 1**: 
  - FINISH Labs 1, 2, 3 (each ~3 days)
  - Integrate feedback, polish
  
- **Dev 2**:
  - FINISH Labs 4, 5
  - START Labs 6, 7
  
- **Curriculum**:
  - Finish Story 3.1 (Beginner)
  - START Story 3.2 (Intermediate) with Lab 1-4 examples

#### Week 6-8
- **Dev 1**: Code review + polish for Labs 1-3
  
- **Dev 2**:
  - FINISH Labs 6, 7, 8 (most complex)
  - Parallel review + iteration
  
- **Curriculum**:
  - FINISH Stories 3.2-3.4 in parallel
  - START Story 3.5 (Glossary, templates, workbooks)

**Exit Criteria Week 8**:
- ✅ All 9 labs (0-8) code-complete
- ✅ >95% test pass rate (mock mode)
- ✅ All exercise solutions documented
- ✅ Both mock and real LLM modes functional
- ✅ All labs merged to `develop`

---

### WEEKS 9-12: Curriculum Finalization + Validation

#### Week 9-10
- **Curriculum Team**: 
  - FINISH Story 3.5 (Glossary, templates, workbooks)
  - Cross-reference all chapters
  - Verify all links
  
- **Architect**: 
  - Code review all curriculum
  - Validate examples match labs

#### Week 11-12
- **Full Team**: Integration testing
  - Run all labs end-to-end
  - Validate curriculum matches lab content
  - User acceptance testing (UAT) prep
  
- **Architect**: Release preparation
  - Release notes
  - Stakeholder communication
  - Go/no-go decision

**Exit Criteria Week 12**:
- ✅ All 21 stories state:done
- ✅ All PRs reviewed + merged
- ✅ Curriculum approved (PO + Architect)
- ✅ Full test suite passing (CI)
- ✅ Documentation >90% complete
- ✅ Ready for public release

---

## 4. PARALLEL BUILD PATTERN

### Three Independent Streams (Can Overlap)

```
STREAM 1: Shared Core (2 weeks sequential)
  Week 1:  Stories 1.1, 1.2 (critical path)
  Week 2:  Stories 1.3-1.8 (parallel)
  ↓
  GATES: All modules 100% tested, interfaces locked

STREAM 2: Labs (6 weeks, staggered parallel)
  Week 2: Lab 0 (blocker for all)
  Week 3-5: Labs 1-5 (parallel after 1.x deps met)
  Week 6-8: Labs 6-8 (parallel, most complex)
  ↓
  GATES: All labs >95% test pass, exercises complete

STREAM 3: Curriculum (4 weeks, mostly parallel)
  Week 8-10: Stories 3.1-3.4 (parallel writing)
  Week 10-12: Story 3.5 + integration (sequential collation)
  ↓
  GATES: All chapters reviewed, links verified, glossary complete
```

**Key Point**: Streams 2 & 3 CAN START IN WEEK 8 (early write). No blocking.

---

## 5. CRITICAL RISK MITIGATION

| Risk | Mitigation |
|------|------------|
| **Core modules late** (blocks all labs) | Architect owns 1.1-1.2 first (Days 1-4), daily reviews. No other work. |
| **Labs have feature creep** | Strict Definition of Done per lab. No nice-to-haves in Weeks 3-8. |
| **Curriculum misaligned with labs** | Weekly sync: Curriculum team pulls latest lab examples. |
| **Testing bottleneck** | CI/CD must be ready Week 1. Automated test runs on every PR. |
| **Team blocked by dependencies** | Dev 2 starts with shared core 1.1-1.5 review while Architect is at 1.6-1.8. |
| **Integration issues Week 8** | Weekly cross-team integration testing starting Week 4. |

---

## 6. BUILD COMMANDS & CI/CD

### Local Development
```bash
# Install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Run tests for core modules
pytest src/agent_labs/ -v --cov=src/agent_labs/ --cov-report=term-missing

# Run tests for specific lab
pytest labs/01/ -v --cov=labs/01/src/ --cov-report=term-missing

# Lint
black src/ labs/
ruff check src/ labs/

# Type checking
mypy src/agent_labs/ --strict
```

### CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/test.yml
- Trigger: Every PR
- Run: pytest (all tests, mock mode only)
- Coverage: >95% for core, >85% for labs
- Lint: black, ruff
- Types: mypy
- Status: Required before merge
```

---

## 7. ARTIFACT ORGANIZATION (Per Rule 11)

```
src/agent_labs/                  ← Shared core (stories 1.1-1.8)
├── llm_providers/              (Story 1.1)
├── orchestrator/               (Story 1.2)
├── tools/                       (Story 1.3)
├── memory/                      (Story 1.4)
├── context/                     (Story 1.5)
├── observability/              (Story 1.6)
├── evaluation/                 (Story 1.7)
└── safety/                      (Story 1.8)

labs/
├── 00/                          (Story 2.0) → Lab 0: Setup
│   ├── README.md
│   ├── src/
│   ├── tests/
│   └── exercises/
├── 01/ through 08/              (Stories 2.1-2.8) → Labs 1-8

.context/curriculum/             (Stories 3.1-3.5)
├── chapters/
│   ├── b01_motivation.md        (Story 3.1)
│   ├── i01_orchestrator.md      (Story 3.2)
│   ├── a01_design_decisions.md  (Story 3.3)
│   ├── p01_support_agents.md    (Story 3.4)
│   └── ... (25 chapters total)
├── templates/                   (Story 3.5)
├── workbooks/                   (Story 3.5)
├── glossary.md                  (Story 3.5)
└── quick_reference.md           (Story 3.5)

.github/workflows/
├── test.yml                     (CI: pytest, coverage, types)
├── lint.yml                     (CI: black, ruff)
└── release.yml                  (Manual: release to PyPI)

tests/                           (Integration tests, E2E)
├── test_core_integration.py     (All modules together)
├── test_labs_integration.py     (All labs together)
└── test_curriculum_links.py     (Link validation)
```

---

## 8. SUCCESS CRITERIA (Per Epic)

✅ **Week 2 Gates**: Shared core 100% tested, all modules merged
✅ **Week 8 Gates**: All labs >95% pass rate, exercises complete  
✅ **Week 12 Gates**: Curriculum approved, all stories done, release ready

**Exit Criteria for Epic → state:done**:
- ✅ All 21 stories state:done
- ✅ All PRs merged to develop
- ✅ 2+ code reviewer sign-off per story
- ✅ CI passing (tests, lint, types)
- ✅ Curriculum reviewed (PO + Architect)
- ✅ Release notes ready
- ✅ Stakeholders notified → Go to Phase 2

---

## 9. HANDOFF NOTES

### For Architect (Weeks 1-2, then oversight)
- Focus on Stories 1.1-1.8 only (no multitasking)
- Lock interfaces by EOD Week 1 (1.1-1.2)
- Parallel 1.4-1.8 Week 2 with daily reviews
- Own code review for all core PRs
- Attend daily standups starting Week 3 (oversight)

### For Dev 1 (Weeks 2-8)
- Week 2: Lab 0 (integrate core modules)
- Weeks 3-5: Labs 1-3 (can parallelize)
- Weeks 6-8: Polish, code review, integration testing
- Unblock Dev 2 with questions about core modules
- Attend daily standups

### For Dev 2 (Weeks 3-8)
- Week 2: Prep lab structure, watch Architect work
- Weeks 3-5: Labs 4-5 (start after core review)
- Weeks 6-8: Labs 6-8 (most complex, most time)
- Partner with Dev 1 on shared patterns/issues
- Attend daily standups

### For Curriculum Team (Weeks 8-12, can start writing Week 8)
- Week 8: Start writing Stories 3.1-3.4 (parallel)
- Week 10: Integrate with final labs, finish Story 3.5
- Week 11-12: Review cycle, polish, link validation
- Attend weekly sync with architects (not daily)

---

## 10. SIGN-OFF

**Architect Review**: APPROVED FOR IMPLEMENTATION  
**Risk Level**: LOW (clear dependencies, sequential critical path, parallelizable labs)  
**Confidence**: HIGH (team skills match scope, timeline realistic)  

**Proceed to Week 1 kickoff.** Deploy Lab 0 by EOD Week 2.

---

**Next Steps**:
1. ✅ Assign stories to team members (PM task)
2. ✅ Set up GitHub branch protection (PM task)
3. ✅ Create CI/CD pipeline (DevOps/Architect task)
4. ✅ Schedule Week 1 kickoff standup
5. ⏭️ **START WEEK 1**: Architect begins Story 1.1
