# AI Agent VSCode Extension

Powerful multi-agent orchestration directly in your IDE. Interact with AI agents, coordinate complex tasks, track execution metrics, and manage conversation history—all without leaving VSCode.

**Version:** 0.1.0 | **Status:** 5/5 phases complete | **Tests:** 189 passing | **Coverage:** 85%+

---

## 📖 Documentation

All documentation is organized for easy navigation. **Choose what you need:**

### For Users - Get Started in 5 Minutes
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - All commands, settings, FAQs
- **[VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md)** - How to install
- **[RELEASE_v0.1.0.md](RELEASE_v0.1.0.md)** - What's new in this version

### For Developers - Setup in 30 Minutes
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Environment setup, architecture, debugging
- **[BUILD.md](BUILD.md)** - Building, testing, creating VSIX packages
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Code standards, PR process, contribution guidelines
- **[TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md)** - Testing strategies and execution

### Archived Documentation
- **[.context/ARCHIVE/](vscode-extension/v1/.context/ARCHIVE)** - Deprecated guides (for reference only)

---

## 🚀 Quick Start - Choose Your Path

### ✨ I Want to **Use the Extension** (5 min)
1. Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Learn all commands
2. Follow [VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md) - Install the extension
3. Open chat panel and start using it!

### 🛠️ I Want to **Develop/Contribute** (30 min)
1. Read [DEVELOPMENT.md](DEVELOPMENT.md) - Set up your environment
2. Review [BUILD.md](BUILD.md) - Understand the build process
3. Check [CONTRIBUTING.md](CONTRIBUTING.md) - Learn code standards
4. Start coding and submit PRs!

### 📦 I Want to **Package for Distribution** (10 min)
1. Follow [BUILD.md](BUILD.md) - VSIX Creation section
2. Prepare for marketplace or direct distribution
3. Deploy your package

---

## 📋 What's Included

**5 Complete Phases (189 tests, 100% passing)**

| Phase | Feature | Status |
|-------|---------|--------|
| **1** | MVP Chat, Configuration, Session Management | ✅ Complete |
| **2** | Observability: Metrics, Traces, Export | ✅ Complete |
| **3** | Code Intelligence: Context, Security, Suggestions | ✅ Complete |
| **4** | Multi-Agent Coordination with Dashboard | ✅ Complete |
| **5** | Conversation History & Export (Markdown/HTML) | ✅ Complete |

**Key Features:**
- 🎯 **Single & Multi-Agent Modes** - Chat or orchestrate multi-agent workflows
- 📊 **Real-Time Metrics** - Token usage, response times, cost tracking
- 🔍 **Trace Viewer** - Watch agent state transitions (Observe → Plan → Act → Verify)
- 💻 **Code Intelligence** - Send code with security filtering (15 pattern detection)
- 📝 **Conversation History** - Searchable, persistent per workspace
- 🔐 **Security** - Local-only storage, no telemetry, sensitive data blocking
- 🌐 **Multi-Provider** - Mock, Ollama, OpenAI, Anthropic, Google, Azure

---

## ⚡ Quick Commands

| Command | Shortcut | Purpose |
|---------|----------|---------|
| Agent: Start Conversation | `Ctrl+Shift+P` | Open chat panel |
| Agent: Settings | `Ctrl+Shift+P` | Configure provider/model |
| Agent: Send Selection to Agent | Right-click | Send code with context |
| Agent: Show Statistics | `Ctrl+Shift+P` | View metrics dashboard |
| Agent: Show Trace Viewer | `Ctrl+Shift+P` | Watch agent state transitions |
| Agent: Start Multi-Agent Task | `Ctrl+Shift+P` | Coordinate agents |
| Agent: Show History | `Ctrl+Shift+P` | Browse past conversations |

**Full command list:** See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 🏗️ Architecture Overview

The extension consists of three layers:

**Extension Layer (TypeScript/VSCode API)**
- ChatPanel, ConfigPanel, StatisticsPanel, TraceViewerPanel
- CodeSuggestionPanel, MultiAgentDashboard, ReasoningPanel, HistoryBrowserPanel

