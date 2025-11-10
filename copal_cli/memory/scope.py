"""Scope resolution helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ScopeManager:
    """Tracks the active memory scope."""

    default_scope: str
    _current_scope: str | None = None

    @classmethod
    def from_config(cls, target_root: Path, config: dict[str, object]) -> ScopeManager:
        configured = config.get("scope") if isinstance(config, dict) else None
        if isinstance(configured, dict):
            default_scope = str(configured.get("default", target_root.name))
        elif isinstance(configured, str):
            default_scope = configured
        else:
            default_scope = target_root.name
        return cls(default_scope=default_scope, _current_scope=None)

    @property
    def current_scope(self) -> str:
        return self._current_scope or self.default_scope

    def set_scope(self, scope: str) -> None:
        self._current_scope = scope

    def resolve(self, override: str | None = None) -> str:
        if override:
            return override
        return self.current_scope
