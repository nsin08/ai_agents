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

### Phase 3 - ✅ Completed (Issue #76)
- **Code Intelligence**: Send code selections to agent with context
- **Security Filtering**: Detects 15 sensitive data patterns (API keys, tokens, passwords)
- **File Type Blocking**: Prevents sending credential files (.env, .pem, .key)
- **Code Suggestions Panel**: Display agent responses with syntax highlighting
- **Multiple Suggestions**: Navigate through multiple code blocks
- **Apply/Preview/Copy**: Insert suggestions with diff preview
- **Context Menu**: Right-click integration for quick access
- **Size Limits**: Enforces 10K lines / 500KB file size limits

### Bug Fixes (Issue #76)
- Fixed Trace Viewer showing wrong provider/model (now shows current session config)
- Fixed Statistics Panel displaying "Top" instead of "Current" provider/model
- Fixed conversation history displaying incorrect provider/model metadata

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
│   │   ├── TraceViewerPanel.ts  # Trace tree view
│   │   └── CodeSuggestionPanel.ts  # Code suggestions viewer (Phase 3)
│   ├── services/
│   │   ├── AgentService.ts   # Backend communication
│   │   ├── ConfigService.ts  # Settings management
│   │   ├── MetricsService.ts # Token/cost tracking
│   │   ├── TraceService.ts   # State transition capture
│   │   ├── ExportService.ts  # CSV/JSON export
│   │   ├── CodeContextService.ts   # Code extraction & security (Phase 3)
│   │   └── CodeInsertionService.ts # Code parsing & insertion (Phase 3)
│   ├── models/
│   │   ├── Statistics.ts     # Metrics data models
│   │   └── Trace.ts          # Trace data models
│   └── views/
│       ├── chatView.html     # Chat UI template
│       └── configView.html   # Config UI template
├── webview/
│   └── src/                  # Frontend code for webviews
├── tests/                    # 150 tests (9 suites)
│   ├── unit/                 # 137 unit tests
│   └── integration/          # 13 integration tests
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
npm test             # Run all tests (150 tests)
npm test -- --watch  # Watch mode
npm run lint         # Lint code
```

**Test Coverage:** 150 tests across 9 suites
- **Phase 1:** 15 tests (MVP Chat)
- **Phase 2:** 51 tests (Observability)
- **Phase 3:** 84 tests (Code Intelligence + Bug Fixes)

See [TESTING.md](TESTING.md) for comprehensive testing guide.

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
| Agent: Send Selection to Agent | Right-click | Send selected code with context (Phase 3) |
| Agent: Send File to Agent | Right-click | Send entire file with metadata (Phase 3) |
| Agent: Show Code Suggestions | `Ctrl+Shift+P` | Display code suggestions panel (Phase 3) |
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
**Phase 1 (MVP Chat):**
- [x] Side panel chat component renders
- [x] Configuration UI displays
- [x] Messages send and display
- [x] Session persists across restarts
- [x] Command palette integration works
- [x] All tests passing (15/15)
- [x] Documentation complete
- [x] PR merged to develop

**Phase 2 (Observability):**
- [x] Statistics panel with metrics
- [Usage Examples

### Send Code to Agent
1. Select code in editor
2. Right-click → "Agent: Send Selection to Agent"
3. Chat panel opens with formatted code
4. Agent analyzes and provides suggestions

### Apply Code Suggestions
1. Get agent response with code blocks
2. Command: "Agent: Show Code Suggestions"
3. Review suggestions with syntax highlighting
4. Click "Apply to Editor" or "Preview Diff"

### Monitor Agent Behavior
1. Command: "Agent: Show Trace Viewer"
2. Expand conversation nodes
3. View state transitions (Observe → Plan → Act → Verify)
4. Export traces for analysis

### Track Metrics
1. Command: "Agent: Show Statistics"
2. View token usage, response times, costs
3. Monitor current provider/model
4. Export to CSV for reporting

## Security Features

- **15 Sensitive Data Patterns**: API keys, tokens, passwords, credit cards, JWT, GitHub/OpenAI/Google keys
- **11 Blocked File Types**: .env, .pem, .key, .p12, .pfx, .crt, and more
- **User Warnings**: Alerts before sending sensitive data
- **Size Limits**: 10,000 lines / 500KB per operation
- **No External Telemetry**: All data stays local

## Next Steps

**Phase 3 Completed! ✅**

1. ✅ All features implemented
2. ✅ All tests passing (150/150)
3. ✅ Bug fixes validated
4. ✅ Documentation updated
5. ⏭️ Create PR to feature/74-phase-1-mvp-chat-panel
6. ⏭️ Request code review
7. ⏭️ Merge to develop after approval

**Phase 3 (Code Intelligence):**
- [x] Code context extraction
- [x] Sensitive data detection (15 patterns)
- [x] File type blocking (11 types)
- [x] Code suggestion display panel
- [x] Apply/Preview/Copy functionality
- [x] Context menu integration
- [x] Size limit enforcement
- [x] Bug fixes (3 issues)
- [x] All tests passing (150/150)
- [x] Documentation complete
- [x] Ready for PR review

**Overall:**
- [x] All 3 phases implemented
- [x] 150/150 tests passing
- [x] No TypeScript compilation errors
- [x] All acceptance criteria met
- [x] Security audit passed
- [x] Performance acceptable
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
