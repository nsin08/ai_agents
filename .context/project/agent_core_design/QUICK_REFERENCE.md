# Phase 1 MVP - Quick Reference

**Repository:** nsin08/ai_agents  
**Branch:** release/0.1.0  
**Timeline:** 2026-01-25 to 2026-03-22 (8 weeks)

---

## 📊 OVERVIEW

✅ **21 Issues Created**
- 1 Parent Epic (#85)
- 4 Child Epics (#86-89)
- 16 Stories (#90-102)

✅ **5 Milestones**
- Phase 1 - Agent Core MVP (Mar 22)
- Week 1-2: Foundation (Feb 8)
- Week 3-4: Core (Feb 22)
- Week 5-6: Orchestration (Mar 8)
- Week 7-8: Polish (Mar 22)

---

## 🎯 EPIC HIERARCHY

```
#85 Agent Core Phase 1 MVP (Parent)
├─ #86 Foundation Layer (Week 1-2)
│  ├─ #90 Configuration System
│  ├─ #91 Plugin Registry
│  └─ #92 Test Infrastructure
├─ #87 Core Capabilities (Week 3-4)
│  ├─ #93 Model Abstraction
│  ├─ #94 Tool Executor
│  └─ #95 Short-Term Memory
├─ #88 Orchestration Layer (Week 5-6)
│  ├─ #96 LocalEngine & State Machine ⚠️ CRITICAL
│  ├─ #97 AgentCore Public API ⚠️ CRITICAL
│  └─ #98 Observability
└─ #89 Polish & Release (Week 7-8)
   ├─ #99 RunArtifact & Deterministic
   ├─ #100 Basic CLI
   ├─ #101 Integration Tests
   └─ #102 Documentation
```

---

## 📅 IMPLEMENTATION ORDER

### Week 1-2: Foundation
```bash
git checkout -b feature/90/configuration-system
# Implement #90 (Config) → 2 days
# Implement #91 (Plugins) → 1.5 days (parallel with #90)
# Implement #92 (Test Infra) → 1.5 days
```

### Week 3-4: Core
```bash
# Implement #93 (Model) → 3 days
# Implement #94 (Tools) → 2.5 days
# Implement #95 (Memory) → 1.5 days (can parallel)
```

### Week 5-6: Orchestration ⚠️ CRITICAL
```bash
# Implement #96 (Engine) → 3 days [MUST HAVE WORKING AGENT]
# Implement #97 (API) → 2 days [MUST HAVE PUBLIC API]
# Implement #98 (Observability) → 2 days
```

### Week 7-8: Polish
```bash
# Implement #99 (Artifacts) → 2 days
# Implement #100 (CLI) → 1.5 days
# Implement #101 (Tests) → 2 days
# Implement #102 (Docs) → 1.5 days
```

---

## 🚀 QUICK START

### 1. View Issues
```bash
# All issues
gh issue list --state open

# By milestone
gh issue list --milestone "Week 1-2: Foundation"

# By epic
gh issue list --label "type:epic"
```

### 2. Start First Story
```bash
# Checkout release branch
git checkout release/0.1.0
git pull origin release/0.1.0

# Create feature branch
git checkout -b feature/90/configuration-system

# Implement, test, commit
git add .
git commit -m "feat(story-90): implement config precedence"
git push origin feature/90/configuration-system

# Open PR
gh pr create --base release/0.1.0 --title "feat(story-90): Configuration System" --body "Resolves #90"
```

### 3. View Issue Details
```bash
gh issue view 90  # Configuration System
gh issue view 85  # Parent Epic
```

---

## 🏷️ LABELS

**Type:** type:epic, type:story  
**State:** state:ready, state:approved, state:in-progress, state:in-review, state:done  
**Priority:** priority:critical, priority:high, priority:medium  
**Phase:** phase:phase-1  
**Layer:** layer:foundation, layer:core, layer:orchestration, layer:polish  
**Component:** component:config, component:plugin, component:testing, component:model, component:tools, component:memory, component:engine, component:api, component:observability, component:artifacts, component:cli, component:docs

---

## 🔗 LINKS

**GitHub:**
- Issues: https://github.com/nsin08/ai_agents/issues
- Milestones: https://github.com/nsin08/ai_agents/milestones
- Branch: https://github.com/nsin08/ai_agents/tree/release/0.1.0

**Design Docs:**
- IMPLEMENTATION_PLAN.md
- ISSUE_CREATION_PLAN.md
- TECHNICAL_REVIEW_REPORT.md
- DESIGN_PATTERN_EVIDENCE.md
- 20 design docs in design_docs/

---

## ⚠️ CRITICAL MILESTONES

**Week 2 End:** Foundation complete (config, plugins, tests)  
**Week 4 End:** Core complete (model, tools, memory)  
**Week 5 End:** 🔥 FIRST WORKING AGENT (LocalEngine + AgentCore API)  
**Week 6 End:** Observability integrated  
**Week 8 End:** Release v0.1.0-alpha

---

## ✅ SUCCESS CRITERIA

**By Week 8:**
- [ ] All 16 stories merged to release/0.1.0
- [ ] Test coverage ≥ 85%
- [ ] Agent runs with OpenAI provider (real API call)
- [ ] Deterministic mode validated
- [ ] Documentation complete
- [ ] 5+ runnable examples
- [ ] Tag: v0.1.0-alpha

---

**Status:** ✅ READY TO START  
**Next Action:** Implement Story #90 (Configuration System)  
**Due Date:** Week 1 (by Feb 1, 2026)

