"""Tests for ModelFactory role mapping."""

from __future__ import annotations

import pytest

from agent_core.config.models import ModelSpec
from agent_core.factories import ModelFactory
from agent_core.registry import get_global_registry


def test_model_factory_build_role_map_builds_providers() -> None:
    factory = ModelFactory(get_global_registry().model_providers)
    roles = {
        "actor": {"provider": "mock", "model": "deterministic"},
        "planner": {"provider": "mock", "model": "deterministic"},
    }

    providers = factory.build_role_map(roles)

    assert set(providers.keys()) == {"actor", "planner"}
    assert providers["actor"].__class__.__name__ == "MockProvider"


def test_model_factory_build_role_map_accepts_model_spec() -> None:
    factory = ModelFactory(get_global_registry().model_providers)
    roles = {
        "actor": ModelSpec(provider="mock", model="deterministic"),
    }

    providers = factory.build_role_map(roles)

    assert providers["actor"].__class__.__name__ == "MockProvider"


def test_model_factory_drops_none_fields_for_provider_kwargs() -> None:
    factory = ModelFactory(get_global_registry().model_providers)
    roles = {
        # ModelSpec includes api_key_env/base_url/etc; most are None here and must
        # not be forwarded as kwargs to providers that don't accept them.
        "actor": ModelSpec(provider="ollama", model="mistral:7b"),
    }

    providers = factory.build_role_map(roles)

    assert providers["actor"].__class__.__name__ == "OllamaProvider"


def test_model_factory_build_role_map_requires_provider_key() -> None:
    factory = ModelFactory(get_global_registry().model_providers)

    with pytest.raises(ValueError, match="missing provider key"):
        factory.build_role_map({"actor": {"model": "deterministic"}})
