# Space Framework Governance Setup - Completion Report

**Repository:** https://github.com/nsin08/ai_agents  
**Setup Date:** 2026-01-20  
**Status:** ✅ COMPLETE (8/10 steps automated)

---

## ✅ Automated Setup Summary

### 1. ✅ Copilot Instructions
- **File:** `.github/copilot-instructions.md`
- **Status:** Already exists with proper space_framework integration
- **Content:** Includes framework context, project identity, governance rules, AI agent boundaries

### 2. ✅ CODEOWNERS Configuration
- **File:** `.github/CODEOWNERS`
- **Status:** Updated with @nsin08 as merge authority
- **Content:**
  ```
  *       @nsin08
  /.github/  @nsin08
  ```

### 3. ✅ .gitignore Updates
- **File:** `.gitignore`
- **Status:** Updated with Rule 11 standard ignores
- **Added:**
  ```
  .context/temp/
  .context/issues/
  .context/reports/
  ```

### 4. ✅ Context Documentation
- **Files Created:**
  - `.context/project/README.md` — Project purpose, architecture, governance links
  - `.context/sprint/README.md` — Sprint cadence, naming conventions, approval process

### 5. ✅ Issue Templates (7 templates)
- **Directory:** `.github/ISSUE_TEMPLATE/`
- **Templates Created:**
  - `01-idea.md` — 💡 New business ideas
  - `02-epic.md` — 🎯 Technical breakdowns
  - `03-story.md` — 📖 Implementable units of work
  - `04-task.md` — 🔧 Chores/refactors/docs
  - `05-dor-checklist.md` — Definition of Ready checklist
  - `06-dod-checklist.md` — Definition of Done checklist
  - `07-feature-request.md` — ✨ Feature requests

### 6. ✅ Pull Request Template
- **File:** `.github/pull_request_template.md`
- **Status:** Created from framework template
- **Includes:** Evidence mapping table, code quality checklist, documentation checklist, process checklist

### 7. ✅ Enforcement Workflows (17 workflows)
- **Directory:** `.github/workflows/`
- **All workflows copied from space_framework/70-enforcement/:**
  1. `01-enforce-state-machine.yml` — Validates state transitions
  2. `02-enforce-artifact-linking.yml` — Ensures PR→Story→Epic linking
  3. `03-enforce-approval-gates.yml` — Validates CODEOWNER reviews
  4. `04-audit-logger.yml` — Logs all state/PR changes
  5. `05-security-gate.yml` — Validates security policies
  6. `06-pr-validation.yml` — Comprehensive PR checks
  7. `07-issue-validation.yml` — Issue template compliance
  8. `08-branch-protection.yml` — Enforces branch rules
  9. `09-code-quality.yml` — Linting/formatting/tests
  10. `10-release-automation.yml` — Release workflow
  11. `11-security-checks.yml` — SAST/dependency scanning
  12. `12-epic-story-tracking.yml` — Tracks Epic → Story status
  13. `13-definition-of-ready.yml` — Validates DoR criteria
  14. `14-definition-of-done.yml` — Validates DoD criteria
  15. `15-labeling-standard.yml` — Rule 12 label enforcement
  16. `16-commit-lint.yml` — Conventional commits validation
  17. `17-file-organization.yml` — Rule 11 file organization validation

---

## ⚠️ Manual Setup Required (2 steps)

### 8️⃣ GitHub Labels Setup

**Status:** ❌ REQUIRES MANUAL ACTION (or use gh CLI commands below)

Run these commands to create Rule 12 standard labels:

