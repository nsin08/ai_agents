# Space Framework Adoption - Quick Reference

**Status:** ✅ Automated setup complete (8/10 steps)  
**Repository:** https://github.com/nsin08/ai_agents  
**Framework:** https://github.com/nsin08/space_framework

---

## What's Done ✅

```
✅ .github/copilot-instructions.md    → Framework integration
✅ .github/CODEOWNERS                 → @nsin08 as merge authority  
✅ .github/ISSUE_TEMPLATE/            → 7 issue templates
✅ .github/pull_request_template.md   → Evidence mapping
✅ .github/workflows/                 → 17 enforcement workflows
✅ .context/project/README.md         → Architecture & ADR index
✅ .context/sprint/README.md          → Sprint cadence
✅ .gitignore                         → Rule 11 context organization
```

---

## What's Left (Manual - 5 min)

### 1. Create Labels (gh CLI)

```bash
# Run label creation commands from:
# .github/SETUP_INSTRUCTIONS.md (Section 8)
# OR .github/ADOPTION_SUMMARY.md (Step 8)
```

### 2. Configure Branch Protection (GitHub UI)

```
Visit: https://github.com/nsin08/ai_agents/settings/branches
Add rule for: main
```

---

## File Tree (Expected)

```
.github/
├── CODEOWNERS
├── copilot-instructions.md
├── pull_request_template.md
├── SETUP_INSTRUCTIONS.md
├── ADOPTION_SUMMARY.md
├── ISSUE_TEMPLATE/
│   ├── 01-idea.md
│   ├── 02-epic.md
│   ├── 03-story.md
│   ├── 04-task.md
│   ├── 05-dor-checklist.md
│   ├── 06-dod-checklist.md
│   └── 07-feature-request.md
└── workflows/
    ├── 01-enforce-state-machine.yml
    ├── 02-enforce-artifact-linking.yml
    ├── 03-enforce-approval-gates.yml
    ├── 04-audit-logger.yml
    ├── 05-security-gate.yml
    ├── 06-pr-validation.yml
    ├── 07-issue-validation.yml
    ├── 08-branch-protection.yml
    ├── 09-code-quality.yml
    ├── 10-release-automation.yml
    ├── 11-security-checks.yml
    ├── 12-epic-story-tracking.yml
    ├── 13-definition-of-ready.yml
    ├── 14-definition-of-done.yml
    ├── 15-labeling-standard.yml
    ├── 16-commit-lint.yml
    └── 17-file-organization.yml

.context/
├── project/
│   └── README.md
├── sprint/
│   └── README.md
└── [other directories]

.gitignore (updated)
```

---

## Governance Model

```
IDEA → APPROVED → READY → IN PROGRESS → IN REVIEW → DONE → RELEASED
       ✅ Auto   ✅ Auto  ✅ Auto      ✅ Auto     ✅ Auto  ✅ Auto
```

**Key Rules:**
- Rule 01: State machine (above)
- Rule 02: DoR (Definition of Ready)
- Rule 03: DoD (Definition of Done)
- Rule 04: Artifact linking (PR → Story → Epic)
- Rule 11: File organization (.context/ structure)
- Rule 12: Label taxonomy (state/type/priority/role)

---

## Quick Commit

```bash
git add .github/ .context/ .gitignore
git commit -m "chore: adopt space_framework governance

- CODEOWNERS: @nsin08 as merge authority
- Issue templates: 7 types per framework
- PR template: with evidence mapping
- Workflows: 17 enforcement rules
- Context: project and sprint organization (Rule 11)
- Labels: ready via gh CLI (see SETUP_INSTRUCTIONS.md)

Ref: https://github.com/nsin08/space_framework"
git push
```

---

## Labels to Create

### State Labels
- `state:idea` `state:approved` `state:ready` `state:in-progress` `state:in-review` `state:done` `state:released`

### Type Labels
- `type:idea` `type:epic` `type:story` `type:task` `type:bug` `type:feature-request`

### Priority Labels
- `priority:critical` `priority:high` `priority:medium` `priority:low`

### Role Labels
- `role:implementer` `role:reviewer` `role:codeowner`

**Total: 23 labels**

---

## Branch Protection (main)

✅ Require PR  
✅ Require CODEOWNER review  
✅ Require status checks (≥7)  
✅ Dismiss stale reviews  
✅ Require conversation resolution  
✅ Require linear history  
❌ Allow force push  
❌ Allow delete  

---

## Framework Links

| | URL |
|---|---|
| **Repo** | https://github.com/nsin08/space_framework |
| **Rules** | github.com/nsin08/space_framework/tree/main/20-rules |
| **Roles** | github.com/nsin08/space_framework/tree/main/10-roles |
| **Workflows** | github.com/nsin08/space_framework/tree/main/70-enforcement |

---

**Setup Date:** 2026-01-20  
**Maintainer:** @nsin08
