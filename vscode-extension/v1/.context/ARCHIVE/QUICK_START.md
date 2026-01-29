⚠️ **DEPRECATED:** This guide has been superseded. See [DEVELOPMENT.md](../../DEVELOPMENT.md) for current setup instructions.

---

# VSCode AI Agent Extension - Quick Start (ARCHIVED)

This document is archived for reference only. For current instructions, see [DEVELOPMENT.md](../../DEVELOPMENT.md).

## Running the Extension

### 1. Debug Mode (F5)
Press `F5` to launch the Extension Development Host with the extension loaded.

### 2. Provider Configuration

The extension supports multiple providers:

#### **Mock Provider** (Default - No backend needed)
- Good for testing UI without external dependencies
- Instant responses
- No setup required

#### **Ollama Provider** (Local LLM)
1. Install Ollama: https://ollama.com/download
2. Pull a model: `ollama pull mistral:7b`
3. Start Ollama (runs automatically on Windows)
4. Configure in VSCode:
   - Open Command Palette (`Ctrl+Shift+P`)
   - Run: `Agent: Switch Provider`
   - Select: `ollama`
   - Set model: `mistral:7b`

#### **Cloud Providers** (OpenAI, Anthropic, etc.)
1. Get API key from provider
2. Configure in VSCode:
   - Settings → AI Agent → API Key
   - Settings → AI Agent → Provider → select provider
   - Settings → AI Agent → Model → set model name

## Available Commands

- `Agent: Start Conversation` - Open chat panel
- `Agent: Switch Provider` - Change LLM provider
- `Agent: Switch Model` - Change model
- `Agent: Reset Session` - Clear conversation history
- `Agent: Show Statistics` - View usage metrics
- `Agent: Show Trace Viewer` - View agent execution traces

## Default Settings

```json
{
  "aiAgent.provider": "mock",
  "aiAgent.model": "llama2",
  "aiAgent.baseUrl": "http://localhost:11434",
  "aiAgent.maxTurns": 5,
  "aiAgent.timeout": 30
}
```

## Testing

Run tests:
```bash
npm test
```

See [TESTING.md](./TESTING.md) for comprehensive test scenarios.

## Troubleshooting

### "Backend API error: ECONNREFUSED"
- This means the provider is trying to connect to a backend that isn't running
- **Solution**: Switch to `mock` provider in settings:
  1. `Ctrl+Shift+P` → `Preferences: Open Settings (JSON)`
  2. Add: `"aiAgent.provider": "mock"`
  3. Reload window: `Ctrl+Shift+P` → `Developer: Reload Window`

### Extension not loading
- Compile the extension: `npm run compile`
- Check Extension Host logs: `Help` → `Toggle Developer Tools` → `Console`

### Ollama connection issues
- Verify Ollama is running: `ollama list`
- Check endpoint: `curl http://localhost:11434/api/tags`
- Verify baseUrl in settings: `http://localhost:11434`