```bash
# State Labels (workflow states)
gh label create "state:idea" --description "Initial business idea" --color "FFA500" --repo nsin08/ai_agents
gh label create "state:approved" --description "Idea approved by stakeholder" --color "0075CA" --repo nsin08/ai_agents
gh label create "state:ready" --description "Story ready for implementation (DoR met)" --color "7057FF" --repo nsin08/ai_agents
gh label create "state:in-progress" --description "Currently being worked on" --color "FBCA04" --repo nsin08/ai_agents
gh label create "state:in-review" --description "In code review (PR open)" --color "E99695" --repo nsin08/ai_agents
gh label create "state:done" --description "Complete and merged (DoD met)" --color "28A745" --repo nsin08/ai_agents
gh label create "state:released" --description "Deployed to production" --color "004B87" --repo nsin08/ai_agents

# Type Labels (issue/PR types)
gh label create "type:idea" --description "Business idea or feature concept" --color "1D76DB" --repo nsin08/ai_agents
gh label create "type:epic" --description "Large feature breakdown" --color "0052CC" --repo nsin08/ai_agents
gh label create "type:story" --description "User story or feature" --color "D4C5F9" --repo nsin08/ai_agents
gh label create "type:task" --description "Chore, refactor, or technical work" --color "BFD4F2" --repo nsin08/ai_agents
gh label create "type:bug" --description "Bug report" --color "D73A49" --repo nsin08/ai_agents
gh label create "type:feature-request" --description "Feature request from user" --color "A2EEEF" --repo nsin08/ai_agents

# Priority Labels
gh label create "priority:critical" --description "Blocking, urgent" --color "FF0000" --repo nsin08/ai_agents
gh label create "priority:high" --description "Important, needed soon" --color "FF6B6B" --repo nsin08/ai_agents
gh label create "priority:medium" --description "Normal priority" --color "FFA500" --repo nsin08/ai_agents
gh label create "priority:low" --description "Nice to have, future" --color "90EE90" --repo nsin08/ai_agents

# Role Labels (for assignment/review)
gh label create "role:implementer" --description "Implementation task" --color "CCCCCC" --repo nsin08/ai_agents
gh label create "role:reviewer" --description "Requires review" --color "999999" --repo nsin08/ai_agents
gh label create "role:codeowner" --description "Requires CODEOWNER action" --color "333333" --repo nsin08/ai_agents

# Epic/Tracking Labels (sprint)
gh label create "sprint:2026-W03" --description "Sprint 3, 2026" --color "61DAFB" --repo nsin08/ai_agents
```

**Or via GitHub UI:**
1. Go to https://github.com/nsin08/ai_agents/labels
2. Create labels matching the table in step 9

---

### 9️⃣ Branch Protection Setup

**Status:** ❌ REQUIRES MANUAL ACTION (admin-only)

#### Option A: Use `gh api` command

```bash
# Enable branch protection on 'main' branch
gh api repos/nsin08/ai_agents/branches/main/protection \
  --input /dev/stdin <<< '{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "01-enforce-state-machine",
      "02-enforce-artifact-linking",
      "03-enforce-approval-gates",
      "06-pr-validation",
      "09-code-quality",
      "16-commit-lint",
      "17-file-organization"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "require_linear_history": true,
  "require_conversation_resolution": true
}'
```

#### Option B: Manual GitHub UI Setup

Go to https://github.com/nsin08/ai_agents/settings/branches

**Create rule for:** `main` branch

1. **Require a pull request before merging**
   - ✅ Require approvals
   - Approvals required: **1**
   - ✅ Require review from Code Owners
   - ✅ Dismiss stale pull request approvals when new commits are pushed

2. **Require status checks to pass before merging**
   - ✅ Require branches to be up to date before merging
   - Check these required status checks:
     - `01-enforce-state-machine`
     - `02-enforce-artifact-linking`
     - `03-enforce-approval-gates`
     - `06-pr-validation`
     - `09-code-quality`
     - `16-commit-lint`
     - `17-file-organization`

3. **Require conversation resolution**
   - ✅ Checked

4. **Require linear history**
   - ✅ Checked

5. **Block direct pushes**
   - ✅ Include administrators

6. **Allow force pushes & deletions**
   - ❌ Do NOT allow

---

## 📋 Verification Checklist

Run this checklist to confirm setup is complete:

### Files & Directories

- [ ] `.github/copilot-instructions.md` exists with space_framework references
- [ ] `.github/CODEOWNERS` exists with @nsin08 entries
- [ ] `.github/pull_request_template.md` exists with evidence mapping table
- [ ] `.github/ISSUE_TEMPLATE/` directory has all 7 templates:
  - [ ] `01-idea.md`
  - [ ] `02-epic.md`
  - [ ] `03-story.md`
  - [ ] `04-task.md`
  - [ ] `05-dor-checklist.md`
  - [ ] `06-dod-checklist.md`
  - [ ] `07-feature-request.md`
