# Implementation Plan Updates - Branch Strategy

**Date:** 2026-01-25  
**Change:** Switch from `develop` branch to `release/0.1.0` branch for Phase 1 MVP

---

## CHANGES SUMMARY

### 1. Branch Strategy Updated

**Before:**
- Base branch: `develop`
- Feature branches: `feature/{story-#}/*` → merge to `develop`
- Release: `develop` → `main` (after completion)

**After:**
- Base branch: `release/0.1.0`
- Feature branches: `feature/{story-#}/*` → merge to `release/0.1.0`
- Release: `release/0.1.0` → `main` (after completion, tagged as v0.1.0-alpha)

### 2. Files Updated

| File | Changes | Status |
|------|---------|--------|
| IMPLEMENTATION_PLAN.md | All 'develop' → 'release/0.1.0' | ✅ Updated |
| ISSUE_CREATION_PLAN.md | New file with GitHub issue templates | ✅ Created |

### 3. Key Updates in IMPLEMENTATION_PLAN.md

**Story Exit Criteria (16 stories):**
```markdown
# Before
- [ ] Merged to `develop`

# After
- [ ] Merged to `release/0.1.0`
```

**CI/CD Workflows:**
```yaml
# Before
on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop]

# After
on:
  push:
    branches: [release/*, main]
  pull_request:
    branches: [release/*]
```

**Branch Protection:**
```bash
# Before
Base: `develop` (NOT `main`)

# After
Base: `release/0.1.0` (NOT `main`)
```

---

## RATIONALE

### Why Release Branch?

1. **Semantic Versioning:** `release/0.1.0` explicitly indicates the version being developed
2. **Multiple Releases:** Allows parallel development of future versions (e.g., `release/0.2.0`)
3. **Clear Intent:** Release branches signal "preparing for production" vs "active development"
4. **Hotfix Support:** After v0.1.0 release, can create `release/0.1.1` for patches

### Branch Flow (Updated)

```
main (stable releases)
  ↑
release/0.1.0 (Phase 1 MVP - current)
  ↑
feature/87/configuration-system
feature/88/plugin-registry
feature/91/model-abstraction
...
```

### Workflow

1. **Start Story:**
   ```bash
   git checkout release/0.1.0
   git pull origin release/0.1.0
   git checkout -b feature/87/configuration-system
   ```

2. **Implement & Test:**
   ```bash
   # Make changes
   git add .
   git commit -m "feat(story-87): implement config precedence"
   git push origin feature/87/configuration-system
   ```

3. **Open PR:**
   ```bash
   gh pr create --base release/0.1.0 --title "feat(story-87): Configuration System" --body "Resolves #87"
   ```

4. **After Merge:**
   ```bash
   git checkout release/0.1.0
   git pull origin release/0.1.0
   # Repeat for next story
   ```

5. **After All Stories Complete:**
   ```bash
   # Create PR to main
   gh pr create --base main --head release/0.1.0 --title "Release v0.1.0-alpha"
   
   # After merge, tag release
   git checkout main
   git pull origin main
   git tag v0.1.0-alpha
   git push origin v0.1.0-alpha
   ```

---

## ISSUE CREATION PLAN

New file created: [ISSUE_CREATION_PLAN.md](.context/project/agent_core_design/ISSUE_CREATION_PLAN.md)

### Contents

1. **Prerequisites:** Framework templates, authentication
2. **Issue Structure:** 21 issues (1 parent epic + 4 child epics + 16 stories)
3. **Creation Commands:** Step-by-step `gh` CLI commands
4. **Issue Body Templates:** Complete markdown for each issue
5. **Labels & Milestones:** Standard taxonomy
6. **Verification Checklist:** Quality gates

### Highlighted Features

