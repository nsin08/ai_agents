# QUICK START REFERENCE - PHASE 1 LAUNCH

**Status**: 🟢 GO  
**Commit**: 4b82355  
**Date**: January 9, 2026

---

## FOR ARCHITECT - START HERE

### Right Now (Day 1 Morning)

```bash
# 1. Clone repo
git clone https://github.com/nsin08/ai_agents.git
cd ai_agents

# 2. Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/story-1-1/llm-providers

# 3. Create directories
mkdir -p src/agent_labs/llm_providers
mkdir -p tests/unit/llm_providers

# 4. Read the guide
cat .context/DAY_1_LAUNCH_GUIDE.md

# 5. Follow Steps 1-14 in the guide
```

### What to Build
- **Story 1.1**: LLM Provider Adapters
- **File**: `src/agent_labs/llm_providers/base.py`
- **Test File**: `tests/unit/llm_providers/test_base.py`
- **Target**: >95% coverage, all tests passing
- **Effort**: 8 hours over Days 1-3

### Success = Merged PR

When done:
1. Run `pytest tests/unit/llm_providers/ -v --cov`
2. Create PR: `gh pr create ...`
3. Get approval from CODEOWNER
4. Merge to main
5. Celebrate! 🎉

---

## FOR DEV TEAMS - PREP WORK

### Setup (Today)
```bash
# Clone repo
git clone https://github.com/nsin08/ai_agents.git
cd ai_agents

# Create venv
uv venv
source .venv/bin/activate  # or: .venv\Scripts\activate (Windows)

# Install deps
uv pip install -r requirements.txt

# Verify pytest
pytest --version
```

### This Week (Days 1-5)
- Read: `.context/architect_review_phase_1_build_strategy.md`
- Study: Core module designs (when merged)
- Prepare: Lab 0 structure
- No coding yet (waiting for Architect)

### Next Week (Week 2 start)
- Architect finishes Stories 1.3-1.8
- Dev 1 starts Lab 0 integration
- Dev 2 prepares Labs 4-8
- All attend GATE 1 check (Friday EOD)

---

## FOR PM/SCRUM MASTER

### Send Invitations (Today/Tomorrow)
```bash
# Files to send:
# 1. .context/Week1_Kickoff_Meeting.ics (attach to calendar invite)
# 2. .context/PM_KICKOFF_EMAIL_TEMPLATE.md (copy text into email)

# Recipients:
# - Architect
# - Dev 1
# - Dev 2
# - Curriculum Lead
# - CODEOWNER
# - Any stakeholders

# Include these in pre-read materials:
# - architect_review_phase_1_build_strategy.md
# - phase_1_dependency_build_matrix.md
# - copilot-instructions.md (governance rules)
```

### Daily Standup (Starting Tomorrow 9 AM)
- **Time**: 9:00 AM EST
- **Duration**: 15 minutes
- **Attendees**: All 6 roles
- **Format**: Yesterday / Today / Blockers
- **Frequency**: Every weekday

### Weekly Sync (Starting Friday 4 PM)
- **Time**: 4:00 PM EST
- **Duration**: 30 minutes
- **Attendees**: All 6 roles
- **Agenda**: Progress, next week, gates
- **Frequency**: Every Friday

### Key Dates
- **Week 1 End (Jan 14, Friday)**: First weekly sync
- **Week 2 End (Jan 21, Friday)**: GATE 1 check (must pass)
- **Week 8 End (Mar 4, Friday)**: GATE 2 check
- **Week 12 End (Apr 4, Friday)**: GATE 3 check
- **April 9**: Phase 1 Release

---

## FOR CURRICULUM TEAM

### Week 1-7 (Parallel Work)
- Assign chapter writers (1 per level)
- Prepare chapter templates
- Draft chapter outlines
- Plan examples from labs

### Week 8+ (Writing Phase)
- Labs available for examples
- Start writing chapters
- Integrate code examples from Labs 0-8
- Create 12 projects with solutions

### Success = 25 chapters + 12 projects
- Beginner (6 chapters)
- Intermediate (6 chapters)
- Advanced (6 chapters)
- Pro (6 chapters)
- Supporting Materials (1 chapter)
- Projects (12 implementations)

---

## KEY DOCUMENTS

