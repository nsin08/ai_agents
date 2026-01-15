# Quick Reference - Interactive Agent Playground Setup

## 30-Second Setup

### Linux / macOS
```bash
cd scripts
chmod +x setup.sh
./setup.sh
source .venv/bin/activate
python interactive_agent.py
```

### Windows
```cmd
cd scripts
setup.bat
.venv\Scripts\activate.bat
python interactive_agent.py
```

## Or Use Make (Recommended)

```bash
make setup
make run
```

## Key Commands Inside Playground

| Command | Purpose |
|---------|---------|
| `/help` | Show all commands |
| `/config` | Show current settings |
| `/provider mock` | Use MockProvider (fast) |
| `/provider ollama` | Use OllamaProvider (real LLM) |
| `/reset` | Reset agent memory |
| `/history` | Show conversation |
| `/exit` | Quit |

## Installation Methods

### Method 1: Automated Script (Easiest)
```bash
./setup.sh          # Linux/macOS
setup.bat           # Windows
```

### Method 2: Manual with uv
```bash
uv venv --python 3.11 .venv
source .venv/bin/activate          # Linux/macOS
# or
.venv\Scripts\activate.bat          # Windows
uv pip install -r requirements.txt
```

### Method 3: Using Make (Quickest)
```bash
make setup          # Set up environment
make run            # Run agent
make test           # Run tests
make check          # Run all checks
```

## File Structure

```
scripts/
├── interactive_agent.py        ← Main REPL script
├── pyproject.toml             ← Project config
├── requirements.txt           ← Dependencies
├── .python-version            ← Python 3.11
├── .env.example               ← Config template
├── .gitignore                 ← Git ignores
├── setup.sh / setup.bat       ← Auto setup
├── Makefile                   ← Make commands
└── README.md                  ← Full documentation
```

## Environment Variables

Create `.env` file from `.env.example`:

```bash
cp .env.example .env
# Edit .env with your settings
```

Key variables:
- `OLLAMA_BASE_URL=http://localhost:11434` - Ollama service URL
- `OLLAMA_MODEL=mistral:7b` - LLM model name
- `AGENT_PROVIDER=ollama` - Provider type (mock/ollama)

## Providers

### MockProvider (Default)
- ⚡ Fast & free
- ✅ Deterministic
- ❌ Not real LLM

```
/provider mock
```

### OllamaProvider (Real)
- 🟡 Slower
- ✅ Real LLM
- Requires: Ollama running locally

```
/provider ollama
/model mistral:7b
```

## Installation Variations

### Minimal (just run script)
```bash
make setup
```

### With Dev Tools (lint, format, type-check)
```bash
make install-dev
```

### With Ollama Support (HTTP requests)
```bash
make install-ollama
```

### Everything
```bash
make install-all
```

## Troubleshooting

### Virtual environment not created
```bash
rm -rf .venv
make setup
```

### Module not found errors
```bash
# Ensure you're in scripts directory
cd scripts
source .venv/bin/activate
```

### Ollama connection refused
```bash
# In another terminal:
ollama serve
```

### Python version mismatch
```bash
# Check Python version
python --version  # Should be 3.11+

# Or create with specific version
uv venv --python 3.11 .venv
```

## Common Tasks

### Run Interactive Agent
```bash
make run
```

### Test Code
```bash
make test
make test-cov  # With coverage report
```

### Format & Lint
```bash
make format    # Auto-format with black
make lint-fix  # Fix linting issues
make check     # Run all checks
```

### Type Check
```bash
make type-check
```

### Clean Everything
```bash
make clean     # Remove venv and caches
make clean-cache  # Just remove caches
```

## Next Steps

1. ✅ Run `make setup` to initialize environment
2. ✅ Run `make run` to start interactive agent
3. ✅ Try commands: `/help`, `/config`, ask a question
4. ✅ Switch providers: `/provider mock` or `/provider ollama`
5. ✅ Run tests: `make test`
6. ✅ Check code: `make check`

## Resources

- **Ollama**: https://ollama.ai
- **uv**: https://github.com/astral-sh/uv
- **Project Docs**: ../../Agents/
- **Full README**: README.md (in this directory)

---

**Setup Time**: < 5 minutes  
**Status**: ✅ Ready to use