- [ ] `.github/workflows/` has all 17 enforcement workflows (*.yml)
- [ ] `.gitignore` includes:
  - [ ] `.context/temp/`
  - [ ] `.context/issues/`
  - [ ] `.context/reports/`
- [ ] `.context/project/README.md` exists
- [ ] `.context/sprint/README.md` exists

### GitHub Configuration

- [ ] **Labels Created** (Rule 12):
  - [ ] State labels: `state:idea`, `state:approved`, `state:ready`, `state:in-progress`, `state:in-review`, `state:done`, `state:released`
  - [ ] Type labels: `type:idea`, `type:epic`, `type:story`, `type:task`, `type:bug`, `type:feature-request`
  - [ ] Priority labels: `priority:critical`, `priority:high`, `priority:medium`, `priority:low`
  - [ ] Role labels: `role:implementer`, `role:reviewer`, `role:codeowner`

- [ ] **Branch Protection** (admin action):
  - [ ] Main branch requires PRs
  - [ ] Main branch requires CODEOWNER review
  - [ ] Main branch requires status checks (at least 7)
  - [ ] Main branch blocks direct pushes
  - [ ] Main branch blocks force pushes

- [ ] **Workflow Triggers:**
  - [ ] At least one workflow appears in Actions tab
  - [ ] Pull request validations are active

### Documentation

- [ ] Project README links to governance framework
- [ ] `.context/project/README.md` documents architecture and ADR process
- [ ] `.context/sprint/README.md` documents sprint cadence

---

## 🚀 Next Steps

### 1. Verify Files are Committed

```bash
cd /path/to/ai_agents
git status
git add .github/ .context/ .gitignore
git commit -m "chore: adopt space_framework governance model

- Add copilot-instructions.md with framework integration
- Create CODEOWNERS file (@nsin08 as merge authority)
- Update .gitignore per Rule 11 (context org)
- Create issue templates (7 types)
- Create PR template with evidence mapping
- Install 17 enforcement workflows
- Create project and sprint context docs

Governance enforced via GitHub Actions + branch protection.
Ref: https://github.com/nsin08/space_framework"

git push origin develop
```

### 2. Create Setup PR (or merge directly if CODEOWNER)

```bash
# If using a branch
git checkout -b setup/space-framework-adoption
git push origin setup/space-framework-adoption
# Then open PR to develop
```

### 3. Configure Labels (run commands from Section 8)

```bash
# Run the gh label create commands above
```

### 4. Configure Branch Protection (admin action, Section 9)

Open https://github.com/nsin08/ai_agents/settings/branches and follow the checklist.

### 5. Create First Tracked Items

Once setup is complete, test the governance:

```bash
# Create an Idea issue (this will auto-add state:idea label)
gh issue create --title "Example: Setup verification" \
  --body "Testing space_framework governance" \
  --label "type:idea" \
  --repo nsin08/ai_agents
```

---

## 📚 Framework References

- **Framework Repository:** https://github.com/nsin08/space_framework
- **Rules:** https://github.com/nsin08/space_framework/tree/main/20-rules
- **Roles:** https://github.com/nsin08/space_framework/tree/main/10-roles
- **Workflows:** https://github.com/nsin08/space_framework/tree/main/70-enforcement

---

## ✅ Setup Status Summary

| Component | Status | Location |
|-----------|--------|----------|
| Copilot Instructions | ✅ Done | `.github/copilot-instructions.md` |
| CODEOWNERS | ✅ Done | `.github/CODEOWNERS` |
| .gitignore | ✅ Done | `.gitignore` |
| Issue Templates | ✅ Done | `.github/ISSUE_TEMPLATE/` (7 files) |
| PR Template | ✅ Done | `.github/pull_request_template.md` |
| Enforcement Workflows | ✅ Done | `.github/workflows/` (17 files) |
| Context Docs | ✅ Done | `.context/project/` + `.context/sprint/` |
| GitHub Labels | ⚠️ Manual | See Section 8 |
| Branch Protection | ⚠️ Manual | See Section 9 |

---

