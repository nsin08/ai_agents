# AI Agent VSCode Extension

Powerful multi-agent orchestration directly in your IDE. Interact with AI agents, coordinate complex tasks, track execution metrics, and manage conversation history—all without leaving VSCode.

**Version:** 0.1.0 | **Release Date:** January 29, 2026 | **Status:** Production Ready ✅

---

## 📦 Download

**VSIX File:** [`ai-agent-extension.vsix`](ai-agent-extension.vsix) (1.11 MB)

**Quick Install:**
```bash
# Option 1: Drag & drop VSIX file onto VSCode
# Option 2: Extensions panel → ... → Install from VSIX
# Option 3: Command line
code --install-extension ai-agent-extension.vsix
```

**Full Installation Guide:** [VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md)

---

## 📖 Documentation for All Users

### 👤 For Users - Get Started in 5 Minutes
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - All commands, settings, FAQs (the only guide you need as a user)
- **[VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md)** - How to install the VSIX file
- **[RELEASE_v0.1.0.md](RELEASE_v0.1.0.md)** - What's new in this version

### 👨‍💻 For Developers - Setup in 30 Minutes
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - How to set up your development environment and understand the codebase
- **[BUILD.md](BUILD.md)** - How to build, test, and create VSIX packages for distribution
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Code standards, testing requirements, PR process if you want to contribute

### 🧪 For QA/Testing
- **[TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md)** - Full testing guide with strategies and execution
- **[SANITY_TESTS.md](SANITY_TESTS.md)** - Quick sanity checks to verify the extension works

---

## 🚀 Quick Start

### Option 1: Just Use It (5 minutes)
1. Download [`ai-agent-extension.vsix`](ai-agent-extension.vsix)
2. Drag & drop it onto VSCode or install via Extensions panel
3. Press `Ctrl+Shift+P` → "Agent: Start Conversation"
4. Start chatting with the agent!

### Option 2: Develop/Modify (30 minutes)
1. Read [DEVELOPMENT.md](DEVELOPMENT.md) - Set up your environment
2. Press `F5` to launch Extension Development Host
3. Make changes and test
4. Build VSIX with instructions in [BUILD.md](BUILD.md)

---

## ✨ What This Extension Does

**5 Complete Phases - All Production Ready**

| Phase | Feature | Status |
|-------|---------|--------|
| **Phase 1** | MVP Chat, Configuration, Session Management | ✅ Complete |
| **Phase 2** | Observability: Metrics, Traces, Export | ✅ Complete |
| **Phase 3** | Code Intelligence: Context, Security, Suggestions | ✅ Complete |
| **Phase 4** | Multi-Agent Coordination with Dashboard | ✅ Complete |
| **Phase 5** | Conversation History & Export (Markdown/HTML) | ✅ Complete |

**Key Capabilities:**
- 💬 **Chat with AI Agents** - Single or multi-agent conversations
- 🔍 **Code Intelligence** - Send code selections with security filtering
- 📊 **Real-Time Metrics** - Token usage, response times, cost tracking
- 🕵️ **Trace Viewer** - Watch agent state transitions (Observe → Plan → Act → Verify)
- 🤖 **Multi-Agent Orchestration** - Coordinate planner, executor, verifier agents
- 📝 **Conversation History** - Search, replay, export past conversations
- 🔐 **Security Built-In** - Detects 15 sensitive data patterns, blocks 11 file types
- 🌐 **Multi-Provider** - Mock, Ollama (local), OpenAI, Anthropic, Google, Azure

---

## ⚡ Most Used Commands

| Command | Shortcut | What It Does |
|---------|----------|--------------|
| Agent: Start Conversation | `Ctrl+Shift+P` | Open chat panel |
| Agent: Settings | `Ctrl+Shift+P` | Configure provider/model |
| Agent: Send Selection to Agent | Right-click code | Send selected code to agent |
| Agent: Show Statistics | `Ctrl+Shift+P` | View token usage & costs |
| Agent: Show Trace Viewer | `Ctrl+Shift+P` | Watch agent thinking process |
| Agent: Start Multi-Agent Task | `Ctrl+Shift+P` | Coordinate multiple agents |
| Agent: Show History | `Ctrl+Shift+P` | Browse past conversations |

**All commands:** See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## ⚙️ Configuration (Single Agent Mode)

The extension supports single-agent chat (default) and multi-agent orchestration.

**Configure via Settings Panel:**
1. Press `Ctrl+Shift+P` → "Agent: Settings"
2. Select your provider and model
3. Start chatting!

**Supported Providers:**
- **Mock** - No setup needed, instant responses (for testing)
- **Ollama** - Local LLM (requires Ollama installation)
- **OpenAI** - GPT models (requires API key)
- **Anthropic** - Claude models (requires API key)
- **Google** - Gemini models (requires API key)
- **Azure OpenAI** - Azure-hosted models (requires endpoint + key)

