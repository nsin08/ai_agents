"""Plugin discovery and loading via entry points."""

from __future__ import annotations

from importlib import metadata
from typing import Iterable, List

from .exceptions import PluginDependencyError, PluginLoadError, PluginNotFoundError

ENTRY_POINT_GROUP = "ai_agents.agent_core.plugins"

_loaded_plugins: set[str] = set()


def _iter_entry_points() -> List[metadata.EntryPoint]:
    entry_points = metadata.entry_points()
    if hasattr(entry_points, "select"):
        return list(entry_points.select(group=ENTRY_POINT_GROUP))
    return list(entry_points.get(ENTRY_POINT_GROUP, []))


def _install_hint(key: str) -> str:
    return f"Install ai_agents[{key}] to enable '{key}'."


def load_plugin(key: str, registry: object | None = None) -> None:
    if key in _loaded_plugins:
        return

    if registry is None:
        from .registry import get_global_registry

        registry = get_global_registry()

    for entry_point in _iter_entry_points():
        if entry_point.name != key:
            continue

        try:
            plugin = entry_point.load()
        except ModuleNotFoundError as exc:
            raise PluginDependencyError(_install_hint(key)) from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise PluginLoadError(f"Failed to load plugin '{key}': {exc}") from exc

        try:
            if callable(plugin):
                plugin(registry)
            elif hasattr(plugin, "register"):
                plugin.register(registry)
            else:
                raise PluginLoadError(
                    f"Plugin '{key}' does not define register(registry)."
                )
        except ModuleNotFoundError as exc:
            raise PluginDependencyError(_install_hint(key)) from exc
        except PluginLoadError:
            raise
        except Exception as exc:
            raise PluginLoadError(f"Plugin '{key}' failed to register: {exc}") from exc

        _loaded_plugins.add(key)
        return

    raise PluginNotFoundError(
        f"No plugin found for key '{key}' in entry points '{ENTRY_POINT_GROUP}'."
    )


__all__ = ["ENTRY_POINT_GROUP", "load_plugin"]