**Comprehensive Story Example (Issue #87):**
- 14 numbered acceptance criteria (testable)
- Implementation notes (file structure, key algorithms)
- Definition of Done (checklist)
- Linked issues (Resolves, Blocks, Related)
- Resources (Design Docs with file paths, ADRs, Code References)
- Testing strategy (unit tests, integration tests, coverage targets)
- Evidence requirements (screenshots, logs, metrics)

**Template Compliance:**
- Follows space_framework 02-epic.md and 03-story.md templates
- Includes all required sections (Overview, Context, Acceptance Criteria, DoD)
- Proper parent-child relationships documented
- Cross-references to design documents and ADRs

---

## NEXT STEPS

### 1. Create Release Branch

```bash
# Create and push release branch
git checkout -b release/0.1.0
git push origin release/0.1.0

# Configure branch protection (require PR + review + CI)
gh api repos/nsin08/ai_agents_review/branches/release/0.1.0/protection -X PUT \
  -f required_pull_request_reviews[required_approving_review_count]=1 \
  -f required_status_checks[strict]=true \
  -f required_status_checks[contexts][]=test \
  -f enforce_admins=false
```

### 2. Create Milestones

```bash
gh api repos/nsin08/ai_agents_review/milestones -X POST \
  -f title="Week 1-2: Foundation" \
  -f due_on="2026-02-08T23:59:59Z"

gh api repos/nsin08/ai_agents_review/milestones -X POST \
  -f title="Week 3-4: Core" \
  -f due_on="2026-02-22T23:59:59Z"

gh api repos/nsin08/ai_agents_review/milestones -X POST \
  -f title="Week 5-6: Orchestration" \
  -f due_on="2026-03-08T23:59:59Z"

gh api repos/nsin08/ai_agents_review/milestones -X POST \
  -f title="Week 7-8: Polish" \
  -f due_on="2026-03-22T23:59:59Z"

gh api repos/nsin08/ai_agents_review/milestones -X POST \
  -f title="Phase 1 - Agent Core MVP" \
  -f due_on="2026-03-22T23:59:59Z"
```

### 3. Prepare Issue Body Files

```bash
# Create directory
mkdir -p .context/project/agent_core_design/issues

# Extract issue bodies from ISSUE_CREATION_PLAN.md
# Each body is a complete markdown section
# Save to individual files: epic-85-body.md, story-87-body.md, etc.
```

### 4. Create GitHub Issues

```bash
# Follow ISSUE_CREATION_PLAN.md step-by-step commands
# Start with parent epic, then child epics, then stories

# Example (Issue #85):
gh issue create \
  --title "Epic: Agent Core Phase 1 MVP Implementation" \
  --label "type:epic,state:approved,priority:high,phase:phase-1" \
  --milestone "Phase 1 - Agent Core MVP" \
  --body-file .context/project/agent_core_design/issues/epic-85-body.md
```

### 5. Update Cross-References

After all issues created, update bodies with actual issue numbers:
```bash
# Update Epic #85 with child epic links (#86, #90, #94, #98)
gh issue edit 85 --body-file .context/project/agent_core_design/issues/epic-85-body-updated.md

# Update Epic #86 with story links (#87, #88, #89)
gh issue edit 86 --body-file .context/project/agent_core_design/issues/epic-86-body-updated.md

# Repeat for all epics
```

---

## VALIDATION

### IMPLEMENTATION_PLAN.md Changes

✅ All story merge targets updated (16 stories)  
✅ CI/CD triggers updated (push to `release/*`)  
✅ Branch protection updated (base: `release/0.1.0`)  
✅ Workflow examples updated  
✅ Release checklist updated  

### ISSUE_CREATION_PLAN.md Content

✅ 21 issue templates (1 parent + 4 child epics + 16 stories)  
✅ Complete issue bodies with all required sections  
✅ Proper labels (type, state, priority, phase, layer, component)  
✅ Milestone assignments  
✅ Parent-child relationships documented  
✅ Cross-references to design documents  
✅ Testing strategies defined  
✅ Evidence requirements specified  
✅ GitHub CLI commands provided  

---

## SUMMARY

**Branch Strategy:** Phase 1 MVP will be developed on `release/0.1.0` branch, not `develop`

**Implementation Plan:** Updated with 20+ references to release branch

**Issue Creation Plan:** Comprehensive 95-page guide with:
- 21 complete GitHub issue templates
- Step-by-step creation commands
- Quality checklists
- Verification procedures

**Ready for Execution:** 
1. Create release branch
2. Configure protection
3. Create milestones
4. Create 21 GitHub issues
5. Begin Story #87 (Configuration System)

---

**Status:** ✅ COMPLETE  
**Next Action:** Create release branch and GitHub issues  
**Estimated Time:** 2-3 hours for issue creation

