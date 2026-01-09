# Phase 1 Week 1 Kickoff Checklist

**Date**: 2026-01-09 (Planning)  
**Kickoff Meeting**: TBD (Schedule this!)  
**Duration**: 12 weeks (Jan 9 - Apr 9, 2026)

---

## PRE-KICKOFF (PM/Architect - This Week)

- [ ] **Assign Stories to Team**
  - [ ] Architect assigned to Stories 1.1-1.8 (all core)
  - [ ] Dev 1 assigned to Stories 2.0-2.3 (Labs 0-3)
  - [ ] Dev 2 assigned to Stories 2.4-2.8 (Labs 4-8)
  - [ ] Curriculum Team (2-3 people) assigned to Stories 3.1-3.5
  - [ ] All team members notified + aware of timeline

- [ ] **GitHub Setup (PM Task)**
  - [ ] Assign Epic #2 to Architect + team leads
  - [ ] Assign Stories #3-#24 to respective team members
  - [ ] Create GitHub milestones: Week 1-2, Week 3-8, Week 9-12
  - [ ] Set up branch protection rules:
    - [ ] `main`: require PRs, CODEOWNERS approval, CI passing, 2 reviewers
    - [ ] `develop`: allow PRs from feature/* branches, require CI pass
    - [ ] Feature branches: `feature/story-{id}/{slug}` naming convention
  - [ ] Update CODEOWNERS with team members (if needed)

- [ ] **CI/CD Setup (Architect/DevOps Task)**
  - [ ] Create `.github/workflows/test.yml`:
    - [ ] Run pytest on all code changes (mock mode only)
    - [ ] Require >95% coverage for core, >85% for labs
    - [ ] Check for broken imports, type errors
    - [ ] Status required before merge
  - [ ] Create `.github/workflows/lint.yml`:
    - [ ] Run black, ruff on all Python code
    - [ ] Status required before merge
  - [ ] Create `.github/workflows/type-check.yml`:
    - [ ] Run mypy for type safety
    - [ ] Status optional (warning only) in Phase 1
  - [ ] Test CI pipeline with a dummy PR

- [ ] **Development Environment Prep**
  - [ ] Architect: Clone repo, set up `uv venv`, install deps
  - [ ] All team: Verify `pytest`, `black`, `ruff`, `mypy` installed
  - [ ] All team: Create feature branch for Story work
  - [ ] All team: Verify ability to push/create PRs

- [ ] **Documentation & Onboarding**
  - [ ] Share `.context/architect_review_phase_1_build_strategy.md` with team
  - [ ] Share `.context/phase_1_dependency_build_matrix.md` with team
  - [ ] Share `.github/copilot-instructions.md` with team (governance rules)
  - [ ] Architect walks through space_framework rules (state machine, approval gates)
  - [ ] All team: Read Story acceptance criteria for assigned stories

---

## WEEK 1 KICKOFF MEETING (1 hour)

### Attendees
- Architect
- Dev 1, Dev 2
- Curriculum Team Lead
- PM / Project Lead
- (Optional) CODEOWNER / Stakeholder

### Agenda

**1. Vision Alignment (10 min)**
- [ ] Recap Idea #1: What are we building and why?
- [ ] Show Epic #2: 21 stories, 3 streams, 12-week timeline
- [ ] Clarify success metrics: >95% tests, >90% docs, zero critical bugs

**2. Build Strategy Overview (15 min)**
- [ ] Present dependency graph (critical path: 1.1 → 1.2 → 1.3-1.8)
- [ ] Explain team allocation: Architect (core), Dev 1 (labs 0-3), Dev 2 (labs 4-8), Team (curriculum)
- [ ] Highlight critical gates: Week 2 (core done), Week 8 (labs done), Week 12 (curriculum done)
- [ ] Show week-by-week timeline with parallel streams

**3. Team Expectations (10 min)**
- [ ] Architect owns Stories 1.1-1.8 (no multitasking, focus only on core)
- [ ] Dev 1/2: Start with structure prep Week 1, begin implementation Week 2
- [ ] Daily standups (15 min): blockers, progress, adjustments
- [ ] Weekly architecture syncs (architect reviews PR, gives feedback)
- [ ] Code review: At least 2 reviewers per PR, CODEOWNERS must approve core PRs

**4. Process & Governance (10 min)**
- [ ] space_framework state machine: Story → Ready → In Progress → In Review → Done
- [ ] GitHub workflow: Create feature branch → Work locally → Push → Create PR → Code review → Merge
- [ ] Naming: `feature/story-{id}/{slug}` branches, e.g., `feature/story-1-1/llm-providers`
- [ ] PR template: Link to Story, describe changes, include evidence (test results, screenshots)
- [ ] Definition of Done: Tests pass (>95%), docs complete, no critical bugs, CODEOWNERS approved

**5. Week 1-2 Focus (5 min)**
- [ ] Architect: Start Story 1.1 TODAY
  - [ ] Set up LLM provider interface
  - [ ] Implement MockProvider (deterministic for tests)
  - [ ] Write tests: >95% coverage
  - [ ] Target: Code complete by EOD Day 2
- [ ] Dev 1: Prep Lab 0 structure
  - [ ] Create directory layout: labs/00/README, src/, tests/, exercises/
  - [ ] Draft README with learning objectives
  - [ ] Wait for core modules before implementing
- [ ] Dev 2: Review core modules, prep lab structure
  - [ ] Study Architect's work on 1.1-1.2
  - [ ] Understand shared patterns (interfaces, testing approach)
  - [ ] Prep Lab 4-5 structure templates

**6. Q&A (5 min)**
- [ ] Open questions from team
- [ ] Clarify blockers, dependencies, expectations
- [ ] Confirm everyone has necessary access (GitHub, CI/CD, docs)

### Outcomes
- ✅ Team aligned on vision, strategy, timeline
- ✅ Everyone knows their story assignments + dependencies
- ✅ All tools configured (git, CI/CD, branch protection)
- ✅ Schedule next week's daily standup + end-of-week sync

---

## WEEK 1 EXECUTION CHECKLIST

### Daily (Architect)

**Day 1 (Monday)**
- [ ] Architect creates branch: `feature/story-1-1/llm-providers`
- [ ] Architect sets up `src/agent_labs/llm_providers/` directory
- [ ] Architect drafts Provider abstract class interface
- [ ] Architect creates `tests/test_providers.py` (TDD)
- [ ] Daily standup (5 min): Architect shares progress

**Day 2 (Tuesday)**
- [ ] Architect implements MockProvider
- [ ] Architect adds Ollama provider adapter
- [ ] Architect runs tests: >95% coverage
- [ ] Architect creates PR for Story 1.1
- [ ] Daily standup: Story 1.1 PR ready for review

**Day 3 (Wednesday)**
- [ ] Code review: 2+ reviewers examine PR (architect + PM)
- [ ] Architect: Address review feedback
- [ ] Architect: Prepare for merge once approved
- [ ] Architect: Start Story 1.2 (Orchestrator)
- [ ] Daily standup: Story 1.1 review status + Story 1.2 start

**Day 4 (Thursday)**
- [ ] Architect merges Story 1.1 PR (after review approval)
- [ ] Architect continues Story 1.2
- [ ] Dev 1/2: Begin studying merged Story 1.1 code
- [ ] Daily standup: Story 1.1 merged, Story 1.2 in progress

**Day 5 (Friday) - End of Week Sync**
- [ ] Architect: Story 1.2 code complete, ready for review
- [ ] Architect: Wrap up any blockers from Days 1-4
- [ ] Weekly sync meeting (30 min):
  - [ ] Architect presents Story 1.1-1.2 design
  - [ ] Dev 1 confirms Lab 0 structure + questions
  - [ ] Dev 2 confirms understanding of core patterns
  - [ ] PM updates stakeholders on progress
- [ ] Update Epic #2 with progress comment
  - [ ] Stories 1.1 merged, 1.2 in review, on track for Week 2 completion

### Daily (Dev 1)

**Days 1-2**
- [ ] Set up `labs/00/` directory structure
- [ ] Draft README with learning objectives
- [ ] Create `labs/00/src/` and `labs/00/tests/` skeletons
- [ ] Study Story 1.1 PR and merged code
- [ ] Daily standup: Progress on Lab 0 structure

**Days 3-5**
- [ ] Wait for Story 1.1 merge (Thursday)
- [ ] Start integrating MockProvider into Lab 0
- [ ] Write first example: "Hello Orchestrator" agent
- [ ] Weekly sync: Confirm Lab 0 approach with architect
- [ ] Prepare to start real implementation Week 2

### Daily (Dev 2)

**Days 1-3**
- [ ] Read through Story 1.1 PR + 1.2 progress
- [ ] Review shared core interfaces + patterns
- [ ] Create documentation on core patterns for own reference
- [ ] Set up `labs/04/` and `labs/05/` basic structures
- [ ] Daily standup: Questions on architecture, readiness

**Days 4-5**
- [ ] Confirm understanding of LLM provider + orchestrator with Architect
- [ ] Prepare to start Labs 4-5 implementation after Story 1.2 merge
- [ ] Weekly sync: Confirm readiness for Week 2 start

### Daily (Curriculum Team)

**Days 1-5**
- [ ] This week: Observation & preparation (no writing yet)
- [ ] Curriculum lead: Gather Agents/ reference docs
- [ ] Curriculum lead: Organize chapter outlines (6 per level)
- [ ] Team: Discuss writing assignments (who writes which chapters)
- [ ] Team: Prepare workbook templates + slide templates
- [ ] Weekly sync: Confirm Chapter 1 assignments + examples needed

### Daily (All)

- [ ] **Daily Standup (5-10 min)**:
  - [ ] Each person: "What I did, what I'm doing, what's blocking me"
  - [ ] Flag blockers ASAP (don't wait until Friday)
  - [ ] Architect: Resolve blockers same day if possible

- [ ] **End of Day (5 min)**:
  - [ ] Commit work to feature branch (do not merge)
  - [ ] Update GitHub issue with progress comment (optional but helpful)
  - [ ] Set up tomorrow's focus

---

## WEEK 1 SUCCESS CRITERIA

✅ **Architect**:
- [ ] Story 1.1 merged (MockProvider + tests)
- [ ] Story 1.2 code complete + in review
- [ ] No critical bugs found in reviews
- [ ] Lab team understands core interfaces

✅ **Dev 1**:
- [ ] Lab 0 structure ready for implementation
- [ ] First example drafted (can run with mock provider)
- [ ] Ready to start real Lab 0 work Week 2

✅ **Dev 2**:
- [ ] Understands core architecture + patterns
- [ ] Lab 4-5 structure prepared
- [ ] Ready to start implementation after Lab 0 merge

✅ **Curriculum**:
- [ ] Chapter assignments finalized
- [ ] Outlines ready (6 chapters per level drafted)
- [ ] Writing to start Week 8

✅ **All**:
- [ ] CI/CD pipeline working (tests run on PRs)
- [ ] GitHub branch protection active
- [ ] Team aligned on timeline + expectations
- [ ] No blockers preventing Week 2 continuation

---

## RISK WATCH LIST (Week 1)

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Story 1.1 design issues found in review | Medium | HIGH | Architect designs carefully, daily reviews with 2 people |
| CI/CD not ready by Week 1 start | Low | HIGH | Set up during pre-kickoff, test with dummy PR |
| Architect gets blocked on tools/deps | Low | MEDIUM | Architect coordinates with DevOps immediately |
| Team context/understanding gaps | Medium | MEDIUM | Weekly sync, architecture review document, Q&A time |
| Lab team blocked waiting for core | Low | HIGH | Structure prep (Labs 0-1) can start Day 3 after 1.1 review |

---

## POST-WEEK 1 (Friday EOD)

- [ ] Architect submits Story 1.1-1.2 progress to Epic #2 comment
- [ ] PM summarizes Week 1 progress in Epic comment:
  - [ ] 1 story merged (1.1)
  - [ ] 1 story in review (1.2)
  - [ ] Team on track for Week 2 gates
  - [ ] No blockers
- [ ] PM sends stakeholder update (executive summary)
- [ ] Architect + team: Review & adjust timeline if needed
- [ ] **Schedule Week 2 focus**: Lab 0 integration testing

---

## WEEK 2 PREVIEW (Looking Ahead)

**Week 2 Goals**:
- [ ] Stories 1.3-1.8: Complete + merged (Architect parallel)
- [ ] Lab 0: Integrated + ready to ship
- [ ] All core modules in `src/agent_labs/` with >95% coverage

**Critical Gate Week 2, EOD**:
- [ ] All 8 core modules merged + tested
- [ ] Lab 0 ready to merge
- [ ] Zero critical bugs in core

**If gate passes**: Labs 1-8 implementation begins Week 3

---

**Created**: 2026-01-09  
**Version**: 1.0  
**Status**: READY FOR KICKOFF

Print this checklist. Review daily. Update progress.
