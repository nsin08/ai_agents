# AI Agent VSCode Extension

Powerful multi-agent orchestration directly in your IDE. Interact with AI agents, coordinate complex tasks, track execution metrics, and manage conversation history—all without leaving VSCode.

**Version:** 0.1.0 | **Status:** 5/5 phases complete | **Tests:** 189 passing | **Coverage:** 85%+

---

## 🚀 Quick Start - Choose Your Path

### ✨ I Want to **Use the Extension**
Get started in 5 minutes. Install, configure, and start chatting with agents.
- **Time:** ~5 minutes
- **Path:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → [VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md) → Chat Panel

### 🛠️ I Want to **Develop/Contribute**
Set up your development environment and understand the codebase.
- **Time:** ~30 minutes (setup) + development time
- **Path:** [DEVELOPMENT.md](DEVELOPMENT.md) → [BUILD.md](BUILD.md) → [CONTRIBUTING.md](CONTRIBUTING.md)

### 📦 I Want to **Package for Distribution**
Build VSIX, deploy, or publish to VSCode marketplace.
- **Time:** ~10 minutes
- **Path:** [BUILD.md](BUILD.md) → Package/Deploy section

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

## 🌍 Resources

### For Users
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Commands, features, FAQ (5 min read)
- [VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md) - Installation methods (VSIX, marketplace, dev)
- [RELEASE_v0.1.0.md](RELEASE_v0.1.0.md) - Release notes and changelog

### For Developers
- [DEVELOPMENT.md](DEVELOPMENT.md) - Setup, architecture, debugging, common tasks
- [BUILD.md](BUILD.md) - Building, testing, VSIX creation, deployment
- [CONTRIBUTING.md](CONTRIBUTING.md) - Code standards, PR process, issue workflow
- [TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md) - Test strategies, running tests, coverage

### Archived Docs
See [.context/ARCHIVE/](vscode-extension/v1/.context/ARCHIVE) for deprecated guides.

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

See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for complete command list.

---

## 🏗️ Architecture Overview

```
Extension Layer (TypeScript/VSCode API)
  ├── ChatPanel (Side panel UI)
  ├── ConfigPanel (Settings management)
  ├── StatisticsPanel (Metrics dashboard)
  ├── TraceViewerPanel (State transitions)
  ├── CodeSuggestionPanel (Code intelligence)
  ├── MultiAgentDashboard (Orchestration)
  ├── ReasoningPanel (Agent reasoning)
  └── HistoryBrowserPanel (Conversation storage)

Service Layer (Business logic)
  ├── AgentService (Chat communication)
  ├── ConfigService (Settings)
  ├── MetricsService (Token/cost tracking)
  ├── TraceService (State capture)
  ├── ExportService (CSV/JSON/Markdown/HTML)
  ├── HistoryService (Workspace persistence)
  ├── MultiAgentCoordinator (Orchestration)
  ├── CodeContextService (Security)
  └── CodeInsertionService (Code parsing)

Provider Layer (LLM abstraction)
  ├── Mock Provider (Testing)
  ├── Ollama (Local)
  └── Cloud Providers (OpenAI, Anthropic, etc.)
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed architecture.

---

## 🔒 Security

- ✅ **15 Sensitive Data Patterns** - Detects API keys, tokens, passwords, JWTs
- ✅ **11 Blocked File Types** - Prevents .env, .pem, .key from being sent
- ✅ **Local-Only Storage** - No cloud telemetry, no external calls
- ✅ **Size Limits** - 10K lines / 500KB per operation
- ✅ **User Warnings** - Alerts before sending potentially sensitive code

See [DEVELOPMENT.md](DEVELOPMENT.md#security-features) for details.

---

## 🧪 Testing

- **189 tests** across 14 suites
- **100% pass rate**
- **85%+ code coverage**
- Unit + integration tests
- Mock provider for deterministic testing

```bash
npm test                    # Run all tests
npm test -- --watch        # Watch mode
npm run lint                # Code quality
```

See [TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md) for full testing guide.

---

## 📞 Need Help?

### Getting Started Issues
- Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) FAQ section
- Review [VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md) troubleshooting

### Development Questions
- See [DEVELOPMENT.md](DEVELOPMENT.md) for setup and common issues
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for code standards

### Build/Package Issues
- See [BUILD.md](BUILD.md) troubleshooting section
- Review test failures in [TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md)

### Report an Issue
Create an issue on GitHub with:
- Extension version
- VSCode version
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs from Extension Host console

---

## 📖 Full Reference

### User Documentation
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - All commands, settings, examples
- [VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md) - Installation methods
- [RELEASE_v0.1.0.md](RELEASE_v0.1.0.md) - What's new in this release

### Developer Documentation
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development setup, architecture, debugging
- [BUILD.md](BUILD.md) - Building, packaging, deployment
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines
- [TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md) - Testing guide

### External References
- [VSCode Extension API](https://code.visualstudio.com/api)
- [VSCode Webview API](https://code.visualstudio.com/api/extension-guides/webview)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Jest Testing Framework](https://jestjs.io/)

---

## 📊 Project Status

**Current Version:** 0.1.0  
**Release Date:** January 2025  
**Next Milestone:** v0.2.0 (Marketplace publication)

- ✅ All 5 phases implemented
- ✅ 189/189 tests passing
- ✅ 0 TypeScript errors
- ✅ 85%+ code coverage
- ✅ Security audit complete
- ✅ VSIX package ready
- ✅ Documentation complete

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code standards and style guide
- Testing requirements
- PR process
- Issue workflow
- Development setup

---

## 📜 License

[License information - add as needed]

---

## 📞 Support & Feedback

- **Issues:** Report bugs or request features via GitHub Issues
- **Discussions:** Ask questions in GitHub Discussions
- **Email:** [contact email - add as needed]

---

**Last Updated:** January 2025 | **Maintainer:** [Your Name]
