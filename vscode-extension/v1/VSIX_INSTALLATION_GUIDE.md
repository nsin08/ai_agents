# AI Agent VSCode Extension - VSIX Installation Guide

**Version:** 0.1.0  
**Release Date:** January 29, 2026  
**File:** `ai-agent-extension.vsix` (1.11 MB)

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation Methods](#installation-methods)
4. [Post-Installation Setup](#post-installation-setup)
5. [Troubleshooting](#troubleshooting)
6. [Uninstallation](#uninstallation)
7. [What's Included](#whats-included)

---

## Overview

The **AI Agent Interaction** extension enables seamless interaction with AI agents directly from Visual Studio Code. This comprehensive extension includes 4 development phases with features for chat, observability, code intelligence, and multi-agent coordination.

### Key Features

- 🤖 **Agent Chat:** Interactive conversations with AI agents in VSCode sidebar
- 📊 **Statistics & Observability:** Real-time token usage, cost tracking, and performance metrics
- 🔐 **Code Intelligence:** Context-aware code suggestions with security filtering
- 👥 **Multi-Agent Coordination:** Orchestrate multiple specialized agents (Planner, Executor, Verifier)
- 💾 **Conversation History:** Searchable history with export to Markdown/HTML

---

## System Requirements

### Minimum Requirements

- **VSCode:** Version 1.85.0 or higher
- **OS:** Windows, macOS, or Linux
- **Node.js:** 14.0+ (only if building from source)
- **RAM:** 256 MB minimum
- **Disk Space:** ~50 MB (extension + dependencies)

### Recommended Requirements

- **VSCode:** Latest version (1.90+)
- **RAM:** 1 GB or more
- **Disk Space:** 200 MB (including local LLM models if using Ollama)

### Optional Dependencies

- **Ollama:** For local LLM support (download from https://ollama.ai)
- **Docker:** For containerized LLM deployment

---

## Installation Methods

### Method 1: VSCode Extensions Panel (Easiest)

1. **Open VSCode Extensions:**
   - Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (macOS)

2. **Open VSIX File:**
   - Click the three-dot menu (⋯) in the Extensions panel
   - Select `Install from VSIX...`
   - Navigate to `ai-agent-extension.vsix`
   - Click Open

3. **Wait for Installation:**
   - VSCode will install the extension
   - A notification will appear when complete
   - **No reload required** — extension activates on startup

4. **Verify Installation:**
   - Look for "AI Agent Interaction" in your Extensions list
   - Status should show "Installed"

### Method 2: Command Line (Quick)

#### Windows (PowerShell)
```powershell
# Navigate to your VSCode extensions directory
$extensionsPath = "$env:USERPROFILE\.vscode\extensions"

# Copy the VSIX file
Copy-Item -Path ".\ai-agent-extension.vsix" -Destination "$extensionsPath\"

# Or use VSCode CLI directly
code --install-extension ./ai-agent-extension.vsix
```

#### macOS / Linux (Bash)
```bash
# Using VSCode CLI (simplest)
code --install-extension ./ai-agent-extension.vsix

# Or manually to extensions folder
mkdir -p ~/.vscode/extensions
cp ai-agent-extension.vsix ~/.vscode/extensions/
```

### Method 3: Drag & Drop (Fastest)

1. **Open VSCode Extensions panel** (`Ctrl+Shift+X`)
2. **Drag the `ai-agent-extension.vsix` file** into the Extensions panel
3. **Click Install** on the prompt
4. **Reload VSCode** when prompted

### Method 4: GitHub Release (When Published)

Once published to VSCode Marketplace:

```
1. Open VSCode Extensions
2. Search: "AI Agent Interaction"
3. Click Install
```

---

## Post-Installation Setup

### Step 1: Initialize Extension

1. **Reload VSCode** if not done automatically
   - Press `Ctrl+Shift+P` and run `Developer: Reload Window`

2. **Verify Activation:**
   - Open Command Palette: `Ctrl+Shift+P`
   - Type: "Agent: Start Conversation"
   - The command should autocomplete

### Step 2: Configure LLM Provider

1. **Open Settings Panel:**
   - Command Palette → `Agent: Settings`
   - Or use the sidebar settings icon

2. **Select Provider:**
   - **Mock (default):** For testing without LLM
   - **Ollama:** For local open-source models
   - **OpenAI:** For GPT-4, GPT-3.5
   - **Anthropic:** For Claude models
   - **Google:** For Gemini models

3. **For Ollama (Recommended for Local Development):**
   ```
   - Install: https://ollama.ai/download
   - Run: ollama serve
   - Configure extension:
     - Provider: Ollama
     - Base URL: http://localhost:11434
     - Model: mistral (or any available model)
   ```

4. **For Cloud Providers:**
   - Provide API key in Settings panel
   - Test connection before proceeding

### Step 3: Launch Chat Panel

1. **Open Chat:**
   - Command Palette → `Agent: Start Conversation`
   - Or use the chat icon in the sidebar

2. **Send First Message:**
   ```
   "Hello! Can you help me understand this code?"
   ```

3. **View Conversation:**
   - Messages appear in real-time
   - Provider/model info shown at top
   - Session time displayed

### Step 4: Explore Features

**Statistics Panel:**
- View token usage and costs
- Monitor response times
- Export metrics

**Code Intelligence:**
- Select code in editor
- Right-click → `Agent: Send Code to Agent`
- View suggestions in Code Suggestion panel

**Conversation History:**
- View all past conversations
- Search by keyword, date, or agent mode
- Export to Markdown or HTML

**Multi-Agent (Advanced):**
- Submit complex tasks
- Watch agents collaborate
- View reasoning chains

---

## Configuration

### Via Settings Panel

The Settings panel (`Agent: Settings`) provides:

| Setting | Default | Options |
|---------|---------|---------|
| **Agent Mode** | Single | Single, Multi |
| **Provider** | Mock | Ollama, OpenAI, Anthropic, Google, Azure |
| **Model** | llama2 | Varies by provider |
| **Base URL** | http://localhost:11434 | Custom URL for Ollama |
| **API Key** | (empty) | Your provider API key |
| **Max Turns** | 5 | 1-20 |
| **Timeout** | 30 seconds | Adjustable |

### Via VSCode Settings (settings.json)

```json
{
  "ai-agent.provider": "ollama",
  "ai-agent.model": "mistral",
  "ai-agent.baseUrl": "http://localhost:11434",
  "ai-agent.apiKey": "${env:OPENAI_API_KEY}",
  "ai-agent.maxTurns": 5,
  "ai-agent.timeout": 30
}
```

### Via Environment Variables

```bash
# Windows (PowerShell)
$env:LLM_PROVIDER = "ollama"
$env:LLM_MODEL = "mistral"
$env:OPENAI_API_KEY = "sk-..."

# Linux/macOS (Bash)
export LLM_PROVIDER=ollama
export LLM_MODEL=mistral
export OPENAI_API_KEY=sk-...
```

---

## Quick Start

### Scenario 1: Local Development (No API Keys)

1. **Install Ollama:** https://ollama.ai
2. **Start Ollama:** `ollama serve` (in terminal)
3. **In VSCode:**
   - Open `Agent: Settings`
   - Provider: Ollama
   - Model: mistral (or mistral:latest)
   - Click Save
4. **Start Chat:** `Ctrl+Shift+P` → `Agent: Start Conversation`
5. **Type:** "Hello!"

### Scenario 2: Cloud LLM (OpenAI)

1. **Get API Key:** https://platform.openai.com/api-keys
2. **In VSCode:**
   - Open `Agent: Settings`
   - Provider: OpenAI
   - Model: gpt-4 (or gpt-3.5-turbo)
   - Paste API key
   - Click Save
3. **Start Chat:** Begin conversation immediately

### Scenario 3: Multi-Agent Coordination

1. **Configure Settings:**
   - Agent Mode: Multi
   - Provider: Ollama (or cloud)
2. **Open Multi-Agent Dashboard:**
   - Command Palette → `Agent: Show Multi-Agent Dashboard`
3. **Submit Task:**
   ```
   "Analyze this code structure and suggest improvements.
   Break it into: planning phase, execution phase, verification."
   ```
4. **Watch Agents:**
   - Planner designs approach
   - Executor implements solution
   - Verifier checks quality

---

## Troubleshooting

### Extension Not Installing

**Problem:** "Installation failed"

**Solutions:**
- Check VSCode version: `Help` → `About`
- Update VSCode to 1.85.0+
- Restart VSCode and try again
- Check disk space (need ~50 MB)

### Commands Not Appearing

**Problem:** Commands don't autocomplete in Command Palette

**Solutions:**
```powershell
# Reload VSCode
Ctrl+Shift+P → Developer: Reload Window

# Clear VSCode cache
rm -r $env:USERPROFILE\.vscode\extensions
# Reinstall extension
```

### Provider Connection Fails

**Problem:** "Failed to connect to Ollama"

**Solutions:**
```bash
# Check Ollama is running
ollama serve

# Test connection
curl http://localhost:11434/api/tags

# If running on different machine:
# Update Base URL in Settings to: http://remote-ip:11434
```

**For OpenAI/Cloud providers:**
- Verify API key is correct (no spaces, full key)
- Check key has permissions for completions API
- Ensure API key isn't revoked or expired

### Extension Slow / Crashing

**Problem:** VSCode lags when using agent

**Solutions:**
- Check available RAM: `Task Manager` (Windows) or `Activity Monitor` (macOS)
- Reduce **Max Turns** to 3-5 in Settings
- Use smaller models (mistral instead of larger)
- Enable Debug mode to see performance metrics
- Close other heavy extensions

### Code Suggestions Not Working

**Problem:** "Code Suggestion Panel doesn't appear"

**Solutions:**
```
1. Right-click on code selection
2. Select: "Agent: Send Code to Agent"
3. Wait 5-10 seconds for response
4. Panel should appear automatically

If still not working:
- Reload Window: Ctrl+Shift+P → Reload
- Check Console for errors: Help → Toggle Developer Tools
```

### Settings Not Saving

**Problem:** Configuration resets on restart

**Solutions:**
```json
// Check settings.json permissions
// Windows: C:\Users\<user>\AppData\Roaming\Code\User\settings.json
// macOS: ~/Library/Application Support/Code/User/settings.json
// Linux: ~/.config/Code/User/settings.json

// Verify JSON syntax is valid (no trailing commas)
// Restart VSCode after making changes
```

---

## Features Overview

### Phase 1: MVP Chat
- ✅ Chat sidebar panel
- ✅ Provider/model configuration
- ✅ Session persistence
- ✅ Command palette integration

### Phase 2: Statistics & Observability
- ✅ Token usage tracking
- ✅ Cost calculation
- ✅ Response time metrics
- ✅ Trace viewer with state transitions
- ✅ CSV/JSON export

### Phase 3: Code Intelligence
- ✅ Code context extraction
- ✅ Sensitive data detection (15 patterns)
- ✅ Blocked file types (11 types)
- ✅ Code suggestions panel
- ✅ Apply/Preview/Copy functionality
- ✅ Security filtering

### Phase 4: Multi-Agent Coordination
- ✅ Multi-agent orchestrator
- ✅ Specialized agents (Planner, Executor, Verifier)
- ✅ Live coordination dashboard
- ✅ Agent reasoning panel
- ✅ Per-agent metrics

### Phase 5: Conversation History
- ✅ Searchable conversation history
- ✅ History browser with filters
- ✅ Markdown export
- ✅ HTML export with styling

---

## Uninstallation

### Method 1: VSCode Extensions Panel (Recommended)

1. Open Extensions: `Ctrl+Shift+X`
2. Find "AI Agent Interaction"
3. Click the gear icon ⚙️
4. Select "Uninstall"
5. Reload VSCode

### Method 2: Manual Cleanup

```powershell
# Windows
rm "$env:USERPROFILE\.vscode\extensions\ai-agent-extension-*"

# macOS/Linux
rm -rf ~/.vscode/extensions/ai-agent-extension-*
```

### Clean Uninstall (Removes Settings Too)

```powershell
# Windows - Remove settings
rm "$env:APPDATA\Code\User\settings.json"  # ⚠️ Removes ALL settings

# Better: Edit settings.json and remove only AI Agent settings:
# Remove these lines:
# "ai-agent.provider": "...",
# "ai-agent.model": "...",
# etc.
```

---

## Support & Feedback

### Getting Help

1. **Documentation:**
   - [README.md](README.md) - Feature overview
   - [TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md) - Testing guide
   - [SANITY_TESTS.md](SANITY_TESTS.md) - Quick verification

2. **GitHub Issues:**
   - Report bugs: https://github.com/nsin08/ai_agents/issues
   - Feature requests welcome!

3. **Community:**
   - VSCode Extension Discussions: https://github.com/nsin08/ai_agents/discussions

### Providing Feedback

When reporting issues, include:
```
- VSCode version: Help → About
- Extension version: See Extensions panel
- Provider: (Ollama, OpenAI, etc.)
- Error message: Help → Toggle Developer Tools → Console
- Steps to reproduce
```

---

## Advanced Usage

### Developing the Extension

To modify the extension locally:

```bash
# Clone repository
git clone https://github.com/nsin08/ai_agents.git
cd ai_agents/vscode-extension/v1

# Install dependencies
npm install

# Start debug mode
F5 (in VSCode)

# Build VSIX
npm run package

# New VSIX will be generated
```

### Custom Provider Integration

To add a custom LLM provider:

1. Create provider implementation in `src/providers/`
2. Add configuration in Settings panel
3. Test with chat/code intelligence
4. Submit PR with tests

### Multi-Agent Customization

To add custom agent roles:

1. Edit `src/models/AgentRole.ts`
2. Add role definition with capabilities
3. Implement agent in `src/services/agents/`
4. Register in coordinator

---

## Version History

### v0.1.0 (January 29, 2026) - Initial Release ✅

**Phases Included:**
- Phase 1: MVP Chat Panel (15 tests)
- Phase 2: Statistics & Observability (51 tests)
- Phase 3: Code Intelligence & Security (84 tests)
- Phase 4: Multi-Agent Coordination (39 tests)
- Phase 5: Conversation History & Export (new)

**Total:** 189 tests passing, 85%+ coverage

**Key Files:**
- 39 source files (TypeScript)
- 14 test suites
- 300+ lines of documentation
- 555 total files packaged

---

## License

This extension is part of the **AI Agents** project.  
See LICENSE file in the repository for details.

---

## Acknowledgments

Built with:
- VSCode Extension API
- TypeScript
- LangChain & LangGraph
- Pydantic
- Jest (testing)

Providers supported:
- Ollama (local, open-source)
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Azure OpenAI

---

## 📚 Related Resources

- **[README.md](README.md)** ← Main documentation hub (start here)
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** ← Commands, settings, FAQs
- **[RELEASE_v0.1.0.md](RELEASE_v0.1.0.md)** ← Release notes and changelog
- **[DEVELOPMENT.md](DEVELOPMENT.md)** ← For developers

---

**Last Updated:** January 29, 2026  
**Repository:** https://github.com/nsin08/ai_agents

**Back to:** [README.md](README.md)

