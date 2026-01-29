⚠️ **DEPRECATED:** This guide has been superseded. See [DEVELOPMENT.md](../../DEVELOPMENT.md) for current setup instructions.

---

# VSCode Plugin Development Workflow (ARCHIVED)

This document is archived for reference only. For current instructions, see [DEVELOPMENT.md](../../DEVELOPMENT.md).

---

## 1. Environment Setup (ARCHIVED)

1. Install Node.js (18+ recommended)
2. Install VSCode
3. Clone repository and install dependencies:

```bash
cd vscode-extension/v1
npm install
```

---

## 2. Extension Development Host

1. Open VSCode in the `vscode-extension/v1` folder
2. Press `F5` to launch Extension Development Host
3. Use command palette to test features

---

## 3. Core Commands

| Command | Purpose |
|---------|---------|
| Agent: Start Conversation | Open chat panel |
| Agent: Settings | Configure providers, models, and debug toggle |
| Agent: Show Statistics | Open metrics dashboard |
| Agent: Show Trace Viewer | View traces |
| Agent: Show Multi-Agent Dashboard | View multi-agent coordination |
| Agent: Show History | Browse conversation history |

---

## 4. Configuration Workflow

1. Open `Agent: Settings`
2. Select **Single-Agent** or **Multi-Agent**
3. Configure provider/model for the selected mode
4. Toggle **Debug Mode** if verbose logging is needed
5. Click "Save Configuration"

---

## 5. Testing Workflow

- Quick validation: `SANITY_TESTS.md`
- Full validation: `TESTING_COMPREHENSIVE.md`
- Automated tests:

```bash
npm test
```

---

## 6. Debugging & Logging

### 6.1 Debug Configuration

- Debug mode is toggled from the **Agent: Settings** panel.
- It is stored per workspace (not in VS Code settings).
- Environment override:

```bash
DEBUG_MULTI_AGENT=true npm run watch
```

### 6.2 Console Output

- View output in **Extension Host** console
- Debug logs appear only when enabled

---

## 7. Build & Package

```bash
npm run compile
vsce package
```

---

## 8. Release Checklist

- ? Update README and testing docs
- ? Run `npm test`
- ? Validate history/export flows
- ? Create PR + link to issue

---

**Last Updated:** 2026-01-28
