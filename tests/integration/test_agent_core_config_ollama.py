"""
Integration tests for agent_core config with Ollama.

Requires:
- Ollama running at http://localhost:11434
- A phi* or llama2 model installed
"""

from __future__ import annotations

import os

import pytest
import httpx

from agent_core.config import load_config


pytestmark = pytest.mark.ollama

SKIP_OLLAMA = os.getenv("SKIP_OLLAMA", "false").lower() == "true"


def _get_available_models(base_url: str) -> list[str]:
    try:
        resp = httpx.get(f"{base_url}/api/tags", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        return []


def _select_model(names: list[str]) -> str | None:
    for name in names:
        if name.startswith("phi") or name == "llama2" or name.startswith("llama2:"):
            return name
    return None


@pytest.mark.skipif(SKIP_OLLAMA, reason="Ollama tests disabled (set SKIP_OLLAMA=false to run)")
def test_load_config_with_ollama_role(monkeypatch):
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    models = _get_available_models(base_url)
    selected = _select_model(models)
    if not selected:
        pytest.skip("No phi* or llama2 model found in Ollama. Pull one to run this test.")

    monkeypatch.setenv("AGENT_CORE_MODE", "real")
    monkeypatch.setenv("AGENT_CORE_MODELS__ROLES__ACTOR__PROVIDER", "ollama")
    monkeypatch.setenv("AGENT_CORE_MODELS__ROLES__ACTOR__MODEL", selected)
    monkeypatch.setenv("AGENT_CORE_MODELS__ROLES__ACTOR__BASE_URL", base_url)

    config = load_config(load_dotenv_file=False)
    assert config.mode == "real"
    assert config.models.roles["actor"].provider == "ollama"
    assert config.models.roles["actor"].model == selected
    assert config.models.roles["actor"].base_url == base_url
