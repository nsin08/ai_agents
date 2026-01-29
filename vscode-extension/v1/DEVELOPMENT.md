# Development Guide

**For developers who want to build, extend, or contribute to the AI Agent VSCode Extension.**

---

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Project Structure](#project-structure)
3. [Getting Started](#getting-started)
4. [Available Commands](#available-commands)
5. [Debugging & Testing](#debugging--testing)
6. [Project Architecture](#project-architecture)
7. [Common Tasks](#common-tasks)
8. [Troubleshooting](#troubleshooting)

---

## Environment Setup

### Prerequisites

- **Node.js:** 14.0+ (18+ recommended)
- **VSCode:** 1.85.0+
- **Git:** Latest version
- **npm:** 6.0+

### Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/nsin08/ai_agents.git
   cd ai_agents/vscode-extension/v1
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Verify Installation**
   ```bash
   npm run compile
   npm test
   ```

---

## Project Structure

### Directory Layout

```
vscode-extension/v1/
├── src/                           # TypeScript source
│   ├── extension.ts              # Extension entry point
│   ├── panels/                   # UI components (Webviews)
│   │   ├── ChatPanel.ts
│   │   ├── ConfigPanel.ts
│   │   ├── StatisticsPanel.ts
│   │   ├── TraceViewerPanel.ts
│   │   ├── CodeSuggestionPanel.ts
│   │   ├── MultiAgentDashboard.ts
│   │   ├── ReasoningPanel.ts
│   │   ├── HistoryBrowserPanel.ts
│   │   └── SettingsPanel.ts
│   ├── services/                 # Business logic
│   │   ├── AgentService.ts
│   │   ├── ConfigService.ts
│   │   ├── MetricsService.ts
│   │   ├── TraceService.ts
│   │   ├── ExportService.ts
│   │   ├── HistoryService.ts
│   │   ├── CodeContextService.ts
│   │   ├── CodeInsertionService.ts
│   │   ├── MultiAgentCoordinator.ts
│   │   └── agents/
│   │       ├── PlannerAgent.ts
│   │       ├── ExecutorAgent.ts
│   │       └── VerifierAgent.ts
│   ├── models/                   # Type definitions
│   │   ├── AgentRole.ts
│   │   ├── AgentMessage.ts
│   │   ├── Statistics.ts
│   │   ├── Trace.ts
│   │   └── History.ts
│   └── views/                    # HTML templates
│       ├── chatView.html
│       ├── configView.html
│       └── [other UI templates]
├── tests/                        # Test suites (189 tests)
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── dist/                         # Compiled JavaScript (generated)
├── package.json                  # Dependencies & scripts
├── tsconfig.json                 # TypeScript config
├── jest.config.js               # Test configuration
└── README.md                     # ← Start here
```

### Key Files

| File | Purpose |
|------|---------|
| **src/extension.ts** | Entry point, command registration, panel lifecycle |
| **src/services/AgentService.ts** | Core agent communication |
| **src/services/MultiAgentCoordinator.ts** | Multi-agent orchestration |
| **src/services/HistoryService.ts** | Conversation persistence |
| **package.json** | Dependencies, build scripts, manifest |

---

## Getting Started

### 1. Launch Development Mode

**Option A: Using VSCode (Recommended)**
```bash
# Open folder in VSCode
code vscode-extension/v1

# Press F5 (or Debug → Start Debugging)
# New VSCode window opens with extension loaded
```

**Option B: Using Command Line**
```bash
npm run watch    # Compile in watch mode
# In another terminal:
code --extensionDevelopmentPath=. .
```

### 2. Test the Extension

Once Extension Development Host opens:

1. **Open Command Palette:** `Ctrl+Shift+P`
2. **Type:** `Agent: Start Conversation`
3. **Chat panel opens** with mock provider active
4. **Test a message:** "Hello!"
5. **See response:** Extension working!

### 3. Make Your First Change

1. **Edit:** `src/panels/ChatPanel.ts`
2. **Change:** Something visual (UI message)
3. **Save:** Ctrl+S
4. **Reload:** `Ctrl+Shift+P` → `Developer: Reload Window`
5. **Verify:** Change appears in extension

---

## Available Commands

### Extension Commands

Users can run these via Command Palette (`Ctrl+Shift+P`):

| Command | Function | File |
|---------|----------|------|
| `Agent: Start Conversation` | Open chat panel | ChatPanel.ts |
| `Agent: Settings` | Open settings panel | SettingsPanel.ts |
| `Agent: Switch Model` | Change LLM model | AgentService.ts |
| `Agent: Show Statistics` | Display metrics | StatisticsPanel.ts |
| `Agent: Show Trace Viewer` | View execution traces | TraceViewerPanel.ts |
| `Agent: Send Code to Agent` | Analyze selected code | CodeSuggestionPanel.ts |
| `Agent: Show Code Suggestions` | View suggestions | CodeSuggestionPanel.ts |
| `Agent: Show Conversation History` | Browse history | HistoryBrowserPanel.ts |
| `Agent: Show Multi-Agent Dashboard` | Coordinate agents | MultiAgentDashboard.ts |
| `Agent: Reset Session` | Clear conversation | AgentService.ts |

### Build & Test Commands

```bash
# Compile TypeScript
npm run compile

# Compile in watch mode (auto-recompile on save)
npm run watch

# Run all tests
npm test

# Run specific test file
npm test -- tests/unit/test_file.test.ts

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch

# Lint code
npm run lint

# Auto-fix lint issues
npm run lint -- --fix

# Format code
npm run format

# Type check
npm run type-check

# Clean build
npm run clean

# Build for distribution
npm run compile && npm run package
```

---

## Debugging & Testing

### Debug Mode (F5)

When you press `F5`:
1. TypeScript compiles
2. Extension Development Host opens (new VSCode window)
3. Extension loads and activates
4. You can test features

**Debugging Tips:**
- **Breakpoints:** Click line number in VS editor
- **Watches:** Right panel → Debug → Add watch expression
- **Console:** Output panel shows logs
- **Reload:** `Ctrl+Shift+P` → `Developer: Reload Window`

### Developer Tools

In the Extension Development Host:
- **Show Console:** `Help → Toggle Developer Tools`
- **View Logs:** Output panel → Select "AI Agent Extension"
- **Check Errors:** Problems panel (`Ctrl+Shift+M`)

### Running Tests

```bash
# All tests
npm test

# One test file
npm test -- tests/unit/AgentService.test.ts

# Tests matching pattern
npm test -- -t "should save conversation"

# Coverage report
npm test -- --coverage
```

**Test Output:**
```
 PASS  tests/unit/AgentService.test.ts
 PASS  tests/services/HistoryService.test.ts
 ...
Test Suites: 14 passed, 14 total
Tests:       189 passed, 189 total
```

---

## Project Architecture

### Communication Flow

```
User Input (Chat Panel)
    ↓
AgentService.sendMessage()
    ↓
Agent Provider (Ollama/OpenAI/etc.)
    ↓
Response Processing
    ↓
Update Chat Panel UI
    ↓
Save to HistoryService
    ↓
Record in MetricsService & TraceService
```

### Service Layer

**Core Services:**

1. **AgentService** - LLM communication
   - Manages conversations
   - Handles providers
   - Persists sessions

2. **HistoryService** - Conversation storage
   - Saves conversations
   - Indexes for search
   - Manages workspace folders

3. **MetricsService** - Usage tracking
   - Token counting
   - Cost calculation
   - Response timing

4. **TraceService** - Execution tracing
   - Records agent states
   - Tracks tool usage
   - Performance metrics

5. **ExportService** - Output formatting
   - CSV/JSON metrics
   - Markdown/HTML conversations
   - File management

6. **MultiAgentCoordinator** - Agent orchestration
   - Task decomposition
   - Agent routing
   - Result aggregation

### Panel Layer (UI)

Each panel is a webview component:
- **ChatPanel** - Conversation interface
- **SettingsPanel** - Configuration UI
- **StatisticsPanel** - Metrics dashboard
- **HistoryBrowserPanel** - Conversation browser
- **MultiAgentDashboard** - Agent coordination UI

Communication: `panel.webview.postMessage()` ↔️ Message handler

---

## Common Tasks

### Add a New Command

1. **Edit `package.json`:**
   ```json
   "contributes": {
     "commands": [
       {
         "command": "ai-agent.myNewCommand",
         "title": "Agent: My New Command"
       }
     ]
   }
   ```

2. **Register in `src/extension.ts`:**
   ```typescript
   context.subscriptions.push(
     vscode.commands.registerCommand('ai-agent.myNewCommand', async () => {
       // Your implementation
     })
   );
   ```

3. **Test:** `Ctrl+Shift+P` → `Agent: My New Command`

### Add a New Service

1. **Create:** `src/services/MyService.ts`
   ```typescript
   export class MyService {
     constructor(context: vscode.ExtensionContext) {
       // Initialize
     }

     public async doSomething(): Promise<void> {
       // Implementation
     }
   }
   ```

2. **Register in `extension.ts`:**
   ```typescript
   const myService = new MyService(context);
   ```

3. **Use:** Inject into panels that need it

4. **Test:** Add test file `tests/unit/MyService.test.ts`

### Add a New Panel

1. **Create panel file:** `src/panels/MyPanel.ts`
   ```typescript
   export class MyPanel {
     private panel: vscode.WebviewPanel;

     constructor(extensionUri: vscode.Uri) {
       this.panel = vscode.window.createWebviewPanel(/*...*/);
     }

     public async show(): Promise<void> {
       this.panel.reveal();
     }
   }
   ```

2. **Create HTML view:** `src/views/myPanel.html`

3. **Register in `extension.ts`:**
   ```typescript
   const myPanel = new MyPanel(context.extensionUri);
   context.subscriptions.push(
     vscode.commands.registerCommand('ai-agent.showMyPanel', () => {
       myPanel.show();
     })
   );
   ```

4. **Test:** Create test file in `tests/panels/MyPanel.test.ts`

### Run Linter & Format

```bash
# Check for issues
npm run lint

# Auto-fix issues
npm run lint -- --fix

# Format code
npm run format
```

---

## Troubleshooting

### Extension Not Loading (F5 Fails)

**Problem:** Extension Development Host doesn't open or crashes

**Solutions:**
```bash
# 1. Clean and rebuild
npm run clean
npm install
npm run compile

# 2. Check TypeScript errors
npm run compile -- --noEmit

# 3. Check test suite
npm test

# 4. Verify dependencies
npm ls
```

### Changes Not Appearing

**Problem:** Code changes don't show in extension

**Solutions:**
1. **Reload window:** `Ctrl+Shift+P` → `Developer: Reload Window`
2. **Restart debug session:** Stop (Shift+F5) and restart (F5)
3. **Check compile errors:** See Output panel for TS errors

### Tests Failing

**Problem:** `npm test` fails

**Solutions:**
```bash
# Run specific failing test
npm test -- -t "test name"

# See full error details
npm test -- --verbose

# Check test file for issues
npm test -- tests/path/to/test.test.ts
```

### Type Errors in IDE

**Problem:** Red squiggles in VSCode editor

**Solutions:**
```bash
# Generate type definitions
npm run compile

# Check TypeScript strict mode
npx tsc --strict --noEmit

# Reload VSCode window
Ctrl+Shift+P → Developer: Reload Window
```

### Memory/Performance Issues

**Problem:** Extension is slow or crashes

**Solutions:**
- Close other extensions
- Reduce `agentMaxTurns` setting (Agent: Settings)
- Use smaller models (e.g., mistral instead of larger)
- Enable debug mode to see bottlenecks

---

## Next Steps

- 📖 **Build for distribution:** See [BUILD.md](BUILD.md)
- 🤝 **Contributing code:** See [CONTRIBUTING.md](CONTRIBUTING.md)
- 🧪 **Testing guide:** See [TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md)
- ⚡ **Quick verification:** See [SANITY_TESTS.md](SANITY_TESTS.md)
- 👤 **User docs:** See [README.md](README.md) → User section

---

## Resources

### Official Documentation
- [VSCode Extension API](https://code.visualstudio.com/api)
- [Webview API](https://code.visualstudio.com/api/extension-guides/webview)
- [Extension Manifest](https://code.visualstudio.com/api/references/extension-manifest)

### Project Documentation
- [README.md](README.md) - Project overview
- [BUILD.md](BUILD.md) - Building & packaging
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [.context/](.context/) - Internal documentation

### Community
- [GitHub Issues](https://github.com/nsin08/ai_agents/issues)
- [GitHub Discussions](https://github.com/nsin08/ai_agents/discussions)

---

## 📚 Related Guides

- **[README.md](README.md)** ← Main documentation hub
- **[BUILD.md](BUILD.md)** ← Building, testing, packaging, deployment
- **[CONTRIBUTING.md](CONTRIBUTING.md)** ← Code standards, PR process, contribution workflow
- **[TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md)** ← Testing strategies and coverage

---

**Back to:** [README.md](README.md)

