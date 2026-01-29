# GitHub Project Board - Manual Setup Instructions

**Project**: Phase 1 MVP Implementation  
**Repository**: nsin08/ai_agents  
**Created**: January 25, 2026  
**Framework**: space_framework governance

---

## ⚠️ Prerequisites

**Required Permission**: Organization owner or admin access to create projects

**Authenticated User**: Must be @nsin08 or authorized admin

---

## Step-by-Step Setup

### 1. Create the Project Board

**Via GitHub Web UI**:
1. Go to https://github.com/nsin08/ai_agents
2. Click **Projects** tab (top navigation)
3. Click **New project** button (green)
4. Choose **Board** template (Kanban layout)
5. Name: `Phase 1 MVP Implementation (8 weeks)`
6. Description: `Kanban board for Agent Core Phase 1 MVP (Feb 1 - Mar 22, 2026)`
7. Visibility: **Private** (or Public if preferred)
8. Click **Create project**

**Via GitHub CLI** (if you have permission):
```bash
gh project create \
  --owner nsin08 \
  --title "Phase 1 MVP Implementation (8 weeks)" \
  --format json
```

---

### 2. Configure Board Columns

**Default columns to create**:

| Column Name | Purpose | Color |
|-------------|---------|-------|
| **Backlog** | Stories awaiting assignment | Gray |
| **In Progress** | Active development (WIP: 3) | Yellow |
| **In Review** | Code review pending | Orange |
| **Done** | Completed + merged | Green |

**How to add columns**:
1. In project board, click **+ Add column**
2. Enter column name
3. Set column limit (for "In Progress": 3)
4. Click **Create**
5. Repeat for each column

---

### 3. Add Issues to Board

**Bulk Add (Recommended)**:
```bash
# Add all Phase 1 MVP issues (stories #90-102)
gh project item-add <PROJECT_ID> --owner nsin08 --url https://github.com/nsin08/ai_agents/issues/90
gh project item-add <PROJECT_ID> --owner nsin08 --url https://github.com/nsin08/ai_agents/issues/91
gh project item-add <PROJECT_ID> --owner nsin08 --url https://github.com/nsin08/ai_agents/issues/92
# ... repeat for issues 93-102

# Add all epics (#85-89)
gh project item-add <PROJECT_ID> --owner nsin08 --url https://github.com/nsin08/ai_agents/issues/85
gh project item-add <PROJECT_ID> --owner nsin08 --url https://github.com/nsin08/ai_agents/issues/86
gh project item-add <PROJECT_ID> --owner nsin08 --url https://github.com/nsin08/ai_agents/issues/87
gh project item-add <PROJECT_ID> --owner nsin08 --url https://github.com/nsin08/ai_agents/issues/88
gh project item-add <PROJECT_ID> --owner nsin08 --url https://github.com/nsin08/ai_agents/issues/89
```

**Manual Add (via Web UI)**:
1. Open project board
2. Click **Add item** in any column
3. Search for issue by number (e.g., `#90`)
4. Select issue → it appears as card
5. Drag card to appropriate column based on `state:` label

---

### 4. Configure Automation Workflows

**Built-in Automation** (recommended):
1. In project board, click **⋮** (menu) → **Settings**
2. Scroll to **Workflows** section
3. Enable these automations:

```yaml
✓ Auto-add new issues to "Backlog"
  - Filter: label:phase:phase-1

✓ Pull request opened → "In Review"
  - When PR links to issue

✓ Pull request merged → "Done"
  - Auto-close linked issue

✓ Issue labeled "state:in-progress" → "In Progress"

✓ Issue closed → "Done"
```

**GitHub Actions Workflow** (already created):
- File: `.github/workflows/kanban-automation.yml`
- Status: ✅ Committed to release/0.1.0
- Features:
  - Auto-label new issues as `state:idea`
  - Validate state transitions
  - Block `state:in-review` without PR
  - Auto-transition on PR events

---

### 5. Configure Board Views

**Default View: By Status**
- Columns: Backlog | In Progress | In Review | Done
- Sort: Priority (Critical → High → Medium)
- Filter: `phase:phase-1`

**Create Additional Views**:

1. **By Assignee** (List view)
   - Group by: Assignee
   - Sort: Created date
   - Filter: `state:in-progress OR state:in-review`

2. **By Priority** (Table view)
   - Columns: Issue, Assignee, State, Priority, Milestone
   - Sort: Priority (descending)
   - Filter: `phase:phase-1`