**Generated:** 2026-01-20  
**Framework Version:** space_framework (latest from 2026-01-20 clone)  
**Maintainer:** @nsin08

### Step 1: Replace Placeholders in Created Files

**In `.github/copilot-instructions.md`:**
- `[PROJECT_NAME]` → Your project name (e.g., "AI Agents Documentation")
- `[ONE_LINE_PROJECT_DESCRIPTION]` → Brief purpose (e.g., "Comprehensive AI agent architecture documentation")
- `[GITHUB_ORG]` → Your GitHub organization or username
- `[REPO_NAME]` → Your repository name
- `[LANGUAGES/FRAMEWORKS]` → Tech stack (e.g., "Markdown, Python examples")
- `[BUILD_COMMAND]` → Build command (e.g., "N/A for documentation" or "mkdocs build")
- `[TEST_COMMAND]` → Test command (e.g., "markdownlint *.md" or "N/A")
- `[LINT_COMMAND]` → Lint command (e.g., "markdownlint ." or "N/A")
- `[RUN_COMMAND]` → Run command (e.g., "mkdocs serve" or "N/A")
- `[COMPONENT_*]` → Key architectural components (or remove if N/A)
- `[FILE_PATH_*]` → Important files in your project
- `[LIST_KEY_DEPENDENCIES_WITH_VERSIONS]` → Main dependencies (or "None" for docs)
- `[LIST_REQUIRED_ENV_VARS_AND_PURPOSE]` → Environment variables (or "None")

**In `.github/CODEOWNERS`:**
- `[GITHUB_USERNAME]` → Your GitHub username (e.g., `@nsin08`)

---

### Step 2: Create GitHub Labels