**Service Layer (Business Logic)**
- AgentService, ConfigService, MetricsService, TraceService
- ExportService, HistoryService, MultiAgentCoordinator
- CodeContextService, CodeInsertionService

**Provider Layer (LLM Abstraction)**
- Mock Provider (Testing)
- Ollama (Local)
- Cloud Providers (OpenAI, Anthropic, Google, Azure)

**Details:** See [DEVELOPMENT.md](DEVELOPMENT.md#architecture)

---

## 🔒 Security

- ✅ **15 Sensitive Data Patterns** - Detects API keys, tokens, passwords, JWTs
- ✅ **11 Blocked File Types** - Prevents .env, .pem, .key from being sent
- ✅ **Local-Only Storage** - No cloud telemetry, no external calls
- ✅ **Size Limits** - 10K lines / 500KB per operation
- ✅ **User Warnings** - Alerts before sending potentially sensitive code

**Details:** See [DEVELOPMENT.md - Security Features](DEVELOPMENT.md#-security-features)

---

## 🧪 Testing

- **189 tests** across 14 suites
- **100% pass rate**
- **85%+ code coverage**
- Unit + integration tests
- Mock provider for deterministic testing

**Run Tests:**
```bash
npm test                    # Run all tests
npm test -- --watch        # Watch mode
npm run lint                # Code quality
```

**Details:** See [TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md)

---

## 📊 Project Status

**Current Version:** 0.1.0  
**Release Date:** January 29, 2026  
**Next Milestone:** v0.2.0 (Marketplace publication)

**Status:**
- ✅ All 5 phases implemented
- ✅ 189/189 tests passing
- ✅ 0 TypeScript errors
- ✅ 85%+ code coverage
- ✅ Security audit complete
- ✅ VSIX package ready
- ✅ Documentation complete

---

## 📞 Need Help?

### Getting Started
- **Installation issues?** → [VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md) troubleshooting
- **How do I use this?** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md) FAQ section

### Development
- **Setting up dev environment?** → [DEVELOPMENT.md](DEVELOPMENT.md#environment-setup)
- **Code standards?** → [CONTRIBUTING.md](CONTRIBUTING.md#-code-standards)
- **Running tests?** → [TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md)
- **Building VSIX?** → [BUILD.md](BUILD.md#-vsix-creation)

### Report Issues
Create a GitHub issue with:
- Extension version
- VSCode version
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs from Extension Host console

---

## 🤝 Contributing

We welcome contributions! Start here:

1. **Read the guides:**
   - [DEVELOPMENT.md](DEVELOPMENT.md) - How to set up your environment
   - [CONTRIBUTING.md](CONTRIBUTING.md) - Code standards and PR process
   - [TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md) - Testing requirements

2. **Make your changes** following code standards

3. **Run tests:** `npm test`

4. **Submit a PR** with clear description linking to related issues

**Details:** See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📚 All Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| **README.md** | You are here - Overview and navigation | Everyone |
| **QUICK_REFERENCE.md** | Commands, settings, examples | Users |
| **DEVELOPMENT.md** | Setup, architecture, debugging | Developers |
| **BUILD.md** | Building, testing, packaging, deployment | Developers/Release Engineers |
| **CONTRIBUTING.md** | Code standards, PR process | Contributors |
| **VSIX_INSTALLATION_GUIDE.md** | Installation methods and troubleshooting | Users |
| **RELEASE_v0.1.0.md** | Release notes and changelog | Everyone |
| **TESTING_COMPREHENSIVE.md** | Testing strategies and execution | Developers/QA |
| **.context/ARCHIVE/** | Deprecated documentation | Reference only |

---

## 📜 License

[License information - add as needed]

---

## 📞 Support & Feedback

- **Report Bugs:** [GitHub Issues](https://github.com/nsin08/ai_agents/issues)
- **Ask Questions:** [GitHub Discussions](https://github.com/nsin08/ai_agents/discussions)
- **Email:** [contact email - add as needed]

---

**Last Updated:** January 29, 2026  
**Maintainer:** [Your Name]

**Start reading:** Choose a guide above based on what you want to do!
