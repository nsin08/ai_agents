.PHONY: help setup run test lint format type-check clean install-all install-dev

SHELL := /bin/bash
VENV_DIR := .venv

help:
	@echo "Interactive Agent Playground - Make Commands"
	@echo "=============================================="
	@echo ""
	@echo "setup              - Set up environment with uv"
	@echo "run                - Run interactive agent"
	@echo "test               - Run tests"
	@echo "test-cov           - Run tests with coverage"
	@echo "lint               - Run ruff linter"
	@echo "lint-fix           - Fix linting issues"
	@echo "format             - Format code with black"
	@echo "type-check         - Run mypy type checking"
	@echo "check              - Run all checks (lint, format, type)"
	@echo "install-dev        - Install dev dependencies"
	@echo "install-ollama     - Install Ollama support"
	@echo "install-all        - Install all dependencies"
	@echo "clean              - Remove virtual environment and cache"
	@echo "clean-cache        - Remove only cache files"
	@echo ""

setup:
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "✓ Virtual environment already exists"; \
	else \
		echo "📦 Creating virtual environment..."; \
		uv venv --python 3.11 $(VENV_DIR); \
	fi
	@echo "📥 Installing base dependencies..."
	@uv pip install -r requirements.txt
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Activate environment:"
	@echo "  source $(VENV_DIR)/bin/activate"

run: setup
	@echo "🚀 Starting Interactive Agent Playground..."
	@python interactive_agent.py

test: setup
	@echo "🧪 Running tests..."
	@python -m pytest tests/ -v

test-cov: setup
	@echo "📊 Running tests with coverage..."
	@python -m pytest tests/ --cov=interactive_agent --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

lint: setup
	@echo "🔍 Running linter..."
	@python -m ruff check interactive_agent.py

lint-fix: setup
	@echo "🔧 Auto-fixing linting issues..."
	@python -m ruff check interactive_agent.py --fix

format: setup
	@echo "🎨 Formatting code..."
	@python -m black interactive_agent.py

type-check: setup
	@echo "🔬 Type checking..."
	@python -m mypy interactive_agent.py

check: lint type-check format
	@echo "✅ All checks passed!"

install-dev: setup
	@echo "🔧 Installing development tools..."
	@uv pip install mypy black ruff
	@echo "✅ Dev tools installed!"

install-ollama: setup
	@echo "📦 Installing Ollama support..."
	@uv pip install requests>=2.31.0
	@echo "✅ Ollama support installed!"

install-all: setup install-dev install-ollama
	@echo "✅ All dependencies installed!"

clean:
	@echo "🧹 Cleaning up..."
	@rm -rf $(VENV_DIR)
	@rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	@rm -rf htmlcov .coverage
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete!"

clean-cache:
	@echo "🧹 Cleaning cache files..."
	@rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	@rm -rf htmlcov .coverage
	@echo "✅ Cache cleanup complete!"

.DEFAULT_GOAL := help
