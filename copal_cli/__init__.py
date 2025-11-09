"""CoPal CLI package."""

from __future__ import annotations

from typing import Any

__all__ = ["main"]


def __getattr__(name: str) -> Any:  # pragma: no cover - simple lazy loader
    if name == "main":
        from .cli import main as cli_main

        return cli_main
    raise AttributeError(name)