Run these commands using GitHub CLI (install from https://cli.github.com if needed):

```bash
# Navigate to your repository directory first
cd d:\wsl_shared\src\ai_agents

# State labels (state machine enforcement)
gh label create "state:idea" --color "d4c5f9" --description "Initial concept, needs approval"
gh label create "state:approved" --color "bfd4f2" --description "Approved, needs breakdown"
gh label create "state:ready" --color "0e8a16" --description "Ready for implementation"
gh label create "state:in-progress" --color "fbca04" --description "Work in progress"
gh label create "state:in-review" --color "ff9800" --description "PR under review"
gh label create "state:done" --color "5319e7" --description "Complete, not released"
gh label create "state:released" --color "000000" --description "Released to production"

# Type labels (artifact categorization)
gh label create "type:idea" --color "d4c5f9" --description "Business need"
gh label create "type:epic" --color "3e4b9e" --description "Large feature"
gh label create "type:story" --color "0075ca" --description "Implementable unit"
gh label create "type:task" --color "d4edda" --description "Technical task"
gh label create "type:bug" --color "d73a4a" --description "Bug fix"

# Priority labels
gh label create "priority:critical" --color "b60205" --description "Blocking issue"
gh label create "priority:high" --color "d93f0b" --description "Important"
gh label create "priority:medium" --color "fbca04" --description "Normal priority"
gh label create "priority:low" --color "0e8a16" --description "Nice to have"

# Role labels (assignment)
gh label create "role:client" --color "e99695" --description "Client/stakeholder"
gh label create "role:po" --color "f9d0c4" --description "Product Owner"
gh label create "role:pm" --color "fef2c0" --description "Project Manager"
gh label create "role:architect" --color "c5def5" --description "Architect"
gh label create "role:implementer" --color "c2e0c6" --description "Developer/Implementer"
gh label create "role:reviewer" --color "d4c5f9" --description "Code Reviewer"
gh label create "role:devops" --color "bfdadc" --description "DevOps Engineer"
gh label create "role:codeowner" --color "0e8a16" --description "CODEOWNER (merge authority)"
```

**Alternative: Create labels via GitHub Web UI:**
1. Go to your repository on GitHub
2. Navigate to: **Issues** → **Labels** → **New label**
3. Create each label with the color and description shown above

---

### Step 3: Configure Branch Protection Rules

**Important:** This must be done via GitHub Web UI (branch protection cannot be set via CLI for security reasons).

#### For `main` branch:

1. Go to your repository on GitHub
2. Navigate to: **Settings** → **Branches** → **Add rule**
3. Set **Branch name pattern:** `main`
4. Enable these settings:

   **✅ Require a pull request before merging**
   - ✅ Require approvals: **1**
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require review from Code Owners

   **✅ Require status checks to pass before merging**
   - ✅ Require branches to be up to date before merging
   - (Add specific status checks once you have CI workflows)

   **✅ Require conversation resolution before merging**

   **✅ Do not allow bypassing the above settings**
   - This ensures even admins follow the process

5. Click **Create** or **Save changes**

#### For `develop` branch (if using GitFlow):

Repeat the same steps for branch name pattern: `develop`

---

### Step 4: Optional - Copy Enforcement Workflows

To enable automated validation of space_framework rules, copy workflows from the framework repository.

**Recommended workflows:**

```bash
# Create workflows directory if it doesn't exist
mkdir -p .github/workflows

# Download workflows (using curl or manually from GitHub)
# Visit: https://github.com/nsin08/space_framework/tree/main/70-enforcement

# Essential workflows to copy:
# - 01-enforce-state-machine.yml - Validates state transitions
# - 02-enforce-artifact-linking.yml - Ensures PR → Story → Epic links
# - 06-pr-validation.yml - Validates PR structure and evidence
# - 07-issue-validation.yml - Validates issue templates
```

**Manual steps:**
1. Visit https://github.com/nsin08/space_framework/tree/main/70-enforcement
2. Download the workflows you want
3. Place them in `.github/workflows/` directory
4. Review and customize for your project needs
5. Commit and push to trigger first validation

---

### Step 5: Create Initial Issue Templates

Copy issue templates from space_framework to standardize issue creation:

```bash
# Create templates directory
mkdir -p .github/ISSUE_TEMPLATE

# Download templates from:
# https://github.com/nsin08/space_framework/tree/main/50-templates
```

**Recommended templates:**
- `01-idea.md` → `.github/ISSUE_TEMPLATE/idea.md`
- `02-epic.md` → `.github/ISSUE_TEMPLATE/epic.md`
- `03-story.md` → `.github/ISSUE_TEMPLATE/story.md`
- `04-bug.md` → `.github/ISSUE_TEMPLATE/bug.md` (if exists)

---

## 🧪 Verification Checklist

Once all steps are complete, verify your setup:

- [ ] `.github/copilot-instructions.md` has all placeholders replaced
- [ ] `.github/CODEOWNERS` has your GitHub username
- [ ] All 23 labels created in repository
- [ ] Branch protection enabled for `main` (and `develop` if applicable)
- [ ] CODEOWNERS file recognized (check Settings → Code and automation → CODEOWNERS)
- [ ] Enforcement workflows added (optional but recommended)
- [ ] Issue templates added (optional but recommended)

**Test the setup:**
1. Create a test branch
2. Make a small change
3. Open a PR
4. Verify:
   - CODEOWNER is automatically requested as reviewer
   - Cannot merge without approval
   - Labels are available for categorization

---

## 📚 Next Steps

1. **Customize placeholders** in copilot-instructions.md with actual project details
2. **Create your first Epic** using type:epic label to start planning
3. **Break down Epic into Stories** using type:story and state:ready labels
4. **Assign AI agents** to implement Stories following the framework workflow
5. **Review framework documentation** at https://github.com/nsin08/space_framework

---

## 🆘 Troubleshooting

**Labels already exist?**
- Skip creation or delete existing labels first: `gh label delete "label-name"`

**Branch protection not working?**
- Ensure you have admin permissions on the repository
- Check that CODEOWNERS file is in correct location (`.github/CODEOWNERS`)
- Verify CODEOWNERS syntax with GitHub's validator

**CODEOWNERS not recognized?**
- Must be in `.github/CODEOWNERS` or repository root
- Requires exact GitHub username format: `@username` or `@org/team`
- Push the file to the default branch (usually `main`)

**Need help?**
- Framework issues: https://github.com/nsin08/space_framework/issues
- GitHub docs: https://docs.github.com

---

**Setup created by:** GitHub Copilot  
**Framework version:** space_framework v1.0  
**Setup date:** 2026-01-09
