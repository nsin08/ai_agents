# Story Assignment Guide

**Project**: ai_agents - Phase 1 MVP Implementation  
**Created**: January 25, 2026  
**Framework**: space_framework governance model  
**Branch Strategy**: Feature branches → `release/0.1.0` (NOT develop)

---

## Story Assignment Process

### Prerequisites for Assignment

Before a story can be assigned, it must meet **Definition of Ready**:
- [ ] Story has clear acceptance criteria
- [ ] Story is labeled `state:ready`
- [ ] Story is scoped to 1-3 days max
- [ ] Story has linked Epic (parent)
- [ ] Story has priority label
- [ ] Story has no blocking dependencies OR blockers are resolved

---

## Assignment Methods

### Method 1: Via GitHub Web UI (Recommended)

1. **Navigate to issue**: https://github.com/nsin08/ai_agents/issues/[NUMBER]
2. **Right sidebar** → **Assignees** section
3. Click **"Assign yourself"** (if you're taking it)
   - OR search for teammate's GitHub username
4. Click **Assign**
5. **Add label** `state:in-progress` (triggers automation)
6. **Optional**: Add comment announcing you're starting work

**Example Comment**:
```markdown
## 🚀 Starting Work

**Assigned to**: @username  
**Estimated completion**: Jan 27, 2026  
**Feature branch**: `feature/90-configuration-system`

**Next steps**:
- [ ] Create feature branch from release/0.1.0
- [ ] Implement acceptance criteria 1-3
- [ ] Write unit tests
- [ ] Submit PR to release/0.1.0
```

---

### Method 2: Via GitHub CLI (Fastest)

```bash
# Assign yourself to story #90
gh issue edit 90 --add-assignee @me

# Assign someone else
gh issue edit 90 --add-assignee nsin08

# Update state to in-progress
gh issue edit 90 --add-label "state:in-progress"

# Combined (assign + start work)
gh issue edit 90 --add-assignee @me --add-label "state:in-progress" --remove-label "state:ready"
```

---

### Method 3: Via Project Board (Visual)

1. Open project board: https://github.com/nsin08/ai_agents/projects/[PROJECT_ID]
2. Find story card in **Backlog** column
3. Click card to open details
4. **Assignees** → Select yourself
5. **Drag card** from Backlog → **In Progress** column
6. Automation will auto-add `state:in-progress` label

---

## Branch Creation (CRITICAL)

### Correct Branch Strategy ✅

**Base Branch**: `release/0.1.0` (NOT develop, NOT main)

```bash
# 1. Fetch latest release/0.1.0
git fetch origin
git checkout release/0.1.0
git pull origin release/0.1.0

# 2. Create feature branch
git checkout -b feature/90-configuration-system

# 3. Verify base branch
git branch -vv
# Output should show: feature/90-configuration-system tracking release/0.1.0
```

### Branch Naming Convention

**Format**: `feature/{story-#}-{short-descriptor}`

**Examples**:
- `feature/90-configuration-system` (Story #90)
- `feature/91-plugin-registry` (Story #91)
- `feature/92-test-infrastructure` (Story #92)
- `feature/96-local-engine` (Story #96)

**For bugs**: `fix/{issue-#}-{descriptor}`  
**For tasks**: `task/{issue-#}-{descriptor}`

---

## Assignment Workflow (Step-by-Step)

### Step 1: Pick Story from Backlog

**Check Project Board** or **Filter issues**:
```bash
# List all ready stories
gh issue list --label "state:ready" --label "phase:phase-1"

# List stories by priority
gh issue list --label "state:ready" --label "priority:high"

# List stories by layer (Foundation, Core, Orchestration, Polish)
gh issue list --label "state:ready" --label "layer:foundation"
```

**Selection Criteria**:
- Priority: `priority:critical` → `priority:high` → `priority:medium`
- Dependencies: Check "Depends on" section in story description
- Skillset: Match story to your expertise (config, testing, API, etc.)
- WIP limit: Max 3 stories per person at a time

---

### Step 2: Assign to Yourself

**Via CLI**:
```bash
gh issue edit 90 --add-assignee @me --add-label "state:in-progress"
```

**Via Web**:
1. Open issue #90
2. Right sidebar → Assignees → Assign yourself
3. Labels → Add `state:in-progress`, Remove `state:ready`

---

### Step 3: Create Feature Branch

```bash
# Always branch from release/0.1.0
git fetch origin
git checkout release/0.1.0
git pull origin release/0.1.0
git checkout -b feature/90-configuration-system
```

**NEVER branch from**:
- ❌ `main` (stable production)
- ❌ `develop` (not used in Phase 1)
- ❌ Another feature branch (creates dependency hell)

---

### Step 4: Implement Story

Follow **Definition of Done**:
- [ ] All acceptance criteria met
- [ ] Unit tests written and passing
- [ ] Integration tests (if applicable)
- [ ] Code follows Python conventions (PEP8, type hints)
- [ ] Docstrings for public APIs
- [ ] No hardcoded values (use config)
- [ ] Security review (no secrets in code)

**Commit Message Format**:
```bash
git commit -m "feat(story-90): Implement configuration system

- Add ProviderConfig with Pydantic validation
- Support env vars, YAML, explicit params
- Implement precedence: Explicit > Env > File > Default
- Add 14 unit tests with 100% coverage

Resolves #90
"
```

---

### Step 5: Push and Create PR

```bash
# Push feature branch
git push origin feature/90-configuration-system

# Create PR via CLI (CRITICAL: base=release/0.1.0)
gh pr create \
  --base release/0.1.0 \
  --title "Story #90: Configuration System" \
  --body "Resolves #90

## Changes
- Implemented ProviderConfig with Pydantic validation
- Added environment variable support
- Config precedence: Explicit > Env > File > Default
- 14 unit tests with 100% coverage

## Testing
\`\`\`bash
pytest tests/unit/test_config.py -v
\`\`\`

## Checklist
- [x] All acceptance criteria met
- [x] Tests passing (100% coverage)
- [x] Documentation updated
- [x] No breaking changes
- [x] Follows space_framework DoD
" \
  --assignee nsin08 \
  --label "state:in-review"
```

**OR via Web**:
1. Go to: https://github.com/nsin08/ai_agents/pulls
2. Click **New pull request**
3. **IMPORTANT**: Set **base: release/0.1.0** (NOT main, NOT develop)
4. Set **compare: feature/90-configuration-system**
5. Fill PR template
6. Request reviewers
7. Create PR

---

### Step 6: Code Review

**Automation** (already configured):
- PR creation → Issue moves to `state:in-review` automatically
- PR merged → Issue moves to `state:done` and closes

**Manual Actions**:
1. Request reviews: @nsin08 (CODEOWNER - required)
2. Address review comments
3. Update PR with fixes
4. Wait for approval ✅

---

### Step 7: Merge (CODEOWNER Only)

**CODEOWNER (@nsin08) merges** when:
- [ ] All CI checks pass ✅
- [ ] Code review approved ✅
- [ ] All acceptance criteria met ✅
- [ ] No merge conflicts
- [ ] Tests passing (95%+ coverage)

**Merge Strategy**: Squash merge (keeps history clean)

```bash
gh pr merge 150 --squash --delete-branch
```

**Automation** (post-merge):
- Issue #90 automatically gets `state:done` label
- Issue #90 automatically closes
- Feature branch deleted
- Release/0.1.0 updated with changes

---

## Assignment Rules (space_framework)

### Rule 1: Only One Story in Progress at a Time (Per Person)

**Why**: Prevents context switching, ensures completion over starting

**Exception**: If blocked, you can start second story while waiting for unblock

**Check your workload**:
```bash
gh issue list --assignee @me --label "state:in-progress"
```

**If you see 3+ stories**: Finish one before starting another

---

### Rule 2: Stories Must Be `state:ready` Before Assignment

**Invalid**:
- ❌ Assigning `state:idea` (not approved yet)
- ❌ Assigning `state:approved` (not broken down yet)

**Valid**:
- ✅ Assigning `state:ready` (DoR met, ready for dev)

**How to check**:
```bash
# Only show ready stories
gh issue list --label "state:ready" --label "phase:phase-1"
```

---

### Rule 3: Respect Dependencies

**Check "Depends on" section** in story description:
- If dependency story is `state:done` → You can start ✅
- If dependency story is `state:in-progress` → Wait or pair program
- If dependency story is `state:ready` → Coordinate with assignee

**Example** (Story #93 depends on Story #90):
```markdown
## Linked Issues
- **Depends on:** Story #90 (Config) ← Must be merged first
- **Blocks:** Story #96 (LocalEngine)
```

**Action**: Wait for #90 to be `state:done` before starting #93

---

### Rule 4: Always Create PR to `release/0.1.0`

**Correct PR base** ✅:
```
base: release/0.1.0 ← compare: feature/90-configuration-system
```

**Incorrect PR base** ❌:
```
base: main          ← WRONG (main is stable production)
base: develop       ← WRONG (not used in Phase 1)
```

**How to verify**:
```bash
git log --oneline --graph --decorate --all | head -20
```

Your feature branch should show `release/0.1.0` as upstream.

---

### Rule 5: No Self-Approval

**Who Can Merge**:
- ✅ @nsin08 (CODEOWNER) - Required approval
- ✅ Designated reviewers (if assigned)
- ❌ Story implementer (cannot self-merge)

**Enforcement**: CODEOWNERS file + branch protection

---

## WIP (Work In Progress) Limits

### Individual Limits
- **Max 1-2 stories per person** at a time
- **Max 3 days per story** (if longer, break down further)

### Team Limits (Project Board)
- **Backlog**: No limit (planning queue)
- **In Progress**: Max 3 stories total (prevents bottleneck)
- **In Review**: No limit (encourage reviews)
- **Done**: Archive weekly (keep board clean)

**Check WIP violations**:
```bash
# Count stories in progress
gh issue list --label "state:in-progress" --json number,title,assignees

# If count > 3 → WIP limit violated
```

---

## Story Assignment Matrix

| Story # | Title | Layer | Priority | Effort | Dependencies | Status |
|---------|-------|-------|----------|--------|--------------|--------|
| #90 | Configuration System | Foundation | High | 2d | None | Ready |
| #91 | Plugin Registry | Foundation | High | 1.5d | #90 | Ready |
| #92 | Test Infrastructure | Foundation | High | 1.5d | None | Ready |
| #93 | Model Abstraction | Core | High | 3d | #90, #91, #92 | Approved |
| #94 | Tool Executor | Core | High | 2.5d | #93 | Approved |
| #95 | Short-Term Memory | Core | High | 1.5d | None | Approved |
| #96 | LocalEngine | Orchestration | Critical | 3d | #93, #94, #95 | Approved |
| #97 | AgentCore API | Orchestration | Critical | 2d | #96 | Approved |
| #98 | Observability | Orchestration | High | 2d | #96 | Approved |
| #99 | Artifacts | Polish | High | 1.5d | #97, #98 | Approved |
| #100 | CLI | Polish | Medium | 1.5d | #97 | Approved |
| #101 | Integration Tests | Polish | High | 2d | #99, #100 | Approved |
| #102 | Documentation | Polish | Medium | 1.5d | #97, #99 | Approved |

**How to use this matrix**:
1. Pick stories with `state:ready`
2. Check dependencies column
3. Assign stories in order (Foundation → Core → Orchestration → Polish)

---

## Quick Reference Commands

### Assignment
```bash
# Assign story to yourself
gh issue edit 90 --add-assignee @me --add-label "state:in-progress"

# Create feature branch
git checkout release/0.1.0 && git pull && git checkout -b feature/90-config

# Push and create PR
git push origin feature/90-config
gh pr create --base release/0.1.0 --title "Story #90: Config" --body "Resolves #90"
```

### Monitoring
```bash
# My assigned stories
gh issue list --assignee @me

# All in-progress stories
gh issue list --label "state:in-progress"

# Ready stories (available for assignment)
gh issue list --label "state:ready"

# Check dependencies
gh issue view 93 --json title,body
```

---

## Troubleshooting

### "I can't assign myself"
**Cause**: Not a repository collaborator  
**Fix**: Ask @nsin08 to add you as collaborator

### "PR created to wrong base branch"
**Cause**: Forgot to set base=release/0.1.0  
**Fix**: Edit PR, change base branch to `release/0.1.0`

### "Story blocked by dependency"
**Cause**: Dependency story not yet `state:done`  
**Fix**: Wait, or coordinate with dependency story assignee

### "More than 3 stories in progress"
**Cause**: WIP limit violation  
**Fix**: Finish stories before starting new ones

---

## Related Resources

- **Epic #85**: Phase 1 MVP Implementation (parent)
- **Kanban Board**: https://github.com/nsin08/ai_agents/projects/[ID]
- **Branch Strategy**: `.context/project/governance/BRANCH_STRATEGY.md`
- **Workflow Automation**: `.github/workflows/kanban-automation.yml`

---

**Guide Owner**: @nsin08  
**Last Updated**: January 25, 2026  
**Status**: Active - Phase 1 MVP
