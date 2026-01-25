# AI Agent VSCode Extension

Interact with AI agents directly from VSCode with integrated configuration management.

## Features

### Phase 1 (MVP) - ✅ Completed
- **Chat Panel**: Dedicated sidebar panel for agent conversations
- **Configuration UI**: Switch providers, models, and settings without file editing
- **Command Palette**: Quick access to agent commands (`Ctrl+Shift+P`)
- **Session Management**: Conversation state persists across restarts

### Phase 2 - ✅ Completed
- **Statistics Panel**: Token usage, response times, and cost tracking with multi-provider support
- **Trace Viewer**: Agent state transition visualization (Observe → Plan → Act → Verify)
- **Auto-Refresh**: Toggle-able 2-second interval refresh for live trace monitoring
- **Export Functionality**: Export metrics and traces to CSV/JSON
- **Ollama Integration**: Direct API calls with automatic model detection
- **Provider-Specific UI**: Dynamic field behavior based on selected provider

### Phase 3 (Planned) - Issue #76
- **Code Intelligence**: Code selection, security filtering, insertion, and syntax highlighting

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
│   │   ├── ConfigPanel.ts    # Configuration panel
│   │   ├── StatisticsPanel.ts   # Metrics dashboard
│   │   └── TraceViewerPanel.ts  # Trace tree view
│   ├── services/
│   │   ├── AgentService.ts   # Backend communication
│   │   ├── ConfigService.ts  # Settings management
│   │   ├── MetricsService.ts # Token/cost tracking
│   │   ├── TraceService.ts   # State transition capture
│   │   └── ExportService.ts  # CSV/JSON export
│   ├── models/
│   │   ├── Statistics.ts     # Metrics data models
│   │   └── Trace.ts          # Trace data models
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
| Agent: Settings | `Ctrl+Shift+P` | Configure provider/model/settings |
| Agent: Reset Session | `Ctrl+Shift+P` | Clear conversation |
| Agent: Show Statistics | `Ctrl+Shift+P` | View metrics dashboard |
| Agent: Show Trace Viewer | `Ctrl+Shift+P` | View execution traces |

## Architecture

### Provider Support

- **Mock Provider**: Built-in, no backend required (instant responses for testing)
- **Ollama**: Direct API integration via `callOllamaAPI()` method
  - Auto-detects installed models from `/api/tags` endpoint
  - Dynamic dropdown model selection
  - Default endpoint: `http://localhost:11434`
- **Cloud Providers**: OpenAI, Anthropic, Google, Azure OpenAI
  - Requires API key configuration
  - Cost tracking per provider

### Backend Communication

The extension communicates with agents via:
- **Direct Ollama API** (localhost:11434)
- **HTTP API** (web/backend for other providers)
- **Mock responses** (testing/development)
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
