# AI Agent VSCode Extension

Interact with AI agents directly from VSCode with integrated configuration management.

## Features

### Phase 1 (MVP) - Current
- **Chat Panel**: Dedicated sidebar panel for agent conversations
- **Configuration UI**: Switch providers, models, and settings without file editing
- **Command Palette**: Quick access to agent commands (`Ctrl+Shift+P`)
- **Session Management**: Conversation state persists across restarts

### Phase 2 (Planned)
- Statistics panel with token usage, response times, and cost tracking
- Trace viewer for agent state transitions

### Phase 3 (Planned)
- Code context awareness (send selected code to agent)
- Multi-agent orchestration dashboard
- Conversation history search and replay

## Installation

1. Clone the repository
2. Navigate to `vscode-extension` folder
3. Install dependencies: `npm install`
4. Compile: `npm run compile`
5. Press `F5` to launch the extension in debug mode

## Development

### Project Structure

```
vscode-extension/
├── src/
│   ├── extension.ts          # Extension entry point
│   ├── panels/
│   │   ├── ChatPanel.ts      # Chat side panel
│   │   └── ConfigPanel.ts    # Configuration panel
│   ├── services/
│   │   ├── AgentService.ts   # Backend communication
│   │   └── ConfigService.ts  # Settings management
│   └── views/
│       ├── chatView.html     # Chat UI template
│       └── configView.html   # Config UI template
├── webview/
│   └── src/                  # Frontend code for webviews
├── tests/                    # Test files
└── package.json
```

### Building

```bash
npm install
npm run compile      # One-time compile
npm run watch        # Watch mode during development
```

### Testing

```bash
npm test             # Run all tests
npm test -- --watch  # Watch mode
npm run lint         # Lint code
```

## Configuration

Settings available in VSCode Settings UI:

- **AI Agent: Provider** - Select LLM provider (mock, ollama, openai, etc.)
- **AI Agent: Model** - Model name
- **AI Agent: Base URL** - Ollama endpoint (default: http://localhost:11434)
- **AI Agent: API Key** - Cloud provider API key
- **AI Agent: Max Turns** - Maximum conversation turns
- **AI Agent: Timeout** - Request timeout in seconds

## Commands

| Command | Shortcut | Description |
|---------|----------|-------------|
| Agent: Start Conversation | `Ctrl+Shift+P` | Open chat panel |
| Agent: Switch Provider | `Ctrl+Shift+P` | Change LLM provider |
| Agent: Switch Model | `Ctrl+Shift+P` | Change model |
| Agent: Reset Session | `Ctrl+Shift+P` | Clear conversation |

## Architecture

### Backend Communication

The extension communicates with the Python agent backend via:
- **HTTP API** (web/backend from PR #73)
- **Subprocess** (local agent_labs execution)
- **LSP Protocol** (Language Server Protocol, future)

### Session Management

Sessions are stored locally in VSCode global storage:
- Session ID
- Message history
- Configuration snapshot
- Timestamps

Sessions persist across VSCode restarts.

## Testing Strategy

### Unit Tests
- Configuration service tests
- Settings validation
- Message formatting

### Integration Tests
- Chat message sending/receiving
- Session persistence
- Provider switching
- Error handling

### E2E Tests
- Full chat workflow
- Configuration changes taking effect
- Command palette execution

## Definition of Done

- [x] Side panel chat component renders
- [x] Configuration UI displays
- [ ] Messages send and display
- [ ] Session persists across restarts
- [ ] Command palette integration works
- [ ] All tests passing
- [ ] Documentation complete
- [ ] PR ready for review

## Next Steps

1. Implement chat message sending
2. Add session persistence
3. Write comprehensive tests
4. Create PR linking to Story #74

## References

- [VSCode Extension API](https://code.visualstudio.com/api)
- [Webview API](https://code.visualstudio.com/api/extension-guides/webview)
- [Agent Labs Python Backend](../web/backend/)
