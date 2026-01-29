# AI Agent VSCode Extension - Quick Reference

**Version:** 0.1.0 | **Status:** Ready to Install

---

## 🚀 Install in 30 Seconds

### Method 1: Drag & Drop (Easiest)
```
1. Ctrl+Shift+X (Open Extensions)
2. Drag ai-agent-extension.vsix into panel
3. Click Install
Done! ✅
```

### Method 2: Command Line
```bash
code --install-extension ./ai-agent-extension.vsix
```

### Method 3: VSCode Menu
```
Extensions (Ctrl+Shift+X)
⋯ Menu → Install from VSIX
Select ai-agent-extension.vsix → Open
```

---

## ⚡ Quick Start (First 5 Minutes)

### 1. Configure Provider
```
Ctrl+Shift+P → Agent: Settings
→ Select Provider (Ollama, OpenAI, etc.)
→ Save
```

**No API Key?** Use **Mock** mode for testing.

**Want Local LLM?** 
- Download: https://ollama.ai
- Run: `ollama serve`
- Select: Ollama in settings

### 2. Start Chat
```
Ctrl+Shift+P → Agent: Start Conversation
→ Type your message
→ Get instant response
```

### 3. Explore
- **Code Help:** Right-click code → `Agent: Send Code to Agent`
- **Statistics:** View tokens, costs, timing
- **History:** Search past conversations
- **Multi-Agent:** Advanced task coordination

---

## 🎮 Key Commands

| Action | Command |
|--------|---------|
| Open Chat | `Agent: Start Conversation` |
| Configure | `Agent: Settings` |
| Code Suggestions | Right-click code → `Agent: Send Code to Agent` |
| Statistics | `Agent: Show Statistics` |
| History | `Agent: Show Conversation History` |
| Multi-Agent | `Agent: Show Multi-Agent Dashboard` |
| Reload | `Developer: Reload Window` |

---

## 🔧 Common Configurations

### Local Development (Ollama)
```json
{
  "provider": "Ollama",
  "model": "mistral",
  "baseUrl": "http://localhost:11434"
}
```

### OpenAI Cloud
```json
{
  "provider": "OpenAI",
  "model": "gpt-4",
  "apiKey": "sk-..."
}
```

### Testing (No API)
```json
{
  "provider": "Mock",
  "model": "mock-model"
}
```

---

## ❓ Common Issues

### "Commands not appearing"
```
Ctrl+Shift+P → Developer: Reload Window
```

### "Can't connect to Ollama"
```bash
# Check Ollama is running
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

### "Slow or crashing"
- Reduce Max Turns: Settings → 3-5
- Use smaller model: mistral instead of larger
- Close other extensions

### "Settings not saving"
```
Check JSON syntax (no trailing commas)
Reload: Ctrl+Shift+P → Developer: Reload Window
```

---

## 📚 Documentation

| Need | Link |
|------|------|
| **Full Setup** | [VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md) |
| **Release Info** | [RELEASE_v0.1.0.md](RELEASE_v0.1.0.md) |
| **Features** | [README.md](README.md) |
| **Testing** | [TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md) |
| **Quick Tests** | [SANITY_TESTS.md](SANITY_TESTS.md) |

---

## 🎯 Use Cases

### Case 1: Code Review Help
```
1. Open file in editor
2. Select code section
3. Right-click → Agent: Send Code to Agent
4. Ask: "Review this code for bugs"
5. Get suggestions in Code Suggestion panel
6. Apply with diff preview
```

### Case 2: Learn Something New
```
1. Start conversation
2. Ask: "Explain how REST APIs work"
3. Follow-up: "Show me an example"
4. Export conversation to HTML
5. Share with team
```

### Case 3: Complex Task Planning
```
1. Open Multi-Agent Dashboard
2. Submit: "Design a caching strategy for [system]"
3. Watch 3 agents collaborate:
   - Planner: "Here's my approach..."
   - Executor: "I'll implement..."
   - Verifier: "Quality looks good"
