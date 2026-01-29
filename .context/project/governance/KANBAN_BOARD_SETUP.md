# Kanban Board Setup Guide

**Created**: January 25, 2026  
**Project**: ai_agents - Phase 1 MVP Implementation  
**Framework**: space_framework governance model

---

## Board Configuration

### Board Name
**Phase 1 MVP Implementation (8 weeks)**

### Board Type
**Kanban** with automated state transitions

### Timeline
- Start Date: February 1, 2026 (after design review approval)
- End Date: March 22, 2026 (8 weeks)
- Review Frequency: Daily (async standups), Weekly sprint reviews

---

## Column Structure

| Column | Purpose | Entry Criteria | Exit Criteria |
|--------|---------|----------------|---------------|
| **Backlog** | Stories awaiting assignment | state:ready | Story assigned |
| **In Progress** | Active development | state:in-progress | PR created |
| **In Review** | Code review pending | state:in-review, PR linked | PR approved |
| **Done** | Completed + merged | state:done, PR merged | Released to main |

---

## Automation Rules

### GitHub Actions Workflow
**File**: `.github/workflows/kanban-automation.yml`

**Triggers**:
1. **Issue Labeled** → Auto-transition based on state label
2. **PR Opened** → Move linked issue to "In Review"
3. **PR Merged** → Move issue to "Done" + close issue
4. **New Issue** → Auto-label as `state:idea`

**State Validation**:
- Only one state label per issue (auto-removes old states)
- `state:in-review` requires linked PR (blocks transition if missing)
- `state:done` requires PR merged (enforced by automation)

---

## Label System

### State Labels (Mutually Exclusive)
- `state:idea` — Initial request (backlog candidate)
- `state:approved` — Business approved (ready for breakdown)
- `state:ready` — Definition of Ready met (ready for dev)
- `state:in-progress` — Currently being worked on
- `state:in-review` — PR submitted, awaiting approval
- `state:done` — PR merged to base branch
- `state:released` — In production (main branch)

### Type Labels
- `type:epic` — Large feature (multiple stories)
- `type:story` — Implementable unit (1-3 days)
- `type:task` — Non-user-facing work
- `type:bug` — Defect fix

### Priority Labels
- `priority:critical` — Blocks other work
- `priority:high` — Phase 1 MVP
- `priority:medium` — Phase 2+
- `priority:low` — Nice-to-have

### Phase Labels
- `phase:design` — Design review work
- `phase:phase-1` — Phase 1 MVP
- `phase:phase-2` — Future phases

### Component Labels
- `component:foundation` — Core abstractions
- `component:config` — Configuration system
- `component:plugin` — Plugin registry
- `component:testing` — Test infrastructure
- `component:model` — Model abstraction
- `component:tools` — Tool layer
- `component:memory` — Memory systems
- `component:engine` — Execution engine
- `component:api` — Public API
- `component:observability` — Events, logging
- `component:artifacts` — Artifact generation
- `component:cli` — Command-line interface
- `component:docs` — Documentation

### Layer Labels
- `layer:foundation` — Config, plugins, testing
- `layer:core` — Model, tools, memory
- `layer:orchestration` — Engine, API, observability
- `layer:polish` — CLI, docs, release

---

## Work In Progress (WIP) Limits

| Column | WIP Limit | Reason |
|--------|-----------|--------|
| Backlog | No limit | Planning queue |
| In Progress | 3 items max | Prevent context switching |
| In Review | No limit | Encourage reviews |
| Done | Archive weekly | Keep board clean |

---

## Daily Workflow

### Morning (Start of Day)
1. Check "In Progress" column
2. Update status comment on your assigned issue
3. Flag blockers immediately

### During Development
1. Move card when starting work (→ In Progress)
2. Create PR when ready (→ In Review)
3. Request reviewers explicitly

### End of Day
1. Post daily standup comment:
   ```markdown
   ## Daily Update - Jan 25
   
   **Completed**: 
   - [x] Task 1
   
   **In Progress**:
   - [ ] Task 2 (blocked by X)
   
   **Next**:
   - [ ] Task 3 (tomorrow)
   
   **Blockers**: None | [Describe blocker]
   ```

---

## Board Views

### Default View: By Status
```
Backlog → In Progress → In Review → Done
```

### Alternate View: By Assignee
Filter by assignee to see individual workload

### Alternate View: By Priority
Sort by `priority:critical` → `priority:high` → `priority:medium`

---

## Sprint Planning (Weekly)

Every Friday EOD:
1. Review "Done" column (celebrate wins)
2. Check "In Review" column (clear blockers)
3. Plan next week's "In Progress" (pick 3-5 stories from Backlog)
4. Update Epic #85 with progress

---

## Metrics Dashboard

Track weekly:
- **Velocity**: Stories completed per week
- **Cycle Time**: Backlog → Done (days)
- **Blocked Items**: Count + duration
- **PR Review Time**: In Review → Done (hours)

**Target Metrics**:
- Velocity: 5-7 stories/week
- Cycle Time: <3 days
- Blocked Items: 0
- PR Review Time: <24 hours

---

## Escalation Process

### Blocked Item
1. Flag in daily update
2. Tag @nsin08 (CODEOWNER)
3. Escalate if blocked >1 day

### PR Review Delay
1. Ping reviewers after 24 hours
2. Request @nsin08 review if no response
3. Escalate if blocked >48 hours

### Critical Blocker
1. Immediately notify @nsin08
2. Pause other work if needed
3. Document resolution

---

## Board Maintenance

### Weekly Cleanup (Every Sunday)
- Archive "Done" items from last week
- Update WIP limits if needed
- Sync backlog with Epic #85

### Monthly Retrospective
- Review metrics
- Adjust WIP limits
- Improve automation

---

## Quick Reference Commands

### Create a Story
```bash
gh issue create --title "Story: [Title]" --body "[Description]" --label "type:story,state:ready,priority:high,phase:phase-1"
```

### Add Issue to Project
```bash
gh project item-add <project-id> --owner nsin08 --url https://github.com/nsin08/ai_agents/issues/[number]
```

### List Project Items
```bash
gh project item-list <project-id> --owner nsin08 --format json
```

### Update Issue Labels
```bash
gh issue edit [number] --add-label "state:in-progress" --remove-label "state:ready"
```

---

## Success Indicators

✅ **Working Well**:
- <3 items in "In Progress"
- <24 hour PR review time
- 0 blocked items
- Daily standup comments present

❌ **Needs Attention**:
- >5 items in "In Progress" (context switching)
- >48 hour PR review time (bottleneck)
- >2 blocked items (process issue)
- Missing daily updates (communication gap)

---

## Related Resources

- **Epic #85**: Phase 1 MVP Implementation (parent)
- **Workflow File**: `.github/workflows/kanban-automation.yml`
- **Framework**: https://github.com/nsin08/space_framework
- **Label Guide**: `.context/project/governance/LABEL_TAXONOMY.md`

---

**Board Owner**: @nsin08  
**Last Updated**: January 25, 2026  
**Status**: Active (Week 1 of 8)
