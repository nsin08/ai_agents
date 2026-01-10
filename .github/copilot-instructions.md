# Copilot Instructions: [PROJECT_NAME]

**Framework:** space_framework (SDLC Governance Control Plane)  
**Framework Repository:** https://github.com/nsin08/space_framework  
**Purpose:** [ONE_LINE_PROJECT_DESCRIPTION]  
**Last Updated:** 2026-01-10

---

## Framework Integration

This project follows the **space_framework** governance model for AI-native SDLC enforcement.

**Load Framework Context:**
All governance rules are loaded from the framework repository. When working on this project, reference:

@workspace https://github.com/nsin08/space_framework

Or if using Copilot Spaces:

@space_framework

**Core Framework Principles:**
- **Enforcement-first:** Automation enforces policy, not documentation
- **State machine:** All work flows through: Idea → Approved → Ready → In Progress → In Review → Done → Released
- **Artifact linking:** Every PR links to Story, every Story links to Epic
- **Approval gates:** Only CODEOWNER can merge PRs
- **Evidence-based:** PRs require evidence (tests, screenshots, metrics)

---

## Essential Framework Files

When you need governance context, load these from https://github.com/nsin08/space_framework:

**Roles (10-roles/):**
- `00-shared-context.md` — ALWAYS load first for base constraints
- `05-implementer.md` — AI agent implementing Stories
- `06-reviewer.md` — AI agent reviewing PRs
- `09-codeowner.md` — Human maintainer (merge authority)

**Rules (20-rules/):**
- `01-state-machine.md` — Mandatory workflow states and transitions
- `02-definition-of-ready.md` — Exit criteria for state:ready
- `03-definition-of-done.md` — Exit criteria for state:done
- `04-artifact-linking.md` — PR → Story → Epic traceability
- `10-ai-agent-boundaries.md` — What AI agents can/cannot do
- `11-file-organization.md` — Where to place files (tests, temp, context)
- `12-label-taxonomy.md` — Standard label set and meanings

**Templates (50-templates/):**
- `01-idea.md` — Initial business need
- `02-epic.md` — Large feature breakdown
- `03-story.md` — Implementable unit of work
- `05-pull-request.md` — PR structure with evidence
- `05-dor-checklist.md` — Definition of Ready checklist
- `06-dod-checklist.md` — Definition of Done checklist

**Enforcement (70-enforcement/):**
- GitHub Actions workflows validate state transitions, artifact linking, approval gates
- Copy workflows from framework to project `.github/workflows/` as needed

---

## Project-Specific Context

**Project Name:** [PROJECT_NAME]  
**Repository:** [GITHUB_ORG]/[REPO_NAME]  
**Tech Stack:** [LANGUAGES/FRAMEWORKS]

### Build/Test Commands
```bash
# Build
[BUILD_COMMAND]

# Test
[TEST_COMMAND]

# Lint
[LINT_COMMAND]

# Run
[RUN_COMMAND]
```

### Architecture Overview
[2-3 SENTENCE ARCHITECTURE SUMMARY]

Key components:
- [COMPONENT_1]: [PURPOSE]
- [COMPONENT_2]: [PURPOSE]
- [COMPONENT_3]: [PURPOSE]

### Key Files
- [FILE_PATH_1]: [PURPOSE]
- [FILE_PATH_2]: [PURPOSE]
- [FILE_PATH_3]: [PURPOSE]

### File Organization (per Rule 11)
- **Application code:** `src/`, `lib/`, `app/` (standard project structure)
- **Tests:** `tests/unit/`, `tests/integration/`, `tests/e2e/`
- **Context docs:** `.context/` (project-level documentation)
- **Task working files:** `.context/tasks-{id}-{slug}__gh/` (temp files, gitignored)
- **CI/CD:** `.github/workflows/`

### Dependencies
[LIST_KEY_DEPENDENCIES_WITH_VERSIONS]

### Environment Variables
[LIST_REQUIRED_ENV_VARS_AND_PURPOSE]

---

## AI Agent Responsibilities

When working as an AI agent on this project:

### ✅ What You CAN Do
- Read/create issues following framework templates
- Implement code within assigned Story scope
- Create branches from `develop`: `feature/{story-#}/*` or `fix/{issue-#}/*`
- Open PRs back to `develop` linking to Stories: "Resolves #{story-#}"
- Run tests and provide evidence in PRs
- Request reviews (never self-approve)
- Write files per Rule 11 (tests in `tests/`, context in `.context/`)

### ❌ What You CANNOT Do
- Merge PRs (CODEOWNER only)
- Approve PRs (human reviewers only)
- Skip workflow states (enforced by GitHub Actions)
- Change issue state without meeting exit criteria
- Access secrets/credentials
- Write temp files to project root (Rule 11 violation)

### 🎯 Critical Workflow
1. Load framework context: `@space_framework` or reference GitHub repo
2. Read Story in `state:ready`
3. Create branch from `develop`: `git checkout develop && git pull origin develop && git checkout -b feature/{story-#}/{descriptor}`
4. Implement within Story acceptance criteria
5. Push commits with "fixes #{story-#}" or "feat(story-#): description"
6. Open PR to `develop` (not main) with evidence (tests pass, screenshots, metrics)
7. Request reviewers
8. Wait for approval + CI pass
9. CODEOWNER merges to `develop`
10. Main is synced from develop when ready for release

**Never skip states. Never self-merge. Always provide evidence. All feature branches merge to develop.**

---

## Response Format (REQUIRED)

Every AI agent response MUST follow this structure for clarity and auditability:

```markdown
## 1. Understanding
[What was requested, in 2-3 bullets]

## 2. Actions
- [ ] Action 1
- [ ] Action 2

## 3. Artifacts
| Item | Template | Action |
|------|----------|--------|

## 4. Tool Plan
[Commands to execute]

## 5. Exit Criteria
[What defines done]
```

---

## When You're Stuck

**Missing information?** Explicitly list what's needed:
```markdown
## ⚠️ Cannot Proceed
- Missing: Assignment to Story (required to create branch)
- Missing: Acceptance criteria in Story (needed to scope work)

Please provide above, then re-run with [Role: Implementer].
```

**Invalid state transition?** Check framework `20-rules/01-state-machine.md`:
```markdown
## ⚠️ Transition Blocked
Story cannot move from `state:in-progress` → `state:done` directly.
Required path: In Progress → In Review (PR required) → Done

Next: Open PR linking to this Story.
```

---

## Git Workflow - Branch Strategy

### Branch Naming
- **Feature branches**: `feature/{story-#}/{descriptor}` (e.g., `feature/12-lab-1-rag-fundamentals`)
- **Fix branches**: `fix/{issue-#}/{descriptor}` (e.g., `fix/15-memory-leak`)
- **Release**: `release/{version}` (e.g., `release/0.1.0`)

### Merge Strategy
- **Feature branches** → `develop` (via PR, CODEOWNER merges)
- **Develop** → `main` (when ready for release, CODEOWNER merges)
- **Never merge** feature branches directly to `main`
- **Always use squash merge** for clean commit history

### Base Branch Rules
- **Create from**: Always branch from latest `develop` (`git checkout develop && git pull origin develop`)
- **Submit PR to**: `develop` (base branch in PR)
- **Develop** is release candidate after weekly gate approval
- **Main** is stable release version

---

## Framework Home

**Repository:** https://github.com/nsin08/space_framework  
**Issues/Support:** https://github.com/nsin08/space_framework/issues  
**Documentation:** See framework README and 90-guides/

---
