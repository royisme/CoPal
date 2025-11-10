"""Configuration helpers for the memory subsystem."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_CONFIG: dict[str, Any] = {
    "backend": "networkx",
    "auto_capture": True,
    "database": ".copal/memory.db",
}


def load_memory_config(target_root: Path) -> dict[str, Any]:
    """Load memory configuration from `.copal/config.json` if available."""

    config_path = target_root / ".copal" / "config.json"
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()

    try:
        payload = json.loads(config_path.read_text())
    except json.JSONDecodeError:
        return DEFAULT_CONFIG.copy()

    memory_cfg = payload.get("memory", {}) if isinstance(payload, dict) else {}
    merged = DEFAULT_CONFIG.copy()
    for key, value in memory_cfg.items():
        merged[key] = value
    return merged


def resolve_database_path(target_root: Path, config: dict[str, Any]) -> Path:
    """Determine the persistence path for the memory database."""

    database_value = config.get("database", DEFAULT_CONFIG["database"])
    db_path = Path(database_value)
    if not db_path.is_absolute():
        db_path = target_root / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def is_memory_enabled(config: dict[str, Any]) -> bool:
    return bool(config.get("enabled", True))


def is_auto_capture_enabled(config: dict[str, Any]) -> bool:
    return bool(config.get("auto_capture", DEFAULT_CONFIG["auto_capture"]))
