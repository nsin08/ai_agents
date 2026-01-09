# Lab 0: Environment Setup

## Learning Objectives

- Set up a local Python 3.11 environment with `uv`.
- Run the sample hello agent.
- Execute lab tests and validate imports from `src/agent_labs/`.

## Prerequisites

- Python 3.11 installed
- Git
- `uv` installed

## Installation (Manual)

```bash
uv venv
uv pip install -r requirements.txt
```

## Installation (Script)

```bash
./labs/00/setup.sh
```

## Quick Start (<5 minutes)

```bash
uv venv
uv pip install -r requirements.txt
uv run python labs/00/src/hello_agent.py
uv run pytest labs/00/tests/test_hello_agent.py -v
```

## Run with Ollama (Optional)

```bash
$env:USE_OLLAMA='true'
$env:OLLAMA_MODEL='llama2'
$env:OLLAMA_BASE_URL='http://localhost:11434'
python labs/00/src/hello_agent.py
```

## UV Workflow

- Create venv: `uv venv`
- Install deps: `uv pip install -r requirements.txt`
- Run Python: `uv run python <script.py>`
- Run tests: `uv run pytest <path>`

## Lab Structure

```
labs/00/
  README.md
  Makefile
  .env.example
  src/
    hello_agent.py
  tests/
    test_hello_agent.py
  exercises/
    exercise_1.md
```

## Troubleshooting

- `uv` not found: install from https://github.com/astral-sh/uv
- Python 3.11 missing: install from https://www.python.org/downloads/
- Import error for `agent_labs`: run from repo root.

## Notes

- This lab must run before others.
- Use `.env.example` to set optional env vars.
