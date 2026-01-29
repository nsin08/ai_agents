# Build & Package Guide

**For developers who want to build, package, and distribute the AI Agent VSCode Extension.**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Build Process](#build-process)
3. [Create VSIX Package](#create-vsix-package)
4. [Verify Package](#verify-package)
5. [Distribution Options](#distribution-options)
6. [Publishing to Marketplace](#publishing-to-marketplace)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

```bash
# Node.js 14+ (18+ recommended)
node --version

# npm 6+
npm --version

# vsce (VSCode Extension Compiler)
npm install --save-dev @vscode/vsce
# or globally
npm install -g @vscode/vsce
```

### Verify Installation

```bash
# Check all prerequisites
node --version && npm --version && npx vsce --version
```

---

## Build Process

### 1. Compile TypeScript

```bash
# Navigate to extension folder
cd vscode-extension/v1

# Install dependencies
npm install

# Compile TypeScript to JavaScript
npm run compile
```

**Output:**
```
> ai-agent-extension@0.1.0 compile
> tsc -p ./

# No errors = success ✅
```

### 2. Run Tests

```bash
# Run full test suite
npm test

# Expected output:
# Test Suites: 14 passed, 14 total
# Tests:       189 passed, 189 total
# Coverage:    85%+
```

### 3. Lint Code

```bash
# Check for code quality issues
npm run lint

# Auto-fix issues
npm run lint -- --fix
```

### 4. Type Check

```bash
# Verify no type errors
npm run compile -- --noEmit
```

---

## Create VSIX Package

### Method 1: Using npm Scripts (Recommended)

**If script exists in package.json:**
```bash
npm run package
```

### Method 2: Using vsce CLI

```bash
# Create VSIX file
npx vsce package --out ai-agent-extension.vsix

# Output:
# DONE  Packaged: ai-agent-extension.vsix (555 files, 1.11MB)
```

### What Happens During Packaging

1. ✅ Runs `npm run vscode:prepublish` (compiles TypeScript)
2. ✅ Validates `package.json` manifest
3. ✅ Bundles source code and dependencies
4. ✅ Excludes test files and build artifacts
5. ✅ Creates `.vsix` archive file
6. ✅ Generates checksums

### Output

**File created:** `ai-agent-extension.vsix` (typically 1-2 MB)

**Contains:**
- Compiled JavaScript
- All dependencies (node_modules)
- HTML views and assets
- package.json manifest
- 555 total files

---

## Verify Package

### Check File Exists

```bash
# Windows
dir ai-agent-extension.vsix

# macOS/Linux
ls -lh ai-agent-extension.vsix

# Expected: ~1.1 MB file
```

### Test Installation

```bash
# Install VSIX locally
code --install-extension ./ai-agent-extension.vsix

# Verify in VSCode
# Extensions (Ctrl+Shift+X) → Find "AI Agent Interaction"
# Status should show: "Installed"
```

### Verify Functionality

1. **Open VSCode Extensions:** `Ctrl+Shift+X`
2. **Find:** "AI Agent Interaction" 
3. **Status:** Should show "Installed"
4. **Test command:** `Ctrl+Shift+P` → `Agent: Start Conversation`
5. **Result:** Chat panel opens ✅

### Check Package Contents

```bash
# List files in VSIX (it's a zip archive)
unzip -l ai-agent-extension.vsix | head -20

# Extract for inspection
unzip ai-agent-extension.vsix -d vsix-contents
```

---

## Distribution Options

### Option 1: Direct Distribution (Current) ✅

**How:** Share VSIX file directly

**Steps:**
```bash
# Users receive: ai-agent-extension.vsix
# Users do:
code --install-extension ./ai-agent-extension.vsix
# OR drag into VSCode Extensions panel
```

**Pros:**
- Works immediately
- No marketplace dependency
- Offline installation
- Full control over versions

**Cons:**
- Manual distribution
- No auto-updates
- Users must manage upgrades

---

### Option 2: GitHub Release (Recommended for v0.1.0)

**How:** Host VSIX on GitHub Releases

**Steps:**

1. **Create GitHub Release**
   ```bash
   # Create tag
   git tag v0.1.0
   git push origin v0.1.0
   
   # OR create release manually:
   # GitHub → Releases → Draft new release
   ```

2. **Attach VSIX File**
   - Go to release page
   - Upload `ai-agent-extension.vsix`
   - Add release notes
   - Publish

3. **Users Install From Release**
   ```bash
   # Users download from: 
   # https://github.com/nsin08/ai_agents/releases/v0.1.0/ai-agent-extension.vsix
   
   # Then install:
   code --install-extension ./ai-agent-extension.vsix
   ```

**Pros:**
- Public visibility
- Version tracking
- Release notes
- Easy to share

**Cons:**
- No auto-updates
- Manual upload each release

---

### Option 3: VSCode Marketplace (v0.2.0+)

**How:** Publish official extension to marketplace

**Prerequisites:**
1. VSCode Marketplace account (free)
2. Create publisher (free)
3. Azure DevOps account (free)

**Steps:**

1. **Create Publisher**
   ```bash
   vsce create-publisher <publisher-name>
   ```

2. **Login to Publisher**
   ```bash
   vsce login <publisher-name>
   ```

3. **Publish Extension**
   ```bash
   vsce publish --publisher <publisher-name>
   ```

4. **Users Install from VSCode**
   - Extensions → Search "AI Agent Interaction"
   - Click Install
   - Automatic updates available

**Pros:**
- Official distribution
- Searchable in VSCode
- Auto-updates
- Analytics
- Professional

**Cons:**
- Marketplace review process
- Publisher account required
- Takes time to set up

---

### Option 4: Internal Distribution

**How:** Host VSIX on internal server

**Steps:**
```bash
# Copy VSIX to server
scp ai-agent-extension.vsix server:/path/to/extensions/

# Users install via URL
code --install-extension https://internal-server.com/extensions/ai-agent-extension.vsix

# OR via installer script
./install-extension.sh
```

**Pros:**
- Complete control
- Private distribution
- Can customize
- Corporate requirements

**Cons:**
- Requires infrastructure
- Manual deployment
- Maintenance burden

---

## Publishing to Marketplace

### Step 1: Create Publisher Account

1. Visit: https://marketplace.visualstudio.com
2. Click "Create a Publisher"
3. Login with Microsoft account (or create new)
4. Fill in publisher name and details
5. Complete verification

### Step 2: Get Personal Access Token

1. Go to: https://dev.azure.com
2. User settings → Personal access tokens
3. Create token:
   - Scope: All accessible organizations
   - Valid for: 90 days (or custom)
4. Copy token

### Step 3: Prepare Extension

```bash
# Update version in package.json
# Change: "version": "0.1.0" → "0.2.0"

# Update README for marketplace
# Add badges, shields, etc.

# Verify all tests pass
npm test

# Build
npm run compile
```

### Step 4: Publish

```bash
# Login with token
vsce login <publisher-name>
# Paste token when prompted

# Publish
vsce publish

# Result:
# https://marketplace.visualstudio.com/items?itemName=<publisher-name>.ai-agent-extension
```

### Step 5: Verify

1. Visit marketplace URL
2. Download statistics available
3. Users can search and install
4. Auto-updates work

---

## Update Process

### Publishing an Update

```bash
# 1. Update version in package.json
# "version": "0.1.0" → "0.1.1"

# 2. Update CHANGELOG.md
# Document what changed

# 3. Commit and tag
git add .
git commit -m "release: v0.1.1"
git tag v0.1.1
git push origin v0.1.1

# 4. Build
npm run compile
npm run package

# 5. Publish to marketplace (if using marketplace)
vsce publish
# OR GitHub Release
# Upload new VSIX to release

# 6. Users get auto-updates (if on marketplace)
```

---

## Troubleshooting

### Build Fails

**Problem:** `npm run compile` fails

**Solutions:**
```bash
# 1. Check Node.js version
node --version  # Should be 14+

# 2. Clean install
rm -rf node_modules package-lock.json
npm install
npm run compile

# 3. Check for TypeScript errors
npx tsc --noEmit

# 4. Check for missing dependencies
npm ls
```

### VSIX Creation Fails

**Problem:** `vsce package` fails

**Solutions:**
```bash
# 1. Check vsce is installed
npm ls @vscode/vsce

# 2. Ensure package.json is valid
node -e "console.log(JSON.parse(require('fs').readFileSync('package.json','utf8')))"

# 3. Check repository field exists
# Should have in package.json:
# "repository": {
#   "type": "git",
#   "url": "https://github.com/nsin08/ai_agents.git"
# }

# 4. Add LICENSE file if missing
touch LICENSE
echo "MIT License" > LICENSE

# 5. Try packaging again
vsce package --out ai-agent-extension.vsix
```

### Installation Fails

**Problem:** Extension doesn't install or activate

**Solutions:**
```bash
# 1. Check compatibility
# VSCode must be 1.85.0+
Help → About → Check version

# 2. Uninstall old version
code --uninstall-extension ai-agent-extension

# 3. Install VSIX
code --install-extension ./ai-agent-extension.vsix

# 4. Reload VSCode
Ctrl+Shift+P → Developer: Reload Window

# 5. Check Output panel for errors
Help → Toggle Developer Tools → Output tab
```

### VSIX Too Large

**Problem:** VSIX file is very large (>5 MB)

**Solutions:**
```bash
# 1. Check what's included
unzip -l ai-agent-extension.vsix | sort -k4 -n | tail -20

# 2. Add .vscodeignore to exclude files
echo "node_modules" >> .vscodeignore
echo "tests" >> .vscodeignore
echo "**/*.test.js" >> .vscodeignore

# 3. Rebuild
npm run compile && vsce package
```

---

## Checklist: Release Ready

Before distributing, verify:

- [ ] All tests passing: `npm test` → 189/189 ✅
- [ ] No TypeScript errors: `npm run compile` ✅
- [ ] No ESLint violations: `npm run lint` ✅
- [ ] Version updated in package.json
- [ ] CHANGELOG.md updated
- [ ] README.md updated
- [ ] VSIX file created: `ai-agent-extension.vsix` ✅
- [ ] VSIX installation tested locally
- [ ] All commands work in test
- [ ] Documentation links work
- [ ] Repository field in package.json correct

---

## Next Steps

- 🚀 **User installation:** See [VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md)
- 👨‍💻 **Development:** See [DEVELOPMENT.md](DEVELOPMENT.md)
- 🤝 **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md)
- 📖 **Overview:** See [README.md](README.md)

---

## Resources

### VSCode Extension Publishing
- [Publishing Extensions](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
- [vsce Documentation](https://github.com/Microsoft/vscode-vsce)
- [Marketplace Policies](https://code.visualstudio.com/api/references/extension-manifest)

### Our Documentation
- [README.md](README.md) - Project overview
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

---

## 📚 Related Guides

- **[README.md](README.md)** ← Main documentation hub
- **[DEVELOPMENT.md](DEVELOPMENT.md)** ← Development setup, architecture, debugging
- **[CONTRIBUTING.md](CONTRIBUTING.md)** ← Code standards, PR process, contribution workflow
- **[TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md)** ← Testing strategies and coverage

---

**Back to:** [README.md](README.md)

