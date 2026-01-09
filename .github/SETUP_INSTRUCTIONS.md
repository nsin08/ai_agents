# space_framework Setup - Manual Configuration Steps

**Date:** 2026-01-09  
**Project:** AI Agents (ai_agents)

This document contains the manual configuration steps required to complete your space_framework SDLC governance setup.

---

## ✅ Completed

The following files have been created automatically:

- [x] `.github/copilot-instructions.md` - Framework integration and project context
- [x] `.github/CODEOWNERS` - Merge authority definition

---

## 📋 TODO: Manual GitHub Configuration

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