4. Review reasoning chains
5. Export results
```

### Case 4: Analyze Project Code
```
1. Select large code block
2. Ask: "What does this module do?"
3. Follow-up: "How can we optimize?"
4. Get suggestions with impact analysis
5. Apply and test
```

---

## 💾 What Gets Stored

### On Your Computer
- Chat history: `.vscode/agent-history/`
- Settings: VSCode settings.json
- Metrics: Session statistics

### Not Sent to Cloud (by default)
- Using Ollama? Everything local ✅
- Using OpenAI? Only prompts sent (encrypted)
- Code sensitive? Filter in settings

---

## 🔐 Privacy & Security

### Built-in Protections
- ✅ Detects 15 types of secrets (API keys, tokens, passwords)
- ✅ Blocks credential files (.env, .pem, .key)
- ✅ XSS protection in HTML exports
- ✅ Input validation on all providers

### Your Control
- Choose where LLM runs (local vs cloud)
- Configure what gets sent
- Delete history anytime
- Use settings to filter sensitive patterns

---

## 📊 What's Included (v0.1.0)

✅ Chat panel  
✅ Provider/model switching  
✅ Code intelligence  
✅ Security filtering  
✅ Statistics dashboard  
✅ Trace viewer  
✅ Export (CSV/JSON/Markdown/HTML)  
✅ Multi-agent orchestration  
✅ Conversation history  
✅ 189 automated tests  

---

## 🆘 Get Help

### Documentation
- Read: [VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md)
- Search: Troubleshooting section

### GitHub
- Report bugs: https://github.com/nsin08/ai_agents/issues
- Ask questions: https://github.com/nsin08/ai_agents/discussions

### Logs
```
Help → Toggle Developer Tools → Console
(Look for red errors if something fails)
```

---

## 🎁 Features Preview

### Phase 1: MVP Chat
- Chat in sidebar
- Switch providers instantly
- Persist across restarts

### Phase 2: Observability
- Token usage tracker
- Cost calculator
- Trace visualizer
- Export metrics

### Phase 3: Code Intelligence
- Select code → get suggestions
- Security checks built-in
- Apply with diff preview
- 11 file types protected

### Phase 4: Multi-Agent
- 3 specialized agents
- Watch them collaborate
- See reasoning chains
- Per-agent metrics

### Phase 5: History
- Search past chats
- Filter by date/type/keyword
- Export as Markdown/HTML
- Privacy-focused storage

---

## ⚙️ Settings Quick Reference

```json
// In VSCode settings.json or Settings panel:

{
  "ai-agent.provider": "ollama",           // or openai, anthropic, google, azure
  "ai-agent.model": "mistral",             // varies by provider
  "ai-agent.baseUrl": "http://localhost:11434",  // Ollama only
  "ai-agent.apiKey": "${env:OPENAI_API_KEY}",   // Cloud providers
  "ai-agent.maxTurns": 5,                  // Agent response limit
  "ai-agent.timeout": 30                   // Seconds before timeout
}
```

---

## 📱 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+P` | Command Palette |
| `Ctrl+Shift+X` | Extensions Panel |
| `Ctrl+K Ctrl+0` | Fold All (organize chat) |
| Right-click | Context menu (for code agent) |

---

## 🔄 Update/Reinstall

### Update to New Version
```
Extensions (Ctrl+Shift+X) → AI Agent Interaction
→ If "Update" shows, click it
→ Reload VSCode
```

### Uninstall
```
Extensions → AI Agent Interaction
→ Gear icon ⚙️ → Uninstall
→ Reload VSCode
```

### Reinstall
```
Download ai-agent-extension.vsix (v0.1.0)
code --install-extension ./ai-agent-extension.vsix
```

---

## 📞 Support

**Need Help?**
1. Check [VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md) Troubleshooting
2. Search [GitHub Issues](https://github.com/nsin08/ai_agents/issues)
3. Create [New Issue](https://github.com/nsin08/ai_agents/issues/new) with error details

**Found a Bug?**
Include:
- VSCode version (Help → About)
- What you were doing
- Error message from Console
- Steps to reproduce

---

## ✨ Pro Tips

1. **Use Ollama locally** - No API keys needed, faster, private
2. **Export conversations** - Great for documentation
3. **Enable debug mode** - See what agent is thinking
4. **Bookmark common prompts** - Create snippets for reuse
5. **Start simple** - Test with "Hello!" before complex tasks

---

## 🎊 You're All Set!

```
1. ✅ Installed extension
2. ✅ Configured provider
3. ✅ Opened chat
4. ✅ Sent first message

Ready to use AI agents in VSCode! 🚀
```---

**File:** `ai-agent-extension.vsix` (1.11 MB)  
**Version:** 0.1.0  
**Status:** Production Ready ✅  
**Support:** [GitHub Issues](https://github.com/nsin08/ai_agents/issues)

---

## 📚 Related Resources

- **[README.md](README.md)** ← Main documentation hub (start here)
- **[VSIX_INSTALLATION_GUIDE.md](VSIX_INSTALLATION_GUIDE.md)** ← Detailed installation instructions
- **[RELEASE_v0.1.0.md](RELEASE_v0.1.0.md)** ← Release notes and changelog
- **[DEVELOPMENT.md](DEVELOPMENT.md)** ← For developers
- **[CONTRIBUTING.md](CONTRIBUTING.md)** ← For contributors

---

**Back to:** [README.md](README.md)

