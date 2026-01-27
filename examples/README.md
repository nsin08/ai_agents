# AgentCore Examples

These examples are runnable scripts that demonstrate AgentCore behavior.

Prerequisite (from repo root):

```bash
python -m pip install -e .
```

## Examples

Simple Q&A:

```bash
python examples/simple_qna.py --config examples/configs/mock.json "hello"
```

Tool use (calculator):

```bash
python examples/tool_use.py
```

Multi-turn conversation (shared session store):

```bash
python examples/multi_turn.py
# Optional: use a real provider config (requires Ollama/OpenAI setup)
python examples/multi_turn.py --config examples/configs/ollama.json "My name is Alice." "What is my name?"
```

## Example Configs

- `examples/configs/mock.json`
- `examples/configs/deterministic.json`
- `examples/configs/ollama.json`
- `examples/configs/openai.json`