3. **By Layer** (Board view)
   - Columns: Foundation | Core | Orchestration | Polish
   - Group by: `layer:` label
   - Filter: `phase:phase-1`

---

### 6. Set Up Custom Fields (Optional)

**Recommended custom fields**:
1. **Effort** (Single select)
   - Options: Small (1 day) | Medium (2 days) | Large (3+ days)

2. **Days Remaining** (Number)
   - Countdown to Mar 22 deadline

3. **Blocker** (Checkbox)
   - Flag blocking issues

**How to add custom fields**:
1. Project board → **⋮** → **Settings**
2. Scroll to **Custom fields**
3. Click **+ New field**
4. Configure field type and options
5. Click **Save**

---

## Post-Setup Checklist

### Verify Board Configuration
- [ ] Board created with correct name
- [ ] 4 columns configured (Backlog, In Progress, In Review, Done)
- [ ] WIP limit set on "In Progress" (max 3)
- [ ] All 18 issues added (epics #85-89, stories #90-102)
- [ ] Automation workflows enabled
- [ ] GitHub Actions workflow active
- [ ] Custom fields added (if using)

### Test Automation
- [ ] Create test issue → auto-gets `state:idea` label
- [ ] Move issue to "In Progress" → gets `state:in-progress` label
- [ ] Open PR linking to issue → issue moves to "In Review"
- [ ] Merge PR → issue moves to "Done" and closes

### Documentation
- [ ] Board link added to README
- [ ] Team notified of board location
- [ ] Daily standup process documented
- [ ] Escalation process shared

---

## Board Access

**Project URL**: https://github.com/orgs/nsin08/projects/[PROJECT_NUMBER]

**Finding Project Number**:
```bash
gh project list --owner nsin08 --format json | jq '.projects[] | select(.title=="Phase 1 MVP Implementation (8 weeks)") | .number'
```

**Who Can Access**:
- Repository collaborators (read access)
- Organization members (based on org settings)
- Assigned developers (full access to their cards)

---

## Quick Commands Reference

### Add Issue to Project
```bash
gh project item-add <PROJECT_ID> --owner nsin08 --url https://github.com/nsin08/ai_agents/issues/[NUMBER]
```

### List Project Items
```bash
gh project item-list <PROJECT_ID> --owner nsin08 --format json
```

### View Project
```bash
gh project view <PROJECT_ID> --owner nsin08
```

### Update Issue State
```bash
gh issue edit [NUMBER] --add-label "state:in-progress" --remove-label "state:ready"
```

---

## Integration with Epic #85

**Epic #85** is the parent of this project board.

**Linkage**:
- All stories (#90-102) reference Epic #85 in description
- Epic #85 has checklist of all stories
- Board filters by `phase:phase-1` to show relevant work

**Weekly Sync**:
1. Review board metrics
2. Update Epic #85 with progress
3. Capture retrospective notes
4. Adjust next sprint priorities

---

## Success Metrics

Track in board or external dashboard:

| Metric | Target | Current |
|--------|--------|---------|
| **Velocity** | 5-7 stories/week | TBD |
| **Cycle Time** | <3 days (Backlog→Done) | TBD |
| **PR Review Time** | <24 hours | TBD |
| **Blocked Items** | 0 | TBD |
| **WIP Violations** | 0 (max 3 in progress) | TBD |

---

## Troubleshooting

### Issue Not Auto-Adding to Board
**Cause**: Missing `phase:phase-1` label  
**Fix**: Add label manually

### Issue Not Transitioning on PR Merge
**Cause**: PR doesn't reference issue in body  
**Fix**: Add "Resolves #[number]" to PR description

### GitHub Actions Not Running
**Cause**: Workflow file not in main/.github/workflows/  
**Fix**: Merge release/0.1.0 to main, or enable workflow on feature branch

### Permission Denied Creating Project
**Cause**: User lacks organization admin rights  
**Fix**: Ask @nsin08 (CODEOWNER) to create project

---

## Next Steps After Setup

1. **Announce Board**:
   - Post link in team chat
   - Add to Epic #85 description
   - Update README with board badge

2. **Run Kickoff**:
   - Review board with team
   - Demonstrate workflow
   - Assign first stories

3. **Start Sprint 1**:
   - Move 3-5 stories to "In Progress"
   - Daily standup comments
   - Weekly retrospective

---

**Setup Owner**: @nsin08 (must have org admin permission)  
**Last Updated**: January 25, 2026  
**Status**: ⏳ Awaiting manual setup by authorized user
