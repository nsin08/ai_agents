# Space Framework Governance - Setup Documentation Index

**Repository:** https://github.com/nsin08/ai_agents  
**Adoption Date:** 2026-01-20  
**Status:** ✅ **COMPLETE** (8 of 10 automated steps done)

---

## 📄 Documentation Files (in `.github/`)

| File | Purpose | Read Time |
|------|---------|-----------|
| **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** | 1-page summary of setup (START HERE) | 2 min |
| **[ADOPTION_SUMMARY.md](./ADOPTION_SUMMARY.md)** | Comprehensive guide with all manual steps | 10 min |
| **[SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md)** | Original setup guide with detailed checklists | 10 min |
| **[README.md (this file)](./README.md)** | This index | 5 min |

---

## 📋 How to Use This Setup

### 1. **First Time?** (5 minutes)

Read: **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)**

It tells you:
- ✅ What's already done
- ⚠️ What still needs manual work
- 🚀 How to proceed

### 2. **Need Details?** (10 minutes)

Read: **[ADOPTION_SUMMARY.md](./ADOPTION_SUMMARY.md)**

It contains:
- Complete file tree showing what was created
- Step-by-step manual configuration
- Full `gh` CLI commands (copy/paste ready)
- GitHub UI instructions with screenshots
- Verification checklist

### 3. **Creating Labels?**

Use the scripts:
- **Bash/Linux/Mac:** Run `./create-labels.sh`
- **PowerShell/Windows:** Run `./create-labels.ps1`

Or copy commands from **[ADOPTION_SUMMARY.md](./ADOPTION_SUMMARY.md)** Section 8

### 4. **Configuring Branch Protection?**

See **[ADOPTION_SUMMARY.md](./ADOPTION_SUMMARY.md)** Section 9:
- Option A: Use `gh api` command
- Option B: Manual GitHub UI steps (recommended)

### 5. **Following the Governance Model?**

Read the framework documentation:
- **Shared Context:** https://github.com/nsin08/space_framework/blob/main/10-roles/00-shared-context.md
- **State Machine:** https://github.com/nsin08/space_framework/blob/main/20-rules/01-state-machine.md
- **All Rules:** https://github.com/nsin08/space_framework/tree/main/20-rules

---

## ✅ What Was Automated (8 Steps)

```
✅ 1. Copilot Instructions          (.github/copilot-instructions.md)
✅ 2. CODEOWNERS                    (.github/CODEOWNERS)
✅ 3. .gitignore (Rule 11)          (.gitignore)
✅ 4. Context Directories           (.context/project/, .context/sprint/)
✅ 5. Issue Templates (7)           (.github/ISSUE_TEMPLATE/*)
✅ 6. PR Template                   (.github/pull_request_template.md)
✅ 7. Enforcement Workflows (17)    (.github/workflows/*)
✅ 8. Documentation                 (This set of files)

⚠️  9. GitHub Labels                (Manual - use gh CLI or GitHub UI)
⚠️  10. Branch Protection           (Manual - GitHub admin action)
```

---

## 🎯 Next Actions (In Order)

### Immediate (5 min)
1. Read [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
2. Commit the changes:
   ```bash
   git add .github/ .context/ .gitignore
   git commit -m "chore: adopt space_framework governance"
   git push
   ```

### Within 1 Hour (5 min each)
3. Create GitHub labels (use script or `gh` commands)
4. Configure branch protection (GitHub UI)

### Verify (5 min)
5. Check labels created: https://github.com/nsin08/ai_agents/labels
6. Check branch protection: https://github.com/nsin08/ai_agents/settings/branches
7. Test by creating an issue with the Idea template

---

## 📊 File Structure Overview

```
.github/
├── copilot-instructions.md     → Framework integration guide
├── CODEOWNERS                  → Merge authority (@nsin08)
├── pull_request_template.md    → PR checklist with evidence mapping
├── create-labels.sh            → Script to create labels (bash)
├── create-labels.ps1           → Script to create labels (PowerShell)
├── QUICK_REFERENCE.md          → 1-page summary (START HERE!)
├── ADOPTION_SUMMARY.md         → Complete guide with all steps
├── SETUP_INSTRUCTIONS.md       → Original detailed setup guide
├── README.md                   → This file (documentation index)
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
│   └── README.md               → Architecture & ADR index
├── sprint/
│   └── README.md               → Sprint cadence & process
└── [other directories preserved]

.gitignore                       → Updated with Rule 11 ignores
```

---

## 🔗 Key Links

| Purpose | URL |
|---------|-----|
| **Framework Repo** | https://github.com/nsin08/space_framework |
| **This Repo** | https://github.com/nsin08/ai_agents |
| **Labels** | https://github.com/nsin08/ai_agents/labels |
| **Branch Protection** | https://github.com/nsin08/ai_agents/settings/branches |
| **CODEOWNERS Settings** | https://github.com/nsin08/ai_agents/settings/access |
| **Workflows** | https://github.com/nsin08/ai_agents/actions |

---

## ❓ FAQ

**Q: Where do I start?**  
A: Read [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) (2 min), then [ADOPTION_SUMMARY.md](./ADOPTION_SUMMARY.md) Section 8 (create labels).

**Q: Do I need to use all 17 workflows?**  
A: Yes. They're designed to enforce the space_framework governance model automatically. They're lightweight and only run on pull requests and issues.

**Q: Can I modify the issue templates?**  
A: Yes. They're in `.github/ISSUE_TEMPLATE/` and can be customized. See the framework repo for examples.

**Q: What if I don't have admin access?**  
A: You can still create labels with `gh` CLI (requires auth). Branch protection requires admin and must be set via GitHub UI.

**Q: How do I use the governance model?**  
A: Create an Idea issue, approve it, break into Epic, create Stories, implement with PRs. See the framework documentation.

**Q: Where do I put my notes/work?**  
A: Use `.context/temp/` (git-ignored) for drafts, then move stable docs to `.context/project/` or `.context/sprint/` (committed).

---

## 📞 Support

**Questions about this setup?**  
See [ADOPTION_SUMMARY.md](./ADOPTION_SUMMARY.md) - Troubleshooting section

**Questions about the framework?**  
Visit https://github.com/nsin08/space_framework/issues

**Questions about GitHub features?**  
See https://docs.github.com

---

## ✨ What Happens Now

When files are committed and pushed:

1. ✅ Workflows start validating PRs/Issues
2. ✅ CODEOWNERS is recognized as merge authority
3. ✅ Team members see issue templates when creating issues
4. ✅ PRs use the evidence mapping template
5. ⚠️ Labels are available (once created)
6. ⚠️ Branch protection enforces rules (once configured)

---

**Setup Generated:** 2026-01-20  
**Framework Version:** space_framework (main branch, Jan 20 2026)  
**Status:** ✅ Ready for label creation and branch protection configuration

→ **Next:** Read [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