| Document | Purpose | Read When |
|----------|---------|-----------|
| [PHASE_1_GO_STATUS.md](#) | Executive summary | First thing |
| [DAY_1_LAUNCH_GUIDE.md](#) | Architect execution | Day 1 morning |
| [WEEK_1_SPRINT_LOG.md](#) | Daily tracking | Each day |
| [architect_review_phase_1_build_strategy.md](#) | Full strategy | Before kickoff |
| [phase_1_dependency_build_matrix.md](#) | Dependencies | Before kickoff |
| [week_1_kickoff_checklist.md](#) | Pre-kickoff prep | Before kickoff |

---

## CRITICAL PATHS

### Core Module Path (Weeks 1-2)
```
Story 1.1 (LLM Providers)
    ↓
Story 1.2 (Orchestrator)
    ↓
Stories 1.3-1.8 (parallel)
    ↓
GATE 1: All core merged >95% coverage
```

### Lab Path (Weeks 3-8)
```
Lab 0 (environment setup)
    ↓
Labs 1-3 (Dev 1)  + Labs 4-8 (Dev 2) [parallel]
    ↓
GATE 2: All labs >95% coverage
```

### Curriculum Path (Weeks 8-12)
```
Outlines ready (Week 7)
    ↓
Chapter writing (Weeks 8-11, parallel with labs)
    ↓
GATE 3: All chapters + projects ready
```

---

## SUCCESS METRICS

### Week 1 (Days 1-5)
- ✅ Story 1.1 merged
- ✅ Story 1.2 merged
- ✅ >95% coverage both
- ✅ Zero critical bugs

### Week 2 (Days 6-12)
- ✅ Stories 1.3-1.8 merged
- ✅ Lab 0 passing smoke tests
- ✅ GATE 1: PASS
- ✅ Ready to launch Labs Week 3

### Week 8 (End of lab development)
- ✅ All labs complete + tested
- ✅ GATE 2: PASS
- ✅ Ready for curriculum writing

### Week 12 (Final week)
- ✅ All chapters written + reviewed
- ✅ All 12 projects implemented
- ✅ GATE 3: PASS
- ✅ **PHASE 1 RELEASE** 🎉

---

## BLOCKERS / RISKS

### Current Issues
🟢 **NONE** - System is GO

### Watch List
- **Async bugs**: Mitigated by TDD + comprehensive tests
- **Integration issues**: Mitigated by clean API design + mock implementations
- **Timeline slip**: Mitigated by realistic estimates + weekly gates

---

## QUICK LINKS

- **GitHub Repo**: https://github.com/nsin08/ai_agents
- **Issues**: https://github.com/nsin08/ai_agents/issues
- **Discussions**: https://github.com/nsin08/ai_agents/discussions
- **Framework Repo**: https://github.com/nsin08/space_framework

---

## NEXT IMMEDIATE ACTIONS

### Today/Tomorrow (Before Day 1)
1. PM: Send kickoff invitations
2. All: Confirm repo access
3. All: Read strategy docs
4. Architect: Read DAY_1_LAUNCH_GUIDE.md

### Day 1 Morning (Jan 10)
1. Architect: Create branch (Step 1)
2. Team: Join standup (9 AM)
3. Dev teams: Set up venv
4. All: Read progress updates

### Day 1 Afternoon (Jan 10)
1. Architect: Design interface (Steps 2-5)
2. Architect: Write tests (Step 5)
3. Dev teams: Study architecture
4. All: Evening check-in

### By EOD Day 5 (Jan 14)
1. Story 1.1: Merged ✅
2. Story 1.2: Merged ✅
3. Team: Ready for Week 2
4. GATE 1: On track

---

## QUESTIONS?

- **Governance**: See `.github/copilot-instructions.md`
- **Architecture**: See `.context/architect_review_phase_1_build_strategy.md`
- **Execution**: See `.context/DAY_1_LAUNCH_GUIDE.md`
- **Tracking**: See `.context/WEEK_1_SPRINT_LOG.md`

---

## 🚀 YOU'RE READY

Everything is in place. All blockers cleared. All documents created.

**It's time to build.**

Start with Day 1 Launch Guide. Follow the steps. Trust the plan.

**Let's launch Phase 1!** 🔥