**For multi-agent setup:** See [DEVELOPMENT.md](DEVELOPMENT.md#multi-agent-configuration)

---

## 🏗️ Architecture (High Level)

```
VSCode Extension (TypeScript)
├── 8 Panels (Chat, Config, Statistics, Trace, Code, Multi-Agent, Reasoning, History)
├── 9 Services (Agent, Config, Metrics, Trace, Export, History, Coordinator, Context, Insertion)
└── 3 Provider Types (Mock, Ollama Local, Cloud APIs)
```

**Full architecture details:** [DEVELOPMENT.md](DEVELOPMENT.md#architecture)

---

## 🔒 Security Features

- ✅ **15 Sensitive Data Patterns** - API keys, tokens, passwords, JWTs, credit cards
- ✅ **11 Blocked File Types** - `.env`, `.pem`, `.key`, `.p12`, `.pfx`, etc.
- ✅ **Local-Only Storage** - No external telemetry, all data stays on your machine
- ✅ **Size Limits** - 10K lines / 500KB per operation
- ✅ **User Warnings** - Alerts before sending potentially sensitive code

**Details:** [DEVELOPMENT.md - Security](DEVELOPMENT.md#-security-features)

---

## 🧪 Testing & Quality

- **189 tests** across 14 suites (100% passing)
- **85%+ code coverage**
- **0 TypeScript compilation errors**
- **0 ESLint violations**

**Run tests yourself:**
```bash
npm test                    # All tests
npm test -- --watch        # Watch mode
npm run lint                # Code quality check
```

**Testing guides:**
- **[TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md)** - Full testing guide
- **[SANITY_TESTS.md](SANITY_TESTS.md)** - Quick sanity checks

---

## 📊 Release Status

**Current Version:** 0.1.0  
**Release Date:** January 29, 2026  
**VSIX File:** [`ai-agent-extension.vsix`](ai-agent-extension.vsix) (1.11 MB)

**What's Complete:**
- ✅ All 5 phases implemented and tested
- ✅ 189/189 tests passing
- ✅ VSIX package created and ready to install
- ✅ Documentation complete
- ✅ Security audit passed
- ✅ Production ready

**What's Next:** v0.2.0 will include marketplace publication

**Release notes:** [RELEASE_v0.1.0.md](RELEASE_v0.1.0.md)

---

## 📞 Need Help?

### Installation Issues
→ See [VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md) troubleshooting section

### Using the Extension
→ See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Has FAQ, examples, and all commands

### Development Setup
→ See [DEVELOPMENT.md](DEVELOPMENT.md) - Complete setup guide

### Building VSIX
→ See [BUILD.md](BUILD.md) - Build and packaging instructions

### Running Tests
→ See [TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md) and [SANITY_TESTS.md](SANITY_TESTS.md)

### Contributing Code
→ See [CONTRIBUTING.md](CONTRIBUTING.md) - Code standards and PR process

---

## 🤝 Want to Contribute?

1. Read [DEVELOPMENT.md](DEVELOPMENT.md) - Set up your dev environment
2. Read [CONTRIBUTING.md](CONTRIBUTING.md) - Understand code standards
3. Make your changes and run tests: `npm test`
4. Submit a PR with clear description

---

## 📚 Complete Documentation Index

| File | Purpose | Who Should Read |
|------|---------|-----------------|
| **README.md** | Overview and quick start | Everyone (you are here) |
| **ai-agent-extension.vsix** | The extension package to install | Users who want to install |
| **QUICK_REFERENCE.md** | All commands, settings, FAQs | Users |
| **VSIX_INSTALLATION_GUIDE.md** | How to install the VSIX file | Users |
| **RELEASE_v0.1.0.md** | Release notes and changelog | Everyone |
| **DEVELOPMENT.md** | Dev setup, architecture, debugging | Developers |
| **BUILD.md** | Building, testing, creating VSIX | Developers/Release Engineers |
| **CONTRIBUTING.md** | Code standards, PR process | Contributors |
| **TESTING_COMPREHENSIVE.md** | Full testing guide | Developers/QA |
| **SANITY_TESTS.md** | Quick sanity checks | Developers/QA |

---

## 📜 License

[License information - add as needed]

---

## 📞 Support & Feedback

- **Report Bugs:** [GitHub Issues](https://github.com/nsin08/ai_agents/issues)
- **Ask Questions:** [GitHub Discussions](https://github.com/nsin08/ai_agents/discussions)

---

**🎉 Ready to start? Download [`ai-agent-extension.vsix`](ai-agent-extension.vsix) and install it in VSCode!**

**Need help?** Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (for users) or [DEVELOPMENT.md](DEVELOPMENT.md) (for developers).
