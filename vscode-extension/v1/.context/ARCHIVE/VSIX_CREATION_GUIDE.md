⚠️ **DEPRECATED:** This guide has been superseded. See [BUILD.md](../../BUILD.md) for current VSIX creation instructions.

---

# VSIX Creation Guide (ARCHIVED)

This document is archived for reference only. For current instructions, see [BUILD.md](../../BUILD.md).

---

## Prerequisites (ARCHIVED)

- Node.js 18+
- VSCode
- `vsce` installed globally:

```bash
npm install -g @vscode/vsce
```

---

## Build & Package

From `vscode-extension/v1`:

```bash
npm install
npm run compile
vsce package
```

---

## Validate Extension

1. Launch Extension Development Host (`F5`).
2. Open **Agent: Settings** and configure provider/model.
3. Toggle **Debug Mode** if needed for verbose logs.
4. Run a short chat session and confirm responses.
5. Open **Agent: Show History** and export Markdown/HTML.
6. Run `npm test` to ensure full test suite passes.

---

## Debug Mode Notes

- Debug mode is now toggled inside **Agent: Settings**.
- The setting is stored per workspace (not VS Code settings).
- Environment override remains:

```bash
DEBUG_MULTI_AGENT=true npm run watch
```

---

## Troubleshooting

- If the extension fails to load, check **Extension Host** console.
- If no response, verify provider config in **Agent: Settings**.
- If Ollama models are empty, confirm Ollama is running on `http://localhost:11434`.

---

**Last Updated:** 2026-01-28
